#!/bin/bash

docker stop $(docker ps -a -q)
docker system prune --all --force
docker compose -f docker-compose.yml build
docker compose -f docker-compose.yml up -d
