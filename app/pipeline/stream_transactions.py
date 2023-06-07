from __future__ import annotations
from omegaconf import OmegaConf
from pyflink.datastream import StreamExecutionEnvironment, OutputTag
from pyflink.datastream.functions import ProcessFunction
from pyflink.datastream.connectors.cassandra import CassandraSink
from pyflink.common.typeinfo import Types
from pyflink.common.types import Row
from app.infrastructure import Database, DatabaseTables, Cache, ConsumerFlink
from app.model import Account
from app.pipeline import Parser, FraudDetection

class StreamSplitter(ProcessFunction):
    def __init__(self, tag):
        super().__init__()
        self._tag = tag

    def process_element(self, value, ctx: 'ProcessFunction.Context'):
        # Main -> Fraud detection
        yield value
        # Side -> Account balance update
        yield self._tag, Row(
            balance = value["balance_after"],
            account_id = value['account_id']
        )

class StreamTransactions:
    def __init__(
        self,
        conf,
        cache_conf_args,
        db_conf_args
    ):
        self.conf = conf
        self.cache_conf_args = cache_conf_args
        self.db_conf_args = db_conf_args

    def execute_env(self, pconf, procs=2):
        source = ConsumerFlink.from_conf(
            name=f"flink-{pconf.source.name}",
            conf_broker=self.conf.kafka,
            conf_log=self.conf.logs,
            conf_parser=pconf,
            types = Parser.get_types(pconf.source.file)
        )
        #
        sink = Database.from_conf(**self.db_conf_args)
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
        ds = ds.map(parser.parse(self.cache_conf_args), parser.get_target_types())
        # 4. Split stream in two:
        # - main: fraud detection + transaction insert
        # - side: account balance update
        # NOTE: flink needs types for tags to be defined here
        #       i.e., do not import them from external libs
        tag = OutputTag("side", Types.ROW_NAMED(["balance", "account_id"],
                                                [Types.DOUBLE(), Types.STRING()]))
        smain = ds.process(StreamSplitter(tag), parser.get_target_types())
        side = smain.get_side_output(tag)
        # 5.1 Main -> Fraud detection
        smain = smain.map(FraudDetection(), parser.get_target_types())
        # 5.2 Main -> save transaction
        ## AUTH IS (apparently) NOT IMPLEMENTED!
        CassandraSink.add_sink(smain) \
            .set_query(sink.get_insert_query(
                DatabaseTables.TRANSACTIONS,
                parser.query.keys(),
                parser.query.values()
            )) \
            .set_host(sink.get_host(), sink.get_port()) \
            .build()
        # 6.1 Side -> Account balance update
        CassandraSink.add_sink(side) \
            .set_query(sink.get_update_query(
                DatabaseTables.ACCOUNTS,
                "account_id", "?",
                "balance", "?")) \
            .set_host(sink.get_host(), sink.get_port()) \
            .build()
        # 7. Execute environment
        env.execute(f"Parser {pconf.source.name} -> {pconf.target.name} + AD + Account balance update")

    def submit_all(self):
        procs = self.conf.flink.parser.parallelism
        for pconf in self.conf.parsers:
            self.execute_env(pconf, procs)
