"""
GUIメインウィンドウの実装
"""

import os
import sys
import time
import threading
from pathlib import Path

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QFileDialog, QMessageBox, QTabWidget,
        QTextEdit, QProgressBar, QComboBox, QCheckBox, QGroupBox,
        QStatusBar, QAction, QToolBar, QSplitter, QFrame
    )
    from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer, QDateTime
    from PyQt5.QtGui import QIcon, QPixmap, QImage, QFont
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False

from pdfexpy.utils.logger import get_logger
from pdfexpy.utils.screenshot import take_screenshot, ScreenshotError
from pdfexpy.models.model_loader import ModelLoader

logger = get_logger(__name__)


class WorkerThread(QThread):
    """
    バックグラウンド処理用のスレッドクラス
    """
    # シグナル定義
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(bool, object, str)
    
    def __init__(self, func, *args, **kwargs):
        """
        初期化
        
        Args:
            func (callable): 実行する関数
            *args: 関数に渡す位置引数
            **kwargs: 関数に渡すキーワード引数
        """
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
    
    def run(self):
        """
        スレッド実行メソッド
        """
        try:
            # 進捗シグナル処理の追加
            if 'progress_callback' not in self.kwargs and hasattr(self, 'progress_signal'):
                self.kwargs['progress_callback'] = self.progress_signal.emit
            
            # 関数実行
            result = self.func(*self.args, **self.kwargs)
            self.finished_signal.emit(True, result, "")
        except Exception as e:
            logger.error(f"ワーカースレッドでエラーが発生しました: {e}")
            self.finished_signal.emit(False, None, str(e))


