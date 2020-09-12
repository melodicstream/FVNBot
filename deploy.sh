#!/usr/bin/env bash

# Convenience script that redeploys the bot.

docker kill fvnbot
docker rm fvnbot
git pull
docker build -t fvnbot .
docker run -d --env-file .env --name fvnbot --mount source=fvnbot-database,target=/app/database --restart unless-stopped fvnbot
