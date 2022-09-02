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

sudo ln -s /home/ubuntu/Starfish-master/nginx/production.conf /etc/nginx/sites-available/starfish-production.conf
sudo ln -s /etc/nginx/sites-available/starfish-production.conf /etc/nginx/sites-enabled/

sudo systemctl enable nginx
sudo systemctl restart nginx

sudo snap install core
sudo snap refresh core

sudo snap install --classic certbot

sudo ln -s /snap/bin/certbot /usr/bin/certbot

sudo certbot --nginx

sudo systemctl enable memcached
