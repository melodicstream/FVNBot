#!/bin/bash

cd /var/lib/docker/volumes/fvnbot-database/_data

git add .

git commit -m "backup `date -Is`"

git push
