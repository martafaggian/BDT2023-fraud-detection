import json
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    '''
    Represents an user with associated attributes.
    '''
    email: str
    name: str
    ssn: str
    registration_date: datetime = None
    birthdate: datetime = None

    def to_dict(self):
        '''
        Convert an user object to a dictionary
        
        :return: The user object as a dictionary.
        :rtype: dict
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
        Converts the user object to a JSON string.
        
        :return: The user object as a JSON string.
        :rtype: str
        '''
        return json.dumps(self.to_dict())

    def submit(self, broker, topic):
        '''
        Submits the user object to the specified broker.

        :param broker: The broker to submit the data to.
        :type broker: Broker
        :param topic: The topic to which the data should be submitted.
        :type topic: str
        '''
        # broker.send(self.to_json(), topic)
        msg = self.to_dict()
        msg.update({
            'registration_date': self.registration_date.strftime('%Y-%m-%d'),
            'birthdate': self.birthdate.strftime('%Y-%m-%d')
        })
        broker.send(msg, topic)

    def __str__(self):
        return f"User(email={self.email}, name={self.name}, ssn={self.ssn}, registration_date={self.registration_date}, birthdate={self.birthdate})"

    @staticmethod
    def get_query_dict(auto_id = True):
        '''
        Get the query dictionary for creating a user.
        
        :param auto_id: Flag indicating whether to generate an auto ID for the user (optional).
        :type auto_id: bool, optional
        :return: The query dictionary for creating a user.
        :rtype: dict
        '''
        usr_id = "CAST(uuid() AS TEXT)" if auto_id else "?"
        return {
            'user_id': usr_id,
            'ssn': '?',
            'registration_date': '?',
            'name': '?',
            'email': '?',
            'birthdate': '?',
        }
