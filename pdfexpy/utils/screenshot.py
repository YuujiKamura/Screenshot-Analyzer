"""
スクリーンショット機能を提供するモジュール
"""

import os
import time
import datetime
from pathlib import Path
from PIL import Image

# スクリーンショット機能用のライブラリ
try:
    import mss
    import mss.tools
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

from .logger import get_logger

logger = get_logger(__name__)


class ScreenshotError(Exception):
    """スクリーンショット取得時のエラーを表すカスタム例外"""
    pass


def ensure_dir(directory):
    """
    ディレクトリが存在しない場合は作成します。
    
    Args:
        directory (str): 作成するディレクトリパス
        
    Returns:
        Path: 作成されたディレクトリのPathオブジェクト
    """
    dir_path = Path(directory)
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"ディレクトリを作成しました: {dir_path}")
    return dir_path


def get_screenshot_mss(output_dir, filename=None, monitor=0, image_format="png"):
    """
    MSSライブラリを使用してスクリーンショットを取得します。
    
    Args:
        output_dir (str): スクリーンショットの保存先ディレクトリ
        filename (str, optional): 出力ファイル名。指定しない場合はタイムスタンプを使用
        monitor (int, optional): キャプチャするモニター番号。デフォルトは主モニター (0)
        image_format (str, optional): 画像フォーマット (png, jpg, etc.)
        
    Returns:
        tuple: (成功フラグ, 出力ファイルパス, エラーメッセージ)
    """
    if not MSS_AVAILABLE:
        return False, None, "MSSライブラリがインストールされていません。'pip install mss' を実行してください。"
    
    try:
        logger.info(f"MSSを使用してスクリーンショットを取得します (モニター: {monitor})")
        
        # 出力先ディレクトリを確保
        output_path = ensure_dir(output_dir)
        
        # ファイル名の生成
        if not filename:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.{image_format}"
        elif not filename.endswith(f".{image_format}"):
            filename = f"{filename}.{image_format}"
        
        output_file = output_path / filename
        
        # スクリーンショット取得
        start_time = time.time()
        with mss.mss() as sct:
            # モニターリスト取得
            monitors = sct.monitors
            
            # モニター番号の検証
            if monitor < 0 or monitor >= len(monitors):
                logger.warning(f"指定されたモニター番号が無効です: {monitor}。代わりに主モニター(0)を使用します。")
                monitor = 0
            
            # スクリーンショット取得
            monitor_dict = monitors[monitor]
            img = sct.grab(monitor_dict)
            
            # 画像保存
            mss.tools.to_png(img.rgb, img.size, output=str(output_file))
        
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"スクリーンショットを保存しました: {output_file} ({elapsed:.1f}ms)")
        
        return True, str(output_file), None
    
    except Exception as e:
        error_msg = f"MSSでのスクリーンショット取得中にエラーが発生しました: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg


def get_screenshot_pyautogui(output_dir, filename=None, image_format="png"):
    """
    PyAutoGUIライブラリを使用してスクリーンショットを取得します。
    
    Args:
        output_dir (str): スクリーンショットの保存先ディレクトリ
        filename (str, optional): 出力ファイル名。指定しない場合はタイムスタンプを使用
        image_format (str, optional): 画像フォーマット (png, jpg, etc.)
        
    Returns:
        tuple: (成功フラグ, 出力ファイルパス, エラーメッセージ)
    """
    if not PYAUTOGUI_AVAILABLE:
        return False, None, "PyAutoGUIライブラリがインストールされていません。'pip install pyautogui' を実行してください。"
    
    try:
        logger.info("PyAutoGUIを使用してスクリーンショットを取得します")
        
        # 出力先ディレクトリを確保
        output_path = ensure_dir(output_dir)
        
        # ファイル名の生成
        if not filename:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"screenshot_{timestamp}.{image_format}"
        elif not filename.endswith(f".{image_format}"):
            filename = f"{filename}.{image_format}"
        
        output_file = output_path / filename
        
        # スクリーンショット取得
        start_time = time.time()
        screenshot = pyautogui.screenshot()
        screenshot.save(str(output_file))
        
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"スクリーンショットを保存しました: {output_file} ({elapsed:.1f}ms)")
        
        return True, str(output_file), None
    
    except Exception as e:
        error_msg = f"PyAutoGUIでのスクリーンショット取得中にエラーが発生しました: {str(e)}"
        logger.error(error_msg)
        return False, None, error_msg


def take_screenshot(output_dir="screenshots", method="auto", filename=None, 
                   monitor=0, image_format="png", delay=0):
    """
    設定に基づいてスクリーンショットを取得する統合関数
    
    Args:
        output_dir (str): スクリーンショットの保存先ディレクトリ
        method (str): 使用するスクリーンショット方法 ('mss', 'pyautogui', 'auto')
        filename (str, optional): 出力ファイル名
        monitor (int, optional): キャプチャするモニター番号（MSSのみ）
        image_format (str, optional): 画像フォーマット
        delay (float, optional): スクリーンショット前の遅延（秒）
        
    Returns:
        tuple: (成功フラグ, 出力ファイルパス, エラーメッセージ)
        
    Raises:
        ScreenshotError: スクリーンショット取得に失敗した場合
    """
    # 遅延処理
    if delay > 0:
        logger.debug(f"スクリーンショット前に {delay}秒 待機します")
        time.sleep(delay)
    
    # 利用可能なライブラリの確認と自動選択
    if method.lower() == "auto":
        if MSS_AVAILABLE:
            method = "mss"
        elif PYAUTOGUI_AVAILABLE:
            method = "pyautogui"
        else:
            raise ScreenshotError("スクリーンショット機能が利用できません。'pip install mss pyautogui' を実行してください。")
    
    # メソッドに応じて処理を分岐
    if method.lower() == "mss" and MSS_AVAILABLE:
        success, filepath, error = get_screenshot_mss(
            output_dir, filename, monitor, image_format
        )
    elif method.lower() == "pyautogui" and PYAUTOGUI_AVAILABLE:
        success, filepath, error = get_screenshot_pyautogui(
            output_dir, filename, image_format
        )
    else:
        raise ScreenshotError(f"指定されたスクリーンショット方法はサポートされていません: {method}")
    
    # 結果の処理
    if not success:
        raise ScreenshotError(error or "不明なエラーが発生しました")
    
    return success, filepath, error 