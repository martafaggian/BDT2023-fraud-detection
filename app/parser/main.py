# import os
# import pandas as pd
# from datetime import datetime
# from pyflink.datastream import StreamExecutionEnvironment, ProcessFunction
# from pyflink.common import SimpleStringSchema, WatermarkStrategy, Encoder
# from pyflink.datastream.connectors import KafkaSource, StreamingFileSink
# from pyflink.datastream.connectors.file_system import OutputFileConfig
# from pyflink.table.udf import udf

# env = StreamExecutionEnvironment.get_execution_environment()
# # current_dir = os.path.dirname(os.path.realpath(__file__))
# # env.add_jars(f"file:///jar/flink-sql-connector-kafka-1.17.1.jar")
# # env.set_python_requirements(
    # # requirements_file_path="/app/requirements.txt")
# # env.set_python_executable("/root/mambaforge/envs/flink/bin/python")

# # class MyProcessFunction(ProcessFunction):
    # # def process_element(self, value, ctx: 'ProcessFunction.Context'):
        # # timestamp = pd.to_datetime(ctx.timestamp(), unit='ms')
        # # result = f"Value: {value}, Timestamp: {timestamp}"
        # # with open("output.txt", "a") as f:
            # # print(result, file=f)

# source = KafkaSource \
    # .builder() \
    # .set_bootstrap_servers('kafka:9092') \
    # .set_topics('streamer1', 'streamer2') \
    # .set_value_only_deserializer(SimpleStringSchema()) \
    # .build()

# sink = StreamingFileSink \
    # .for_row_format('/opt/flink/output', Encoder.simple_string_encoder()) \
    # .with_output_file_config(OutputFileConfig.builder().with_part_prefix('pre').with_part_suffix('.txt').build()) \
    # .build()

# ds = env.from_source(source, WatermarkStrategy.no_watermarks(), "kafka source")
# ds.add_sink(sink)
# # ds.print()
# # ds.process(MyProcessFunction())
# env.execute("pyflink print to file")

import json
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import FlinkKafkaConsumer
from pyflink.datastream.connectors.cassandra import CassandraSink
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.formats.json import JsonRowDeserializationSchema
from pyflink.common.typeinfo import Types

env = StreamExecutionEnvironment.get_execution_environment()

kafka_props = {
    'bootstrap.servers': 'kafka:9092',
}

type_info = Types.ROW_NAMED(
    ['step', 'type', 'amount', 'nameOrig', 'oldbalanceOrg', 'newbalanceOrig', 'nameDest', 'oldbalanceDest', 'newbalanceDest', 'isFraud', 'isFlaggedFraud'],
    [Types.INT(), Types.STRING(), Types.FLOAT(), Types.STRING(), Types.FLOAT(), Types.FLOAT(), Types.STRING(), Types.FLOAT(), Types.FLOAT(), Types.INT(), Types.INT()]
)

deserializer = JsonRowDeserializationSchema.builder().type_info(type_info=type_info).build()

consumer = FlinkKafkaConsumer(
    topics=[
        'streamer1',
        # 'streamer2'
    ],
    # deserialization_schema=SimpleStringSchema(),
    deserialization_schema=deserializer,
    properties=kafka_props
)

ds = env.add_source(consumer)

cassandra_props = {
    'cassandra.host': 'cassandra-1',
    'cassandra.port': '9042',
    # 'cassandra.username': 'user',
    # 'cassandra.password': 'password',
    # 'cassandra.write.mode': 'upsert',
    # 'cassandra.write.batch.size.rows': '1000'
}

def is_fraud(record):
    if float(record['amount']) > 10000:
        record['isFraud'] = 1
    else:
        record['isFraud'] = 0
    return record

create_db = """
CREATE KEYSPACE IF NOT EXISTS fraud_detection WITH REPLICATION = {'class': 'NetworkTopologyStrategy', 'replication_factor': 3}
"""

create_table = """
CREATE TABLE IF NOT EXISTS fraud_detection.transactions (
    id UUID,
    step int,
    type text,
    amount float,
    nameOrig text,
    oldbalanceOrg float,
    newbalanceOrig float,
    nameDest text,
    oldbalanceDest float,
    newbalanceDest float,
    isFraud int,
    isFlaggedFraud int,
    primary key ((isFraud), id)
)
"""

insert_query = """
INSERT INTO fraud_detection.transactions (id, step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig, nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud) VALUES (uuid(), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

# ds = ds.map(is_fraud)
cassandra_sink = CassandraSink.add_sink(ds). \
    set_query(insert_query). \
    set_host('cassandra-1'). \
    build()

env.execute("Kafka to Cassandra")
