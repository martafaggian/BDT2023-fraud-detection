'''
The Transaction class is a data class representing a transaction. 
It has various attributes representing different properties of a transaction. 

    :param transaction_id: The ID of the transaction.
    :type transaction_id: str
    :param timestamp: The timestamp of the transaction.
    :type timestamp: datetime
    :param user_id: The ID of the user associated with the transaction.
    :type user_id: str
    :param account_id: The ID of the account associated with the transaction.
    :type account_id: str
    :param bank_id: The ID of the bank associated with the transaction.
    :type bank_id: str
    :param balance_before: The balance before the transaction.
    :type balance_before: float
    :param balance_after: The balance after the transaction.
    :type balance_after: float
    :param account_type: The type of the account.
    :type account_type: str
    :param counterparty_account_id: The ID of the counterparty account.
    :type counterparty_account_id: str
    :param counterparty_isinternal: Indicates if the counterparty is internal or external.
    :type counterparty_isinternal: status: boo
    :param counterparty_type: The type of the counterparty
    :type counterparty_type: str
    :param counterparty_name: The name of the counterparty.
    :type counterparty_name: str
    :param amount: The amount of the transaction.
    :type amount: float
    :param direction: The direction of the transaction (inbound or outbound).
    :type direction: str
    :param status: The status of the transaction.
    :type status: str
    :param source_location: The source location of the transaction.
    :type source_location: str
    :param is_fraud: Indicates if the transaction is a fraud.
    :type is_fraud: bool
    :param fraud_confidence: The confidence level of the fraud detection.
    :type fraud_confidence: float
'''
from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
import json

@dataclass
class Transaction:
    '''
    Data class representing a transaction.
    '''
    @staticmethod
    def get_query_dict(auto_id = True):
        '''
         Get a dictionary representation of the transaction attributes for database queries.
         
         :param auto_id: Indicates if the transaction ID should be automatically generated
         :type auto_id: bool
         :return: The dictionary representing the transaction attributes for database queries.
        '''
        trs_id = "CAST(uuid() AS TEXT)" if auto_id else "?"
        return {
            'transaction_id' : trs_id,
            '"timestamp"' : '?',
            'user_id' : '?',
            'account_id' : '?',
            'bank_id' : '?',
            'balance_before' : '?',
            'balance_after' : '?',
            'account_type' : '?',
            'counterparty_account_id' : '?',
            'counterparty_isinternal' : '?',
            'counterparty_type' : '?',
            'counterparty_name' : '?',
            'amount' : '?',
            'direction' : '?',
            'status' : '?',
            'source_location' : '?',
            'is_fraud' : '?',
            'fraud_confidence' : '?',
        }

# TODO: model only if necessary to insert transactions by hand
# class TransactionStatus(IntEnum):
    # PENDING = 0
    # COMPLETED = 1
    # FAILED = 2
    # CANCELED = 3

# class TransactionDirection(IntEnum):
    # INBOUND = 0
    # OUTBOUND = 1

    # transaction_id: str = None
    # user_ID: str
    # account_ID: str
    # direction: TransactionDirection = None
    # amount: float = None
    # _currency: str = None
    # source_balance_before: float = None
    # source_balance_after: float = None
    # destination_balance_before: float = None
    # destination_balance_after: float = None
    # timestamp: str = None
    # ip_lat: float = None
    # ip_lon: float = None
    # _ip_address: str = None
    # _ip_location: str = None
    # status: TransactionStatus = None

    # def set_ip_location(self):
        # # detect ip address location give address
        # # TODO: write
        # pass

    # def location_to_coords(self):
        # # TODO: write
        # # better have numerical data for models!
        # pass

    # def convert_to_usd(self):
        # # TODO: write
        # # better standardize currencies!
        # self._currency = 'usd'
        # pass

    # def to_dict(self):
        # return {
            # 'ID': self.ID,
            # 'timestamp': self.timestamp,
            # # '_ip_address': self._ip_address,
            # # '_ip_location': self._ip_location,
            # 'ip_lat': self.ip_lat,
            # 'ip_lon': self.ip_lon,
            # 'direction': self.direction.name,
            # 'user_ID': self.user_ID,
            # 'source_ID': self.source_ID,
            # 'destination_ID': self.destination_ID,
            # 'amount': self.amount,
            # # '_currency': self._currency,
            # 'source_balance_before': self.source_balance_before,
            # 'source_balance_after': self.source_balance_after,
            # 'destination_balance_before': self.destination_balance_before,
            # 'destination_balance_after': self.destination_balance_after,
            # 'status': self.status.name
        # }

    # def to_json(self):
        # return json.dumps(self.to_dict())
