import os
import time
import csv
import argparse
import pandas as pd
from omegaconf import OmegaConf
from pipeline import Producer
from utils import Logger

def main(conf):
    logger = Logger.get_logger_from_conf("kafka.producer", conf.logs)
    producer = Producer(conf.kafka.host, conf.kafka.port, logger)
    if producer.is_connected():
        for source in conf.sources.files:
            with open(os.path.join(conf.sources.dir, source), 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    producer.send(row, topic="test")
                    time.sleep(float(1/conf.streamer.messages_per_second))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', help='YAML config file')
    args = parser.parse_args()
    conf = OmegaConf.load(args.conf)
    main(conf)
