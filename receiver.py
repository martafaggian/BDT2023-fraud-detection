import os
import time
import csv
import argparse
import pandas as pd
from omegaconf import OmegaConf
from broker import Consumer

def main(conf):
    consumer = Consumer(conf.kafka.host, conf.kafka.port, "test")
    while True:
        consumer.retrieve()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', help='YAML config file')
    args = parser.parse_args()
    conf = OmegaConf.load(args.conf)
    main(conf)
