#!/bin/zsh
# Runs the notebook start to finish as it is saved and writes the executed copy to last_run.ipynb.
# The key is read from .env into this process only.
cd "$(dirname "$0")" || exit 1
OPENROUTER_API_KEY="$(sed -n 's/^OPENROUTER_API_KEY=//p' .env | tail -1 | tr -d ' "\r\n'"'")"
[ -z "$OPENROUTER_API_KEY" ] && { echo "No key in .env"; exit 1; }
export OPENROUTER_API_KEY
exec caffeinate -is .venv/bin/jupyter execute --timeout=-1 --output=last_run experiment.ipynb
