"""
NB: flink requires all code in one single file!
"""
from __future__ import annotations
import json
from enum import Enum
from omegaconf import OmegaConf
from pyflink.datastream import StreamExecutionEnvironment, OutputTag
from pyflink.datastream.functions import ProcessFunction, MapFunction
from pyflink.datastream.connectors.cassandra import CassandraSink
from pyflink.common.typeinfo import Types
from pyflink.common.types import Row
from app.infrastructure import Database, DatabaseTables, Cache, ConsumerFlink
from app.model import Account, Transaction
from app.pipeline import Parser, SFDToTarget, SourceTypes, FraudDetection


def main(conf, cache_conf_args, db_conf_args):
    procs = conf.flink.parser.parallelism
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
        sink = Database.from_conf(**db_conf_args)
        #
        consumer = source.get_consumer()
        #
        parser = Parser(
            source = pconf.source.name,
            target = pconf.target.name,
            source_parser_file_path = pconf.source.file,
            target_parser_file_path = pconf.target.file
        )
        # 1. Create Streaming
        env = StreamExecutionEnvironment\
            .get_execution_environment()\
            .set_parallelism(procs)
        # 2. Add Kafka Source
        ds = env.add_source(consumer)
        # 3. Parse input to target (db) output
        ds = ds.map(parser.parse(cache_conf_args),
                    parser._target_types)
        # 4. Split stream in two:
        # - main: fraud detection + transaction insert
        # - side: account balance update
        # NOTE: flink needs types for tags to be defined here
        #       i.e., do not import them from external libs
        tag = OutputTag("side", Types.ROW_NAMED(["balance", "account_id"],
                                                [Types.DOUBLE(), Types.STRING()]))

        class StreamSplitter(ProcessFunction):
            def process_element(self, value, ctx: 'ProcessFunction.Context'):
                # Main -> Fraud detection
                yield value
                # Side -> Account balance update
                yield tag, Row(
                    balance = value["balance_after"],
                    account_id = value['account_id']
                )

        main = ds.process(StreamSplitter(), parser._target_types)
        side = main.get_side_output(tag)
        # Main -> Fraud detection
        main = main.map(lambda x: FraudDetection.update_record(x), parser._target_types)
        # Main -> save transaction
        ## AUTH IS (apparently) NOT IMPLEMENTED!
        CassandraSink.add_sink(main) \
            .set_query(sink.get_insert_query(
                DatabaseTables.TRANSACTIONS,
                parser.query.keys(),
                parser.query.values()
            )) \
            .set_host(sink.get_host(), sink.get_port()) \
            .build()
        # Side -> Account balance update
        CassandraSink.add_sink(side) \
            .set_query(sink.get_update_query(
                DatabaseTables.ACCOUNTS,
                "account_id", "?",
                "balance", "?")) \
            .set_host(sink.get_host(), sink.get_port()) \
            .build()
        # Execute environment
        env.execute(f"Parser {pconf.source.name} -> {pconf.target.name} + AD + Account balance update")

if __name__ == '__main__':
    conf = OmegaConf.load("config.yaml")
    cache_conf_args = {
        "name": "parser-cache",
        "conf_cache": conf.redis,
        "conf_log": conf.logs,
        "db" : conf.redis.accounts.db
    }
    db_conf_args = {
        "name": "parser-cassandra",
        "conf_db": conf.cassandra,
        "conf_log": conf.logs
    }
    cache = Cache.from_conf(**cache_conf_args)
    db = Database.from_conf(**db_conf_args)
    Account.cassandra_to_cache(cache, db)
    # Account.csv_to_cache(cache, conf.redis.accounts.file)
    main(conf, cache_conf_args, db_conf_args)
