# FVNBot

A bot made to help keep track of Furry Visual Novels in the Furry Visual Novels
Discord server.

## Configuration

The bot uses environment variables to be configured. For that, we use a `.env`
file. A template can be found in `.env.template`.

## How to run

This bot runs on Docker. To run the bot, use the docker-compose command:

```
docker-compose up --build -d
```

It will start a Docker container in daemon mode, and it will always restart
unless manually stopped.

## How to update

After pulling the new source from git, just run the same run command again:

```
docker-compose up --build -d
```

## Current setup

In the server I run this bot in, I make hourly backups of the database file int
another git repository. The script is located in `/etc/cron.hourly/fvnbot_backup`,
and the source is the script `fvnbot_backup.sh`. Don't forget to configure `git`
properly before running the script.

Running `docker volume inspect fvnbot-database` shows the location of the Docker
volume which contains the database. That location is what needs to be included
in the `fvnbot_backup.sh` script.
