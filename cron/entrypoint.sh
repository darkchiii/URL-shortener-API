#!/bin/sh

# crontab /etc/cron.d/deactivate_cron
# pip install -r /app/requirements.txt

echo "Connecting to DB with:"
echo "User: $POSTGRES_USER"
echo "DB: $POSTGRES_DB"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"


# prawa do logów
touch /var/log/cron.log
chmod 0666 /var/log/cron.log

# cron działa w tle
cron

# trzymaj kontener przy życiu, czytaj logi crona
tail -f /var/log/cron.log
