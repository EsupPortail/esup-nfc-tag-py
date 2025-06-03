param (
    [string]$action = ""
)

$AppName = "esup-nfc-agent"
$MainScript = "esup-nfc-agent.py"
$IconFile = "icon.ico"
$ConfigFile = "config.ini"
$VenvDir = ".\venv"

# 1. Créer le venv s'il n'existe pas
if (-not (Test-Path "$VenvDir")) {
    Write-Host "Création de l'environnement virtuel..."
    python3.exe -m venv $VenvDir
}

# 2. Activer le venv
& "$VenvDir\Scripts\Activate.ps1"

# 3. Installer les dépendances
Write-Host "Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# 4. Exécution

if ($action -eq "run") {
    Write-Host "Lancement de l'application..."
    python $MainScript
    exit
}

if ($action -eq "build") {
    Write-Host "Construction de l'exécutable Windows..."

    Remove-Item -Recurse -Force build, dist, "$AppName.spec" -ErrorAction SilentlyContinue

    pyinstaller --onefile --noconsole `
        --icon "$IconFile" `
        --add-data "$IconFile;." `
        --add-data "$ConfigFile;." `        
        --name "$AppName" `
        "$MainScript"

    Write-Host "Fichier exe généré dans le repertoire dist"
    exit
}

Write-Host "Utilisation :"
Write-Host "  ./setup.ps1            installe les dependances"
Write-Host "  ./setup.ps1 run        lance l'app"
Write-Host "  ./setup.ps1 build      exe Windows"
