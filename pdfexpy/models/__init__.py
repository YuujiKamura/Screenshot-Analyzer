"""
画像分析用のモデルモジュール
"""

try:
    from .yolo_model import YOLOModel, YOLO_AVAILABLE
except ImportError:
    YOLO_AVAILABLE = False
    
    # モジュールが存在しない場合のダミークラス
    class YOLOModel:
        def __init__(self, *args, **kwargs):
            pass
        
        def load(self):
            return False
        
        def detect(self, image_path):
            return {"error": "YOLOモデルがインストールされていません", "objects": []}
        
        def get_model_info(self):
            return {"loaded": False, "available": False}

from .model_loader import ModelLoader, ModelLoadError 