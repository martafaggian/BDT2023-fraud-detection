#!/bin/bash

python app3.py &
sleep 10
python app2.py &
sleep 10
python app1.py
