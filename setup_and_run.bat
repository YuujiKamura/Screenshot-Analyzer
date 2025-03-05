@echo off
REM スクリーンショット画像解析テストのセットアップと実行を一括で行うスクリプト

echo ===== スクリーンショット画像解析テストのセットアップと実行 =====

REM 依存関係のインストール
echo 依存関係をインストールしています...
powershell -ExecutionPolicy Bypass -File "%~dp0install_dependencies.ps1"

REM インストールが成功したか確認
if %ERRORLEVEL% NEQ 0 (
    echo 依存関係のインストールに失敗しました。
    goto :end
)

echo.
echo 依存関係のインストールが完了しました。テストを実行します...
echo.

REM テストの実行
powershell -ExecutionPolicy Bypass -File "%~dp0run_screenshot_test.ps1" %*

:end
echo.
echo 処理が完了しました。
pause 