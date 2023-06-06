'''
The code represents a Streamer class that is used for streaming data from a CSV file and 
producing messages to a Kafka topic. It has methods for enabling, disabling, and interrupting 
the streamer, as well as methods for checking the status of the streamer. The stream method 
starts streaming data from the CSV file and continuously produces messages to the Kafka topic 
until interrupted.

The class also includes a static method from_conf that creates a Streamer object based on 
the provided configurations. It uses the configurations for the logger, cache, Kafka broker,
and streamer itself to initialize the Streamer object.

The code includes inline documentation explaining the purpose and usage of each method and class.

The model can be used as follow:

producer = Producer(...)
logger = Logger(...)
cache = Cache(...)
streamer = Streamer(producer, logger, cache, csv_file_path, ...)
streamer.enable()
streamer.stream()

'''
from __future__ import annotations
import csv
import time
from enum import IntEnum
#
from app.infrastructure import Cache, Producer
from app.utils import Logger

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
    '''
    A class representing a streamer that reads data from a CSV file and sends it to a Kafka
    topic using a producer.
    
    :param producer: The Kafka object
    :type producer: Producer
    :param logger: The logger object for logging
    :type logger: Logger
    :param cache: The cache object for managing streamer status
    :type cache: Cache
    :param csv_file_path: The path to the CSV file to be streamed
    :type csv_file_path: str
    :param cache_key: The cache key to store the streamer status
    :type cache_key: str
    :param producer_topic: The Kafka topic to which the data will be sent
    :type producer_topic: str
    :param messages_per_second: The number of messages to send per second
    :type messages_per_second: int
    :param sleep_disabled: The number of seconds to sleep if the streamer is disabled 
    :type sleep_disabled: int
    :param init_status: The initial status of the streamer
    :type init_status: StreamerStatus
    '''
    def __init__(
        self,
        producer: Producer,
        logger: Logger,
        cache: Cache,
        csv_file_path: str,
        cache_key: str = "streamer_active",
        producer_topic: str = "custom_source",
        messages_per_second: int = 1,
        sleep_disabled: int = 10, # seconds of sleep if disabled to check again
        init_status: StreamerStatus = StreamerStatus.ENABLED
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
        '''
        Get the current status of the streamer.
        
        :return: The current status of the streamer
        '''
        return int(self.cache.read(self.cache_key))

    def set_status(self, status):
        '''
        Set the status of the streamer
        
        :param status: The status to set
        :type key: StreamerStatus
        '''
        self.cache.write(self.cache_key, int(status))

    def print_status(self):
        '''
        Print the current status of the streamer
        '''
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
        '''
        Enable the streamer
        '''
        self.set_status(StreamerStatus.ENABLED)
        self.print_status()

    def disable(self):
        '''
        Disabel the streamer
        '''
        self.set_status(StreamerStatus.DISABLED)
        self.print_status()

    def interrupt(self):
        '''
        Interrupt the streamer
        '''
        self.set_status(StreamerStatus.INTERRUPTED)
        self.print_status()

    def is_enabled(self):
        '''
        Check if the streamer is enabled
        
        :return: True if the streamer is disabled. False otherwise
        '''
        return self.get_status() == StreamerStatus.ENABLED

    def is_disabled(self):
        '''
        Check if the streamer is disabled
        
        :return: True if the streamer is disabled. False otherwise.
        
        '''
        return self.get_status() == StreamerStatus.DISABLED

    def is_interrupted(self):
        '''
        Check if the streamer is interrupted.
        
        :return: True if the streamer is interrupted, False otherwise.
        '''
        return self.get_status() == StreamerStatus.INTERRUPTED

    def stream(self):
        '''
        Start streaming data from the CSV file and produce messages to the Kafka topic
        '''
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
                        # TODO: save on redis last sent row and resume
                        # from there
            except StreamerNotEnabledException as e:
                self.logger.info(f"{self.cache_key} stream disabled.")
                self.logger.info(f"Sleeping {self.sleep_disabled} seconds...")
                time.sleep(self.sleep_disabled)

    @staticmethod
    def from_conf(conf_stream, conf_log, conf_broker, conf_cache):
        '''
        Create a Streamer object based on the provided configurations.
        
        :param conf_stream: The configuration for the streamer
        :type conf_stream: 
        :param conf_log: The configuration for the logger
        :type conf_log:
        :param conf_broker: The configuration for the Kafka broker
        :type conf_broker:
        :param conf_cache:The configuration for the Cache
        :type conf_cache:
        :return: The created Streamer object 
        
        '''
        logger = Logger.from_conf(conf_stream.name, conf_log)
        cache = Cache.from_conf(
            f"{conf_stream.name}.redis.cache",
            conf_log=conf_log,
            conf_cache=conf_cache,
            db=conf_cache.streamers.db)
        producer = Producer.from_conf(
            f"{conf_stream.name}.kafka.producer", conf_log=conf_log,
            conf_broker=conf_broker)
        return Streamer(
            logger = logger,
            producer = producer,
            cache = cache,
            csv_file_path = conf_stream.file,
            cache_key = conf_stream.status_key,
            producer_topic = conf_stream.topic,
            messages_per_second = conf_stream.messages_per_second,
            sleep_disabled = conf_stream.sleep_disabled
        )
