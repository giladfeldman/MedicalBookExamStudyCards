# Nelson Anki Project — Setup Script (PowerShell)
# Run this once after extracting the project archive.
# In PowerShell: .\setup.ps1   (or: pwsh -File setup.ps1)

$ErrorActionPreference = "Stop"

Write-Host "=== Nelson Anki Project Setup ===" -ForegroundColor Cyan

# Check dependencies
Write-Host "`nChecking Python dependencies..."
$ea = $ErrorActionPreference; $ErrorActionPreference = 'SilentlyContinue'
pip install pymupdf genanki 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) { pip install pymupdf genanki --break-system-packages 2>&1 | Out-Null }
$ErrorActionPreference = $ea
Write-Host "Dependencies installed" -ForegroundColor Green

# Check input files
Write-Host "`nChecking input files..."
$MISSING = 0
$inputDir = "input"

if (-not (Test-Path (Join-Path $inputDir "source.pdf"))) {
    Write-Host "MISSING: input/source.pdf" -ForegroundColor Red
    Write-Host "  -> Copy your Nelson PDF here: input/source.pdf"
    Write-Host "  (The 265-page Hebrew summary PDF)"
    $MISSING = 1
}
if (-not (Test-Path (Join-Path $inputDir "chapter_index.txt"))) {
    Write-Host "MISSING: input/chapter_index.txt" -ForegroundColor Red
    Write-Host "  -> Copy the Nelson 22nd Ed contributor index here"
    Write-Host "  (Nelson_Textbook_of_Pediatrics_-_22nd_Edition__2024___4-41_.txt)"
    $MISSING = 1
}
if (-not (Test-Path (Join-Path $inputDir "pdf_filenames.txt"))) {
    Write-Host "MISSING: input/pdf_filenames.txt" -ForegroundColor Red
    Write-Host "  -> Copy the Google Drive PDF filename index here"
    Write-Host "  (nelson_pdf_index.txt)"
    $MISSING = 1
}

if ($MISSING -eq 0) {
    Write-Host "All input files present" -ForegroundColor Green

    # Verify PDF
    Write-Host "`nVerifying PDF..."
    $py = 'import fitz; doc = fitz.open("input/source.pdf"); print("PDF loaded:", len(doc), "pages"); doc.close()'
    python -c $py
    Write-Host "PDF OK" -ForegroundColor Green
} else {
    Write-Host "`nPlace the missing files and re-run this script." -ForegroundColor Yellow
    exit 1
}

# Create output directories
New-Item -ItemType Directory -Force -Path "output", "work" | Out-Null
Write-Host "`nOutput directories ready" -ForegroundColor Green

# Verify progress.json
if (Test-Path "progress.json") {
    Write-Host "progress.json present" -ForegroundColor Green
} else {
    Write-Host "progress.json missing" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "`nTo run the pilot:"
Write-Host '  claude "Read CLAUDE.md, then prompt.md, then orchestrator.md. Run the pilot batch (pages 162-164)."'
Write-Host "`nTo process the next batch:"
Write-Host '  claude "Read CLAUDE.md, then orchestrator.md, then progress.json. Process the next pending batch."'
