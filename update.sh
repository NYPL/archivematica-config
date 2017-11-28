#!/bin/bash
set -e

# This all happens in here:
cd /usr/lib/archivematica/archivematica-config/

# Grab a version ID:
VERSION=$(git describe --always --tag)

echo -e "\nDeploying into master branch:"
# Just in case something changed while we generated the data:
git checkout master
git pull origin master

# Generate new stuff:
/usr/share/python/archivematica-config/bin/python cli.py

# Add the new stuff:
git add --all .
git commit -am "Updated MCPs added."