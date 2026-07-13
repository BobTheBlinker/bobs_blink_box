#!/usr/bin/env bash
set -Eeuo pipefail

# ============================================================================
# Bob's Blink Box - Personal Launcher
# Edit this section per user. Do not put passwords, tokens, or private keys here.
# ============================================================================
MAINTAINER_NAME="Your Name"
GIT_USERNAME="your-git-username"
GIT_EMAIL="you@example.com"

DEFAULT_BUILD_ROOT="$HOME/builds"
DEFAULT_RELEASE_ROOT="$HOME/releases"
DEFAULT_EDITOR="nano"
REMOTE_HOST=""

# Public application repository. Cloning and updates require no GitHub account.
BLINKBOX_REPO_URL="https://github.com/BobTheBlinker/bobs_blink_box.git"
BLINKBOX_BRANCH="main"

# never | ask | always
AUTO_UPDATE="ask"
# ============================================================================

APP_ROOT="${BLINKBOX_APP_ROOT:-$HOME/.local/share/blinkbox}"
APP_DIR="$APP_ROOT/app"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/blinkbox"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/blinkbox"

is_termux() {
    [[ -n "${TERMUX_VERSION:-}" || -d "/data/data/com.termux/files/usr" ]]
}

python_cmd() {
    if command -v python3 >/dev/null 2>&1; then
        printf '%s\n' python3
    elif command -v python >/dev/null 2>&1; then
        printf '%s\n' python
    else
        return 1
    fi
}

say()   { printf '\n%s\n' "$*"; }
warn()  { printf '\nWARNING: %s\n' "$*" >&2; }
die()   { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

confirm() {
    local prompt="${1:-Continue?}"
    local answer
    read -r -p "$prompt [y/N] " answer || true
    [[ "$answer" =~ ^[Yy]([Ee][Ss])?$ ]]
}

install_dependencies() {
    local missing=()
    command -v git >/dev/null 2>&1 || missing+=(git)
    python_cmd >/dev/null 2>&1 || missing+=(python)

    ((${#missing[@]} == 0)) && return 0

    warn "Missing required programs: ${missing[*]}"
    confirm "Install the required packages now?" || die "Cannot continue without Git and Python."

    if is_termux; then
        pkg update
        pkg install -y git python ncurses-utils
    elif command -v apt-get >/dev/null 2>&1; then
        command -v sudo >/dev/null 2>&1 || die "sudo is required for apt package installation."
        sudo apt-get update
        sudo apt-get install -y git python3 python3-venv
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y git python3
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -S --needed git python
    else
        die "Unsupported package manager. Install Git and Python 3 manually, then rerun this launcher."
    fi
}

validate_repo_url() {
    [[ "$BLINKBOX_REPO_URL" != *"CHANGE-ME"* ]] || die \
        "Set BLINKBOX_REPO_URL near the top of this launcher before installing."
}

app_installed() {
    [[ -d "$APP_DIR/.git" && -f "$APP_DIR/blinkbox/__main__.py" ]]
}

write_runtime_config() {
    mkdir -p "$CONFIG_DIR" "$STATE_DIR" "$DEFAULT_BUILD_ROOT" "$DEFAULT_RELEASE_ROOT"
    umask 077
    cat > "$CONFIG_DIR/user.env" <<CFG
BLINKBOX_MAINTAINER_NAME=$(printf '%q' "$MAINTAINER_NAME")
BLINKBOX_GIT_USERNAME=$(printf '%q' "$GIT_USERNAME")
BLINKBOX_GIT_EMAIL=$(printf '%q' "$GIT_EMAIL")
BLINKBOX_BUILD_ROOT=$(printf '%q' "$DEFAULT_BUILD_ROOT")
BLINKBOX_RELEASE_ROOT=$(printf '%q' "$DEFAULT_RELEASE_ROOT")
BLINKBOX_EDITOR=$(printf '%q' "$DEFAULT_EDITOR")
BLINKBOX_REMOTE_HOST=$(printf '%q' "$REMOTE_HOST")
BLINKBOX_CONFIG_DIR=$(printf '%q' "$CONFIG_DIR")
BLINKBOX_STATE_DIR=$(printf '%q' "$STATE_DIR")
CFG
}

install_app() {
    validate_repo_url
    install_dependencies
    mkdir -p "$APP_ROOT"

    if [[ -e "$APP_DIR" ]]; then
        die "$APP_DIR already exists but is not a valid Blink Box clone. Move or remove it first."
    fi

    say "Cloning Bob's Blink Box..."
    git clone --branch "$BLINKBOX_BRANCH" --single-branch "$BLINKBOX_REPO_URL" "$APP_DIR"
    write_runtime_config
    say "Installed in $APP_DIR"
}

update_app() {
    app_installed || die "Blink Box is not installed."
    validate_repo_url

    say "Checking for updates..."
    git -C "$APP_DIR" fetch origin "$BLINKBOX_BRANCH"

    local local_rev remote_rev
    local_rev="$(git -C "$APP_DIR" rev-parse HEAD)"
    remote_rev="$(git -C "$APP_DIR" rev-parse "origin/$BLINKBOX_BRANCH")"

    if [[ "$local_rev" == "$remote_rev" ]]; then
        say "Blink Box is already current."
        return 0
    fi

    git -C "$APP_DIR" pull --ff-only origin "$BLINKBOX_BRANCH"
    say "Blink Box updated."
}

maybe_update() {
    app_installed || return 0
    case "$AUTO_UPDATE" in
        never) return 0 ;;
        always) update_app ;;
        ask)
            if git -C "$APP_DIR" fetch --quiet origin "$BLINKBOX_BRANCH" 2>/dev/null; then
                local local_rev remote_rev
                local_rev="$(git -C "$APP_DIR" rev-parse HEAD)"
                remote_rev="$(git -C "$APP_DIR" rev-parse "origin/$BLINKBOX_BRANCH")"
                if [[ "$local_rev" != "$remote_rev" ]] && confirm "A Blink Box update is available. Install it?"; then
                    git -C "$APP_DIR" pull --ff-only origin "$BLINKBOX_BRANCH"
                fi
            fi
            ;;
        *) warn "Invalid AUTO_UPDATE value '$AUTO_UPDATE'; using 'ask'." ;;
    esac
}

