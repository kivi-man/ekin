#!/bin/sh
# Ekin - macOS / Linux kısayolu.
#   chmod +x ekin.sh
#   ln -s "$(pwd)/ekin.sh" ~/.local/bin/ekin     (her yerden "ekin" yazmak için)
DIZIN="$(cd "$(dirname "$(readlink -f "$0" 2>/dev/null || echo "$0")")" && pwd)"
exec python3 "$DIZIN/ekin.py" "$@"
