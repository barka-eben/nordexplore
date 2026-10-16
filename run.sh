#!/usr/bin/env sh
# Lance NordExplore sur http://127.0.0.1:5000
cd "$(dirname "$0")" || exit 1
python3 -m nordexplore.app
