
from __future__ import annotations
import json
from enum import Enum
from pyflink.datastream.functions import MapFunction
from pyflink.common.typeinfo import Types
from pyflink.common.types import Row
from app.infrastructure import Cache
from app.model import Transaction


class SourceTypes(str, Enum):
    SYNTHETIC_FINANCIAL_DATASETS = "synthetic_financial_datasets"
    TARGET = "target"


class Parser:
    def __init__(
        self,
        source: str,
        target: str,
        source_parser_file_path: str,
        target_parser_file_path: str,
    ):
        self._source_types = self.get_types(source_parser_file_path)
        self._target_types = self.get_types(target_parser_file_path)
        self._source = source
        self._target = target
        self._source = source
        self.query = None

        if self._source == SourceTypes.SYNTHETIC_FINANCIAL_DATASETS and self._target == SourceTypes.TARGET:
            self.parse = SFDToTarget
            self.set_query(SFDToTarget.get_query())
        else:
            raise NotImplementedError(f"Parser from {self._source} to {self._target} not implemented")

    def get_query(self):
        return self.query

    def set_query(self, query):
        self.query = query

    def get_target_types(self):
        return self._target_types

    def get_source_types(self):
        return self._source_types

    @classmethod
    def get_types(cls, file: str):
        with open(file) as f:
            types = json.load(f)
        converted = {}
        for k,v in types.items():
            converted[k] = cls.convert_types(v)
        return Types.ROW_NAMED(
            list(converted.keys()),
            list(converted.values())
        )

    @classmethod
    def convert_types(cls, type_str: str) -> Types:
        type_str = type_str.lower().strip()
        if type_str in ["string", "text"]:
            return Types.STRING()
        elif type_str in ["double"]:
            return Types.DOUBLE()
        elif type_str in ["boolean", "bool"]:
            return Types.BOOLEAN()
        elif type_str in ["int", "integer"]:
            return Types.INT()
        elif type_str in ["float"]:
            return Types.FLOAT()
        elif type_str in ["floattuple"]:
            return Types.TUPLE([Types.FLOAT(), Types.FLOAT()])
        else:
            raise Exception(f"Unknown type {type_str}")


class SFDToTarget(MapFunction):
    def __init__(self, cache_conf_args):
        super().__init__()
        self._cache_conf_args = cache_conf_args

    def map(self, record):
        # Declaration must be internal due to Flink contraints!
        cache = Cache.from_conf(**self._cache_conf_args)
        #
        account = cache.read(record["nameOrig"], is_dict=True)
        counterparty_id = record["nameDest"]
        counterparty_type = None
        counterparty_isinternal = False
        if cache.key_exists(counterparty_id):
            counterparty = cache.read(record["nameDest"], is_dict=True)
            counterparty_id = counterparty["user_id"]
            counterparty_type = counterparty["type"]
            counterparty_isinternal = True
        #
        if float(record["oldbalanceOrg"]) > float(record["newbalanceOrig"]):
            direction = "inbound"
        else:
            direction = "outbound"
        #
        return Row(
            user_id = account["user_id"],
            account_id = record["nameOrig"],
            bank_id = account["bank_id"],
            balance_before = record["oldbalanceOrg"],
            balance_after = record["newbalanceOrig"],
            account_type = account["type"],
            counterparty_account_id = counterparty_id,
            counterparty_isinternal = counterparty_isinternal,
            counterparty_type = counterparty_type,
            counterparty_name = None,
            amount = record["amount"],
            direction = direction,
            status = "confirmed",
            source_location = None,
            is_fraud = None,
            fraud_confidence = None)

    @staticmethod
    def get_query():
        query = Transaction.get_query_dict()
        query.update({
            'transaction_id' : 'CAST(uuid() AS TEXT)',
            '"timestamp"' : 'toTimestamp(now())'
        })
        return query
