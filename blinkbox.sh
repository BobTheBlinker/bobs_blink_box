#!/usr/bin/env bash
set -Eeuo pipefail

# =============================================================================
# Bob's Blink Box - user settings
# =============================================================================
MAINTAINER_NAME="BOBtheBlinker"
GIT_USERNAME="BOBtheBlinker"
GIT_EMAIL="BOBtheBlinker@gMail.com"

ANDROID_ROOT="$HOME/Android"
ROMS_ROOT="$ANDROID_ROOT/ROMs"
RECOVERIES_ROOT="$ANDROID_ROOT/Recoveries"
TOOLS_ROOT="$ANDROID_ROOT/Tools"
RELEASES_ROOT="$ANDROID_ROOT/Releases"

DEFAULT_EDITOR="nano"
REMOTE_HOST=""

BLINKBOX_REPO_URL="https://github.com/BobTheBlinker/bobs_blink_box.git"
BLINKBOX_BRANCH="main"
AUTO_UPDATE="ask" # never | ask | always
# =============================================================================

APP_ROOT="${BLINKBOX_APP_ROOT:-$HOME/.local/share/blinkbox}"
APP_DIR="$APP_ROOT/app"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/blinkbox"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/blinkbox"

on_error() {
    local status=$?
    printf '\nERROR: Blink Box stopped at line %s while running:\n  %s\n' \
        "${BASH_LINENO[0]:-unknown}" "${BASH_COMMAND:-unknown}" >&2
    printf 'Exit status: %s\n' "$status" >&2
    exit "$status"
}
trap on_error ERR

say()  { printf '\n%s\n' "$*"; }
warn() { printf '\nWARNING: %s\n' "$*" >&2; }
die()  { printf '\nERROR: %s\n' "$*" >&2; exit 1; }

confirm() {
    local prompt="${1:-Continue?}" answer
    [[ -t 0 ]] || return 1
    read -r -p "$prompt [y/N] " answer || return 1
    [[ "$answer" =~ ^[Yy]([Ee][Ss])?$ ]]
}

is_termux() {
    [[ -n "${TERMUX_VERSION:-}" || -d /data/data/com.termux/files/usr ]]
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

install_dependencies() {
    local need_git=0 need_python=0
    command -v git >/dev/null 2>&1 || need_git=1
    python_cmd >/dev/null 2>&1 || need_python=1
    (( need_git == 0 && need_python == 0 )) && return 0

    warn "Git and Python 3 are required."
    confirm "Install the missing packages now?" || die "Install Git and Python 3, then rerun Blink Box."

    if is_termux; then
        pkg update
        pkg install -y git python
    elif command -v apt-get >/dev/null 2>&1; then
        command -v sudo >/dev/null 2>&1 || die "sudo is required to install packages."
        sudo apt-get update
        sudo apt-get install -y git python3
    elif command -v dnf >/dev/null 2>&1; then
        sudo dnf install -y git python3
    elif command -v pacman >/dev/null 2>&1; then
        sudo pacman -S --needed git python
    else
        die "Unsupported package manager. Install Git and Python 3 manually."
    fi
}

app_installed() {
    [[ -d "$APP_DIR/.git" && -f "$APP_DIR/blinkbox/__main__.py" ]]
}

write_runtime_config() {
    mkdir -p "$CONFIG_DIR" "$STATE_DIR" \
        "$ANDROID_ROOT" "$ROMS_ROOT" "$RECOVERIES_ROOT" \
        "$TOOLS_ROOT" "$RELEASES_ROOT"

    umask 077
    {
        printf 'BLINKBOX_MAINTAINER_NAME=%q\n' "$MAINTAINER_NAME"
        printf 'BLINKBOX_GIT_USERNAME=%q\n' "$GIT_USERNAME"
        printf 'BLINKBOX_GIT_EMAIL=%q\n' "$GIT_EMAIL"
        printf 'BLINKBOX_ANDROID_ROOT=%q\n' "$ANDROID_ROOT"
        printf 'BLINKBOX_ROMS_ROOT=%q\n' "$ROMS_ROOT"
        printf 'BLINKBOX_RECOVERIES_ROOT=%q\n' "$RECOVERIES_ROOT"
        printf 'BLINKBOX_TOOLS_ROOT=%q\n' "$TOOLS_ROOT"
        printf 'BLINKBOX_RELEASES_ROOT=%q\n' "$RELEASES_ROOT"
        printf 'BLINKBOX_DEFAULT_EDITOR=%q\n' "$DEFAULT_EDITOR"
        printf 'BLINKBOX_REMOTE_HOST=%q\n' "$REMOTE_HOST"
    } > "$CONFIG_DIR/user.env"
}

install_app() {
    install_dependencies
    app_installed && die "Blink Box is already installed at $APP_DIR"

    local tmp_dir="$APP_ROOT/app.tmp.$$"
    rm -rf "$tmp_dir"
    mkdir -p "$APP_ROOT"

    say "Cloning Bob's Blink Box..."
    if ! git clone --depth 1 --branch "$BLINKBOX_BRANCH" --single-branch \
        "$BLINKBOX_REPO_URL" "$tmp_dir"; then
        rm -rf "$tmp_dir"
        die "Git clone failed. The application was not installed."
    fi

    [[ -f "$tmp_dir/blinkbox/__main__.py" ]] || {
        rm -rf "$tmp_dir"
        die "The cloned repository is missing blinkbox/__main__.py"
    }

    rm -rf "$APP_DIR"
    mv "$tmp_dir" "$APP_DIR"
    write_runtime_config
    say "Blink Box installed successfully."
}

update_app() {
    app_installed || die "Blink Box is not installed."
    say "Updating Blink Box..."
    git -C "$APP_DIR" pull --ff-only origin "$BLINKBOX_BRANCH"
}

maybe_update() {
    app_installed || return 0
    case "$AUTO_UPDATE" in
        never) return 0 ;;
        always) update_app ;;
        ask)
            git -C "$APP_DIR" fetch -q origin "$BLINKBOX_BRANCH" || {
                warn "Could not check for updates; launching the installed copy."
                return 0
            }
            local current remote
            current="$(git -C "$APP_DIR" rev-parse HEAD)"
            remote="$(git -C "$APP_DIR" rev-parse "origin/$BLINKBOX_BRANCH")"
            if [[ "$current" != "$remote" ]] && confirm "A Blink Box update is available. Install it?"; then
                update_app
            fi
            ;;
        *) warn "Invalid AUTO_UPDATE='$AUTO_UPDATE'; skipping update check." ;;
    esac
}

