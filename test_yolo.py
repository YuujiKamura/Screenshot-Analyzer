"""
YOLOv8モデルをテストするスクリプト
"""
import os
import sys
import argparse
import time
from pathlib import Path

# 現在のディレクトリをPYTHONPATHに追加
sys.path.insert(0, os.getcwd())

# pdfexpyパッケージから必要なモジュールをインポート
from pdfexpy.models import YOLOModel, YOLO_AVAILABLE
from pdfexpy.utils.image_analysis import analyze_image


def test_yolo_model(image_path, use_mock=False, output_dir="output", model_path=None):
    """
    YOLOモデルをテストします
    
    Args:
        image_path (str): テスト対象の画像パス
        use_mock (bool): モックデータを使用するかどうか
        output_dir (str): 出力ディレクトリ
        model_path (str): 使用するモデルのパス
    """
    print(f"テスト画像: {image_path}")
    print(f"YOLOモデルは利用可能: {YOLO_AVAILABLE}")
    
    if use_mock:
        print("モックモードで実行します")
    elif not YOLO_AVAILABLE:
        print("YOLOモデルが利用できないため、モックモードで実行します")
        use_mock = True
    
    # 開始時間
    start_time = time.time()
    
    if not use_mock:
        # YOLOモデルの初期化
        print(f"モデルを初期化します: {model_path or 'デフォルト'}")
        yolo = YOLOModel(model_path=model_path)
        
        # モデルのロード
        load_start = time.time()
        success = yolo.load()
        load_time = time.time() - load_start
        
        if not success:
            print(f"モデルのロードに失敗しました。モックモードで実行します。")
            use_mock = True
        else:
            print(f"モデルのロードに成功しました。所要時間: {load_time:.2f}秒")
            
            # モデル情報
            model_info = yolo.get_model_info()
            print(f"モデル情報: {model_info}")
            
            # オブジェクト検出
            detect_start = time.time()
            results = yolo.detect(image_path)
            detect_time = time.time() - detect_start
            
            print(f"検出完了！所要時間: {detect_time:.2f}秒")
            print(f"検出されたオブジェクト: {results.get('count', 0)}個")
            
            for i, obj in enumerate(results.get("objects", []), 1):
                print(f"  {i}. {obj['label']} (信頼度: {obj['confidence']:.2f})")
    
    # 画像分析の実行（完全な処理を含む）
    print("\n画像の総合分析を実行中...")
    analysis_start = time.time()
    result = analyze_image(
        image_path=image_path,
        output_dir=output_dir,
        generate_visual=True,
        mock=use_mock,
        model_path=model_path
    )
    analysis_time = time.time() - analysis_start
    
    if result["success"]:
        print(f"画像分析が完了しました。所要時間: {analysis_time:.2f}秒")
        print(f"結果ファイル: {result['result_file']}")
        print(f"視覚的フィードバック: {result['visual_feedback']}")
    else:
        print(f"画像分析中にエラーが発生しました: {result.get('error', '不明なエラー')}")
    
    # 総実行時間
    total_time = time.time() - start_time
    print(f"\n総実行時間: {total_time:.2f}秒")


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="YOLOv8モデルテスト")
    parser.add_argument("--image", required=True, help="テスト画像のパス")
    parser.add_argument("--mock", action="store_true", help="モックデータを使用")
    parser.add_argument("--model", help="使用するモデルファイルのパス")
    parser.add_argument("--output", default="output", help="出力ディレクトリ")
    
    args = parser.parse_args()
    
    # 出力ディレクトリの作成
    os.makedirs(args.output, exist_ok=True)
    
    # テストの実行
    test_yolo_model(
        image_path=args.image,
        use_mock=args.mock,
        output_dir=args.output,
        model_path=args.model
    )


if __name__ == "__main__":
    main() 