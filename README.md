# esup-nfc-tag-py 
*A python agent for esup-nfc-tag project*

esup-nfc-tag-py is a lightweight Python-based background agent with a system tray icon, 
designed to listen for NFC card events and relay them to a remote esup-nfc-tag-server instance.

Unlike esup-nfc-tag-desktop or esup-nfc-tag-droid, this agent does not allow users to manually authenticate 
and select a "badge room". 
Instead, it acts as a passive client, configured in advance to target a specific room —
defined within esup-nfc-tag-server under the "devices" section — and associated with a predefined room.

This application was initially developed to support a specific use case: 
enabling Multi-Factor Authentication (MFA) via NFC card badge.
When integrated with esup-otp-api and CAS, it allows the user to seamlessly complete MFA by simply presenting 
their DESFire NFC card to their reader-equipped workstation.

The key benefit of esup-nfc-tag-py lies in its ability to:

- run silently in the background ;

- consume minimal resources ;

- provide a frictionless user experience, requiring no interaction other than tapping the card.

It is ideally suited for deployment on Windows user machines (via .exe packaging), but is cross-platform and works under Linux as well.

## Features

- NFC reader detection (supports multiple readers)
- Background agent with system tray icon
- Event-driven card detection
- HTTP session with cookie persistence
- Easily deployable on Windows (via `.exe` generation)
- Lightweight footprint (much smaller than a Java-based equivalent)

## Requirements

- esup-nfc-tag-server (running on a remote server)
- compatible USB NFC reader
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
numero_id = numero-hexa-peripherique-esup-nfc-tag-pour-esup-otp
```

## Windows Usage

### Generation of executable

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

### Standalone Deployment

Once the `.exe` is successfully generated with the `.\setup.ps1 build` command, it becomes a **fully standalone executable**. This means:

- It **embeds the Python interpreter and all dependencies**,
- It can be **copied and executed on any Windows machine** without needing Python or any extra libraries installed,

This makes it easy to **distribute the agent across multiple Windows clients** using a software deployment tool (e.g. WAPT, SCCM, or others).

## Linux/macOS Usage (for development)
Use bash and make sure python3, pip, and NFC libraries are installed.
```bash
./setup.sh          # Install dependencies
./setup.sh run      # Run the agent
./setup.sh build    # (Optional) Build Linux executable
```

## Deployment Notes
Ensure the config.ini is correctly configured before generating and distributing the .exe.

You may package the dist/esup-nfc-agent.exe using any Windows installer solution (e.g., Inno Setup, NSIS) to ease end-user deployment.

## License
This project is licensed under the Apache 2 License.
