"""
画像解析機能のテスト
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from PIL import Image
from pathlib import Path

from pdfexpy.utils.image_analysis import (
    analyze_image,
    generate_visual_feedback,
    get_image_details,
    ensure_output_dir,
    ImageAnalysisError
)

class TestImageAnalysis:
    """画像解析機能のテストクラス"""
    
    @pytest.fixture
    def mock_image(self):
        """テスト用のモック画像を作成する"""
        img = Image.new('RGB', (100, 100), color=(255, 255, 255))
        return img
    
    @pytest.fixture
    def image_path(self, tmp_path, mock_image):
        """テスト用の一時的な画像ファイルを作成する"""
        img_path = tmp_path / "test_image.png"
        mock_image.save(img_path)
        return str(img_path)
    
    @pytest.fixture
    def output_dir(self, tmp_path):
        """テスト用の出力ディレクトリを作成する"""
        out_dir = tmp_path / "output"
        return str(out_dir)
    
    def test_ensure_output_dir(self, output_dir):
        """ensure_output_dir関数のテスト"""
        # ディレクトリが存在しない場合、作成されることを確認
        assert not os.path.exists(output_dir)
        ensure_output_dir(output_dir)
        assert os.path.exists(output_dir)
        
        # 既に存在する場合もエラーにならないことを確認
        ensure_output_dir(output_dir)
        assert os.path.exists(output_dir)
    
    def test_get_image_details(self, image_path):
        """get_image_details関数のテスト"""
        details = get_image_details(image_path)
        assert isinstance(details, dict)
        assert "image_info" in details
        assert "format" in details["image_info"]
        
        # アスペクト比が1:1であることを確認（100x100の画像）
        assert "aspect_ratio" in details["image_info"]
        assert details["image_info"]["aspect_ratio"] == 1.0
    
    def test_get_image_details_invalid_path(self):
        """存在しない画像パスでエラーが発生することを確認"""
        with pytest.raises(ImageAnalysisError):
            get_image_details("non_existent_image.png")
    
    @patch("pdfexpy.utils.image_analysis.generate_mock_analysis_results")
    def test_analyze_image(self, mock_generate_analysis, image_path, output_dir):
        """analyze_image関数のテスト"""
        # モックの戻り値を設定
        mock_result = {
            "elements": [
                {"type": "text", "confidence": 0.95, "box": [10, 10, 50, 30]},
                {"type": "image", "confidence": 0.85, "box": [60, 10, 90, 40]}
            ],
            "summary": {
                "text_count": 1,
                "image_count": 1
            }
        }
        mock_generate_analysis.return_value = mock_result
        
        # 通常の呼び出し
        result = analyze_image(image_path, output_dir)
        
        # 結果の構造を確認
        assert "results" in result
        assert "elements" in result["results"]
        assert "summary" in result["results"]
        
        # 視覚的フィードバックを無効にしたケース
        result = analyze_image(image_path, output_dir, generate_visual=False)
        
        assert "results" in result
        assert "elements" in result["results"]
        assert "summary" in result["results"]
    
    @patch("pdfexpy.utils.image_analysis.PIL_AVAILABLE", True)
    @patch("pdfexpy.utils.image_analysis.get_image_details")
    @patch("pathlib.Path.exists")
    @patch("pdfexpy.utils.image_analysis.ensure_output_dir")
    @patch("PIL.Image.open")
    def test_generate_visual_feedback_simple(self, mock_image_open, mock_ensure_dir, mock_exists, mock_get_details, image_path, output_dir):
        """generate_visual_feedback関数の簡易バージョンのテスト"""
        # 画像詳細情報のモック
        mock_image_details = {
            "image_info": {
                "width": 100,
                "height": 100,
                "orientation": "横向き",
                "aspect_ratio": 1.0,
                "aspect_ratio_name": "1:1（正方形）"
            }
        }
        mock_get_details.return_value = mock_image_details
        
        # 画像のモック
        mock_image = MagicMock()
        mock_image.width = 100
        mock_image.height = 100
        mock_image.mode = "RGB"
        mock_image.__enter__.return_value = mock_image
        mock_image_open.return_value = mock_image
        
        # draw機能のモック
        mock_draw = MagicMock()
        
        with patch("PIL.ImageDraw.Draw", return_value=mock_draw):
            # テスト用の解析結果
            analysis_result = {
                "elements": [
                    {"type": "text", "confidence": 0.95, "box": [10, 10, 50, 30]},
                    {"type": "image", "confidence": 0.85, "box": [60, 10, 90, 40]}
                ],
                "image_details": mock_image_details
            }
            
            # 出力ファイルのモック
            mock_ensure_dir.return_value = Path(output_dir)
            mock_exists.return_value = True
            
            # 関数呼び出し
            result_path = generate_visual_feedback(image_path, analysis_result, output_dir)
            
            # 検証
            assert output_dir in str(result_path)
            assert mock_image_open.called
            assert mock_draw.text.called or mock_draw.rectangle.called 