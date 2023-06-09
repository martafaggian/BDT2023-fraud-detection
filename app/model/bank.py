'''
The purpose of this code is to define a data class Bank that represents a bank entity and provides
methods for converting the bank object to a dictionary or JSON string, submitting the object
to a broker, and obtaining a query dictionary template for inserting bank data.
It encapsulates the logic and functionality related to working with bank objects, making it
easier to create, manipulate, and interact with bank data in a structured manner.

The module can be used as follows:

bank = Bank(name="Example Bank", address="123 Main Street", phone="555-1234")
print(bank.name)
print(bank.address)
print(bank.phone)

bank_dict = bank.to_dict()
print(bank_dict)

broker = Broker()
topic = "bank_data"
bank.submit(broker, topic)
'''

import json
from dataclasses import dataclass

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
        :return: The bank object as a dictionary.
        :rtype: dict
        '''
        return {
            'name': self.name,
            'address': self.address,
            'phone': self.phone
        }

    def to_json(self):
        '''
        Converts the bank object to a JSON string.

        :return: The bank object as a JSON string.
        :rtype: str
        '''
        return json.dumps(self.to_dict())

    def submit(self, broker, topic):
        '''
        Submits the bank object to the specified broker.

        :param broker: The broker to submit the data to.
        :type broker: Broker
        :param topic: The topic to which the data should be submitted.
        :type topic: str
        '''
        # broker.send(self.to_json(), topic)
        broker.send(self.to_dict(), topic)

    def __str__(self):
        '''
        :return: The string representation of the bank object.
        :rtype: str
        '''
        return f"Bank(name={self.name}, address={self.address}, phone={self.phone})"

    @staticmethod
    def get_query_dict(auto_id = True):
        '''
        Returns a query dictionary representing a template for retrieving bank data.

        :param auto_id: A flag indicating whether to use auto-generated bank IDs or placeholders.
        :type auto_id: bool
        :return: The query dictionary representing the template.
        :rtype: dict
        '''
        bnk_id = "CAST(uuid() AS TEXT)" if auto_id else "?"
        return {
            'bank_id': bnk_id,
            'name': '?',
            'address': '?',
            'phone': '?'
        }
