import os
import glob
import subprocess
import sys
from datetime import datetime

def batch_analyze_images(image_dir="test_images", mock=True, headless=True):
    """
    指定したディレクトリ内の画像を一括で分析します
    
    Args:
        image_dir (str): 画像が格納されているディレクトリパス
        mock (bool): モックデータを使用するかどうか
        headless (bool): ヘッドレスモードで実行するかどうか
    """
    # 画像ファイルのリストを取得
    image_files = glob.glob(os.path.join(image_dir, "*.png"))
    
    if not image_files:
        print(f"[エラー] {image_dir} ディレクトリに画像ファイルが見つかりません")
        return
    
    print(f"[情報] {len(image_files)}個の画像ファイルを処理します")
    
    # 各画像を処理
    for i, image_file in enumerate(image_files, 1):
        print(f"[処理中] {i}/{len(image_files)}: {image_file}")
        
        # コマンドを構築
        cmd = [sys.executable, "-m", "pdfexpy.app", "--image", image_file]
        
        if mock:
            cmd.append("--mock")
        
        if headless:
            cmd.append("--headless")
        
        # 環境変数を設定
        env = os.environ.copy()
        env["PYTHONPATH"] = os.getcwd()
        
        # プロセスを実行
        start_time = datetime.now()
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        end_time = datetime.now()
        
        # 結果を表示
        duration = (end_time - start_time).total_seconds()
        
        if result.returncode == 0:
            print(f"[成功] 処理時間: {duration:.2f}秒")
        else:
            print(f"[失敗] 処理時間: {duration:.2f}秒")
            print(f"エラー出力: {result.stderr}")
    
    print(f"[完了] 全ての画像処理が終了しました")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="複数画像の一括分析")
    parser.add_argument("--dir", default="test_images", help="画像ディレクトリ")
    parser.add_argument("--no-mock", action="store_true", help="モックデータを使用しない")
    parser.add_argument("--no-headless", action="store_true", help="GUIモードで実行")
    
    args = parser.parse_args()
    
    batch_analyze_images(
        image_dir=args.dir,
        mock=not args.no_mock,
        headless=not args.no_headless
    ) 