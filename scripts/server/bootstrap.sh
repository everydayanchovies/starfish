#!/usr/bin/env sh

if ! [ -d "/home/ubuntu/" ]; then
    echo "This script is meant to be run on the production server only."
    exit 1
fi

PROJECT_DIR=/home/ubuntu/Starfish-master

cd "$PROJECT_DIR" || exit

sudo apt update
sudo apt upgrade -y
sudo sh "$PROJECT_DIR/scripts/server/install_packages_ubuntu.sh" || exit

sudo mkdir -p /var/www/Starfish/static
sudo chown -R $USER:$USER /var/www/Starfish
sudo chmod -R 755 /var/www/Starfish

sudo ufw allow "OpenSSH" || exit
sudo ufw allow "Nginx Full" || exit

yes | sudo ufw enable

sudo systemctl enable memcached --now

sudo rm -f /etc/caddy/Caddyfile || true
# TODO fix permissions so that the service works at all
sudo ln -s /home/ubuntu/Starfish-master/caddy/Caddyfile /etc/caddy/

sudo systemctl enable caddy --now
