"""
YOLOモデルで検出されたオブジェクトの視覚化および画像処理用のユーティリティ
"""
import random
import os
import json
from typing import Dict, List, Tuple, Union, Optional
import numpy as np
import cv2


def generate_colors(n: int = 100) -> List[Tuple[int, int, int]]:
    """
    n個の異なる色を生成します（BGR形式）
    
    Args:
        n: 生成する色の数
        
    Returns:
        List[Tuple[int, int, int]]: BGR形式の色のリスト
    """
    colors = []
    
    for i in range(n):
        # HSVからRGBに変換することで視覚的に区別しやすい色を生成
        h = i / n
        s = 0.9
        v = 0.9
        
        # HSVからRGBに変換
        r, g, b = colorsys_hsv_to_rgb(h, s, v)
        
        # 0-255の範囲にスケーリング
        r, g, b = int(r * 255), int(g * 255), int(b * 255)
        
        # OpenCVはBGR形式
        colors.append((b, g, r))
    
    return colors


def colorsys_hsv_to_rgb(h: float, s: float, v: float) -> Tuple[float, float, float]:
    """
    HSVからRGBに変換します（colorsysの代替実装）
    
    Args:
        h: 色相 (0-1)
        s: 彩度 (0-1)
        v: 明度 (0-1)
        
    Returns:
        Tuple[float, float, float]: RGB値 (各0-1)
    """
    if s == 0.0:
        return v, v, v
    
    i = int(h * 6)
    f = (h * 6) - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    
    i %= 6
    
    if i == 0:
        return v, t, p
    elif i == 1:
        return q, v, p
    elif i == 2:
        return p, v, t
    elif i == 3:
        return p, q, v
    elif i == 4:
        return t, p, v
    else:
        return v, p, q


def visualize_annotations(
    image: np.ndarray,
    objects: List[Dict],
    colors: Optional[List[Tuple[int, int, int]]] = None,
    class_names: Optional[Dict[int, str]] = None,
    thickness: int = 2,
    font_scale: float = 0.6,
    show_confidence: bool = True
) -> np.ndarray:
    """
    検出されたオブジェクトを描画します
    
    Args:
        image: 描画対象のCV2画像 (BGR形式)
        objects: 検出オブジェクトのリスト [{"label": "person", "confidence": 0.83, "bbox": {...}}]
        colors: 各クラスの色。Noneの場合は自動生成。
        class_names: クラスID->クラス名の辞書。Noneの場合はobjectsから取得
        thickness: 線の太さ
        font_scale: フォントサイズ
        show_confidence: 信頼度スコアを表示するかどうか
        
    Returns:
        np.ndarray: 注釈付きの画像
    """
    # 画像のコピーを作成（元の画像を変更しないため）
    result_image = image.copy()
    
    # クラス名を抽出（重複なし）
    if class_names is None:
        unique_labels = set(obj["label"] for obj in objects)
        class_names = {i: label for i, label in enumerate(unique_labels)}
    
    # 色を生成（指定されていない場合）
    if colors is None:
        colors = generate_colors(len(class_names))
    
    # 各オブジェクトを描画
    for obj in objects:
        # バウンディングボックスの座標を取得
        bbox = obj["bbox"]
        x, y = bbox["x"], bbox["y"]
        w, h = bbox["width"], bbox["height"]
        
        # ラベルとスコアを取得
        label = obj["label"]
        score = obj.get("confidence", 0.0)
        
        # クラスIDを取得
        class_id = next((i for i, name in class_names.items() if name == label), 0)
        
        # 色を取得
        color = colors[class_id % len(colors)]
        
        # バウンディングボックスを描画
        cv2.rectangle(result_image, (x, y), (x + w, y + h), color, thickness)
        
        # ラベルテキストを準備
        if show_confidence:
            label_text = f"{label} {score:.2f}"
        else:
            label_text = label
        
        # ラベルの背景を描画
        text_size, _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
        cv2.rectangle(
            result_image,
            (x, y - text_size[1] - 5),
            (x + text_size[0], y),
            color,
            -1  # -1は塗りつぶし
        )
        
        # ラベルテキストを描画
        cv2.putText(
            result_image,
            label_text,
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            (255, 255, 255),  # 白色
            thickness
        )
    
    return result_image


def save_detection_results(
    results: Dict,
    output_path: str,
    save_annotated_image: bool = True,
    image_output_path: Optional[str] = None
) -> Dict:
    """
    検出結果をJSONファイルに保存し、オプションで注釈付き画像も保存します
    
    Args:
        results: 検出結果の辞書
        output_path: 出力JSONファイルのパス
        save_annotated_image: 注釈付き画像を保存するかどうか
        image_output_path: 画像の出力パス（Noneの場合はoutput_pathから拡張子を変更）
        
    Returns:
        Dict: ファイルパスを含む結果辞書
    """
    # 結果をJSONとして保存
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    result_files = {
        "json": output_path
    }
    
    # 注釈付き画像を保存
    if save_annotated_image and results.get("image_path") and results.get("objects"):
        if image_output_path is None:
            # 出力パスから拡張子を変更
            image_output_path = os.path.splitext(output_path)[0] + ".png"
        
        # 画像を読み込み
        image = cv2.imread(results["image_path"])
        
        if image is not None:
            # 注釈を描画
            annotated_image = visualize_annotations(
                image=image,
                objects=results["objects"]
            )
            
            # 画像を保存
            cv2.imwrite(image_output_path, annotated_image)
            result_files["image"] = image_output_path
    
    return result_files 