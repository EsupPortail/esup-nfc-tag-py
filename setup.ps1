$AppName = "esup-nfc-agent"
$MainScript = "esup-nfc-agent.py"
$IconFile = "icon.png"
$ConfigFile = "config.ini"
$VenvDir = ".\venv"

# 1. Créer le venv s'il n'existe pas
if (-not (Test-Path "$VenvDir")) {
    Write-Host "🔧 Création de l'environnement virtuel..."
    python -m venv $VenvDir
}

# 2. Activer le venv
& "$VenvDir\Scripts\Activate.ps1"

# 3. Installer les dépendances
Write-Host "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# 4. Exécution
param (
    [string]$action = ""
)

if ($action -eq "run") {
    Write-Host "🚀 Lancement de l'application..."
    python $MainScript
    exit
}

if ($action -eq "build") {
    Write-Host "🏗️ Construction de l'exécutable Windows..."

    Remove-Item -Recurse -Force build, dist, "$AppName.spec" -ErrorAction SilentlyContinue

    pyinstaller --onefile --noconsole `
        --icon "$IconFile" `
        --add-data "$ConfigFile;." `
        --name "$AppName" `
        "$MainScript"

    Write-Host "✅ Fichier généré : dist\$AppName.exe"
    exit
}

Write-Host "🛠️ Utilisation :"
Write-Host "  ./setup.ps1            → installe les dépendances"
Write-Host "  ./setup.ps1 run        → lance l'app"
Write-Host "  ./setup.ps1 build      → génère un .exe Windows"
