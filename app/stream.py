import os
import time
import csv
from redis import Redis
import argparse
import pandas as pd
from omegaconf import OmegaConf
from pipeline import Producer, Streamer, StreamersManager, Cache
from utils import Logger

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', help='YAML config file')
    parser.add_argument('-e', '--enable', help='Enable streamer', action=argparse.BooleanOptionalAction)
    parser.add_argument('-d', '--disable', help='Disable streamer', action=argparse.BooleanOptionalAction)

    args = parser.parse_args()
    conf = OmegaConf.load(args.conf)

    try:
        manager = StreamersManager.from_conf(
            conf_streamers=conf.streamers,
            conf_logs=conf.logs,
            conf_cache=conf.redis,
            conf_broker=conf.kafka
        )

        manager.start_all()
    except KeyboardInterrupt:
        manager.interrupt_all()

    # import pdb
    # pdb.set_trace()
    # prod_logger = Logger.get_logger_from_conf("kafka.producer", conf.logs)
    # stream_logger = Logger.get_logger_from_conf("streamer", conf.logs)
    # cache_logger = Logger.get_logger_from_conf("redis.cache", conf.logs)

    # cache = Cache.get_cache_from_conf("redis.cache", conf.logs, conf.redis)
    # producer = Producer(host=conf.kafka.host, port=conf.kafka.port, logger=prod_logger)

    # stream = conf.streamer[0]
    # streamer = Streamer(
        # producer = producer,
        # logger = stream_logger,
        # cache = cache,
        # csv_file_path = os.path.join(conf.sources.dir, stream.file),
        # cache_key = stream.redis_key,
        # producer_topic = stream.topic,
        # messages_per_second = stream.messages_per_second,
        # sleep_disabled = stream.sleep_disabled
    # )

    # if args.enable:
        # streamer.enable()
    # elif args.disable:
        # streamer.disable()
    # else:
        # streamer.stream()
