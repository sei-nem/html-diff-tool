@echo off
chcp 65001 > nul
echo ============================================
echo  URL HTML差分比較ツール ビルドスクリプト
echo ============================================
echo.

REM --- 仮想環境の有効化 ---
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
) else (
    echo ERROR: 仮想環境 .venv が見つかりません。先に python -m venv .venv を実行してください。
    pause
    exit /b 1
)

REM --- 依存パッケージのインストール ---
echo [1/2] 依存パッケージをインストール中...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: pip install に失敗しました。
    pause
    exit /b 1
)

echo.
echo [2/2] EXEをビルド中...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "html-diff-tool" ^
    --hidden-import=requests ^
    --hidden-import=certifi ^
    --hidden-import=charset_normalizer ^
    --hidden-import=idna ^
    --hidden-import=urllib3 ^
    --hidden-import=lxml ^
    --hidden-import=lxml.html ^
    --hidden-import=lxml.etree ^
    --hidden-import=lxml._elementpath ^
    run.py

if errorlevel 1 (
    echo ERROR: PyInstaller のビルドに失敗しました。
    pause
    exit /b 1
)

echo.
echo ============================================
echo  ビルド完了！
echo  dist\html-diff-tool.exe が生成されました。
echo ============================================
pause