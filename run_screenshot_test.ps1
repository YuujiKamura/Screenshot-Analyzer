# スクリーンショット画像解析テストを実行するPowerShellスクリプト

# エラー発生時に停止
$ErrorActionPreference = "Stop"

# カレントディレクトリを設定
try {
    Set-Location -Path $PSScriptRoot -ErrorAction Stop
    Write-Host "作業ディレクトリを設定しました: $PSScriptRoot" -ForegroundColor Cyan
}
catch {
    Write-Host "ディレクトリの設定に失敗しました: $_" -ForegroundColor Red
    exit 1
}

# 必要なディレクトリを作成
$directories = @(
    "test_results",
    "test_results/screenshots",
    "test_results/analysis",
    "test_results/debug"
)

foreach ($dir in $directories) {
    if (-not (Test-Path -Path $dir)) {
        try {
            New-Item -Path $dir -ItemType Directory -Force | Out-Null
            Write-Host "ディレクトリを作成しました: $dir" -ForegroundColor Green
        }
        catch {
            Write-Host "ディレクトリの作成に失敗しました: $dir" -ForegroundColor Red
            Write-Host "エラー: $_" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host "スクリーンショット画像解析テストを開始します..." -ForegroundColor Green

# テストオプションを取得
$testOption = $args[0]
if (-not $testOption) {
    $testOption = "all"  # デフォルトはすべてのテスト
}

# テストコマンドを実行
try {
    $pythonCmd = "python test_screenshot_analysis.py --test $testOption"
    
    switch ($testOption) {
        "all" {
            Write-Host "すべてのテストを実行します" -ForegroundColor Cyan
        }
        "screenshot" {
            Write-Host "スクリーンショット撮影テストを実行します" -ForegroundColor Cyan
        }
        "analysis" {
            Write-Host "スクリーンショット解析テストを実行します" -ForegroundColor Cyan
        }
        "debug" {
            Write-Host "デバッグモードテストを実行します" -ForegroundColor Cyan
        }
        default {
            Write-Host "無効なテストオプション: $testOption" -ForegroundColor Red
            Write-Host "有効なオプション: all, screenshot, analysis, debug" -ForegroundColor Yellow
            exit 1
        }
    }

    # Pythonスクリプトを実行
    Invoke-Expression $pythonCmd

    if ($LASTEXITCODE -eq 0) {
        Write-Host "テストが正常に完了しました" -ForegroundColor Green
    }
    else {
        Write-Host "テスト中にエラーが発生しました (終了コード: $LASTEXITCODE)" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}
catch {
    Write-Host "エラーが発生しました: $_" -ForegroundColor Red
    exit 1
}

# 結果フォルダのパスを表示
Write-Host "`nテスト結果は以下のフォルダにあります:" -ForegroundColor Cyan
Write-Host "  $((Resolve-Path 'test_results').Path)" -ForegroundColor Yellow 