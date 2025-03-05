# PDF/画像解析ツール（ヘッドレスモード機能）

このツールは、PDFや画像を解析して、テキスト抽出（OCR）や物体検出を行います。GUIモードとヘッドレスモード（コマンドライン）の両方で実行できます。

## 機能

- **TensorFlow.js**による画像分類と物体検出
  - MobileNetによる画像分類
  - COCO-SSDによる物体検出
- **YOLOv8**によるスクリーンショット解析
  - リアルタイムスクリーンショットの自動撮影
  - 画面上の物体検出と視覚的フィードバック
  - デバッグプロセスの視覚的サポート
- **OCR処理**によるテキスト抽出
- **スクリーンショット**の自動撮影と解析
- **ディレクトリ監視**による自動解析
- **定期実行**によるスケジュール解析
- **バッチ処理**による複数画像の一括解析
- **詳細なログ記録**システム

## インストール

### NPMパッケージのインストール
```bash
npm install
```

### Pythonパッケージのインストール
```bash
pip install -r requirements.txt
```

## 使い方

### GUIモード

```bash
npm start
```

### ヘッドレスモード（コマンドライン）

#### 1. スクリーンショット撮影と解析

```bash
npm run screenshot
# または
npx electron . --headless --screenshot
```

#### 2. 特定の画像またはフォルダを解析

```bash
npx electron . --headless --analyze "C:/path/to/image.png"
# フォルダ内のすべての画像
npx electron . --headless --analyze "C:/path/to/folder"
```

#### 3. 定期的にスクリーンショットを撮影して解析

```bash
# 15分ごとに実行
npm run schedule
# または
npx electron . --headless --schedule 15
```

#### 4. フォルダを監視して新しい画像を自動解析

```bash
# デフォルトフォルダを監視
npm run watch
# または特定のフォルダを指定
npx electron . --headless --watch "C:/path/to/watch/folder"
```

#### 5. 解析結果の出力先を指定

```bash
npx electron . --headless --analyze "C:/path/to/image.png" --output "C:/path/to/output"
```

## YOLOv8スクリーンショット解析

YOLOv8を用いたスクリーンショット解析を利用して、デバッグプロセスに視覚的フィードバックを提供できます。

### スクリーンショットの撮影

```bash
python debug_screenshot.py take --output-dir screenshots --prefix debug
```

### 既存スクリーンショットの解析

```bash
python debug_screenshot.py analyze --image screenshots/screenshot.png --output-dir analysis_results
```

### デバッグモードの使用（スクリーンショット撮影と解析を一括実行）

```bash
python debug_screenshot.py debug --action "ログイン画面の解析" --output-dir debug_results
```

### プログラムからの利用例

```python
from pdfexpy.utils.screenshot_analyzer import debug_with_screenshot_analysis

# デバッグモードでスクリーンショット解析を実行
result = debug_with_screenshot_analysis(
    action_description="ボタンクリック後の状態",
    output_dir="debug_results",
    model_path="yolov8n.pt",  # デフォルトモデルを使用する場合は省略可能
    confidence=0.25
)

if result["success"]:
    print(f"解析が完了しました: {result['visual_feedback']}")
    print(f"検出されたオブジェクト: {result['objects_count']}個")
```

## オプション一覧

| オプション | 短縮形 | 説明 |
|------------|--------|------|
| `--headless` | `-h` | GUIなしで実行 |
| `--analyze` | `-a` | 指定した画像/フォルダを解析 |
| `--screenshot` | `-s` | スクリーンショットを撮影して解析 |
| `--output` | `-o` | 結果の出力先を指定 |
| `--schedule` | | 指定した間隔（分）で定期実行 |
| `--watch` | | 指定したフォルダを監視 |
| `--help` | | ヘルプを表示 |

## ログと結果

- ログファイル: `logs/app-log-YYYY-MM-DD.txt`
- 解析結果: `analysis_results/analysis-[画像ID]-[タイムスタンプ].json`

## 要件

- Node.js 16+
- Electron
- TensorFlow.js
- Windows/macOS/Linux

## 注意事項

TensorFlow.jsの実行には比較的高いスペックのマシンが必要です。特に物体検出処理は計算負荷が高くなる場合があります。 