import json
from dataclasses import dataclass
import pandas as pd
from datetime import datetime
from app.infrastructure import DatabaseTables

@dataclass
class Bank:
    '''
    Represents a bank with associated attributes.
    '''
    name: str
    address: str
    phone: str

    def to_dict(self):
        '''
        Convert a bank object to a dictionary
        '''
        return {
            'name': self.name,
            'address': self.address,
            'phone': self.phone
        }

    def to_json(self):
        '''
        Converts the bank object to a JSON string.
        '''
        return json.dumps(self.to_dict())

    def submit(self, broker, topic):
        '''
        Submits the bank object to the specified broker.

        :param broker: The broker to submit the data to
        :type broker:
        '''
        # broker.send(self.to_json(), topic)
        broker.send(self.to_dict(), topic)

    def __str__(self):
        return f"Bank(name={self.name}, address={self.address}, phone={self.phone})"

    @staticmethod
    def get_query_dict(auto_id = True):
        bnk_id = "CAST(uuid() AS TEXT)" if auto_id else "?"
        return {
            'bank_id': bnk_id,
            'name': '?',
            'address': '?',
            'phone': '?'
        }
