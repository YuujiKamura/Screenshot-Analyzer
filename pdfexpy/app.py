"""
アプリケーションのエントリーポイント
"""

import os
import sys
import argparse
from pathlib import Path
import logging

from pdfexpy.utils.logger import setup_logger, get_logger
from pdfexpy.utils.config import load_config, save_config
from pdfexpy.utils.screenshot import take_screenshot, ScreenshotError
from pdfexpy.utils.image_analysis import analyze_image, ImageAnalysisError
from pdfexpy.models.model_loader import ModelLoader, test_model_loading

# ロガー初期化
logger = get_logger(__name__)


def parse_args():
    """
    コマンドライン引数をパースします
    
    Returns:
        argparse.Namespace: パースされた引数
    """
    parser = argparse.ArgumentParser(description="PDFExPy - PDFおよびスクリーンショット解析ツール")
    
    # 基本オプション
    parser.add_argument("--config", "-c", type=str, help="設定ファイルのパス")
    parser.add_argument("--output-dir", "-o", type=str, help="出力ディレクトリ")
    parser.add_argument("--log-level", "-l", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      default="INFO", help="ログレベル")
    
    # モード選択
    parser.add_argument("--headless", action="store_true", help="ヘッドレスモード（GUIなし）で実行")
    parser.add_argument("--gui", action="store_true", help="GUIモードで実行（デフォルト）")
    
    # ヘッドレスモードのオプション
    parser.add_argument("--screenshot", "-s", action="store_true", help="スクリーンショットを取得")
    parser.add_argument("--image", "-i", type=str, help="解析する画像ファイルのパス")
    parser.add_argument("--watch-dir", "-w", type=str, help="画像ファイルを監視するディレクトリ")
    parser.add_argument("--delay", "-d", type=int, default=0, help="スクリーンショット取得前の遅延（秒）")
    
    # 画像解析オプション
    parser.add_argument("--no-visual", action="store_true", help="視覚的フィードバックを生成しない")
    parser.add_argument("--analyze-only", action="store_true", help="画像解析のみを実行（スクリーンショットを撮影しない）")
    
    # モデルテスト
    parser.add_argument("--test-model", "-t", type=str, 
                      choices=["mobilenet", "cocossd", "tesseract", "all"],
                      help="指定したモデルのロードテストを実行")
    
    # モックモード
    parser.add_argument("--mock", "-m", action="store_true", help="モックデータを使用（モデルをロードしない）")
    
    return parser.parse_args()


def process_screenshot(args, config):
    """
    スクリーンショットを撮影し、オプションで解析します
    
    Args:
        args: コマンドライン引数
        config: 設定
        
    Returns:
        dict: 処理結果
    """
    try:
        # スクリーンショットディレクトリの設定
        screenshots_dir = args.output_dir or config.get("output", {}).get("screenshots_dir", "screenshots")
        
        # 遅延の設定
        delay = args.delay or config.get("screenshot", {}).get("delay", 0)
        
        logger.info(f"スクリーンショットを撮影します (遅延: {delay}秒)")
        success, filepath, error = take_screenshot(
            output_dir=screenshots_dir,
            method=config.get("screenshot", {}).get("method", "auto"),
            delay=delay
        )
        
        if not success or not filepath:
            logger.error(f"スクリーンショット撮影に失敗しました: {error}")
            return {"success": False, "error": error}
        
        logger.info(f"スクリーンショット撮影成功: {filepath}")
        
        # 解析オプションが有効な場合、自動的に解析を実行
        if not args.analyze_only:
            try:
                # 解析ディレクトリの設定
                analysis_dir = args.output_dir or config.get("output", {}).get("analysis_dir", "analysis_results")
                
                # 視覚的フィードバックの設定
                generate_visual = not args.no_visual
                
                # 画像解析を実行
                logger.info(f"撮影したスクリーンショットを解析します: {filepath}")
                analysis_result = analyze_image(
                    image_path=filepath,
                    output_dir=analysis_dir,
                    generate_visual=generate_visual,
                    mock=args.mock
                )
                
                if analysis_result["success"]:
                    logger.info(f"画像解析成功: {analysis_result['result_file']}")
                    if generate_visual and analysis_result.get("visual_feedback"):
                        logger.info(f"視覚的フィードバック: {analysis_result['visual_feedback']}")
                    
                    # 処理結果を返す
                    return {
                        "success": True,
                        "screenshot": filepath,
                        "analysis": {
                            "success": True,
                            "result_file": analysis_result["result_file"],
                            "visual_feedback": analysis_result.get("visual_feedback")
                        }
                    }
                else:
                    logger.warning(f"画像解析に失敗しましたが、スクリーンショット自体は成功しています: {analysis_result['error']}")
                    return {
                        "success": True,
                        "screenshot": filepath,
                        "analysis": {
                            "success": False,
                            "error": analysis_result["error"]
                        }
                    }
            except Exception as e:
                logger.warning(f"画像解析中にエラーが発生しましたが、スクリーンショット自体は成功しています: {str(e)}")
                return {
                    "success": True,
                    "screenshot": filepath,
                    "analysis": {
                        "success": False,
                        "error": str(e)
                    }
                }
        
        # 解析を実行しない場合はスクリーンショットの情報のみを返す
        return {"success": True, "screenshot": filepath}
        
    except ScreenshotError as e:
        logger.error(f"スクリーンショット取得中にエラーが発生しました: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {str(e)}")
        return {"success": False, "error": str(e)}


