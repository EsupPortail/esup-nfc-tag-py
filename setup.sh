#!/bin/bash

APP_NAME="esup-nfc-agent"
MAIN_SCRIPT="esup-nfc-agent.py"
ICON_FILE="icon.ico"
CONFIG_FILE="config.ini"
VENV_DIR="venv"

# 1. Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Création de l'environnement virtuel..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Activer l'environnement virtuel
source "$VENV_DIR/bin/activate"

# 3. Mise à jour de pip + installation des dépendances
echo "📦 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# 4. Lancer l'application si demandé
if [ "$1" == "run" ]; then
    echo "🚀 Lancement de l'application..."
    python "$MAIN_SCRIPT"
    exit 0
fi

# 5. Génération de l'exécutable avec PyInstaller
if [ "$1" == "build" ]; then
    echo "🏗️ Construction de l'exécutable..."

    # Nettoyage précédent
    rm -rf build dist "${APP_NAME}.spec"

    # Construction
    pyinstaller --onefile --noconsole \
        --icon="$ICON_FILE" \
        --add-data "$ICON_FILE:." \
        --add-data "$CONFIG_FILE:." \        
        --name "$APP_NAME" \
        "$MAIN_SCRIPT"

    echo "✅ Fichier généré dans dist/${APP_NAME}.exe"
    exit 0
fi

# 6. Affichage de l'aide
echo "🛠️  Utilisation :"
echo "  ./setup.sh             → crée l'env et installe les dépendances"
echo "  ./setup.sh run         → lance l'application"
echo "  ./setup.sh build       → génère un exécutable autonome"
