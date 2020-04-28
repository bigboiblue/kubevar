#!/bin/bash

DIR="$(cd "$(dirname "$0")"; pwd)" # install.sh dir
SRC_DIR="$DIR/src"
DIST_DIR="$SRC_DIR/dist"
PKG_NAME="kubevarpkg"

### Get su privileges
echo "SU privileges required..."
sudo echo ""


### Create egg file
cd "$SRC_DIR"
if [[ -d "build" ]] || [[ -d "dist" ]]; then
    echo "ERROR: Please remove or rename src/build and src/dist before installing..."
    exit
fi
python3 ./setup.py bdist_egg --exclude-source-files

EGG_FILE="$DIST_DIR/$(cd "$DIST_DIR"; ls)"

### Setup /usr/local/lib/kubevar as venv
LIB_PATH="/usr/local/lib/kubevar"
sudo python3 -m venv "$LIB_PATH"
source "$LIB_PATH/bin/activate"
sudo easy_install "$EGG_FILE"
deactivate


### Copy kubevar to /usr/local/bin
BIN_PATH="/usr/local/bin"
sudo cp "$DIR/src/kubevar" "$BIN_PATH"


### Cleanup
echo "Cleaning up..."
cd "$SRC_DIR"
rm -R build
rm -R dist
rm -R "$PKG_NAME.egg-info"

echo "Done!"
