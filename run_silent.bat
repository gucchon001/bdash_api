@echo off
chcp 65001 >nul

REM ==============================================
REM タスクスケジューラー用サイレント実行スクリプト
REM 対話的な要素を削除し、自動実行に最適化
REM ==============================================

REM 仮想環境のパスを設定
set "VENV_PATH=.\venv"

REM 実行するPythonモジュールの名前を設定
set "MODULE_NAME=src.main"

REM ログファイルを設定（オプション）
set "LOG_FILE=logs\scheduler_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log"

echo [%date% %time%] タスクスケジューラー実行開始

REM 仮想環境が存在するか確認
if exist "%VENV_PATH%\Scripts\activate.bat" (
    echo [%date% %time%] 仮想環境をアクティブ化しています...
    call "%VENV_PATH%\Scripts\activate.bat"
) else (
    echo [%date% %time%] ERROR: 仮想環境が見つかりません: %VENV_PATH%
    echo [%date% %time%] 仮想環境を作成するか、正しいパスを設定してください。
    exit /b 1
)

REM モジュールを実行
echo [%date% %time%] モジュールを実行しています: %MODULE_NAME%
python -m %MODULE_NAME%
if errorlevel 1 (
    echo [%date% %time%] ERROR: モジュールの実行中にエラーが発生しました。
    exit /b 1
) else (
    echo [%date% %time%] モジュールの実行が正常に完了しました。
)

REM 仮想環境をディアクティブ化
echo [%date% %time%] 仮想環境をディアクティブ化しています...
deactivate

echo [%date% %time%] タスクスケジューラー実行完了
exit /b 0 