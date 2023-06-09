'''
This code provides a streaming environment for processing transactions in real-time. It reads 
transactions from a Kafka topic, performs parsing and transformation using a Parser object, and 
splits the stream into two branches.
The main branch is processed for fraud detection, and the results are saved to a Cassandra database 
as transactions. The side branch is used to update account balances in the Cassandra database.
The code allows for parallel execution of the streaming process and integrates with Cassandra for 
storing transaction data and updating account balances.
'''

from __future__ import annotations
from pyflink.datastream import StreamExecutionEnvironment, OutputTag
from pyflink.datastream.functions import ProcessFunction
from pyflink.datastream.connectors.cassandra import CassandraSink
from pyflink.common.typeinfo import Types
from pyflink.common.types import Row
from app.infrastructure import Database, DatabaseTables, ConsumerFlink
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
        '''
        Initializes the StreamTransactions object with the provided configurations,
        cache connection arguments, and database connection arguments

        :param conf: Configuration object containing various settings for the streaming process.
        :param cache_conf_args: Cache connection arguments required to establish a connection to the cache.
        :param db_conf_args: Database connection arguments required to establish a connection to the database.
        '''
        self.conf = conf
        self.cache_conf_args = cache_conf_args
        self.db_conf_args = db_conf_args

    def execute_env(self, pconf, procs=2):
        '''
        Executes the streaming environment for a specific transaction processing configuration.

        :param pconf: Configuration object for transaction processing containing settings related
                      to the transaction source, target, and parsing.
        :param procs: The parallelism degree for the streaming environment
        '''
        #Create a  Kafka consumer
        source = ConsumerFlink.from_conf(
            name=f"flink-{pconf.source.name}",
            conf_broker=self.conf.kafka,
            conf_log=self.conf.logs,
            conf_parser=pconf,
            types = Parser.get_types(pconf.source.file)
        )
        # Creates a database sink
        sink = Database.from_conf(**self.db_conf_args)
        # Retrieve the Kafka consumer
        consumer = source.get_consumer()
        # Create a Parser object
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
        '''
        Submits the streaming process for all transaction processing configurations defined in the configuration.
        '''
        procs = self.conf.flink.parser.parallelism
        for pconf in self.conf.parsers:
            self.execute_env(pconf, procs)
