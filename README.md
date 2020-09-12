# FVNBot

A bot made to help keep track of Furry Visual Novels in the Furry Visual Novels
Discord server.

## Configuration

The bot needs to get the configuration from the `config.json` file. 

The bot uses environment variables to be configured. For that, we use a `.env`
file. A template can be found in `.env.template`.

## How to run

This bot runs on Docker. To run the bot, first build the bot:

```
docker build -t fvnbot .
```

After that, run it. The important thing is to mount the `/database` folder into
an external volume. Don't forget to choose a correct `.env` file!

```
docker run -d --env-file .env --name fvnbot --mount source=fvnbot-database,target=/app/database --restart unless-stopped fvnbot
```

It will start a Docker container in daemon mode, and it will always restart
unless manually stopped.

## Current setup

In the server I run this bot in, I make hourly backups of the database file int
another git repository. The script is located in `/etc/cron.hourly/fvnbot_backup`,
and the source is the script `fvnbot_backup.sh`. Don't forget to configure `git`
properly before running the script.

Running `docker volume inspect fvnbot-database` shows the location of the Docker
volume which contains the database. 
