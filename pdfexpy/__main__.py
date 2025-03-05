"""
PDFExPy - メインアプリケーションエントリポイント
"""

import os
import sys
import argparse
from pathlib import Path

# モジュールのインポートを確実にするためにパスを追加
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

from pdfexpy.utils.logger import setup_logger
from pdfexpy.utils.config import load_config
from pdfexpy.gui.main_window import run_gui
from pdfexpy.utils.screenshot import take_screenshot
from pdfexpy.models.model_loader import test_model_loading


def parse_args():
    """
    コマンドライン引数をパースします。
    
    Returns:
        argparse.Namespace: パースされた引数
    """
    parser = argparse.ArgumentParser(description='PDFExPy - PDFとスクリーンショットの解析ツール')
    
    parser.add_argument('--headless', action='store_true',
                        help='ヘッドレスモードで実行する（GUI無し）')
    
    parser.add_argument('--config', type=str, default=None,
                        help='設定ファイルのパス')
    
    parser.add_argument('--log-dir', type=str, default='logs',
                        help='ログファイルのディレクトリ')
    
    parser.add_argument('--screenshot', action='store_true',
                        help='スクリーンショットを取得する')
    
    parser.add_argument('--output-dir', type=str, default='output',
                        help='出力ディレクトリのパス')
    
    parser.add_argument('--analyze', type=str, default=None,
                        help='指定された画像ファイルを解析する')
    
    parser.add_argument('--watch-dir', type=str, default=None,
                        help='監視するディレクトリのパス')
    
    parser.add_argument('--test-model', type=str, default=None, 
                        choices=['mobilenet', 'cocossd', 'tesseract', 'all'],
                        help='テストするモデル名')
    
    parser.add_argument('--force-load-model', action='store_true',
                        help='ヘッドレスモードでもモデルを実際にロードする')
    
    return parser.parse_args()


def main():
    """
    メインアプリケーション実行関数
    """
    # コマンドライン引数のパース
    args = parse_args()
    
    # ロガーのセットアップ
    if not os.path.exists(args.log_dir):
        os.makedirs(args.log_dir, exist_ok=True)
    
    logger = setup_logger('pdfexpy', args.log_dir)
    logger.info('PDFExPy アプリケーションを起動しています...')
    
    # 設定の読み込み
    config = load_config(args.config)
    
    # ヘッドレスモードの設定を更新
    if args.headless:
        config['app']['headless_mode'] = True
        logger.info('ヘッドレスモードで実行します')
    
    # モデルのテスト
    if args.test_model:
        logger.info(f'モデル "{args.test_model}" のテストを実行します')
        result = test_model_loading(args.test_model, args.force_load_model, config)
        logger.info(f'テスト結果: {result}')
        return
    
    # スクリーンショット
    if args.screenshot:
        try:
            logger.info('スクリーンショットを取得します')
            success, filepath, _ = take_screenshot(
                output_dir=args.output_dir,
                method=config['screenshot']['method'],
                monitor=config['screenshot']['monitor'],
                image_format=config['screenshot']['format'],
                delay=config['screenshot']['delay']
            )
            
            if success:
                logger.info(f'スクリーンショットを保存しました: {filepath}')
            else:
                logger.error('スクリーンショットの取得に失敗しました')
                
            # ヘッドレスモードなら終了
            if args.headless:
                return
                
        except Exception as e:
            logger.error(f'スクリーンショット取得中にエラーが発生しました: {e}')
            if args.headless:
                sys.exit(1)
    
    # ここにその他のヘッドレスモード処理を追加
    # ...
    
    # GUIモードで実行
    if not args.headless:
        logger.info('GUIモードでアプリケーションを起動します')
        run_gui(config)
    else:
        logger.info('ヘッドレスモードでの処理を完了しました')


if __name__ == '__main__':
    main() 