# スクリーンショット画像解析テストを実行するPowerShellスクリプト

# カレントディレクトリを設定
Set-Location -Path $PSScriptRoot

# 必要なディレクトリが存在することを確認
if (-not (Test-Path -Path "test_results")) {
    New-Item -Path "test_results" -ItemType Directory -Force
    New-Item -Path "test_results/screenshots" -ItemType Directory -Force
    New-Item -Path "test_results/analysis" -ItemType Directory -Force
    New-Item -Path "test_results/debug" -ItemType Directory -Force
}

Write-Host "スクリーンショット画像解析テストを開始します..." -ForegroundColor Green

# テストオプションを取得
$testOption = $args[0]
if (-not $testOption) {
    $testOption = "all"  # デフォルトはすべてのテスト
}

# テストコマンドを実行
try {
    if ($testOption -eq "all") {
        Write-Host "すべてのテストを実行します" -ForegroundColor Cyan
        python test_screenshot_analysis.py --test all
    }
    elseif ($testOption -eq "screenshot") {
        Write-Host "スクリーンショット撮影テストを実行します" -ForegroundColor Cyan
        python test_screenshot_analysis.py --test screenshot
    }
    elseif ($testOption -eq "analysis") {
        Write-Host "スクリーンショット解析テストを実行します" -ForegroundColor Cyan
        python test_screenshot_analysis.py --test analysis
    }
    elseif ($testOption -eq "debug") {
        Write-Host "デバッグモードテストを実行します" -ForegroundColor Cyan
        python test_screenshot_analysis.py --test debug
    }
    else {
        Write-Host "無効なテストオプション: $testOption" -ForegroundColor Red
        Write-Host "有効なオプション: all, screenshot, analysis, debug" -ForegroundColor Yellow
        exit 1
    }

    if ($LASTEXITCODE -eq 0) {
        Write-Host "テストが正常に完了しました" -ForegroundColor Green
    } else {
        Write-Host "テスト中にエラーが発生しました (終了コード: $LASTEXITCODE)" -ForegroundColor Red
    }
}
catch {
    Write-Host "エラーが発生しました: $_" -ForegroundColor Red
    exit 1
}

# 結果フォルダのパスを表示
Write-Host "テスト結果は以下のフォルダにあります:" -ForegroundColor Cyan
Write-Host "  $((Resolve-Path 'test_results').Path)" -ForegroundColor Yellow 