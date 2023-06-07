#!/bin/bash

docker exec -it pipeline-jobmanager python model/main.py -c config.yaml
