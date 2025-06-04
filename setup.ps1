param (
    [string]$action = ""
)

$AppName = "esup-nfc-agent"
$MainScript = "esup-nfc-agent.py"
$IconFile = "icon.ico"
$ConfigFile = "config.ini"
$VenvDir = ".\venv"

# 1. Create the virtual environment if it doesn't exist
if (-not (Test-Path "$VenvDir")) {
    Write-Host "Create virtual environment..."
    python3.exe -m venv $VenvDir
}

# 2. Activate the virtual environment
& "$VenvDir\Scripts\Activate.ps1"

# 3. Install dependencies
Write-Host "Install dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# 4. Execute the requested action

if ($action -eq "run") {
    Write-Host "Run the application..."
    python $MainScript
    exit
}

if ($action -eq "build") {
    Write-Host "Build the application executable..."

    Remove-Item -Recurse -Force build, dist, "$AppName.spec" -ErrorAction SilentlyContinue

    pyinstaller --onefile --noconsole `
        --icon "$IconFile" `
        --add-data "$IconFile;." `
        --add-data "$ConfigFile;." `
        --name "$AppName" `
        "$MainScript"

    Write-Host "File created in dist/$AppName.exe"
    exit
}

Write-Host "Usage:"
Write-Host "  ./setup.ps1            install dependencies"
Write-Host "  ./setup.ps1 run        run the application"
Write-Host "  ./setup.ps1 build      build the application executable"
