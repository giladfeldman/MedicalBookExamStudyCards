#!/bin/bash
# Nelson Anki Project — Setup Script
# Run this once after extracting the project archive.

set -e

echo "=== Nelson Anki Project Setup ==="

# Check dependencies
echo "Checking Python dependencies..."
pip install pymupdf genanki 2>/dev/null || pip install pymupdf genanki --break-system-packages 2>/dev/null || {
    echo "❌ Failed to install pymupdf and genanki. Please install manually:"
    echo "   pip install pymupdf genanki"
    exit 1
}
echo "✅ Dependencies installed"

# Check input files
echo ""
echo "Checking input files..."
MISSING=0

if [ ! -f "input/source.pdf" ]; then
    echo "❌ MISSING: input/source.pdf"
    echo "   → Copy your Nelson PDF here: input/source.pdf"
    echo "   (The 265-page Hebrew summary: טבלת_נלסון_21_אביעד_שנפ_2024.pdf)"
    MISSING=1
fi

if [ ! -f "input/chapter_index.txt" ]; then
    echo "❌ MISSING: input/chapter_index.txt"
    echo "   → Copy the Nelson 22nd Ed contributor index here"
    echo "   (Nelson_Textbook_of_Pediatrics_-_22nd_Edition__2024___4-41_.txt)"
    MISSING=1
fi

if [ ! -f "input/pdf_filenames.txt" ]; then
    echo "❌ MISSING: input/pdf_filenames.txt"
    echo "   → Copy the Google Drive PDF filename index here"
    echo "   (nelson_pdf_index.txt)"
    MISSING=1
fi

if [ $MISSING -eq 0 ]; then
    echo "✅ All input files present"
else
    echo ""
    echo "⚠️  Place the missing files and re-run this script."
    exit 1
fi

# Verify PDF
echo ""
echo "Verifying PDF..."
python3 -c "
import fitz
doc = fitz.open('input/source.pdf')
print(f'✅ PDF loaded: {len(doc)} pages')
doc.close()
"

# Create output directories
mkdir -p output work
echo "✅ Output directories ready"

# Verify progress.json
if [ -f "progress.json" ]; then
    echo "✅ progress.json present"
else
    echo "❌ progress.json missing — this should have been in the archive"
    exit 1
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To run the pilot:"
echo "  claude \"Read CLAUDE.md, then prompt.md, then orchestrator.md. Run the pilot batch (pages 162-164).\""
echo ""
echo "To process the next batch:"
echo "  claude \"Read CLAUDE.md, then orchestrator.md, then progress.json. Process the next pending batch.\""
