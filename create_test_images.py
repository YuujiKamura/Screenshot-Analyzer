from PIL import Image, ImageDraw
import os

def create_test_images():
    # ディレクトリを作成
    os.makedirs('test_images', exist_ok=True)
    
    # 複数の画像を生成
    for i in range(1, 4):
        # 新規画像を作成
        im = Image.new('RGB', (640, 480), color=(255, 255, 255))
        draw = ImageDraw.Draw(im)
        
        # 赤い枠を描画
        draw.rectangle([(50, 50), (590, 430)], outline=(255, 0, 0), width=2)
        
        # テキストを描画
        draw.text((320, 240), f'テスト画像 {i}', fill=(0, 0, 0))
        
        # 画像を保存
        filename = f'test_images/test_image_{i}.png'
        im.save(filename)
        print(f'画像を保存しました: {filename}')

if __name__ == "__main__":
    create_test_images() 