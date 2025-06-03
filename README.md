# esup-nfc-tag-py : a python agent for esup-nfc-tag project

**esup-nfc-tag-py** is a lightweight Python-based background application with a system tray icon that listens for NFC card events and triggers an authentication request (APDU exchange) to a remote server (such as [esup-otp-api](https://github.com/EsupPortail/esup-otp-api)), typically used in conjunction with a CAS-based MFA system.

**esup-nfc-tag-py** acts as a client to [esup-nfc-tag-server](https://github.com/EsupPortail/esup-nfc-tag-server), which serves as a relay to both construct the required DESFire APDUs and communicate with esup-otp-api in order to complete CAS authentication once the DESFire authentication has been successfully validated.

This project is designed to be deployed on user workstations (especially Windows) to support secure contactless authentication via DESFire NFC cards.

## Features

- NFC reader detection (supports multiple readers)
- Background agent with system tray icon
- Event-driven card detection loop
- HTTP session with cookie persistence
- Easily deployable on Windows (via `.exe` generation)
- Lightweight footprint (much smaller than a Java-based equivalent)

## Requirements

- Python 3.8+
- Compatible USB NFC reader (e.g., ACR122U)
- DESFire-compatible cards

## Project Structure

- config.ini # Configuration file (must be edited before packaging)
- esup-nfc-agent.py # Main Python script
- icon.png # Tray icon
- LICENSE
- requirements.txt # Python dependencies
- setup.ps1 # Windows setup and build script (PowerShell)
- setup.sh # Linux/macOS setup script (bash)


## Configuration

Before packaging or running the application, make sure to edit the `config.ini` file:

```ini
[general]
server_url = https://esup-nfc-tag.example.org
numero_id = numero-hexa-de-esup-nfc-tag-pour-esup-otp
```

## Windows Usage

Requires PowerShell and Python. Visual Studio is needed for some native dependencies.

1. If Python is not already installed:

Open PowerShell

Run the following command to launch the Microsoft Store:

```powershell
python3.exe
```

Follow the instructions to install Python 3.x via the Microsoft Store.

Make sure to allow the installer to add Python to your system PATH.

2. Install Visual Studio (for native module compilation)

Download and install Visual Studio Community Edition.

Add the following components:

- Developpement Python
- Developpement Desktop C++

These are required to build Python packages with native dependencies (like pycairo, pynfc, etc.).

3. Install dependencies
```powershell
.\setup.ps1
```

4. Run the app (with system tray icon)
```powershell
.\setup.ps1 run
```

5. Generate a standalone .exe for deployment
```powershell
.\setup.ps1 build
```

After completion, the .exe will be located in the dist/ folder and can be deployed directly to end-user machines.

Make sure to configure config.ini before generating the .exe.

## Linux/macOS Usage (for development)
Use bash and make sure python3, pip, and NFC libraries are installed.
```powershell
./setup.sh          # Install dependencies
./setup.sh run      # Run the agent
./setup.sh build    # (Optional) Build Linux executable
```

## Deployment Notes
Ensure the config.ini is correctly configured before generating and distributing the .exe.

You may package the dist/esup-nfc-agent.exe using any Windows installer solution (e.g., Inno Setup, NSIS) to ease end-user deployment.

## License
This project is licensed under the Apache 2 License.
