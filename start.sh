#!/bin/bash

docker compose up --build -d
echo "Waiting 30s for Cassandra init..."
sleep 30
./stream_start.sh
docker exec -it pipeline-jobmanager flink run -py pipeline/main.py -d
