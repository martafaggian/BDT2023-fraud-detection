from threading import Thread
from app.utils import Logger
from streamer import Streamer

class StreamersManager:
    # # TODO: handle multiple streamers in multithreading/processing
    # # TODO: disable all streamers
    # # TODO: enable all streamers
    # pass
    def __init__(
        self,
        logger: Logger
    ):
        self._logger = logger
        self._streamers = []
        self._threads = []

    def add_streamer(self, streamer: Streamer):
        self._streamers.append(streamer)

    def start_all(self):
        self.enable_all()
        for streamer in self._streamers:
            thread = Thread(target=streamer.stream)
            self._threads.append(thread)
        for thread in self._threads:
            thread.start()

    def enable_all(self):
        for streamer in self._streamers:
            streamer.enable()

    def disable_all(self):
        for streamer in self._streamers:
            streamer.disable()

    def interrupt_all(self):
        for streamer in self._streamers:
            streamer.interrupt()
        for thread in self._threads:
            thread.join()
        self._threads = []

    @staticmethod
    def from_conf(conf_streamers, conf_broker, conf_cache, conf_logs):
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
