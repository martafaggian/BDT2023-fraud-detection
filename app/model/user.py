import json
from dataclasses import dataclass
import pandas as pd
from datetime import datetime
from app.infrastructure import DatabaseTables

@dataclass
class User:
    '''
    Represents an account with associated attributes.
    '''
    email: str
    name: str
    ssn: str
    registration_date: datetime = None
    birthdate: datetime = None

    def to_dict(self):
        '''
        Convert an account object to a dictionary
        '''
        return {
            'email': self.email,
            'name': self.name,
            'ssn': self.ssn,
            'registration_date': self.registration_date,
            'birthdate': self.birthdate
        }

    def to_json(self):
        '''
        Converts the Account object to a JSON string.
        '''
        return json.dumps(self.to_dict())

    def submit(self, broker, topic):
        '''
        Submits the account object to the specified broker.

        :param broker: The broker to submit the data to
        :type broker:
        '''
        # broker.send(self.to_json(), topic)
        msg = self.to_dict()
        msg.update({
            'registration_date': self.registration_date.strftime('%Y-%m-%d'),
            'birthdate': self.birthdate.strftime('%Y-%m-%d')
        })
        broker.send(msg, topic)

    @staticmethod
    def get_query_dict(auto_id = True):
        usr_id = "CAST(uuid() AS TEXT)" if auto_id else "?"
        return {
            'user_id': usr_id,
            'ssn': '?',
            'registration_date': '?',
            'name': '?',
            'email': '?',
            'birthdate': '?',
        }
