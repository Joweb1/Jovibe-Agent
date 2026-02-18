# Jovibe Agent Windows Installer (PowerShell)
Write-Host "Starting Jovibe Agent installation for Windows..." -ForegroundColor Cyan

# 1. Check for Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host "Python found." -ForegroundColor Green
} else {
    Write-Host "Python not found. Please install Python from https://www.python.org/downloads/ and ensure 'Add to PATH' is checked." -ForegroundColor Red
    exit
}

# 2. Setup JOVIBE_HOME
$JOVIBE_HOME = Join-Path $HOME ".jovibe"
if (-not (Test-Path $JOVIBE_HOME)) {
    New-Item -Path $JOVIBE_HOME -ItemType Directory
    Write-Host "Created Jovibe data directory at $JOVIBE_HOME" -ForegroundColor Green
}

# 3. Install the package
Write-Host "Installing Jovibe Agent..." -ForegroundColor Cyan
python -m pip install .

# 4. Setup environment file
$ENV_FILE = Join-Path $JOVIBE_HOME ".env"
if (-not (Test-Path $ENV_FILE)) {
    Write-Host "Creating default .env at $ENV_FILE" -ForegroundColor Green
    $EnvContent = @"
GEMINI_API_KEY=
TELEGRAM_TOKEN=
GEMINI_MODEL=gemini-2.0-flash
"@
    Set-Content -Path $ENV_FILE -Value $EnvContent
    Write-Host "Please edit $ENV_FILE to add your API keys." -ForegroundColor Yellow
}

Write-Host "------------------------------------------------" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "To start the agent, simply type: jovibe" -ForegroundColor Cyan
Write-Host "Note: You may need to restart your PowerShell window." -ForegroundColor Yellow
Write-Host "------------------------------------------------" -ForegroundColor Cyan
