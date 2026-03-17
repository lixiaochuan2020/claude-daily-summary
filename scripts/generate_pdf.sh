#!/bin/bash
# Generate PDF from a Typst daily summary file.
#
# Usage: bash generate_pdf.sh <input.typ> [output.pdf]
#
# If output is not specified, saves to ~/Documents/daily-summaries/YYYY-MM-DD.pdf
# where the date is extracted from the input filename.

set -euo pipefail

INPUT="${1:?Usage: generate_pdf.sh <input.typ> [output.pdf]}"

if [ ! -f "$INPUT" ]; then
    echo "Error: Input file not found: $INPUT"
    exit 1
fi

# Extract date from filename (expects daily-summary-YYYY-MM-DD.typ)
BASENAME=$(basename "$INPUT" .typ)
# Also handle .md extension for backwards compatibility
BASENAME=$(basename "$BASENAME" .md)
DATE=$(echo "$BASENAME" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}' || date +%Y-%m-%d)

# Determine output path
OUTPUT_DIR="$HOME/Documents/daily-summaries"
OUTPUT="${2:-$OUTPUT_DIR/$DATE.pdf}"

# Ensure output directory exists
mkdir -p "$(dirname "$OUTPUT")"

# Check for typst
if ! command -v typst &> /dev/null; then
    echo "typst not found. Installing via Homebrew..."
    brew install typst
fi

# Generate PDF with typst
# --root / allows absolute path imports in the .typ file
echo "Generating PDF: $OUTPUT"
typst compile --root / "$INPUT" "$OUTPUT" 2>&1

if [ $? -eq 0 ] && [ -f "$OUTPUT" ]; then
    echo "PDF generated successfully: $OUTPUT"
    echo "Size: $(du -h "$OUTPUT" | cut -f1)"
else
    echo "Error: PDF generation failed."
    exit 1
fi
