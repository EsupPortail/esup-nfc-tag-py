#!/bin/bash -x

APP_NAME="esup-nfc-agent"
MAIN_SCRIPT="esup-nfc-agent.py"
ICON_FILE="icon.ico"
CONFIG_FILE="config.ini"
VENV_DIR="venv"

# 1. Create the virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "🔧 Create virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

# 2. Activate the virtual environment
source "$VENV_DIR/bin/activate"

# 3. Install dependencies
echo "📦 Install dependencies..."
pip install --upgrade pip
pip install -r requirements-linux.txt
pip install pyinstaller

# 4. Run the application if no arguments are provided
if [ "$1" == "run" ]; then
    echo "🚀 Run the application..."
    python "$MAIN_SCRIPT"
    exit 0
fi

# 5. Generate the executable with PyInstaller if the first argument is "build"
if [ "$1" == "build" ]; then
    echo "🏗️ Build the executable..."

    # Clean previous builds
    rm -rf build dist "${APP_NAME}.spec"

    echo $MAIN_SCRIPT

    # Build the executable with PyInstaller
    pyinstaller --onefile --noconsole \
        --icon="$ICON_FILE" \
        --add-data "$ICON_FILE:." \
        --add-data "$CONFIG_FILE:." \
        --name "$APP_NAME" \
        "$MAIN_SCRIPT"

    echo "✅ Executable created in the 'dist' directory."
    exit 0
fi

# 6. Affichage de l'aide
echo "🛠️  Usage:"
echo "  ./setup.sh             → install dependencies and prepare the environment"
echo "  ./setup.sh run         → run the application"
echo "  ./setup.sh build       → build the executable"
