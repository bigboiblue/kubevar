#!/bin/bash

SCRIPT_DIR=$(dirname $0)

python3 -m venv "$SCRIPT_DIR/venv"
source "$SCRIPT_DIR/venv/bin/activate"
pip install -r "$SCRIPT_DIR/requirements.txt"

echo "Setup completed!"