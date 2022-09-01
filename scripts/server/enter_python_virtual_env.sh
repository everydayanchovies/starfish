#!/usr/bin/env sh

if ! [ -d "/home/ubuntu/" ]; then
    echo "This script is meant to be run on the production server only."
    exit 1
fi

PROJECT_ROOT=/home/ubuntu/Starfish-master;

echo "Creating python virtual environment (venv)...";
python3 -m venv $PROJECT_ROOT/.venv;

echo "Activating python venv...";
. $PROJECT_ROOT/.venv/bin/activate;

pip install --upgrade pip;

echo "Installing python packages in venv...";
pip install -r $PROJECT_ROOT/requirements.txt
# installing through pip fails on build
pip install https://projects.unbit.it/downloads/uwsgi-lts.tar.gz
