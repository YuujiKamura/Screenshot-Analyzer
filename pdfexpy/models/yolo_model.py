"""
YOLOv8モデルを扱うためのクラス
"""
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# YOLOv8モデルのインポートを試みる
try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False

class YOLOModel:
    """YOLOv8モデルを扱うためのクラス"""
    
    def __init__(self, model_path: Optional[str] = None, confidence: float = 0.25):
        """
        YOLOモデルを初期化します
        
        Args:
            model_path: モデルファイルのパス。Noneの場合はデフォルトモデル(yolov8n)を使用
            confidence: 検出の信頼度しきい値 (0.0-1.0)
        """
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.is_loaded = False
        self.confidence = confidence
        
        # モデルパスが指定されていない場合はデフォルトモデルのパスを使用
        self.model_path = model_path or "yolov8n.pt"
        
        if not YOLO_AVAILABLE:
            self.logger.warning("ultralytics (YOLOv8) がインストールされていないか、インポートできません。")
    
    def load(self) -> bool:
        """
        YOLOモデルをロードします
        
        Returns:
            bool: ロードに成功したかどうか
        """
        if not YOLO_AVAILABLE:
            self.logger.error("YOLOモデルをロードできません: ultralytics がインポートできません")
            return False
        
        try:
            self.logger.info(f"YOLOモデルをロードしています: {self.model_path}")
            self.model = YOLO(self.model_path)
            self.is_loaded = True
            self.logger.info("YOLOモデルのロードに成功しました")
            return True
        except Exception as e:
            self.logger.error(f"YOLOモデルのロード中にエラーが発生しました: {str(e)}")
            self.is_loaded = False
            return False
    
    def detect(self, image_path: str) -> Dict:
        """
        画像内のオブジェクトを検出します
        
        Args:
            image_path: 分析する画像ファイルのパス
            
        Returns:
            Dict: 検出結果を含む辞書
        """
        if not self.is_loaded:
            if not self.load():
                self.logger.error("モデルがロードされていないため、検出を実行できません")
                return {"error": "モデルがロードされていません", "objects": []}
        
        try:
            results = self.model(image_path, conf=self.confidence, verbose=False)
            
            # 検出結果を処理
            detected_objects = []
            
            # 最初の結果を処理 (複数画像の場合は追加処理が必要)
            result = results[0]
            
            # 検出されたオブジェクトを処理
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()  # バウンディングボックス座標
                confidence = float(box.conf[0])        # 信頼度
                class_id = int(box.cls[0])             # クラスID
                label = result.names[class_id]         # クラス名
                
                detected_objects.append({
                    "label": label,
                    "confidence": confidence,
                    "bbox": {
                        "x": int(x1),
                        "y": int(y1),
                        "width": int(x2 - x1),
                        "height": int(y2 - y1)
                    }
                })
            
            return {
                "objects": detected_objects,
                "count": len(detected_objects),
                "image_path": image_path,
                "model": "yolov8"
            }
            
        except Exception as e:
            self.logger.error(f"オブジェクト検出中にエラーが発生しました: {str(e)}")
            return {
                "error": str(e),
                "objects": [],
                "image_path": image_path
            }
    
    def get_model_info(self) -> Dict:
        """
        モデル情報を取得します
        
        Returns:
            Dict: モデル情報を含む辞書
        """
        if not self.is_loaded:
            return {
                "loaded": False,
                "model_path": self.model_path,
                "available": YOLO_AVAILABLE
            }
        
        return {
            "loaded": True,
            "model_path": self.model_path,
            "model_type": "yolov8",
            "confidence_threshold": self.confidence
        } 