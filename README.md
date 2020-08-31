# FVNBot

A bot made to help keep track of Furry Visual Novels in the Furry Visual Novels Discord server.

## Configuration

The bot needs to get the configuration from the `config.json` file. 

## How to run

This bot runs on Docker. To run the bot, first build the bot:

```
docker build -t fvnbot .
```

After that, run it. The important thing is to mount the `/database` folder into an external volume.

```
docker run -d --restart unless-stopped --name fvnbot --mount source=fvnbot-database,target=/app/database fvnbot
```

It will start a Docker container in daemon mode, and it will always restart unless manually stopped.

## Current setup

In the server I run this bot in, I make hourly backups of the database file into another git repository.
The script is located in `/etc/cron.hourly/fvnbot_backup`.

Doing `docker volume inspect fvnbot-database` shows the location of the Docker volume which contains the database. 
