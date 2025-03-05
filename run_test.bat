@echo off
REM スクリーンショット画像解析テストを実行するためのバッチファイル

REM PowerShellスクリプトを実行パスから実行
powershell -ExecutionPolicy Bypass -File "%~dp0run_screenshot_test.ps1" %*

REM 終了前に一時停止（結果を確認できるように）
pause 