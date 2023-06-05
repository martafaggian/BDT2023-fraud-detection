from app.utils import Logger
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

class DatabaseNotConnectedException(Exception):
    def __init__(self, logger, message, *args):
        super().__init__(message)
        self.args = args
        logger.error(message)

class Database:
    def __init__(
        self,
        logger: Logger,
        host: str = 'localhost',
        port: int = 9042,
        keyspace: str = None,
        username: str = None,
        password: str = None
    ):
        self._host = host
        self._port = port
        self._logger = logger
        self._auth = None
        self._keyspace = keyspace
        if username is not None and password is not None:
            self._auth = PlainTextAuthProvider(username, password)
        self._cluster = Cluster([self._host], port=self._port, auth_provider=self._auth)
        self._session = self._cluster.connect()
        self.check_connected()
        if self._keyspace is not None:
            self._session.set_keyspace(self._keyspace)

    def get_host(self):
        return self._host

    def get_port(self):
        return self._port

    def get_keyspace(self):
        return self._keyspace

    def set_keyspace(self, keyspace):
        self._keyspace = keyspace
        self._session.set_keyspace(keyspace)

    def execute(self, query):
        return self._session.execute(query)

    def is_connected(self):
        return self._session.is_connected()

    def check_connected(self):
        try:
            self.execute('SELECT * FROM system.local')
        except Exception as e:
            raise DatabaseNotConnectedException(
                self._logger, f'Database is not connected at {self._host}:{self._port}'
            ) from e

    @staticmethod
    def from_conf(name, conf_db, conf_log):
        logger = Logger.from_conf(name, conf_log)
        return Database(
            logger=logger,
            host=conf_db.host,
            port=conf_db.port,
            keyspace=conf_db.keyspace,
            username=conf_db.username,
            password=conf_db.password
        )
