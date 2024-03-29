#!/usr/bin/env sh

if ! [ -d "/home/ubuntu/" ]; then
    echo "This script is meant to be run on the production server only."
    exit 1
fi

set -x

curl https://starfish-education.eu > /dev/null
curl https://starfish-education.eu/browse > /dev/null
curl https://starfish-education.eu/browse?ftype=goodpractice > /dev/null
curl https://starfish-education.eu/browse?ftype=project > /dev/null
curl https://starfish-education.eu/browse?ftype=event > /dev/null
curl https://starfish-education.eu/browse?ftype=glossary > /dev/null
curl https://starfish-education.eu/browse?ftype=information > /dev/null
curl https://starfish-education.eu/browse?ftype=person > /dev/null
# curl https://starfish-education.eu/browse?ftype=question > /dev/null
curl https://starfish-education.eu/browse?ftype=usercase > /dev/null
curl https://starfish-education.eu/browse?ftype=cpd_scenario > /dev/null
