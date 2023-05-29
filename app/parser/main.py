import os
import pandas as pd
from datetime import datetime
from pyflink.datastream import StreamExecutionEnvironment, ProcessFunction
from pyflink.common import SimpleStringSchema, WatermarkStrategy, Encoder
from pyflink.datastream.connectors import KafkaSource, StreamingFileSink
from pyflink.datastream.connectors.file_system import OutputFileConfig
from pyflink.table.udf import udf

env = StreamExecutionEnvironment.get_execution_environment()
# current_dir = os.path.dirname(os.path.realpath(__file__))
# env.add_jars(f"file:///jar/flink-sql-connector-kafka-1.17.1.jar")
# env.set_python_requirements(
    # requirements_file_path="/app/requirements.txt")
# env.set_python_executable("/root/mambaforge/envs/flink/bin/python")

# class MyProcessFunction(ProcessFunction):
    # def process_element(self, value, ctx: 'ProcessFunction.Context'):
        # timestamp = pd.to_datetime(ctx.timestamp(), unit='ms')
        # result = f"Value: {value}, Timestamp: {timestamp}"
        # with open("output.txt", "a") as f:
            # print(result, file=f)

source = KafkaSource \
    .builder() \
    .set_bootstrap_servers('kafka:9092') \
    .set_topics('streamer1', 'streamer2') \
    .set_value_only_deserializer(SimpleStringSchema()) \
    .build()

sink = StreamingFileSink \
    .for_row_format('/opt/flink/output', Encoder.simple_string_encoder()) \
    .with_output_file_config(OutputFileConfig.builder().with_part_prefix('pre').with_part_suffix('.txt').build()) \
    .build()

ds = env.from_source(source, WatermarkStrategy.no_watermarks(), "kafka source")
ds.add_sink(sink)
# ds.print()
# ds.process(MyProcessFunction())
env.execute("pyflink print kafka messages")
