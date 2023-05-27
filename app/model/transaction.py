from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
import json

class TransactionStatus(IntEnum):
    PENDING = 0
    COMPLETED = 1
    FAILED = 2
    CANCELED = 3

class TransactionDirection(IntEnum):
    INBOUND = 0
    OUTBOUND = 1

@dataclass
class Transaction:
    # ID: str # Autoincremental in cassandra
    timestamp: datetime
    _ip_address: str
    _ip_location: str
    ip_lat: float
    ip_lon: float
    direction: TransactionDirection
    user_ID: str # could have been put into source object, but esistono conti cointestati
    source_ID: str
    destination_ID: str
    amount: float
    _currency: str
    source_balance_before: float
    source_balance_after: float
    destination_balance_before: float
    destination_balance_after: float
    status: TransactionStatus

    def set_ip_location(self):
        # detect ip address location give address
        # TODO: write
        pass

    def location_to_coords(self):
        # TODO: write
        # better have numerical data for models!
        pass

    def convert_to_usd(self):
        # TODO: write
        # better standardize currencies!
        self._currency = 'usd'
        pass

    def to_dict(self):
        return {
            'ID': self.ID,
            'timestamp': self.timestamp,
            # '_ip_address': self._ip_address,
            # '_ip_location': self._ip_location,
            'ip_lat': self.ip_lat,
            'ip_lon': self.ip_lon,
            'direction': self.direction.name,
            'user_ID': self.user_ID,
            'source_ID': self.source_ID,
            'destination_ID': self.destination_ID,
            'amount': self.amount,
            # '_currency': self._currency,
            'source_balance_before': self.source_balance_before,
            'source_balance_after': self.source_balance_after,
            'destination_balance_before': self.destination_balance_before,
            'destination_balance_after': self.destination_balance_after,
            'status': self.status.name
        }

    def to_json(self):
        return json.dumps(self.to_dict())
