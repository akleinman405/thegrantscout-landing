@echo off
REM Whisper Transcription Script for Windows
REM Transcribes all audio files in the input folder using WSL

setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
set "INPUT_DIR=%SCRIPT_DIR%input"
set "OUTPUT_DIR=%SCRIPT_DIR%output"

REM Model: tiny, base, small, medium, large, turbo (default)
if "%~1"=="" (set "MODEL=turbo") else (set "MODEL=%~1")

echo ===================================
echo Whisper Batch Transcription
echo ===================================
echo Input folder:  %INPUT_DIR%
echo Output folder: %OUTPUT_DIR%
echo Model: %MODEL%
echo.

REM Convert Windows paths to WSL paths
for /f "usebackq tokens=*" %%a in (`wsl wslpath -a "%INPUT_DIR%"`) do set "WSL_INPUT=%%a"
for /f "usebackq tokens=*" %%a in (`wsl wslpath -a "%OUTPUT_DIR%"`) do set "WSL_OUTPUT=%%a"

REM Check for audio files
set "FILE_COUNT=0"
for %%e in (m4a mp3 mp4 wav webm flac ogg aac wma M4A MP3 MP4 WAV WEBM FLAC OGG AAC WMA) do (
    for %%f in ("%INPUT_DIR%\*.%%e") do (
        if exist "%%f" (
            set /a FILE_COUNT+=1
            echo   - %%~nxf
        )
    )
)

if %FILE_COUNT%==0 (
    echo No audio files found in input folder.
    echo Supported formats: m4a, mp3, mp4, wav, webm, flac, ogg, aac, wma
    echo.
    echo Drop your audio files into: %INPUT_DIR%
    pause
    exit /b 0
)

echo.
echo Found %FILE_COUNT% file(s) to transcribe.
echo.

REM Transcribe each file
for %%e in (m4a mp3 mp4 wav webm flac ogg aac wma M4A MP3 MP4 WAV WEBM FLAC OGG AAC WMA) do (
    for %%f in ("%INPUT_DIR%\*.%%e") do (
        if exist "%%f" (
            echo -----------------------------------
            echo Transcribing: %%~nxf
            echo -----------------------------------

            for /f "usebackq tokens=*" %%p in (`wsl wslpath -a "%%f"`) do set "WSL_FILE=%%p"

            wsl whisper "!WSL_FILE!" --model %MODEL% --output_dir "%WSL_OUTPUT%" --output_format all --language English --device cpu

            if !errorlevel!==0 (
                echo Done: %%~nxf
            ) else (
                echo Error processing: %%~nxf
            )
            echo.
        )
    )
)

echo ===================================
echo Transcription complete!
echo Output files are in: %OUTPUT_DIR%
echo ===================================
pause