def process_image_analysis(args, config):
    """
    画像解析を実行します
    
    Args:
        args: コマンドライン引数
        config: 設定
        
    Returns:
        dict: 処理結果
    """
    try:
        # 画像パスの取得
        image_path = args.image
        if not image_path:
            return {"success": False, "error": "解析する画像が指定されていません"}
        
        if not os.path.exists(image_path):
            return {"success": False, "error": f"指定された画像が存在しません: {image_path}"}
        
        # 解析ディレクトリの設定
        analysis_dir = args.output_dir or config.get("output", {}).get("analysis_dir", "analysis_results")
        
        # 視覚的フィードバックの設定
        generate_visual = not args.no_visual
        
        # 画像解析を実行
        logger.info(f"画像を解析します: {image_path}")
        analysis_result = analyze_image(
            image_path=image_path,
            output_dir=analysis_dir,
            generate_visual=generate_visual,
            mock=args.mock
        )
        
        if analysis_result["success"]:
            logger.info(f"画像解析成功: {analysis_result['result_file']}")
            if generate_visual and analysis_result.get("visual_feedback"):
                logger.info(f"視覚的フィードバック: {analysis_result['visual_feedback']}")
                
            # コマンドラインに結果を表示
            print("\n----------------- デバッグ支援情報 -----------------")
            print(f"解析画像: {image_path}")
            print(f"解析結果: {analysis_result['result_file']}")
            if analysis_result.get("visual_feedback"):
                print(f"視覚的フィードバック: {analysis_result['visual_feedback']}")
            print("--------------------------------------------------\n")
            
            return {
                "success": True,
                "image": image_path,
                "result_file": analysis_result["result_file"],
                "visual_feedback": analysis_result.get("visual_feedback")
            }
        else:
            logger.error(f"画像解析に失敗しました: {analysis_result['error']}")
            return {
                "success": False,
                "error": analysis_result["error"]
            }
            
    except ImageAnalysisError as e:
        logger.error(f"画像解析中にエラーが発生しました: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {str(e)}")
        return {"success": False, "error": str(e)}


def main():
    """
    アプリケーションのメインエントリーポイント
    """
    # コマンドライン引数のパース
    args = parse_args()
    
    # ロガーのセットアップ
    setup_logger("pdfexpy", console_level=getattr(logging, args.log_level))
    
    # 設定ファイルの読み込み
    config_path = args.config or "config.json"
    config = load_config(config_path)
    
    # ヘッドレスモード
    if args.headless:
        logger.info("ヘッドレスモードで実行します")
        
        # モデルのテスト
        if args.test_model:
            result = test_model_loading(args.test_model)
            logger.info(f"モデルテスト結果: {result}")
            return
        
        # スクリーンショット撮影
        if args.screenshot:
            result = process_screenshot(args, config)
            if result["success"]:
                logger.info("スクリーンショット処理が完了しました")
                if "analysis" in result and result["analysis"]["success"]:
                    logger.info("画像解析も完了しました")
            else:
                logger.error(f"スクリーンショット処理に失敗しました: {result.get('error', '不明なエラー')}")
            return
        
        # 画像解析
        if args.image:
            result = process_image_analysis(args, config)
            if result["success"]:
                logger.info("画像解析が完了しました")
            else:
                logger.error(f"画像解析に失敗しました: {result.get('error', '不明なエラー')}")
            return
        
        # ディレクトリ監視
        if args.watch_dir:
            # TODO: ディレクトリ監視を実装
            logger.info(f"ディレクトリの監視を開始します: {args.watch_dir}")
            # watch_directory(args.watch_dir, args.output_dir)
            return
        
        # コマンドが指定されていない場合
        logger.error("ヘッドレスモードでは --screenshot、--image、--watch-dir、または --test-model オプションが必要です")
        return
    
    # GUIモード（デフォルト）
    else:
        # TODO: GUIモードの実装
        logger.info("GUIモードで実行します")
        logger.error("現在GUIモードは実装されていません")
        return


if __name__ == "__main__":
    main() 