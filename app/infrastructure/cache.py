'''
The Cache module provides a class for interacting with a Redis cache, 
allowing you to store and retrieve key-value pairs. It also includes an 
exception class for handling cache connection errors. 

The module can be used as follows:

from cache import Cache
from app.utils import Logger

logger = Logger()

conf_cache = {
    "host": "localhost",
    "port": 6379
}

conf_log = {
    "dir": "./logs",
    "info_file": "info.log",
    "warning_file": "warning.log",
    "error_file": "error.log",
    "critical_file": "critical.log",
    "debug_file": "debug.log"
}

cache = Cache.from_conf("run_name", conf_cache, conf_log, db=0)
cache.write("key1", "value1")

value = cache.read("key1")
print(value)  # Output: 'value1'

'''
from redis import Redis
from app.utils import Logger

class CacheNotConnectedException(Exception):
    '''
    A class that raise an exception when the 
    cache is not connected. It inherits from the base Exception class.
    
    :param logger: An instance of the Logger class for handling logging 
    :type logger:
    :param message: The error message
    :type message:
    :param args: Additional arguments for the exception
    :type args:
    '''
    def __init__(self, logger, message, *args):
        super().__init__(message)
        self.args = args
        logger.error(message)

class Cache:
    '''
    The Cache class represents a Redis cache and provides methods for interacting with it. 
    It utilizes the redis.Redis class from the redis module for cache operations.
    
    :param logger: An instance of the Logger class for handling logging
    :type logger:
    :param host: The hostname or IP address of the Redis server
    :type host:
    :param port: The port number of the Redis server
    :type port: 
    :param db: The Redis database number
    :param decode_responses: A boolean indicating whether to decode Redis responses
    '''
    
    def __init__(
        self,
        logger: Logger,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        decode_responses: bool = True
    ):
        
        #memorizza l'host, la porta, il numero del database Redis e crea un oggetto Redis
        #per la connessione al cache
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
        '''
        Checks if the cache is connected by pinging the Redis server
        
        :return: True if the cache is connected.
        '''
        return self._cache.ping()

    def check_connected(self):
        '''
        Checks if the cache is connected
        '''
        if not self.is_connected():
            raise CacheNotConnectedException(
                self._logger,
                f'Cache is not connected at {self._host}:{self._port} with db {self._db}'
            )

    def write(self, key, value, is_dict=False):
        '''
        Writes a key-value pair to the cache
        
        :param key: The key to store the value.
        :type key
        :param value: The value to be stored.
        :type value:
        :param is_dict: A boolean indicating whether the value is a dictionary. 
        :type is_dict:
        '''
        self.check_connected()
        if is_dict:
            self._cache.hmset(key, value)
        else:
            self._cache.set(key, value)

    def read(self, key, is_dict=False):
        '''
        Reads the value associated with a key from the cache.

        :param key: The key to retrieve the value.
        :type key:
        :param is_dict: A boolean indicating whether the value is a dictionary. 
        :type is_dict:
        :return: the value associated with the key.
        '''
        self.check_connected()
        if is_dict:
            return self._cache.hgetall(key)
        return self._cache.get(key)

    def write_multiple(self, keys, values, is_dict=False):
        '''
        Writes multiple key-value pairs to the cache using a pipeline.

        :param keys: An iterable of keys.
        :type keys:
        :param values: An iterable of corresponding values.
        :type values:
        :param is_dict: A boolean indicating whether the values are dictionaries. 
        :type is_dict:
        '''
        self.check_connected()
        with self._cache.pipeline() as pipe:
            for key, value in zip(keys, values):
                if is_dict:
                    pipe.hmset(key, value)
                else:
                    pipe.set(key, value)
            pipe.execute()

    def key_exists(self, key: str) -> bool:
        '''
        Checks if a key exists in the cache.

        :param key: The key to check.
        :type key:
        :return: True if the key exists, otherwise False.
        '''
        self.check_connected()
        return self._cache.exists(key) > 0

    @staticmethod
    def from_conf(name, conf_cache, conf_log, db):
        '''
        A static method for creating a Cache object from configuration parameters.

        :param name: The name of the cache instance.
        :type name: str
        :param conf_cache: A configuration dictionary containing cache-related parameters (e.g., host, port).
        :type conf_cache:
        :param conf_log: A configuration dictionary specifying the directory and file names for logging.
        :type conf_log:
        :param db: The Redis database number.
        :type db:
        :return: a new Cache object initialized with the provided configurations.
        '''
        logger = Logger.from_conf(name, conf_log)
        return Cache(
            logger=logger,
            host=conf_cache.host,
            port=conf_cache.port,
            db=db
        )
