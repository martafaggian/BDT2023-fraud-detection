from __future__ import annotations
import csv
import time
from enum import IntEnum
#
from utils import Logger
from pipeline.cache import Cache
from pipeline.broker import Producer

class StreamerStatus(IntEnum):
    DISABLED = 0
    ENABLED = 1
    INTERRUPTED = -1

class StreamerNotEnabledException(Exception):
    def __init__(self, logger, message, *args):
        super().__init__(message)
        self.args = args
        logger.error(message)

class Streamer:
    def __init__(
        self,
        producer: Producer,
        logger: Logger,
        cache: Cache,
        csv_file_path: str,
        cache_key: str = "streamer_active",
        producer_topic: str = "custom_source",
        init_status: StreamerStatus = StreamerStatus.ENABLED,
        messages_per_second: int = 1,
        sleep_disabled: int = 10 # seconds of sleep if disabled to check again
    ):
        self.logger = logger
        self.file_path = csv_file_path
        self.producer = producer
        self.cache = cache
        self.cache_key = cache_key
        self.topic = producer_topic
        self.mps = messages_per_second
        self.sleep_disabled = sleep_disabled
        self.set_status(init_status)
        self.print_status()

    def get_status(self):
        return int(self.cache.read(self.cache_key))

    def set_status(self, status):
        self.cache.write(self.cache_key, int(status))

    def print_status(self):
        status = self.get_status()
        if status == StreamerStatus.ENABLED:
            self.logger.info(f"{self.cache_key} stream enabled.")
        elif status == StreamerStatus.DISABLED:
            self.logger.info(f"{self.cache_key} stream disabled.")
        elif status == StreamerStatus.INTERRUPTED:
            self.logger.info(f"{self.cache_key} stream interrupted.")
        else:
            self.logger.error(f"{self.cache_key} stream unknown status.")

    def enable(self):
        self.set_status(StreamerStatus.ENABLED)
        self.print_status()

    def disable(self):
        self.set_status(StreamerStatus.DISABLED)
        self.print_status()

    def interrupt(self):
        self.set_status(StreamerStatus.INTERRUPTED)
        self.print_status()

    def is_enabled(self):
        return self.get_status() == StreamerStatus.ENABLED

    def is_disabled(self):
        return self.get_status() == StreamerStatus.DISABLED

    def is_interrupted(self):
        return self.get_status() == StreamerStatus.INTERRUPTED

    def stream(self):
        self.print_status()
        while not self.is_interrupted():
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if not self.is_enabled():
                            raise StreamerNotEnabledException(self.logger, 'Streamer is disabled.')
                        self.producer.send(row, topic=self.topic)
                        time.sleep(float(1/self.mps))
                        # TODO: check sending result
                        # TODO: save on redis last sent row and resume
                        # from there
            except StreamerNotEnabledException as e:
                self.logger.info(f"{self.cache_key} stream disabled.")
                self.logger.info(f"Sleeping {self.sleep_disabled} seconds...")
                time.sleep(self.sleep_disabled)

# class StreamersHandler:
    # # TODO: handle multiple streamers in multithreading/processing
    # # TODO: disable all streamers
    # # TODO: enable all streamers
    # pass
