#!/usr/bin/env bash
set -euo pipefail

# Keep Linux dependencies separate from any host node_modules directory.
sudo chown "$(id -u):$(id -g)" frontend/node_modules
python -m pip install --user -r requirements.txt
npm --prefix frontend ci
