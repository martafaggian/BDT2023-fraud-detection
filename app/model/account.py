import json
from dataclasses import dataclass
import pandas as pd

@dataclass
class Account:
    account_id: str
    user_id: str
    bank_id: str
    account_type: str = None
    balance: float = None

    def to_dict(self):
        return {
            'account_id': self.account_id,
            'user_id': self.user_id,
            'bank_id': self.bank_id,
            'type': self.account_type,
            'balance': self.balance
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    def to_cache(self, cache, keyprefix=""):
        value = self.to_dict()
        value.pop('balance')
        key = f"{keyprefix}{value.pop('account_id')}"
        cache.write(key, value, is_dict=True)

    @staticmethod
    def csv_to_cache(cache, file):
        df = pd.read_csv(file)
        keys = df.pop("account_id")
        values = df[["bank_id", "user_id", "type"]].to_dict(orient="records")
        cache.write_multiple(keys, values, is_dict=True)
