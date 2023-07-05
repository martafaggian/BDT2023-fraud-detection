'''
This module defines a data class Account that represents an account and provides methods for
data conversion and caching. The to_dict() method converts the Account object to a dictionary,
to_json() converts it to a JSON string, and to_cache() writes the account data to a cache
object using a specified key. The csv_to_cache() method reads CSV data from a file, extracts
the required columns, and writes the data to the cache using the 'account_id' column as the key.

The module can be used as follows:
account = Account(account_id='123', user_id='456', bank_id='789', account_type='savings', balance=1000.0)

account_dict = account.to_dict()

account_json = account.to_json()

cache = Cache()  # Initialize your cache object
account.to_cache(cache)

Account.csv_to_cache(cache, file='accounts.csv')
'''
import json
from dataclasses import dataclass
import pandas as pd
from app.infrastructure import DatabaseTables

@dataclass
class Account:
    '''
    Represents an account with associated attributes.
    '''
    user_id: str
    bank_id: str
    account_type: str = None
    balance: float = None

    def to_dict(self):
        '''
        Convert an account object to a dictionary
        '''
        return {
            'user_id': self.user_id,
            'bank_id': self.bank_id,
            'type': self.account_type,
            'balance': self.balance
        }

    def to_json(self):
        '''
        Converts the Account object to a JSON string.
        '''
        return json.dumps(self.to_dict())

    def to_cache(self, cache, keyprefix=""):
        '''
        Writes the account object to a cache with the specified key.

        :param cache: The cache object to write the data to
        :type cache: Cache
        :param keyprefix: Prefix to prepend to the key
        :type keyprefix: str
        '''
        value = self.to_dict()
        value.pop('balance')
        key = f"{keyprefix}{value.pop('account_id')}"
        cache.write(key, value, is_dict=True)

    def submit(self, broker, topic):
        '''
        Submits the account object to the specified broker.

        :param broker: The broker to submit the data to
        :type broker: 
        '''
        # broker.send(self.to_json(), topic)
        broker.send(self.to_dict(), topic)

    def __str__(self):
        return f"Account(user_id={self.user_id}, bank_id={self.bank_id}, account_type={self.account_type}, balance={self.balance})"

    @staticmethod
    def csv_to_cache(cache, file):
        '''
        Converts CSV data to cache entries.

        Reads the CSV file, extracts the necessary columns, and writes the data
        to the cache using the 'account_id' column as the key.

        :param cache: The cache object to write the data to
        :type cache: cache object
        :param file: The path to the CSV file
        :type file: str

        '''
        df = pd.read_csv(file)
        keys = df.pop("account_id")
        values = df[["bank_id", "user_id", "type"]].to_dict(orient="records")
        cache.write_multiple(keys, values, is_dict=True)

    @staticmethod
    def cassandra_to_cache(cache, db):
        '''
        Transfers account data from a Cassandra database to a cache.
        
        :param cache: The cache instance used for storing account data.
        :type cache: Cache
        :param db: The Cassandra database instance.
        :type db: Database
        '''
        res = db.execute(f"SELECT account_id, bank_id, user_id, type FROM {DatabaseTables.ACCOUNTS}")
        df = pd.DataFrame(res)
        if len(df) > 0:
            keys = df.pop("account_id")
            values = df.to_dict(orient="records")
            cache.write_multiple(keys, values, is_dict=True)

    @staticmethod
    def get_query_dict(auto_id = True):
        '''
        Returns a query dictionary representing a template for inserting account data.

        :param auto_id: A flag indicating whether to use auto-generated account IDs or placeholders.
        :type auto_id: bool
        :return: The query dictionary representing the template.
        :rtype: dict
        '''
        acc_id = "CAST(uuid() AS TEXT)" if auto_id else "?"
        return {
            'account_id' : acc_id,
            'bank_id' : '?',
            'user_id' : '?',
            'type' : '?',
            'balance' : '?'
        }
