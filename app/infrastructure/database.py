'''
The module provides a database abstraction layer for connecting to and interacting with a
Cassandra database. It includes a Database class that allows you to establish a connection,
execute queries, and manage the keyspace. The module also defines an enum class DatabaseTables
for referencing table names and an exception class DatabaseNotConnectedException for handling
connection-related errors. It relies on the Logger class from the app.utils module for logging.
Overall, this module simplifies Cassandra database operations by providing a convenient and
configurable interface.

The module can be used as follow:
logger = Logger()

host = 'localhost'
port = 9042
keyspace = 'my_keyspace'
username = 'my_username'
password = 'my_password'

database = Database(logger=logger, host=host, port=port, keyspace=keyspace, username=username, password=password)

if database.is_connected():
    print("Database is connected!")
else:
    print("Database is not connected!")

new_keyspace = 'new_keyspace'
database.set_keyspace(new_keyspace)
print(f"Keyspace set to: {database.get_keyspace()}")

query = "SELECT * FROM my_table"
result = database.execute(query)
for row in result:
    print(row)

table_name = DatabaseTables.ACCOUNTS
keys = ['id', 'name', 'balance']
values = ['id_val', 'name_val', 'balance_val']
insert_query = database.get_insert_query(table_name, keys, values)
print(f"Insert query: {insert_query}")
'''

from __future__ import annotations
from enum import Enum
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from app.utils import Logger

class DatabaseTables(str, Enum):
    ACCOUNTS = 'accounts'
    TRANSACTIONS = 'transactions'
    BANKS = 'banks'
    USERS = 'users'

class DatabaseNotConnectedException(Exception):
    def __init__(self, logger, message, *args):
        super().__init__(message)
        self.args = args
        logger.error(message)

class Database:
    '''
    Initialize a Database instance.

    :param logger: The logger instance used for logging.
    :type logger: Logger
    :param host: The hostname or IP address of the database server.
    :type host: str
    :param port: The port number of the database server.
    :type port: int
    :param keyspace: The name of the keyspace to use.
    :type keyspace: str
    :param username: The username for authentication.
    :type username: str
    :param password: The password for authentication.
    :type password: str
    '''
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
        '''
        Returns the hostname or IP address of the database server.
        '''
        return self._host

    def get_port(self):
        '''
        Returns the port number of the database server.
        '''
        return self._port

    def get_keyspace(self):
        '''
        Returns the name of the keyspace being used.
        '''
        return self._keyspace

    def set_keyspace(self, keyspace):
        '''
        Set the keyspace to use

        :param keyspace: name of the keyspace
        :type keyspace: str
        '''
        self._keyspace = keyspace
        self._session.set_keyspace(keyspace)

    def execute(self, query):
        '''
        Executes a CQL query on the database.
        :param query: The CQL query to execute
        :type query: str
        '''
        return self._session.execute(query)

    def is_connected(self):
        '''
        Checks if the database is connected

        :return: True if the database is connected.
        '''
        return self._session.is_connected()

    def check_connected(self):
        '''
        Checks if the database is connected and raises an exception if not.
        '''
        try:
            self.execute('SELECT * FROM system.local')
        except Exception as e:
            raise DatabaseNotConnectedException(
                self._logger, f'Database is not connected at {self._host}:{self._port}'
            ) from e

    def get_insert_query(
        self,
        table_name: DatabaseTables,
        keys: list,
        values: list) -> str:
        '''
        Generates an insert query for a specified table.

        :param table_name: The name of the table
        :type table_name: str
        :param keys: The list of column names
        :type keys: list
        :param values: The list of column values
        :type values: list
        :return: The insert query as a str
        '''
        return f"""
        INSERT INTO {self._keyspace}.{table_name}
        ({','.join(keys)})
        VALUES
        ({','.join(values)})
        """

    def get_update_query(
        self,
        table_name,
        id_key,
        id_value,
        key,
        value) -> str:
        '''
        Update the query for a specified table
        :param table_name: The name of the table
        :type table_name: str
        :param id_key:
        :type id_key: int
        :param id_value:
        :type id-value: int
        :param key: The list of column names
        :type key: list
        :param value:The list of column values
        :type value: list
        :return:

        '''
        return f"""
        UPDATE {self._keyspace}.{table_name}
        SET {key} = {value}
        WHERE {id_key} = {id_value}
        """

    @staticmethod
    def from_conf(name, conf_db, conf_log):
        '''
        Creates a Database instance from configuration settings.

        :param name: The name of the configuration
        :type name: str
        :param cond_db: The database configuration settings
        :type cond_db:
        :param conf_log: The logger configuration settings
        :type cond_db:
        :return: A Database instance
        '''
        logger = Logger.from_conf(name, conf_log)
        return Database(
            logger=logger,
            host=conf_db.host,
            port=conf_db.port,
            keyspace=conf_db.keyspace,
            username=conf_db.username,
            password=conf_db.password
        )
