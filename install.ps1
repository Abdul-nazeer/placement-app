# PlacementPrep Installation Script for Windows
# Run this script in PowerShell as Administrator

Write-Host "PlacementPrep Installation Script" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

# Check if Node.js is installed
Write-Host "Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    Write-Host "Node.js is installed: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Node.js is not installed. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    exit 1
}

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "Python is installed: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed. Please install Python from https://python.org/" -ForegroundColor Red
    exit 1
}

# Install frontend dependencies
Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location "apps/frontend"
try {
    npm install
    Write-Host "Frontend dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Failed to install frontend dependencies. Please check npm installation." -ForegroundColor Red
}
Set-Location "../.."

# Create Python virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
try {
    python -m venv venv
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
} catch {
    Write-Host "Failed to create virtual environment." -ForegroundColor Red
}

# Activate virtual environment and install Python dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
try {
    & "venv\Scripts\Activate.ps1"
    pip install -r apps/backend/requirements.txt
    Write-Host "Python dependencies installed successfully!" -ForegroundColor Green
} catch {
    Write-Host "Failed to install Python dependencies." -ForegroundColor Red
}

# Create environment files if they don't exist
Write-Host "Creating environment files..." -ForegroundColor Yellow

$backendEnvPath = "apps/backend/.env"
if (-not (Test-Path $backendEnvPath)) {
    $backendEnvContent = @"
DATABASE_URL=postgresql://postgres:password@localhost:5432/placement_prep
DATABASE_URL_SYNC=postgresql://postgres:password@localhost:5432/placement_prep
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production-$(Get-Random)
GROQ_API_KEY=your-groq-api-key
ENVIRONMENT=development
DEBUG=true
"@
    Set-Content -Path $backendEnvPath -Value $backendEnvContent
    Write-Host "Backend .env file created at $backendEnvPath" -ForegroundColor Green
}

$frontendEnvPath = "apps/frontend/.env"
if (-not (Test-Path $frontendEnvPath)) {
    $frontendEnvContent = @"
VITE_API_URL=http://localhost:8000/api/v1
"@
    Set-Content -Path $frontendEnvPath -Value $frontendEnvContent
    Write-Host "Frontend .env file created at $frontendEnvPath" -ForegroundColor Green
}

Write-Host ""
Write-Host "Installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Install and start PostgreSQL" -ForegroundColor White
Write-Host "2. Install and start Redis" -ForegroundColor White
Write-Host "3. Create database: createdb placement_prep" -ForegroundColor White
Write-Host "4. Run migrations: cd apps/backend && alembic upgrade head" -ForegroundColor White
Write-Host "5. Start backend: cd apps/backend && uvicorn main:app --reload" -ForegroundColor White
Write-Host "6. Start frontend: cd apps/frontend && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "For detailed setup instructions, see SETUP.md" -ForegroundColor Cyan