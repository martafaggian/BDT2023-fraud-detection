from redis import Redis
from utils import Logger

class CacheNotConnectedException(Exception):
    def __init__(self, logger, message, *args):
        super().__init__(message)
        self.args = args
        logger.error(message)

class Cache:
    def __init__(
        self,
        logger: Logger,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        decode_responses: bool = True
    ):
        self._host = host
        self._port = port
        self._db = db
        self._cache = Redis(
            host=self._host,
            port=self._port,
            db=self._db,
            decode_responses=decode_responses)
        self._logger = logger

    def is_connected(self):
        return self._cache.ping()

    def check_connected(self):
        if not self.is_connected():
            raise CacheNotConnectedException(
                self._logger,
                f'Cache is not connected at {self._host}:{self._port} with db {self._db}'
            )

    def write(self, key, value):
        self.check_connected()
        self._cache.set(key, value)

    def read(self, key):
        self.check_connected()
        return self._cache.get(key)

