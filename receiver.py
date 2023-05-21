import os
import time
import csv
import argparse
import pandas as pd
from omegaconf import OmegaConf
from pipeline import Consumer
from utils import Logger

def main(conf):
    logger = Logger.get_logger_from_conf("kafka.consumer", conf.logs)
    consumer = Consumer(conf.kafka.host, conf.kafka.port, "test", logger)
    if consumer.is_connected():
        while True:
            consumer.retrieve()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', help='YAML config file')
    args = parser.parse_args()
    conf = OmegaConf.load(args.conf)
    main(conf)