class MainWindow(QMainWindow):
    """
    メインウィンドウクラス
    """
    def __init__(self, config=None):
        """
        初期化
        
        Args:
            config (dict, optional): アプリケーション設定
        """
        super().__init__()
        self.config = config or {}
        self.model_loader = None
        self.models_loaded = False
        
        # ウィンドウの基本設定
        self.setWindowTitle("PDFExPy - PDFとスクリーンショットの解析ツール")
        self.setMinimumSize(800, 600)
        
        # UIセットアップ
        self.init_ui()
        
        # 起動ログ
        logger.info("GUIアプリケーションを起動しました")
        self.log_message("アプリケーションを起動しました")
        
        # モデルローダーの初期化
        self.init_model_loader()
    
    def init_ui(self):
        """
        UIコンポーネントを初期化します
        """
        # 中央ウィジェット
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # メインレイアウト
        main_layout = QVBoxLayout(central_widget)
        
        # 上部コントロールエリア
        control_layout = QHBoxLayout()
        
        # スクリーンショットボタン
        self.screenshot_btn = QPushButton("スクリーンショット")
        self.screenshot_btn.setIcon(QIcon.fromTheme("camera-photo"))
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        control_layout.addWidget(self.screenshot_btn)
        
        # 画像読み込みボタン
        self.load_image_btn = QPushButton("画像を開く")
        self.load_image_btn.setIcon(QIcon.fromTheme("document-open"))
        self.load_image_btn.clicked.connect(self.load_image)
        control_layout.addWidget(self.load_image_btn)
        
        # 解析ボタン
        self.analyze_btn = QPushButton("画像を解析")
        self.analyze_btn.setIcon(QIcon.fromTheme("system-search"))
        self.analyze_btn.clicked.connect(self.analyze_image)
        self.analyze_btn.setEnabled(False)  # 初期状態では無効
        control_layout.addWidget(self.analyze_btn)
        
        # 設定ボタン
        self.settings_btn = QPushButton("設定")
        self.settings_btn.setIcon(QIcon.fromTheme("preferences-system"))
        self.settings_btn.clicked.connect(self.show_settings)
        control_layout.addWidget(self.settings_btn)
        
        main_layout.addLayout(control_layout)
        
        # タブウィジェット
        self.tabs = QTabWidget()
        
        # 画像表示タブ
        self.image_tab = QWidget()
        image_layout = QVBoxLayout(self.image_tab)
        
        # 画像表示ラベル
        self.image_label = QLabel("画像を読み込むか、スクリーンショットを撮影してください")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMinimumHeight(300)
        self.image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        image_layout.addWidget(self.image_label)
        
        self.tabs.addTab(self.image_tab, "画像")
        
        # 解析結果タブ
        self.results_tab = QWidget()
        results_layout = QVBoxLayout(self.results_tab)
        
        # 解析結果テキストエリア
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        self.tabs.addTab(self.results_tab, "解析結果")
        
        # ログタブ
        self.log_tab = QWidget()
        log_layout = QVBoxLayout(self.log_tab)
        
        # ログテキストエリア
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        self.tabs.addTab(self.log_tab, "ログ")
        
        # モデル状態タブ
        self.models_tab = QWidget()
        models_layout = QVBoxLayout(self.models_tab)
        
        # モデル状態テキストエリア
        self.models_text = QTextEdit()
        self.models_text.setReadOnly(True)
        models_layout.addWidget(self.models_text)
        
        # モデルロードボタン
        models_btn_layout = QHBoxLayout()
        self.load_models_btn = QPushButton("モデルをロード")
        self.load_models_btn.clicked.connect(self.load_models)
        models_btn_layout.addWidget(self.load_models_btn)
        
        self.test_models_btn = QPushButton("モデルをテスト")
        self.test_models_btn.clicked.connect(self.test_models)
        models_btn_layout.addWidget(self.test_models_btn)
        
        models_layout.addLayout(models_btn_layout)
        
        self.tabs.addTab(self.models_tab, "モデル")
        
        main_layout.addWidget(self.tabs)
        
        # ステータスバー
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # プログレスバー
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setMaximumWidth(200)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
        # 初期ステータス表示
        self.status_bar.showMessage("準備完了")
    
    def init_model_loader(self):
        """
        モデルローダーを初期化します
        """
        self.model_loader = ModelLoader(self.config)
        self.update_model_status()
    
    def update_model_status(self):
        """
        モデル状態表示を更新します
        """
        if not self.model_loader:
            self.models_text.setPlainText("モデルローダーが初期化されていません")
            return
        
        status = self.model_loader.model_status
        
        # ステータステキスト生成
        text = "モデル状態:\n\n"
        
        for model_name, model_status in status.items():
            loaded = model_status.get("loaded", False)
            error = model_status.get("error")
            load_time = model_status.get("time")
            
            text += f"■ {model_name}:\n"
            text += f"  - ロード状態: {'ロード済み' if loaded else '未ロード'}\n"
            
            if load_time is not None:
                text += f"  - ロード時間: {load_time:.2f}秒\n"
            
            if error:
                text += f"  - エラー: {error}\n"
            
            text += "\n"
        
        self.models_text.setPlainText(text)
    
    def load_models(self):
        """
        全てのモデルをロードします
        """
        self.log_message("モデルのロードを開始します...")
        self.status_bar.showMessage("モデルをロード中...")
        self.progress_bar.setValue(0)
        
        # モデルロードスレッド
        self.model_thread = WorkerThread(self.load_models_thread)
        self.model_thread.progress_signal.connect(self.update_model_load_progress)
        self.model_thread.finished_signal.connect(self.on_models_loaded)
        self.model_thread.start()
    
    def load_models_thread(self, progress_callback=None):
        """
        バックグラウンドスレッドでモデルをロードします
        
        Args:
            progress_callback (callable, optional): 進捗コールバック関数
            
        Returns:
            dict: モデルロード結果
        """
        import asyncio
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 進捗更新の設定
        models = ["mobilenet", "cocossd", "tesseract"]
        total_models = len(models)
        results = {}
        
        # 各モデルをシーケンシャルにロード
        for i, model_name in enumerate(models):
            # 進捗更新
            progress = int((i / total_models) * 100)
            if progress_callback:
                progress_callback(progress, f"{model_name}モデルをロード中...")
            
            # モデルロード関数を選択
            if model_name == "mobilenet":
                result = loop.run_until_complete(self.model_loader.load_mobilenet_model())
            elif model_name == "cocossd":
                result = loop.run_until_complete(self.model_loader.load_cocossd_model())
            elif model_name == "tesseract":
                result = loop.run_until_complete(self.model_loader.load_tesseract_model())
            
            results[model_name] = result
        
        # 最終進捗更新
        if progress_callback:
            progress_callback(100, "モデルのロードが完了しました")
        
        return results
    
    def update_model_load_progress(self, progress, message):
        """
        モデルロード進捗を更新します
        
        Args:
            progress (int): 進捗率（0-100）
            message (str): 進捗メッセージ
        """
        self.progress_bar.setValue(progress)
        self.status_bar.showMessage(message)
        self.log_message(message)
    
    def on_models_loaded(self, success, results, error_message):
        """
        モデルロード完了時の処理
        
        Args:
            success (bool): 成功フラグ
            results (dict): ロード結果
            error_message (str): エラーメッセージ
        """
        if success:
            self.models_loaded = True
            self.log_message("全てのモデルのロードが完了しました")
            self.status_bar.showMessage("モデルロード完了")
            
            # 解析ボタンを有効化
            self.analyze_btn.setEnabled(True)
        else:
            self.log_message(f"モデルロード中にエラーが発生しました: {error_message}")
            self.status_bar.showMessage("モデルロード失敗")
            
            # エラーダイアログ
            QMessageBox.warning(
                self,
                "モデルロードエラー",
                f"モデルのロード中にエラーが発生しました:\n{error_message}"
            )
        
        # モデル状態表示を更新
        self.update_model_status()
    
    def test_models(self):
        """
        モデルのテストを実行します
        """
        self.log_message("モデルのテストを開始します...")
        
        # テスト処理はここに実装
        pass
    
    def take_screenshot(self):
        """
        スクリーンショットを取得します
        """
        self.log_message("スクリーンショットを取得しています...")
        self.status_bar.showMessage("スクリーンショット取得中...")
        
        try:
            # スクリーンショット設定
            screenshot_config = self.config.get('screenshot', {})
            output_dir = Path(self.config.get('app', {}).get('output_dir', 'output'))
            
            # スクリーンショット取得
            success, filepath, error = take_screenshot(
                output_dir=output_dir,
                method=screenshot_config.get('method', 'auto'),
                monitor=screenshot_config.get('monitor', 0),
                image_format=screenshot_config.get('format', 'png'),
                delay=screenshot_config.get('delay', 0)
            )
            
            if success:
                self.log_message(f"スクリーンショットを保存しました: {filepath}")
                self.status_bar.showMessage(f"スクリーンショット保存: {filepath}")
                
                # 画像を表示
                self.display_image(filepath)
                
                # 解析ボタンを有効化
                self.current_image_path = filepath
                self.analyze_btn.setEnabled(True)
            else:
                self.log_message(f"スクリーンショット取得に失敗しました: {error}")
                self.status_bar.showMessage("スクリーンショット取得失敗")
                
                QMessageBox.warning(
                    self,
                    "スクリーンショットエラー",
                    f"スクリーンショットの取得に失敗しました:\n{error}"
                )
        
        except ScreenshotError as e:
            self.log_message(f"スクリーンショットエラー: {e}")
            self.status_bar.showMessage("スクリーンショットエラー")
            
            QMessageBox.warning(
                self,
                "スクリーンショットエラー",
                f"スクリーンショットの取得に失敗しました:\n{str(e)}"
            )
        
        except Exception as e:
            self.log_message(f"予期せぬエラー: {e}")
            self.status_bar.showMessage("エラー発生")
            
            QMessageBox.critical(
                self,
                "エラー",
                f"予期せぬエラーが発生しました:\n{str(e)}"
            )
    
    def load_image(self):
        """
        画像ファイルを読み込みます
        """
        file_dialog = QFileDialog()
        filepath, _ = file_dialog.getOpenFileName(
            self,
            "画像ファイルを開く",
            "",
            "画像ファイル (*.png *.jpg *.jpeg *.bmp *.tiff);;全てのファイル (*.*)"
        )
        
        if filepath:
            self.log_message(f"画像ファイルを読み込みました: {filepath}")
            self.display_image(filepath)
            
            # 解析ボタンを有効化
            self.current_image_path = filepath
            self.analyze_btn.setEnabled(True)
    
    def display_image(self, filepath):
        """
        画像を表示します
        
        Args:
            filepath (str): 画像ファイルパス
        """
        try:
            # QPixmapで画像表示
            pixmap = QPixmap(filepath)
            
            # 画像サイズをラベルに合わせて調整
            scaled_pixmap = pixmap.scaled(
                self.image_label.width(),
                self.image_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.image_label.setPixmap(scaled_pixmap)
            
            # タブを画像タブに切り替え
            self.tabs.setCurrentIndex(0)
            
        except Exception as e:
            self.log_message(f"画像の表示中にエラーが発生しました: {e}")
            self.image_label.setText(f"画像の表示に失敗しました: {e}")
    
    def analyze_image(self):
        """
        現在表示中の画像を解析します
        """
        if not hasattr(self, 'current_image_path') or not self.current_image_path:
            QMessageBox.warning(
                self,
                "画像なし",
                "解析する画像がありません。\nスクリーンショットを撮影するか、画像ファイルを開いてください。"
            )
            return
        
        # モデルロード確認
        if not self.models_loaded:
            reply = QMessageBox.question(
                self,
                "モデルロード",
                "モデルがロードされていません。\nモデルをロードしてから解析を続けますか？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # モデルロード開始
                self.load_models()
                return
        
        self.log_message(f"画像の解析を開始します: {self.current_image_path}")
        self.status_bar.showMessage("画像解析中...")
        self.progress_bar.setValue(0)
        
        # 解析処理は未実装（今後実装予定）
        self.status_bar.showMessage("解析機能は現在実装中です...")
        
    def show_settings(self):
        """
        設定ダイアログを表示します
        """
        # 設定ダイアログは未実装（今後実装予定）
        self.log_message("設定ダイアログは現在実装中です...")
        QMessageBox.information(
            self,
            "実装中",
            "設定機能は現在実装中です。"
        )
    
    def log_message(self, message):
        """
        ログメッセージを追加します
        
        Args:
            message (str): ログメッセージ
        """
        timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        log_line = f"[{timestamp}] {message}\n"
        
        # ログテキストエリアに追加
        self.log_text.append(log_line)
        
        # 自動スクロール
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # ロガーにも記録
        logger.info(message)
    
    def closeEvent(self, event):
        """
        ウィンドウを閉じる際の処理
        
        Args:
            event (QCloseEvent): クローズイベント
        """
        # 確認ダイアログ
        reply = QMessageBox.question(
            self,
            "終了確認",
            "アプリケーションを終了してもよろしいですか？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            logger.info("アプリケーションを終了します")
            event.accept()
        else:
            event.ignore()


def run_gui(config=None):
    """
    GUIアプリケーションを実行します
    
    Args:
        config (dict, optional): アプリケーション設定
        
    Returns:
        int: 終了コード
    """
    if not PYQT_AVAILABLE:
        logger.error("PyQt5がインストールされていません。'pip install PyQt5' を実行してください。")
        print("エラー: PyQt5がインストールされていません。'pip install PyQt5' を実行してください。")
        return 1
    
    # アプリケーション実行
    app = QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    return app.exec_() 