"""
スクリーンショットを取得し、YOLOv8モデルで解析するためのユーティリティモジュール。
デバッグプロセスのための視覚的フィードバックを提供します。
"""
import os
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import cv2
import numpy as np
import pyautogui

from pdfexpy.models import YOLOModel
from pdfexpy.utils.image_processing import visualize_annotations

# ロガーの設定
logger = logging.getLogger(__name__)

def take_screenshot(output_dir: str = "screenshots", prefix: str = "debug") -> Optional[str]:
    """
    スクリーンショットを撮影し、ファイルに保存します。
    
    Args:
        output_dir: スクリーンショットを保存するディレクトリ
        prefix: ファイル名の接頭辞
        
    Returns:
        str: 保存されたスクリーンショットのパス、または失敗した場合はNone
    """
    try:
        # 出力ディレクトリを作成
        os.makedirs(output_dir, exist_ok=True)
        
        # タイムスタンプを生成
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
        
        # ファイル名を生成
        filename = f"{prefix}-{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        # スクリーンショットを取得
        screenshot = pyautogui.screenshot()
        
        # 画像ファイルとして保存
        screenshot.save(filepath)
        
        logger.info(f"スクリーンショットを保存しました: {filepath}")
        return filepath
    
    except Exception as e:
        logger.error(f"スクリーンショットの取得中にエラーが発生しました: {str(e)}")
        return None

def analyze_screenshot(
    screenshot_path: Optional[str] = None,
    output_dir: str = "analysis_results",
    model_path: Optional[str] = None,
    confidence: float = 0.25,
    take_new_screenshot: bool = False,
    screenshot_prefix: str = "debug"
) -> Dict:
    """
    スクリーンショットをYOLOv8モデルで解析します。
    
    Args:
        screenshot_path: 解析するスクリーンショットのパス（Noneの場合、新しいスクリーンショットを撮影）
        output_dir: 解析結果の保存先ディレクトリ
        model_path: YOLOモデルのパス
        confidence: 検出の信頼度しきい値
        take_new_screenshot: 新しいスクリーンショットを撮影するかどうか
        screenshot_prefix: スクリーンショットファイル名の接頭辞
        
    Returns:
        Dict: 解析結果
    """
    start_time = time.time()
    
    try:
        # スクリーンショットのパスが指定されていない、または新しいスクリーンショットを撮影する場合
        if screenshot_path is None or take_new_screenshot:
            screenshot_path = take_screenshot(output_dir="screenshots", prefix=screenshot_prefix)
            if screenshot_path is None:
                return {
                    "success": False,
                    "error": "スクリーンショットの取得に失敗しました",
                    "time_taken": time.time() - start_time
                }
        
        # 出力ディレクトリを作成
        os.makedirs(output_dir, exist_ok=True)
        
        # YOLOモデルを初期化
        yolo = YOLOModel(model_path=model_path, confidence=confidence)
        
        # モデルをロード
        if not yolo.load():
            return {
                "success": False,
                "error": "YOLOモデルのロードに失敗しました",
                "screenshot": screenshot_path,
                "time_taken": time.time() - start_time
            }
        
        # オブジェクト検出を実行
        detection_results = yolo.detect(screenshot_path)
        
        if "error" in detection_results:
            return {
                "success": False,
                "error": f"オブジェクト検出中にエラーが発生しました: {detection_results['error']}",
                "screenshot": screenshot_path,
                "time_taken": time.time() - start_time
            }
        
        # 出力ファイル名を生成
        base_filename = os.path.basename(screenshot_path)
        filename_without_ext = os.path.splitext(base_filename)[0]
        
        # JSONファイルに結果を保存
        json_path = os.path.join(output_dir, f"{filename_without_ext}-analysis.json")
        
        # 視覚的フィードバックを生成
        image = cv2.imread(screenshot_path)
        if image is None:
            return {
                "success": False,
                "error": f"画像の読み込みに失敗しました: {screenshot_path}",
                "time_taken": time.time() - start_time
            }
        
        # 検出されたオブジェクトを描画
        objects = detection_results.get("objects", [])
        
        if objects:
            # 結果を視覚化
            annotated_image = visualize_annotations(
                image=image.copy(),
                objects=objects
            )
            
            # 視覚的フィードバックを保存
            visual_path = os.path.join(output_dir, f"{filename_without_ext}-visual.png")
            cv2.imwrite(visual_path, annotated_image)
            
            logger.info(f"視覚的フィードバックを保存しました: {visual_path}")
            logger.info(f"検出されたオブジェクト: {len(objects)}個")
            
            return {
                "success": True,
                "screenshot": screenshot_path,
                "visual_feedback": visual_path,
                "detection_results": detection_results,
                "objects_count": len(objects),
                "time_taken": time.time() - start_time
            }
        else:
            logger.info("オブジェクトが検出されませんでした")
            
            return {
                "success": True,
                "screenshot": screenshot_path,
                "visual_feedback": None,
                "detection_results": detection_results,
                "objects_count": 0,
                "time_taken": time.time() - start_time
            }
    
    except Exception as e:
        logger.error(f"スクリーンショット解析中にエラーが発生しました: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "screenshot": screenshot_path if 'screenshot_path' in locals() else None,
            "time_taken": time.time() - start_time
        }

def debug_with_screenshot_analysis(
    action_description: str = "",
    output_dir: str = "debug_results",
    model_path: Optional[str] = None,
    confidence: float = 0.25
) -> Dict:
    """
    デバッグのための視覚的フィードバックとしてスクリーンショットを解析します。
    
    Args:
        action_description: デバッグ中のアクションの説明
        output_dir: 解析結果の保存先ディレクトリ
        model_path: YOLOモデルのパス
        confidence: 検出の信頼度しきい値
        
    Returns:
        Dict: デバッグ結果
    """
    logger.info(f"デバッグアクション: {action_description}")
    
    # スクリーンショットを撮影して解析
    prefix = "debug" if not action_description else f"debug-{action_description.replace(' ', '_')}"
    result = analyze_screenshot(
        take_new_screenshot=True,
        screenshot_prefix=prefix,
        output_dir=output_dir,
        model_path=model_path,
        confidence=confidence
    )
    
    if result["success"]:
        logger.info(f"デバッグ分析が完了しました。検出オブジェクト: {result.get('objects_count', 0)}個")
    else:
        logger.error(f"デバッグ分析中にエラーが発生しました: {result.get('error', '不明なエラー')}")
    
    return result 