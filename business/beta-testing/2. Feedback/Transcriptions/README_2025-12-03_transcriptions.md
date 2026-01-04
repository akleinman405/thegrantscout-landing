# Whisper Audio Transcription

Automatically transcribe audio files using OpenAI's Whisper model.

## Folder Structure

```
Transcriptions/
├── input/          <- Drop your audio files here
├── output/         <- Transcriptions appear here
├── transcribe.bat  <- Windows batch script (double-click to run)
├── transcribe.sh   <- WSL/Linux script
├── transcribe.py   <- Python script (for WSL)
└── README.md
```

## Quick Start (Windows)

1. Drop your audio files (m4a, mp3, mp4, wav, etc.) into the `input/` folder
2. Double-click `transcribe.bat`
3. Find your transcriptions in the `output/` folder

That's it! The batch file calls Whisper through WSL automatically.

## Alternative: Run from WSL Terminal

If you prefer using the terminal:

```bash
cd "/mnt/c/Business Factory (Research) 11-1-2025/01_VALIDATED_IDEAS/TIER_1_BOOTSTRAPPED/IDEA_062_Grant_Alerts/TheGrantScout/Beta/Feedback/Transcriptions"
./transcribe.sh
```

Or using Python:
```bash
python3 transcribe.py
```

## Supported Audio Formats

- m4a (iPhone voice memos)
- mp3
- mp4
- wav
- webm
- flac
- ogg
- aac
- wma

## Output Formats

Each transcription produces multiple files:
- `.txt` - Plain text transcript
- `.srt` - Subtitles with timestamps
- `.vtt` - Web subtitles format
- `.json` - Full data including word-level timestamps
- `.tsv` - Tab-separated values

## Model Options

Specify a different model for speed/quality tradeoff:

**Windows (Command Prompt):**
```cmd
transcribe.bat small
transcribe.bat turbo
```

**WSL:**
```bash
./transcribe.sh small
./transcribe.sh turbo
```

| Model  | Parameters | Speed   | Quality |
|--------|------------|---------|---------|
| tiny   | 39M        | Fastest | Basic   |
| base   | 74M        | Fast    | Good    |
| small  | 244M       | Medium  | Better  |
| medium | 769M       | Slow    | Great   |
| large  | 1550M      | Slowest | Best    |
| turbo  | 809M       | Fast    | Great   |

Default is `turbo` - good balance of speed and quality.

## Installation Status

Whisper is installed in WSL on this system:
- Location: `/home/alec/.local/bin/whisper`
- Version: openai-whisper 20250625
- ffmpeg: Installed (required for audio conversion)

## Troubleshooting

### "wsl is not recognized"
WSL (Windows Subsystem for Linux) must be installed. The transcription scripts require WSL because Whisper is installed there.

### "whisper: command not found"
Whisper needs to be installed in WSL:
```bash
wsl pip3 install openai-whisper
```

### Slow transcription
The first run downloads the model (~1-3GB depending on size). Subsequent runs are faster. Use `tiny` or `base` models for faster processing.

### Out of memory
Use a smaller model:
```cmd
transcribe.bat tiny
```

### File format not supported
Convert your file using ffmpeg (in WSL):
```bash
wsl ffmpeg -i yourfile.xyz -ar 16000 -ac 1 yourfile.wav
```

## Tips

- For voice memos from iPhone, the m4a format works directly
- English is set as the default language for better accuracy
- Processing time is roughly 1-2x the audio length on CPU
- For faster processing, use the `turbo` or `small` model
- The window will stay open after completion so you can see the results
