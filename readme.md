# 3D Printing Price Calculator

[Features](#features) | [Requirements](#requirements) | [Windows](#windows) | [macOS](#macos) | [Linux](#linux) | [Usage](#usage) | [File Structure](#file-structure) | [Language](#adding-a-language) | [License](#license)

A desktop app (PyQt6) that calculates the price of a 3D print job from material, energy, and design-time costs, and outputs a clean, ready-to-paste WhatsApp receipt.

## Features

- **Printer profiles** — save multiple printers as JSON files (energy cost, printer power draw, material cost, design rate, PC power draw while designing) and switch between them from a dropdown before calculating.
- **Design-time toggle** — include or exclude 3D design hours from the calculation with one checkbox. The PC's energy draw while designing is counted as part of the *Energy* line, so unchecking it correctly lowers the energy cost too.
- **Round-up toggle** — round the total up to the next whole euro. The rounding difference is folded quietly into the *Energy* line instead of being shown as a separate "rounding" line item.
- **WhatsApp-ready receipt** — a clean, symmetrical, plain-text receipt with one click to copy it (wrapped in a code block so the alignment survives the paste into WhatsApp).
- **Multi-language UI** — English (default), Italian, Spanish, French. Add more by editing `languages.json`. The chosen language is remembered between runs.
- **Dark theme** — a clean, modern dark UI.

## Requirements

Only needed if you're running from source (see [Usage](#usage)). If you're using a prebuilt release for your OS, you don't need Python at all — jump to [Windows](#windows), [macOS](#macos), or [Linux](#linux).

- Python 3.10+
- [PyQt6](https://pypi.org/project/PyQt6/)

```bash
pip install PyQt6
```

## Windows

1. Go to the [Releases](../../releases) page.
2. Download the latest `ppcalculator.v_XX.exe` file.
3. Double-click it to run — no installation needed.

> If Windows SmartScreen warns you about an unrecognized app, click **More info → Run anyway**. This happens because the executable isn't code-signed.

## macOS

1. Go to the [Releases](../../releases) page.
2. Download the latest macOS build (`.dmg` or `.zip`, depending on the release).
3. Open it and drag the app into your **Applications** folder.

> On first launch, macOS Gatekeeper may block the app since it isn't notarized. Right-click the app → **Open** → confirm **Open** in the dialog to bypass this once.

## Linux

1. Go to the [Releases](../../releases) page.
2. Download the latest `.tar.gz` archive.
3. Extract it and make the binary executable:

```bash
tar -xzf 3d-print-price-calculator-linux.tar.gz
cd 3d-print-price-calculator
chmod +x ppcalculator
./ppcalculator
```

## Usage

Running from source instead of a release build:

```bash
python main.py
```

1. Pick a printer profile from the dropdown (or create one — see below).
2. Enter print time (hours/minutes), material used (grams), design hours, and number of pieces.
3. Toggle "Include design hours" and "Round up to the next euro" as needed.
4. Click **Calculate**.
5. Click **Copy for WhatsApp** to copy the formatted receipt, or **Export TXT** to save it to a file.

### Managing printer profiles

Click **Settings** to open the profile manager. Each profile stores:

| Field | Description |
| --- | --- |
| Profile name | Shown in the dropdown, used to build the filename |
| Energy cost (€/kWh) | Your electricity rate |
| Printer power (W) | Rated power draw of the printer |
| Material cost (€/kg) | Filament/resin cost |
| Design rate (€/h) | Your hourly rate for 3D design work |
| PC power while designing (W) | Power draw of the computer used for modeling |

Profiles are stored as individual JSON files in the `profiles/` folder next to the script (or next to the executable, for release builds). The filename is derived from the profile name — e.g. a profile named **"Artillery Genius"** is saved as `profiles/artillery_genius.json`.

## File structure

```
.
├── calcolo_stampa3d.py   # main application
├── languages.json        # UI translations (en, it, es, fr)
├── config.json            # auto-created — remembers the selected language
└── profiles/               # auto-created — one JSON file per printer profile
    └── artillery_genius.json
```

## Adding a language

Open `languages.json` and add a new top-level key with the two-letter language code (e.g. `"de"`), copying the full key set from the `"en"` block and translating each value. The `_name` key is what shows up in the language dropdown. The app falls back to English for any missing key.

## License

Open Source, [MIT](LICENSE).