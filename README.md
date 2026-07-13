# Bob's Blink Box

A headless-first Android build and device toolbox designed for:

- Linux desktops and servers
- SSH sessions
- Termux on Android
- Narrow portrait terminals and wider landscape terminals

The public entry point is the small `launcher.sh` in this repository. Users edit the settings at the top of that one file. It then installs, updates, repairs, and launches the Python application from this public repository.

## One-file installation

Download `launcher.sh`, make it executable, and run it:

```bash
chmod +x launcher.sh
./launcher.sh
```

The launcher clones the application from:

```text
https://github.com/BobTheBlinker/bobs_blink_box.git
```

No GitHub account or SSH key is required for installation or updates.

## Application commands

```bash
python3 -m blinkbox
python3 -m blinkbox devices
```

## Design rules

1. Every feature must work headlessly before it receives a richer frontend.
2. No desktop environment is required.
3. Termux is a first-class target and must not require `sudo`.
4. User identity and commonly changed paths stay in the personal launcher.
5. Secrets never belong in the launcher or repository.
