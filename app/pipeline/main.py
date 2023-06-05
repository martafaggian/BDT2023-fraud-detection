"""
NB: flink requires all code in one single file!
"""
from __future__ import annotations
import json
from enum import Enum
import pandas as pd
from omegaconf import OmegaConf
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.cassandra import CassandraSink
from pyflink.common.typeinfo import Types
from pyflink.common.types import Row
from app.infrastructure import Database, DatabaseTables, Cache, ConsumerFlink
from app.model import Account, Transaction

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
            self.parse = self.from_sfd_to_target
            query = Transaction.get_query_dict()
            query.update({
                'transaction_id' : 'uuid()',
                '"timestamp"' : 'toTimestamp(now())'
            })
            self.set_query(query)
        else:
            raise NotImplementedError(f"Parser from {self._source} to {self._target} not implemented")

    def get_query(self):
        return self.query

    def set_query(self, query):
        self.query = query

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

    @staticmethod
    def from_sfd_to_target(record, cache_conf_args):
        # Declaration must be internal due to Flink contraints!
        cache = Cache.from_conf(**cache_conf_args)
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
        output = Row(
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
            fraud_confidence = None
        )
        return output

class FraudDetection:
    @staticmethod
    def compute_fraud(record):
        # Fraud detection :)
        # Pyflink ML should be easy to integrate:
        # https://nightlies.apache.org/flink/flink-ml-docs-master/docs/try-flink-ml/python/quick-start/
        if record["amount"] > 5000:
            is_fraud = 1
            fraud_conf = 1.0
        else:
            is_fraud = 0
            fraud_conf = 0.0
        return is_fraud, fraud_conf

    @staticmethod
    def update_record(record):
        is_fraud, fraud_conf = FraudDetection.compute_fraud(record)
        record["is_fraud"] = is_fraud
        record["fraud_confidence"] = fraud_conf
        return record

def main(conf, cache_conf_args):
    for pconf in conf.parsers:
        #
        source = ConsumerFlink.from_conf(
            name=f"flink-{pconf.source.name}",
            conf_broker=conf.kafka,
            conf_log=conf.logs,
            conf_parser=pconf,
            types = Parser.get_types(pconf.source.file)
        )
        #
        sink = Database.from_conf(
            name=f"cassandra-{pconf.target.name}",
            conf_db = conf.cassandra,
            conf_log = conf.logs
        )
        #
        consumer = source.get_consumer()
        #
        parser = Parser(
            source = pconf.source.name,
            target = pconf.target.name,
            source_parser_file_path = pconf.source.file,
            target_parser_file_path = pconf.target.file
        )
        #
        env = StreamExecutionEnvironment.get_execution_environment()
        ds = env.add_source(consumer)
        ds = ds.map(lambda x: parser.parse(x, cache_conf_args),
                    parser._target_types)
        ds = ds.map(lambda x: FraudDetection.update_record(x),
                    parser._target_types)
        ds = ds.set_parallelism(3)
        # AUTH IS (apparently) NOT IMPLEMENTED!
        #TODO: add account update query
        insert = sink.get_insert_query(
            DatabaseTables.TRANSACTIONS,
            parser.query.keys(),
            parser.query.values()
        )
        CassandraSink.add_sink(ds). \
            set_query(insert). \
            set_host(sink.get_host(), sink.get_port()). \
            build()
        env.execute(f"Parser {pconf.source.name} -> {pconf.target.name} + AD")

if __name__ == '__main__':
    conf = OmegaConf.load("config.yaml")
    cache_conf_args = {
        "name": "parser-cache",
        "conf_cache": conf.redis,
        "conf_log": conf.logs,
        "db" : conf.redis.accounts.db
    }
    cache = Cache.from_conf(**cache_conf_args)
    Account.csv_to_cache(cache, conf.redis.accounts.file)
    main(conf, cache_conf_args)
