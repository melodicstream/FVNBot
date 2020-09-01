#!/usr/bin/env bash

docker kill fvnbot
docker rm fvnbot
git pull
docker build -t fvnbot .
docker run -d --restart unless-stopped --name fvnbot --mount source=fvnbot-database,target=/app/database fvnbot
