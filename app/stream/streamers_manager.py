'''

The provided code consists of two classes: Streamer and StreamersManager.
The Streamer class represents an individual streamer and provides methods to control its status
and perform streaming operations. It reads data from a CSV file and sends it to a Kafka topic
using a producer. The class supports enabling, disabling, and interrupting the streamer, as
well as checking its status.

The StreamersManager class is responsible for managing multiple streamers. It allows adding
streamers to the manager and provides methods to start all streamers in separate threads,
enable/disable all streamers collectively, and interrupt all streamers by stopping their
execution and joining their threads.

The module can be used as follow:
logger = Logger()

streamer1 = Streamer(...)
streamer2 = Streamer(...)

manager = StreamersManager(logger)
manager.add_streamer(streamer1)
manager.add_streamer(streamer2)

manager.start_all()

manager.enable_all()
manager.disable_all()
manager.interrupt_all()
'''
from threading import Thread
from app.utils import Logger
from app.stream import Streamer

class StreamersManager:
    '''
    The StreamersManager class is responsible for managing multiple Streamer instances.
    It provides methods to start, enable, disable, and interrupt all the streamers.

    :param logger: The logger object for logging
    :type logger: Logger
    '''
    def __init__(
        self,
        logger: Logger
    ):
        self._logger = logger
        self._streamers = []
        self._threads = []

    def add_streamer(self, streamer: Streamer):
        '''
        Adds a Streamer instance to the manager.

        :param streamer: The Streamer instance to be added.
        :type streamer: Streamer
        '''
        self._streamers.append(streamer)

    def start_all(self):
        '''
        Starts all the streamers in separate threads.
        '''
        self.enable_all()
        for streamer in self._streamers:
            thread = Thread(target=streamer.stream)
            self._threads.append(thread)
        for thread in self._threads:
            thread.start()

    def enable_all(self):
        '''
        Enables all the streamers.
        '''
        for streamer in self._streamers:
            streamer.enable()

    def disable_all(self):
        '''
        Disables all the streamers.
        '''
        for streamer in self._streamers:
            streamer.disable()

    def interrupt_all(self):
        '''
        Interrupts all the streamers and joins their threads.
        '''
        for streamer in self._streamers:
            streamer.interrupt()
        for thread in self._threads:
            thread.join()
        self._threads = []

    @staticmethod
    def from_conf(conf_streamers, conf_broker, conf_cache, conf_logs):
        '''
        Creates a StreamerManager instance with streamers initialized from the provided
        configurations.

        :param conf_streamers: The configurations for the streamers.
        :type conf_streamers:
        :param conf_broker: The configurations for the broker
        :type conf_broker:
        :param conf_cache: The configurations for the cache
        :type conf_cache:
        :param conf_logs: The configurations for the logger
        :type conf_logs:
        :return: A StreamersManager instance
        '''
        manager = StreamersManager(
            logger=Logger.from_conf("streamer.manager", conf_logs))
        for stream in conf_streamers:
            streamer = Streamer.from_conf(
                conf_stream = stream,
                conf_log = conf_logs,
                conf_broker = conf_broker,
                conf_cache = conf_cache)
            manager.add_streamer(streamer)
        return manager
