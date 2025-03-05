@echo off
REM スクリーンショット画像解析テストのセットアップと実行を一括で行うスクリプト

echo ===== スクリーンショット画像解析テストのセットアップと実行 =====

REM PowerShellの実行ポリシーを一時的に変更して実行
powershell -NoProfile -ExecutionPolicy Bypass -Command "& {Set-Location '%~dp0'; Write-Host 'PowerShell環境を準備しています...' -ForegroundColor Cyan; . './install_dependencies.ps1'; if ($?) { . './run_screenshot_test.ps1' %* }}"

if errorlevel 1 (
    echo エラーが発生しました。
    echo ログを確認してください。
) else (
    echo 処理が正常に完了しました。
)

echo.
pause 