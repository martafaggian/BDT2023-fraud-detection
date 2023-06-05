from redis import Redis
from app.utils import Logger

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

    def write(self, key, value, is_dict=False):
        self.check_connected()
        if is_dict:
            self._cache.hmset(key, value)
        else:
            self._cache.set(key, value)

    def read(self, key, is_dict=False):
        self.check_connected()
        if is_dict:
            return self._cache.hgetall(key)
        return self._cache.get(key)

    def write_multiple(self, keys, values, is_dict=False):
        self.check_connected()
        with self._cache.pipeline() as pipe:
            for key, value in zip(keys, values):
                if is_dict:
                    pipe.hmset(key, value)
                else:
                    pipe.set(key, value)
            pipe.execute()

    def key_exists(self, key: str) -> bool:
        self.check_connected()
        return self._cache.exists(key) > 0

    @staticmethod
    def from_conf(name, conf_cache, conf_log, db):
        logger = Logger.from_conf(name, conf_log)
        return Cache(
            logger=logger,
            host=conf_cache.host,
            port=conf_cache.port,
            db=db
        )
