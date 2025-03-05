# スクリーンショット画像解析テスト

このテストツールは、スクリーンショットを撮影し、YOLOv8モデルを使用して画像内のオブジェクトを検出する機能をテストします。

## 必要条件

- Python 3.6以上
- 以下のPythonパッケージ:
  - ultralytics
  - opencv-python
  - pyautogui
  - numpy

## テスト実行方法

### Windowsの場合

1. `run_test.bat` をダブルクリックで実行するか、コマンドプロンプトで実行します。

```
run_test.bat [テストオプション]
```

### PowerShellから直接実行する場合

```powershell
.\run_screenshot_test.ps1 [テストオプション]
```

### Pythonスクリプトを直接実行する場合

```
python test_screenshot_analysis.py --test [テストオプション]
```

## テストオプション

以下のオプションが使用可能です:

- `all`: すべてのテストを実行（デフォルト）
- `screenshot`: スクリーンショット撮影機能のみテスト
- `analysis`: スクリーンショット解析機能のみテスト
- `debug`: デバッグモード機能のみテスト

## テスト結果

テスト結果は `test_results` ディレクトリ内に保存されます:

- `test_results/screenshots`: 撮影されたスクリーンショット
- `test_results/analysis`: 解析結果
- `test_results/debug`: デバッグモードで生成された結果

## トラブルシューティング

1. **"'python' is not recognized as an internal or external command"** エラーが発生した場合:
   - Pythonがシステムパスに追加されていることを確認してください。

2. **YOLOモデルに関するエラーが発生した場合**:
   - ultralyticsパッケージが正しくインストールされていることを確認してください: `pip install ultralytics`
   - YOLOモデルファイル（yolov8n.pt）がプロジェクトのルートディレクトリに存在することを確認してください。

3. **スクリーンショット撮影に失敗する場合**:
   - pyautoguiパッケージが正しくインストールされていることを確認してください: `pip install pyautogui`

4. **PowerShellスクリプトが実行できない場合**:
   - 実行ポリシーを一時的に変更してみてください: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` 