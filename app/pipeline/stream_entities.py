'''
The provided code defines a class called "StreamEntities" that handles streaming of 
different entities (e.g., user, account, bank) using Apache Flink. It interacts with various 
components such as Kafka, Cassandra, and the application's infrastructure.

'''
from __future__ import annotations
from omegaconf import OmegaConf
from pyflink.datastream import StreamExecutionEnvironment, OutputTag
from pyflink.datastream.functions import ProcessFunction
from pyflink.datastream.connectors.cassandra import CassandraSink
from pyflink.common.typeinfo import Types
from pyflink.common.types import Row
from app.infrastructure import Database, DatabaseTables, Cache, ConsumerFlink
from app.model import Account, User, Bank
from app.pipeline import Parser

class StreamEntities:
    def __init__(
        self,
        conf,
        db_conf_args
    ):
        '''
         Initializes the StreamEntities object with the provided configurations and database 
         connection arguments.
         
         :param conf: Configuration object containing various settings for the streaming process
         :param db_conf_args: Database connection arguments required to establish connection to the database

        '''
        self.conf = conf
        self.db_conf_args = db_conf_args

    def execute_env(self, econf, procs=1):
        '''
        Executes the streaming environment for a specific entity.
        
        :param econf: Configuration object for a specific entity containing settings related 
                      to the entity's source and parsing
        :param procs: The parallelism degree for the streaming environment
        '''
        # Creates a Kafka consumer using the provided configurations 
        source = ConsumerFlink.from_conf(
            name=f"flink-{econf.source.name}",
            conf_broker=self.conf.kafka,
            conf_log=self.conf.logs,
            conf_parser=econf,
            types = Parser.get_types(econf.source.file)
        )
        
        # Creates a database sink using the database connection arguments
        sink = Database.from_conf(**self.db_conf_args)
        
        #Retrieves the Kafka consumer
        consumer = source.get_consumer()
        
        #
        # 1. Creates a StreamExecutionEnvironment and sets the parallelism degree
        env = StreamExecutionEnvironment\
            .get_execution_environment()\
            .set_parallelism(procs)
        # 2. Add Kafka Source
        ds = env.add_source(consumer)
        # 3 Save to sink
        ## AUTH IS (apparently) NOT IMPLEMENTED!
        if econf.source.name == "user":
            dtype = DatabaseTables.USERS
            qdict = User.get_query_dict(auto_id=True)
        elif econf.source.name == "account":
            dtype = DatabaseTables.ACCOUNTS
            qdict = Account.get_query_dict(auto_id=True)
        elif econf.source.name == "bank":
            dtype = DatabaseTables.BANKS
            qdict = Bank.get_query_dict(auto_id=True)
        ##
        query = sink.get_insert_query(
            dtype,
            qdict.keys(),
            qdict.values()
        )
        CassandraSink.add_sink(ds) \
            .set_query(query) \
            .set_host(sink.get_host(), sink.get_port()) \
            .build()
        # 4. Execute environment
        env.execute(f"Stream handle new {econf.source.name} entries")

    def submit_all(self):
        '''
        Submits the streaming process for all entities defined in the configuration.
        '''
        procs = self.conf.flink.parser.parallelism
        for econf in self.conf.entities:
            self.execute_env(econf, procs)
