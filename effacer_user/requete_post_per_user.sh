#!/bin/sh

docker exec -t bc1ef00fb473 psql --dbname=mattermost --username=mmuser -A -t -0 --command="select id from posts where userid = (SELECT id FROM users WHERE username ='$1');"
