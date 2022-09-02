#!/usr/bin/env sh

if ! [ -d "/home/ubuntu/" ]; then
    echo "This script is meant to be run on the production server only."
    exit 1
fi

sudo apt install -y \
    build-essential \
    python3 python3-dev python3-venv python3-pip \
    libsasl2-dev libldap2-dev libssl-dev \
    nginx
