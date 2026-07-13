# Bob's Blink Box

A headless-first Android build and device toolbox designed for:

- Linux desktops and servers
- SSH sessions
- Termux on Android
- Narrow portrait terminals and wider landscape terminals

The public entry point is a small personalized `launcher.sh`. The launcher owns user-adjustable settings, clones this repository, updates it through Git, and launches the Python terminal UI.

## Repository bootstrap

Create an empty remote repository, then push this directory to it. Update `BLINKBOX_REPO_URL` in each user's launcher.

## Application commands

```bash
python3 -m blinkbox
python3 -m blinkbox devices
```

## Design rules

1. Every feature must work headlessly before it receives a richer frontend.
2. No required desktop environment.
3. No required `sudo` in Termux.
4. User identity and common paths stay in the personal launcher.
5. Secrets never belong in the launcher or repository.
