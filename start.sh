#!/bin/bash

docker compose up --build -d
./stream_start.sh
docker exec -it pipeline-jobmanager flink run -py pipeline/main.py &
