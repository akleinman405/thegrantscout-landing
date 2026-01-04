#!/bin/bash
# Whisper Transcription Script
# Transcribes all audio files in the input folder

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INPUT_DIR="$SCRIPT_DIR/input"
OUTPUT_DIR="$SCRIPT_DIR/output"

# Model options: tiny, base, small, medium, large, turbo
# turbo is the default and offers a good balance of speed/quality
MODEL="${1:-turbo}"

echo "==================================="
echo "Whisper Batch Transcription"
echo "==================================="
echo "Input folder:  $INPUT_DIR"
echo "Output folder: $OUTPUT_DIR"
echo "Model: $MODEL"
echo ""

# Check for files
shopt -s nullglob
FILES=("$INPUT_DIR"/*.{m4a,mp3,mp4,wav,webm,flac,ogg,aac,wma,M4A,MP3,MP4,WAV,WEBM,FLAC,OGG,AAC,WMA})
shopt -u nullglob

if [ ${#FILES[@]} -eq 0 ]; then
    echo "No audio files found in input folder."
    echo "Supported formats: m4a, mp3, mp4, wav, webm, flac, ogg, aac, wma"
    exit 0
fi

echo "Found ${#FILES[@]} file(s) to transcribe:"
for f in "${FILES[@]}"; do
    echo "  - $(basename "$f")"
done
echo ""

# Transcribe each file
for file in "${FILES[@]}"; do
    filename=$(basename "$file")
    echo "-----------------------------------"
    echo "Transcribing: $filename"
    echo "-----------------------------------"

    whisper "$file" \
        --model "$MODEL" \
        --output_dir "$OUTPUT_DIR" \
        --output_format all \
        --language English \
        --device cpu

    if [ $? -eq 0 ]; then
        echo "Done: $filename"
        # Move processed file to output folder (optional - uncomment to enable)
        # mv "$file" "$OUTPUT_DIR/"
    else
        echo "Error processing: $filename"
    fi
    echo ""
done

echo "==================================="
echo "Transcription complete!"
echo "Output files are in: $OUTPUT_DIR"
echo "==================================="
