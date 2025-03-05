#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
スクリーンショットをYOLOv8で解析し、デバッグの視覚的フィードバックを生成するスクリプト
"""
import os
import sys
import argparse
import logging
from typing import Dict, List, Optional

# ロギングの設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# 現在のディレクトリをPYTHONPATHに追加
sys.path.insert(0, os.getcwd())

# pdfexpyパッケージから必要なモジュールをインポート
from pdfexpy.utils.screenshot_analyzer import (
    take_screenshot,
    analyze_screenshot,
    debug_with_screenshot_analysis
)


def parse_arguments():
    """コマンドライン引数を解析します"""
    parser = argparse.ArgumentParser(
        description="スクリーンショットをYOLOv8で解析し、デバッグフィードバックを生成"
    )
    
    # サブコマンドの設定
    subparsers = parser.add_subparsers(dest="command", help="実行するコマンド")
    
    # スクリーンショットを撮影するコマンド
    take_parser = subparsers.add_parser("take", help="スクリーンショットを撮影")
    take_parser.add_argument("--output-dir", default="screenshots", help="出力先ディレクトリ")
    take_parser.add_argument("--prefix", default="debug", help="ファイル名接頭辞")
    
    # スクリーンショットを解析するコマンド
    analyze_parser = subparsers.add_parser("analyze", help="スクリーンショットを解析")
    analyze_parser.add_argument("--image", help="解析する画像ファイルのパス")
    analyze_parser.add_argument("--output-dir", default="analysis_results", help="出力先ディレクトリ")
    analyze_parser.add_argument("--model", help="使用するYOLOモデルのパス")
    analyze_parser.add_argument("--confidence", type=float, default=0.25, help="検出の信頼度しきい値 (0-1)")
    analyze_parser.add_argument("--take-new", action="store_true", help="新しいスクリーンショットを撮影")
    
    # デバッグモードで実行するコマンド
    debug_parser = subparsers.add_parser("debug", help="デバッグモード（スクリーンショット撮影と解析）")
    debug_parser.add_argument("--action", default="", help="デバッグ中のアクションの説明")
    debug_parser.add_argument("--output-dir", default="debug_results", help="出力先ディレクトリ")
    debug_parser.add_argument("--model", help="使用するYOLOモデルのパス")
    debug_parser.add_argument("--confidence", type=float, default=0.25, help="検出の信頼度しきい値 (0-1)")
    
    return parser.parse_args()


def main():
    """メイン関数"""
    args = parse_arguments()
    
    # コマンドが指定されていない場合はデバッグモードをデフォルトとする
    if args.command is None:
        args.command = "debug"
        args.action = ""
        args.output_dir = "debug_results"
        args.model = None
        args.confidence = 0.25
    
    # スクリーンショットを撮影
    if args.command == "take":
        logger.info(f"スクリーンショットを撮影します")
        screenshot_path = take_screenshot(output_dir=args.output_dir, prefix=args.prefix)
        
        if screenshot_path:
            logger.info(f"スクリーンショットを保存しました: {screenshot_path}")
        else:
            logger.error("スクリーンショットの撮影に失敗しました")
            return 1
    
    # スクリーンショットを解析
    elif args.command == "analyze":
        logger.info(f"スクリーンショットを解析します")
        
        result = analyze_screenshot(
            screenshot_path=args.image,
            output_dir=args.output_dir,
            model_path=args.model,
            confidence=args.confidence,
            take_new_screenshot=args.take_new
        )
        
        if result["success"]:
            logger.info(f"解析が完了しました")
            logger.info(f"検出されたオブジェクト: {result.get('objects_count', 0)}個")
            
            if result.get("visual_feedback"):
                logger.info(f"視覚的フィードバック: {result['visual_feedback']}")
        else:
            logger.error(f"解析中にエラーが発生しました: {result.get('error', '不明なエラー')}")
            return 1
    
    # デバッグモード
    elif args.command == "debug":
        logger.info(f"デバッグモードで実行します")
        
        result = debug_with_screenshot_analysis(
            action_description=args.action,
            output_dir=args.output_dir,
            model_path=args.model,
            confidence=args.confidence
        )
        
        if result["success"]:
            logger.info(f"デバッグ解析が完了しました")
            logger.info(f"スクリーンショット: {result['screenshot']}")
            
            if result.get("visual_feedback"):
                logger.info(f"視覚的フィードバック: {result['visual_feedback']}")
                logger.info(f"検出されたオブジェクト: {result.get('objects_count', 0)}個")
        else:
            logger.error(f"デバッグ中にエラーが発生しました: {result.get('error', '不明なエラー')}")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 