repair_app() {
    app_installed || die "Blink Box is not installed."
    git -C "$APP_DIR" fetch origin "$BLINKBOX_BRANCH"
    git -C "$APP_DIR" reset --hard "origin/$BLINKBOX_BRANCH"
    git -C "$APP_DIR" clean -fd
    write_runtime_config
    say "Repair complete."
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

show_config() {
    cat <<EOF_CONFIG
Repository:      $BLINKBOX_REPO_URL
Branch:          $BLINKBOX_BRANCH
Application:     $APP_DIR
Android root:    $ANDROID_ROOT
ROMs:            $ROMS_ROOT
Recoveries:      $RECOVERIES_ROOT
Tools:           $TOOLS_ROOT
Releases:        $RELEASES_ROOT
Remote host:     ${REMOTE_HOST:-not configured}
Platform:        $(is_termux && echo Termux || echo Linux)
Auto-update:     $AUTO_UPDATE
EOF_CONFIG
}

uninstall_app() {
    warn "This removes only the cloned application. Your ~/Android workspace stays intact."
    confirm "Remove $APP_DIR?" || exit 0
    rm -rf "$APP_DIR"
    say "Application removed."
}

nuke_app() {
    warn "This removes Blink Box application/config/state data, but preserves $ANDROID_ROOT."
    confirm "Remove Blink Box application data?" || exit 0
    rm -rf "$APP_ROOT" "$CONFIG_DIR" "$STATE_DIR"
    say "Blink Box application data removed."
}

usage() {
    cat <<'EOF_USAGE'
Usage: blinkbox [command]

Commands:
  run        Install if needed, update if requested, and launch
  install    Clone the application
  update     Fast-forward the installed application
  repair     Reset the installed checkout to origin/main
  uninstall  Remove only the installed application
  nuke       Remove application, generated config, and state
  config     Show active paths and settings
  help       Show this help
EOF_USAGE
}

command="${1:-run}"
[[ $# -gt 0 ]] && shift

case "$command" in
    run) run_app "$@" ;;
    install) install_app ;;
    update) update_app ;;
    repair) repair_app ;;
    uninstall) uninstall_app ;;
    nuke) nuke_app ;;
    config) show_config ;;
    help|-h|--help) usage ;;
    *) die "Unknown command '$command'. Run '$0 help'." ;;
esac
