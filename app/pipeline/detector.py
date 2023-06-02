import json
from omegaconf import OmegaConf
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.formats.json import JsonRowDeserializationSchema, JsonRowSerializationSchema
from app.infrastructure.broker import ConsumerFlink, ProducerFlink
import json
from pyflink.datastream.connectors.cassandra import CassandraSink

def main(conf):
    for parser in conf.parsers:
        #
        source = ConsumerFlink.from_conf(
            name=f"flink-{parser.name}",
            conf_broker=conf.kafka,
            conf_log=conf.logs,
            conf_parser=parser
        )
        consumer = source.get_consumer()
        #
        sink = ProducerFlink.from_conf(
            name=f"flink-{parser.name}",
            conf_broker=conf.kafka,
            conf_log=conf.logs,
            conf_parser=parser
        )
        producer = sink.get_producer()
        #
        def parsing(record):
            if record["amount"] > 1000:
                record["isFraud"] = 1
            else:
                record["isFraud"] = 0
            return record
        env = StreamExecutionEnvironment.get_execution_environment()
        ds = env.add_source(consumer)
        ds = ds.map(lambda x: parsing(x), sink._type_info)
        # ds = ds.add_sink(producer)
        cassandra_props = {
            'cassandra.host': 'cassandra-1',
            'cassandra.port': '9042',
            # 'cassandra.username': 'user',
            # 'cassandra.password': 'password',
            # 'cassandra.write.mode': 'upsert',
            # 'cassandra.write.batch.size.rows': '1000'
        }
        insert_query = """
        INSERT INTO test.transactions (id, step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig, nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud) VALUES (uuid(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        cassandra_sink = CassandraSink.add_sink(ds). \
            set_query(insert_query). \
            set_host('cassandra-1'). \
            build()
            #
        env.execute(f"Parser + AD {parser.name}")

if __name__ == '__main__':
    conf = OmegaConf.load("config.yaml")
    main(conf)