repair_app() {
    app_installed || die "Blink Box is not installed."
    install_dependencies
    say "Repairing the application checkout..."
    git -C "$APP_DIR" fetch origin "$BLINKBOX_BRANCH"
    git -C "$APP_DIR" reset --hard "origin/$BLINKBOX_BRANCH"
    git -C "$APP_DIR" clean -fd
    write_runtime_config
    say "Repair complete."
}

uninstall_app() {
    app_installed || die "Blink Box is not installed."
    warn "This removes the cloned application but leaves your builds, releases, and launcher settings alone."
    confirm "Remove $APP_DIR?" || exit 0
    rm -rf "$APP_DIR"
    say "Application removed."
}

nuke_app() {
    warn "This removes the cloned application, generated config, and Blink Box state."
    warn "Build and release directories are intentionally preserved."
    confirm "Remove Blink Box application data?" || exit 0
    rm -rf "$APP_ROOT" "$CONFIG_DIR" "$STATE_DIR"
    say "Blink Box application data removed."
}

show_config() {
    cat <<CFG
Bob's Blink Box launcher configuration

Maintainer:     $MAINTAINER_NAME
Git identity:   $GIT_USERNAME <$GIT_EMAIL>
Repository:     $BLINKBOX_REPO_URL
Branch:         $BLINKBOX_BRANCH
Application:    $APP_DIR
Build root:     $DEFAULT_BUILD_ROOT
Release root:   $DEFAULT_RELEASE_ROOT
Remote host:    ${REMOTE_HOST:-not configured}
Platform:       $(is_termux && echo Termux || echo Linux)
Auto-update:    $AUTO_UPDATE
CFG
}

run_app() {
    install_dependencies

    if ! app_installed; then
        say "Bob's Blink Box is not installed."
        confirm "Clone and install it now?" || exit 0
        install_app
    fi

    maybe_update
    write_runtime_config

    local py
    py="$(python_cmd)" || die "Python 3 was not found."

    set -a
    # shellcheck disable=SC1090
    source "$CONFIG_DIR/user.env"
    set +a

    export PYTHONPATH="$APP_DIR${PYTHONPATH:+:$PYTHONPATH}"
    exec "$py" -m blinkbox "$@"
}

usage() {
    cat <<'USAGE'
Usage: launcher.sh [command]

Commands:
  run         Install if needed, optionally update, and launch the TUI
  install     Clone the application repository
  update      Fast-forward the installed application
  repair      Reset the application checkout to the configured branch
  uninstall   Remove only the cloned application
  nuke        Remove application, generated config, and state
  config      Show the active launcher configuration
  help        Show this help
USAGE
}

command="${1:-run}"
[[ $# -gt 0 ]] && shift

case "$command" in
    run)       run_app "$@" ;;
    install)   install_app ;;
    update)    update_app ;;
    repair)    repair_app ;;
    uninstall) uninstall_app ;;
    nuke)      nuke_app ;;
    config)    show_config ;;
    help|-h|--help) usage ;;
    *) die "Unknown command '$command'. Run '$0 help'." ;;
esac
