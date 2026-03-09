@echo off
chcp 65001 > nul
echo ============================================
echo  URL HTML差分比較ツール ビルドスクリプト
echo ============================================
echo.

REM --- conda 環境のアクティベート ---
REM condaインストール先の候補を順番に探す
set CONDA_BASE=
for %%d in (
    "%USERPROFILE%\miniforge3"
    "%USERPROFILE%\Miniforge3"
    "%USERPROFILE%\miniconda3"
    "%USERPROFILE%\Miniconda3"
    "%USERPROFILE%\anaconda3"
    "%USERPROFILE%\Anaconda3"
    "C:\ProgramData\miniforge3"
    "C:\ProgramData\miniconda3"
    "C:\ProgramData\Anaconda3"
) do (
    if not defined CONDA_BASE (
        if exist "%%~d\Scripts\activate.bat" set CONDA_BASE=%%~d
    )
)
if not defined CONDA_BASE (
    echo ERROR: conda のインストール先が見つかりません。
    echo 以下のいずれかにインストールされているか確認してください:
    echo   %%USERPROFILE%%\miniforge3  /  miniconda3  /  anaconda3
    pause
    exit /b 1
)
echo conda を検出: %CONDA_BASE%
call "%CONDA_BASE%\Scripts\activate.bat" py313
if errorlevel 1 (
    echo ERROR: conda 環境 py313 のアクティベートに失敗しました。
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
    --collect-submodules=src ^
    run.py

if errorlevel 1 (
    echo ERROR: PyInstaller のビルドに失敗しました。
    pause
    exit /b 1
)

echo.
echo ============================================
echo  ビルド完了！
echo  dist\url-diff-tool.exe が生成されました。
echo ============================================
pause
