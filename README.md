# Bob's Blink Box

A headless-first Android build and device toolbox designed for:

- Linux desktops and servers
- SSH sessions
- Termux on Android
- Narrow portrait terminals and wider landscape terminals

## Launcher model

`example.launcher.sh` is the canonical public launcher template. Download it as
`launcher.sh`, edit the user settings at the top, and keep that personalized
file outside the cloned application directory.

```bash
curl -L \
  https://raw.githubusercontent.com/BobTheBlinker/bobs_blink_box/main/example.launcher.sh \
  -o launcher.sh
chmod +x launcher.sh
./launcher.sh
```

The launcher clones and updates the application over public HTTPS from:

```text
https://github.com/BobTheBlinker/bobs_blink_box.git
```

No GitHub account or SSH key is required for installation or updates.

## Android workspace

The default workspace is deliberately organized by source type:

```text
~/Android/
├── ROMs/
│   └── LineageOS-23.2/
├── Recoveries/
│   └── twrp-12.1/
├── Tools/
└── Releases/
```

There is no generic `builds` directory. A ROM or recovery source checkout is
itself the build workspace, and its compiler output normally remains inside
that source tree. Finished packages, checksums, and distributable artifacts go
under `~/Android/Releases`.

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
