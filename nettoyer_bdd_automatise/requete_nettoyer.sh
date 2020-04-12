#!/bin/sh

# effacer les vieux messages
docker exec -t bc1ef00fb473 psql --dbname=mattermost --username=mmuser -A -t -0 --command="DELETE FROM posts WHERE createat < $1;"
# effacer les liens vers les vieux fichiers
docker exec -t bc1ef00fb473 psql --dbname=mattermost --username=mmuser -A -t -0 --command="DELETE FROM fileinfo WHERE createat < $1;"
