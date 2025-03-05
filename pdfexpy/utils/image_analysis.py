"""
画像解析とビジュアルフィードバック機能を提供するモジュール
"""

import os
import time
import json
import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union

# 画像処理
try:
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# OpenCV
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

# 数値計算
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# YOLOモデル
try:
    from ..models import YOLOModel, YOLO_AVAILABLE
except ImportError:
    YOLO_AVAILABLE = False

# ロガー
from .logger import get_logger

logger = get_logger(__name__)


class ImageAnalysisError(Exception):
    """画像解析時のエラーを表すカスタム例外"""
    pass


def ensure_output_dir(directory):
    """
    出力ディレクトリを作成します
    
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


def get_image_details(image_path: str) -> Dict[str, Any]:
    """
    画像の詳細情報を取得します
    
    Args:
        image_path (str): 画像ファイルのパス
        
    Returns:
        Dict[str, Any]: 画像の詳細情報
        
    Raises:
        ImageAnalysisError: 画像読み込みに失敗した場合
    """
    if not PIL_AVAILABLE:
        raise ImageAnalysisError("PIL (Pillow) ライブラリがインストールされていません。'pip install pillow' を実行してください。")
    
    try:
        # ファイル情報
        file_path = Path(image_path)
        file_stat = file_path.stat()
        
        # 画像情報
        with Image.open(image_path) as img:
            width, height = img.size
            format_name = img.format
            mode = img.mode
            
            # 色情報（シンプルなバージョン）
            color_info = {
                "mode": mode,
                "has_alpha": "A" in mode,
                "is_grayscale": mode in ("L", "LA"),
                "is_rgb": mode in ("RGB", "RGBA")
            }
            
            # 高度な色情報（NumPyが利用可能な場合）
            if NUMPY_AVAILABLE:
                try:
                    img_array = np.array(img)
                    if mode in ("RGB", "RGBA"):
                        # RGB平均値
                        rgb_channels = img_array[:, :, :3]  # アルファチャンネルを除外
                        avg_color = rgb_channels.mean(axis=(0, 1)).astype(int)
                        
                        # 明るさ
                        brightness = np.mean(rgb_channels)
                        
                        # カラーバリエーション（標準偏差）
                        color_variance = np.std(rgb_channels)
                        
                        color_info.update({
                            "avg_color_rgb": avg_color.tolist(),
                            "avg_color_hex": f"#{int(avg_color[0]):02x}{int(avg_color[1]):02x}{int(avg_color[2]):02x}",
                            "brightness": float(brightness),
                            "brightness_percent": float(brightness / 255 * 100),
                            "color_variance": float(color_variance)
                        })
                except Exception as e:
                    logger.warning(f"高度な色情報の取得に失敗しました: {e}")
        
        # 詳細情報を構築
        details = {
            "file_info": {
                "filename": file_path.name,
                "filepath": str(file_path.absolute()),
                "filesize_bytes": file_stat.st_size,
                "filesize_kb": file_stat.st_size / 1024,
                "filesize_mb": file_stat.st_size / (1024 * 1024),
                "created_at": datetime.datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                "modified_at": datetime.datetime.fromtimestamp(file_stat.st_mtime).isoformat(),
                "extension": file_path.suffix.lower()
            },
            "image_info": {
                "width": width,
                "height": height,
                "resolution": f"{width}x{height}",
                "aspect_ratio": width / height if height > 0 else 0,
                "format": format_name,
                "orientation": "portrait" if height > width else "landscape" if width > height else "square",
                "is_portrait": height > width,
                "is_landscape": width >= height,
                "color_info": color_info
            }
        }
        
        # アスペクト比の名前を追加
        details["image_info"]["aspect_ratio_name"] = get_aspect_ratio_name(details["image_info"]["aspect_ratio"])
        
        return details
    
    except Exception as e:
        logger.error(f"画像の詳細情報取得中にエラーが発生しました: {e}")
        raise ImageAnalysisError(f"画像の詳細情報取得に失敗しました: {str(e)}")


def get_aspect_ratio_name(ratio: float) -> str:
    """
    アスペクト比から一般的な名前を取得します
    
    Args:
        ratio (float): アスペクト比（幅÷高さ）
        
    Returns:
        str: アスペクト比の名前
    """
    # 小数点以下2桁に丸める
    rounded = round(ratio, 2)
    
    # 一般的なアスペクト比と許容誤差
    if abs(rounded - 1.33) <= 0.03:
        return "4:3（標準）"
    elif abs(rounded - 1.78) <= 0.03:
        return "16:9（ワイド）"
    elif abs(rounded - 1.6) <= 0.03:
        return "16:10"
    elif abs(rounded - 1.85) <= 0.03:
        return "1.85:1（映画）"
    elif abs(rounded - 2.35) <= 0.03:
        return "2.35:1（シネマスコープ）"
    elif abs(rounded - 1.0) <= 0.03:
        return "1:1（正方形）"
    elif abs(rounded - 0.75) <= 0.03:
        return "3:4（縦向き標準）"
    elif abs(rounded - 0.56) <= 0.03:
        return "9:16（縦向きワイド）"
    
    # その他のカスタム比率
    return f"{rounded:.2f}:1"


def analyze_image(image_path: str, output_dir: str = "analysis_results", 
                 generate_visual: bool = True, mock: bool = True,
                 model_path: Optional[str] = None) -> Dict[str, Any]:
    """
    画像を解析し、結果を出力します
    
    Args:
        image_path (str): 解析する画像のパス
        output_dir (str): 結果を出力するディレクトリ
        generate_visual (bool): 視覚的フィードバックを生成するかどうか
        mock (bool): モックデータを使用するかどうか（実際のAIモデルを使用しない）
        model_path (Optional[str]): 使用するモデルのパス（Noneの場合はデフォルトモデルを使用）
        
    Returns:
        Dict[str, Any]: 解析結果
        
    Raises:
        ImageAnalysisError: 解析に失敗した場合
    """
    try:
        # 開始時間を記録
        start_time = time.time()
        logger.info(f"画像解析を開始します: {image_path}")
        
        # 出力ディレクトリを確保
        output_path = ensure_output_dir(output_dir)
        
        # 画像の詳細情報を取得
        image_details = get_image_details(image_path)
        
        # 解析結果
        if mock:
            analysis_results = generate_mock_analysis_results(image_path, image_details)
            model_used = "mock"
        else:
            # YOLOモデルを使用した実際の解析を実行
            if YOLO_AVAILABLE:
                yolo_model = YOLOModel(model_path=model_path)
                detection_results = yolo_model.detect(image_path)
                
                # 詳細な解析結果を構築
                analysis_results = build_analysis_results(image_path, image_details, detection_results)
                model_used = "yolov8"
            else:
                logger.warning("YOLOモデルが利用できないため、モックデータを使用します。")
                analysis_results = generate_mock_analysis_results(image_path, image_details)
                model_used = "mock (YOLO unavailable)"
        
        # メタデータを追加
        metadata = {
            "version": "1.0.0",
            "mode": "mock_analysis" if mock else "yolo_analysis",
            "image_path": image_path
        }
        
        # 完全な結果を構築
        full_results = {
            "metadata": metadata,
            "image_details": image_details,
            "analysis": analysis_results
        }
        
        # デバッグ情報
        full_results["debug_info"] = {
            "mock_data": mock,
            "model_used": None if mock else model_used,
            "color_analysis": {
                "estimated_brightness": "bright" if image_details["image_info"]["color_info"].get("brightness_percent", 50) > 70 else "medium" if image_details["image_info"]["color_info"].get("brightness_percent", 50) > 30 else "dark",
                "dominant_colors": [image_details["image_info"]["color_info"].get("avg_color_hex", "#ffffff")],
                "color_variance": "high" if image_details["image_info"]["color_info"].get("color_variance", 50) > 80 else "medium" if image_details["image_info"]["color_info"].get("color_variance", 50) > 40 else "low"
            }
        }
        
        # 処理時間を記録
        elapsed_time = time.time() - start_time
        full_results["performance"] = {
            "analysis_time_seconds": elapsed_time,
            "analysis_time_ms": elapsed_time * 1000
        }
        
        # 現在の日時
        full_results["timestamp"] = datetime.datetime.now().isoformat()
        
        # JSONファイルに保存
        filename = Path(image_path).stem
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = output_path / f"analysis_{filename}_{timestamp}.json"
        
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(full_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"解析結果をJSONに保存しました: {result_file}")
        
        # 視覚的フィードバックを生成（オプション）
        visual_feedback_path = None
        if generate_visual:
            visual_feedback_path = generate_visual_feedback(
                image_path, 
                full_results, 
                output_path / f"{filename}_feedback_{timestamp}.png"
            )
            
        # 結果を返す
        return {
            "results": full_results,
            "result_file": str(result_file),
            "visual_feedback": str(visual_feedback_path) if visual_feedback_path else None,
            "success": True
        }
            
    except Exception as e:
        logger.error(f"画像解析中にエラーが発生しました: {str(e)}")
        return {
            "error": str(e),
            "success": False
        }


def build_analysis_results(image_path: str, image_details: Dict, detection_results: Dict) -> Dict:
    """
    YOLOv8検出結果から詳細な解析結果を構築します
    
    Args:
        image_path (str): 画像パス
        image_details (Dict): 画像の詳細情報
        detection_results (Dict): YOLOv8検出結果
        
    Returns:
        Dict: 構造化された解析結果
    """
    # 検出されたオブジェクト
    objects = detection_results.get("objects", [])
    
    # 検出されたオブジェクトからタグを生成
    tags = list(set(obj["label"] for obj in objects))
    
    # 検出されたオブジェクトの数から簡単な説明を生成
    object_counts = {}
    for obj in objects:
        label = obj["label"]
        object_counts[label] = object_counts.get(label, 0) + 1
    
    # 説明文を生成
    description_parts = []
    for label, count in object_counts.items():
        if count == 1:
            description_parts.append(f"1つの{label}")
        else:
            description_parts.append(f"{count}個の{label}")
    
    if description_parts:
        description = "この画像には" + "、".join(description_parts) + "が含まれています。"
    else:
        description = "この画像には特定のオブジェクトが検出されませんでした。"
    
    # 平均信頼度を計算
    if objects:
        avg_confidence = sum(obj["confidence"] for obj in objects) / len(objects)
    else:
        avg_confidence = 0.0
    
    # OCR結果（現在はダミー）
    ocr_results = {
        "detected": False,
        "text": "",
        "regions": []
    }
    
    # 結果を構築
    return {
        "objects": objects,
        "description": description,
        "tags": tags,
        "confidence": avg_confidence,
        "ocr": ocr_results
    }


def generate_mock_analysis_results(image_path: str, image_details: Dict) -> Dict:
    """
    モック解析結果を生成します（開発およびテスト用）
    
    Args:
        image_path (str): 画像パス
        image_details (Dict): 画像の詳細情報
        
    Returns:
        Dict: モック解析結果
    """
    # 画像サイズに基づいてモックオブジェクトを生成
    width = image_details["image_info"]["width"]
    height = image_details["image_info"]["height"]
    
    # ダミーオブジェクト
    objects = [
        {
            "label": "window",
            "confidence": 0.92,
            "bbox": {
                "x": int(width * 0.1),
                "y": int(height * 0.1),
                "width": int(width * 0.8),
                "height": int(height * 0.7)
            }
        },
        {
            "label": "icon",
            "confidence": 0.85,
            "bbox": {
                "x": int(width * 0.05),
                "y": int(height * 0.1),
                "width": int(width * 0.05),
                "height": int(height * 0.067)
            }
        },
        {
            "label": "text",
            "confidence": 0.76,
            "bbox": {
                "x": int(width * 0.2),
                "y": int(height * 0.15),
                "width": int(width * 0.6),
                "height": int(height * 0.05)
            }
        }
    ]
    
    # ダミーOCR結果
    ocr = {
        "detected": True,
        "confidence": 0.72,
        "text": "サンプルテキスト - デバッグ用のモックデータです。",
        "regions": [
            {
                "text": "サンプルテキスト",
                "bbox": {
                    "x": int(width * 0.2),
                    "y": int(height * 0.15),
                    "width": int(width * 0.3),
                    "height": int(height * 0.05)
                },
                "confidence": 0.78
            },
            {
                "text": "デバッグ用のモックデータです。",
                "bbox": {
                    "x": int(width * 0.2),
                    "y": int(height * 0.2),
                    "width": int(width * 0.4),
                    "height": int(height * 0.05)
                },
                "confidence": 0.65
            }
        ]
    }
    
    return {
        "objects": objects,
        "ocr": ocr,
        "description": "これはデスクトップのスクリーンショットです。ウィンドウ、アイコン、およびテキストが表示されています。",
        "tags": ["スクリーンショット", "デスクトップ", "ウィンドウ", "UI"],
        "confidence": 0.87
    }


def generate_visual_feedback(image_path: str, analysis_results: Dict[str, Any], 
                            output_file: Path) -> Path:
    """
    解析結果の視覚的フィードバックを生成します
    
    Args:
        image_path (str): 元の画像ファイルのパス
        analysis_results (Dict[str, Any]): 解析結果
        output_file (Path): 出力ファイルのパス
        
    Returns:
        Path: 生成された視覚的フィードバック画像のパス
        
    Raises:
        ImageAnalysisError: 視覚的フィードバック生成に失敗した場合
    """
    if not PIL_AVAILABLE:
        raise ImageAnalysisError("PIL (Pillow) ライブラリがインストールされていません。'pip install pillow' を実行してください。")
    
    try:
        # 元画像の読み込み
        with Image.open(image_path) as img:
            # 画像をRGBAモードに変換（描画用）
            if img.mode != "RGBA":
                img = img.convert("RGBA")
            
            # 作業用の画像を複製
            annotated_img = img.copy()
            draw = ImageDraw.Draw(annotated_img)
            
            # フォントの設定（デフォルトフォント）
            try:
                # Windowsの場合
                font_path = "C:\\Windows\\Fonts\\meiryo.ttc"
                if not os.path.exists(font_path):
                    font_path = "C:\\Windows\\Fonts\\msgothic.ttc"
                
                title_font = ImageFont.truetype(font_path, 20)
                normal_font = ImageFont.truetype(font_path, 14)
            except Exception:
                # フォントが見つからない場合はデフォルトフォントを使用
                title_font = ImageFont.load_default()
                normal_font = ImageFont.load_default()
            
            # 検出されたオブジェクトの描画
            if "objects" in analysis_results.get("analysis", {}):
                for obj in analysis_results["analysis"]["objects"]:
                    # バウンディングボックスの取得
                    bbox = obj["bbox"]
                    x, y = bbox["x"], bbox["y"]
                    w, h = bbox["width"], bbox["height"]
                    
                    # バウンディングボックスの描画
                    draw.rectangle([(x, y), (x + w, y + h)], outline=(0, 255, 0, 220), width=2)
                    
                    # ラベルの背景
                    label_text = f"{obj['label']} ({obj['confidence']:.2f})"
                    draw.rectangle([(x, y - 25), (x + len(label_text) * 7, y)], fill=(0, 255, 0, 180))
                    
                    # ラベルのテキスト
                    draw.text((x + 5, y - 20), label_text, fill=(0, 0, 0, 255), font=normal_font)
            
            # OCRテキスト領域の描画
            if "ocr" in analysis_results.get("analysis", {}) and analysis_results["analysis"]["ocr"].get("detected", False):
                for region in analysis_results["analysis"]["ocr"].get("regions", []):
                    # 領域の取得
                    bbox = region["bbox"]
                    x, y = bbox["x"], bbox["y"]
                    w, h = bbox["width"], bbox["height"]
                    
                    # テキスト領域の描画
                    draw.rectangle([(x, y), (x + w, y + h)], outline=(255, 0, 0, 220), width=2)
                    
                    # テキストの背景
                    text_confidence = f" ({region['confidence']:.2f})"
                    draw.rectangle([(x, y - 25), (x + len(region['text']) * 7, y)], fill=(255, 0, 0, 180))
                    
                    # テキスト内容
                    draw.text((x + 5, y - 20), region['text'] + text_confidence, fill=(255, 255, 255, 255), font=normal_font)
            
            # 画像情報のオーバーレイ
            info_text = [
                f"解析タイムスタンプ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"元画像: {Path(image_path).name}",
                f"解像度: {img.width}x{img.height} ({analysis_results['image_details']['image_info']['orientation']})",
                f"アスペクト比: {analysis_results['image_details']['image_info']['aspect_ratio_name']}"
            ]
            
            # 情報テキストの位置
            info_x, info_y = 10, 10
            
            # 情報の背景
            text_height = len(info_text) * 25 + 10
            draw.rectangle([(info_x - 5, info_y - 5), (info_x + 350, info_y + text_height)], 
                          fill=(0, 0, 0, 180))
            
            # 情報テキストの描画
            for i, text in enumerate(info_text):
                draw.text((info_x, info_y + i * 25), text, fill=(255, 255, 255, 255), font=normal_font)
            
            # 解析情報のオーバーレイ
            if "analysis" in analysis_results:
                analysis_info = [
                    "【解析結果サマリー】",
                    f"検出オブジェクト: {len(analysis_results['analysis'].get('objects', []))}個",
                    f"テキスト検出: {'あり' if analysis_results['analysis'].get('ocr', {}).get('detected', False) else 'なし'}",
                    f"説明: {analysis_results['analysis'].get('description', 'なし')}",
                ]
                
                # 解析情報の位置
                analysis_x = 10
                analysis_y = img.height - len(analysis_info) * 25 - 15
                
                # 解析情報の背景
                analysis_height = len(analysis_info) * 25 + 10
                draw.rectangle([(analysis_x - 5, analysis_y - 5), (analysis_x + 500, analysis_y + analysis_height)], 
                              fill=(0, 0, 0, 180))
                
                # 解析情報テキストの描画
                for i, text in enumerate(analysis_info):
                    if i == 0:  # タイトル
                        draw.text((analysis_x, analysis_y + i * 25), text, fill=(255, 255, 0, 255), font=title_font)
                    else:
                        draw.text((analysis_x, analysis_y + i * 25), text, fill=(255, 255, 255, 255), font=normal_font)
            
            # 結果を保存
            annotated_img.save(output_file)
            
            logger.info(f"視覚的フィードバックをPNG画像として保存しました: {output_file}")
            return output_file
    
    except Exception as e:
        logger.error(f"視覚的フィードバックの生成中にエラーが発生しました: {e}")
        raise ImageAnalysisError(f"視覚的フィードバックの生成に失敗しました: {str(e)}") 