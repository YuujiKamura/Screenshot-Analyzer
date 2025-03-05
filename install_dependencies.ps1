# テストに必要なPythonパッケージをインストールするスクリプト

Write-Host "スクリーンショット画像解析テストに必要なパッケージをインストールします..." -ForegroundColor Green

# 必要なパッケージをインストール
try {
    # ultralyticsがインストールされているか確認
    $output = python -c "import ultralytics" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ultralyticsをインストールしています..." -ForegroundColor Cyan
        python -m pip install ultralytics
    } else {
        Write-Host "ultralyticsはすでにインストールされています" -ForegroundColor Cyan
    }

    # pyautoguiがインストールされているか確認
    $output = python -c "import pyautogui" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "pyautoguiをインストールしています..." -ForegroundColor Cyan
        python -m pip install pyautogui
    } else {
        Write-Host "pyautoguiはすでにインストールされています" -ForegroundColor Cyan
    }

    # opencvがインストールされているか確認
    $output = python -c "import cv2" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "opencv-pythonをインストールしています..." -ForegroundColor Cyan
        python -m pip install opencv-python
    } else {
        Write-Host "opencv-pythonはすでにインストールされています" -ForegroundColor Cyan
    }

    # numpyがインストールされているか確認
    $output = python -c "import numpy" 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "numpyをインストールしています..." -ForegroundColor Cyan
        python -m pip install numpy
    } else {
        Write-Host "numpyはすでにインストールされています" -ForegroundColor Cyan
    }

    Write-Host "必要なパッケージのインストールが完了しました" -ForegroundColor Green

    # YOLOモデルファイルが存在するか確認
    if (-not (Test-Path -Path "yolov8n.pt")) {
        Write-Host "YOLOv8モデルファイルが見つかりません。ダウンロードします..." -ForegroundColor Yellow
        # ultralyticsからモデルファイルをダウンロード
        python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
    } else {
        Write-Host "YOLOv8モデルファイルが見つかりました" -ForegroundColor Cyan
    }
}
catch {
    Write-Host "エラーが発生しました: $_" -ForegroundColor Red
    exit 1
}

Write-Host "インストールが完了しました。テストを実行するには run_test.bat を実行してください。" -ForegroundColor Green
pause 