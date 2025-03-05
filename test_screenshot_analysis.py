#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
スクリーンショットの画像解析テスト用スクリプト
"""
import os
import sys
import time
import argparse
import logging
from pathlib import Path

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


def test_screenshot_taking():
    """スクリーンショットの撮影機能をテストします"""
    logger.info("スクリーンショット撮影テストを開始します")
    
    output_dir = "test_results/screenshots"
    screenshot_path = take_screenshot(output_dir=output_dir, prefix="test")
    
    if screenshot_path and os.path.exists(screenshot_path):
        logger.info(f"テスト成功: スクリーンショットを保存しました: {screenshot_path}")
        return True, screenshot_path
    else:
        logger.error("テスト失敗: スクリーンショットの撮影に失敗しました")
        return False, None


def test_screenshot_analysis(screenshot_path=None):
    """スクリーンショット解析機能をテストします"""
    logger.info("スクリーンショット解析テストを開始します")
    
    output_dir = "test_results/analysis"
    
    # スクリーンショットパスが指定されていない場合は新しく撮影
    take_new = screenshot_path is None
    
    result = analyze_screenshot(
        screenshot_path=screenshot_path,
        output_dir=output_dir,
        model_path="yolov8n.pt",  # デフォルトのYOLOモデル
        confidence=0.25,
        take_new_screenshot=take_new
    )
    
    if result["success"]:
        logger.info(f"テスト成功: スクリーンショット解析が完了しました")
        logger.info(f"検出されたオブジェクト: {result.get('objects_count', 0)}個")
        
        if result.get("visual_feedback"):
            logger.info(f"視覚的フィードバック: {result['visual_feedback']}")
        
        return True, result
    else:
        logger.error(f"テスト失敗: 解析中にエラーが発生しました: {result.get('error', '不明なエラー')}")
        return False, result


def run_all_tests():
    """すべてのテストを実行します"""
    logger.info("=== スクリーンショット画像解析の総合テスト開始 ===")
    
    # テスト結果を格納するディレクトリを作成
    os.makedirs("test_results", exist_ok=True)
    
    # スクリーンショット撮影テスト
    screenshot_success, screenshot_path = test_screenshot_taking()
    
    # スクリーンショット解析テスト
    if screenshot_success:
        analysis_success, analysis_result = test_screenshot_analysis(screenshot_path)
    else:
        # スクリーンショット撮影に失敗した場合は新しく撮影して解析
        analysis_success, analysis_result = test_screenshot_analysis()
    
    # デバッグモードでのテスト
    logger.info("デバッグモードテストを開始します")
    debug_result = debug_with_screenshot_analysis(
        action_description="テスト実行中",
        output_dir="test_results/debug",
        model_path="yolov8n.pt",
        confidence=0.25
    )
    
    debug_success = debug_result.get("success", False)
    
    # 結果の集計
    logger.info("=== テスト結果の集計 ===")
    logger.info(f"スクリーンショット撮影: {'成功' if screenshot_success else '失敗'}")
    logger.info(f"スクリーンショット解析: {'成功' if analysis_success else '失敗'}")
    logger.info(f"デバッグモード: {'成功' if debug_success else '失敗'}")
    
    overall_success = screenshot_success and analysis_success and debug_success
    logger.info(f"総合結果: {'すべてのテストに成功しました' if overall_success else 'テストに一部失敗があります'}")
    
    return overall_success


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="スクリーンショット画像解析テスト"
    )
    
    parser.add_argument("--test", choices=["all", "screenshot", "analysis", "debug"],
                      default="all", help="実行するテスト")
    
    args = parser.parse_args()
    
    if args.test == "all":
        run_all_tests()
    elif args.test == "screenshot":
        test_screenshot_taking()
    elif args.test == "analysis":
        test_screenshot_analysis()
    elif args.test == "debug":
        debug_with_screenshot_analysis(
            action_description="単体テスト実行中",
            output_dir="test_results/debug",
            model_path="yolov8n.pt",
            confidence=0.25
        )
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 