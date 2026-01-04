#!/usr/bin/env python3
"""
Whisper Transcription Script
Transcribes all audio files in the input folder.
"""

import subprocess
import sys
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent
INPUT_DIR = SCRIPT_DIR / "input"
OUTPUT_DIR = SCRIPT_DIR / "output"

# Supported audio formats
AUDIO_EXTENSIONS = {'.m4a', '.mp3', '.mp4', '.wav', '.webm', '.flac', '.ogg', '.aac', '.wma'}

def get_audio_files():
    """Find all audio files in the input directory."""
    files = []
    for ext in AUDIO_EXTENSIONS:
        files.extend(INPUT_DIR.glob(f"*{ext}"))
        files.extend(INPUT_DIR.glob(f"*{ext.upper()}"))
    return sorted(set(files))

def transcribe_file(filepath: Path, model: str = "turbo"):
    """Transcribe a single audio file using Whisper."""
    print(f"\n{'='*50}")
    print(f"Transcribing: {filepath.name}")
    print(f"{'='*50}")

    cmd = [
        "whisper",
        str(filepath),
        "--model", model,
        "--output_dir", str(OUTPUT_DIR),
        "--output_format", "all",
        "--language", "English",
        "--device", "cpu"
    ]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print(f"Success: {filepath.name}")
        return True
    else:
        print(f"Error: {filepath.name}")
        return False

def main():
    # Parse model argument
    model = sys.argv[1] if len(sys.argv) > 1 else "turbo"

    print("=" * 50)
    print("Whisper Batch Transcription")
    print("=" * 50)
    print(f"Input folder:  {INPUT_DIR}")
    print(f"Output folder: {OUTPUT_DIR}")
    print(f"Model: {model}")
    print()

    # Ensure directories exist
    INPUT_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Get audio files
    files = get_audio_files()

    if not files:
        print("No audio files found in input folder.")
        print(f"Supported formats: {', '.join(sorted(AUDIO_EXTENSIONS))}")
        return

    print(f"Found {len(files)} file(s) to transcribe:")
    for f in files:
        print(f"  - {f.name}")

    # Transcribe each file
    success_count = 0
    for filepath in files:
        if transcribe_file(filepath, model):
            success_count += 1

    print()
    print("=" * 50)
    print(f"Transcription complete! {success_count}/{len(files)} successful")
    print(f"Output files are in: {OUTPUT_DIR}")
    print("=" * 50)

if __name__ == "__main__":
    main()
