'''
This code defines the Producer and Consumer classes for working with Kafka brokers. The Producer
class is responsible for sending messages to a broker, and the Consumer class is responsible for
retrieving messages from a broker. The code also includes a custom exception
BrokerNotConnectedException to handle cases where the broker connection fails.
The Producer class uses the KafkaProducer class from the kafka library to establish a connection
to the Kafka broker. The send method is used to send a message to a specified topic.
The Consumer class uses the KafkaConsumer class from the kafka library to connect to the Kafka
broker and retrieve messages. The retrieve method retrieves messages from the broker and prints
them.

There are also ConsumerFlink and ProducerFlink classes that are specific to working with the
Flink Kafka connector. These classes use the FlinkKafkaConsumer and FlinkKafkaProducer classes
from the pyflink.datastream.connectors module.

To use these classes, you would need to create an instance of the desired class and call the
appropriate methods. For example, to create a Producer instance and send a message, you can
use the following code:
producer = Producer(host='localhost', port=9092, logger=logger)
producer.send('Hello, Kafka!', topic='my_topic')

To create a Consumer instance and retrieve messages, you can use the following code:
consumer = Consumer(host='localhost', port=9092, logger=logger)
consumer.retrieve()
'''

from __future__ import annotations
import json
import time
from datetime import datetime
from abc import ABC, abstractmethod
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable
from kafka.admin import KafkaAdminClient, NewTopic
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.datastream.formats.json import JsonRowDeserializationSchema, JsonRowSerializationSchema
from app.utils import Logger

class BrokerNotConnectedException(Exception):
    '''
    Custom exeption for broker not connected.

    :param logger: The logger instance.
    :type logger: Logger
    :param message: The error message.
    :type message: str
    :param args: Additional arguments for the exception.
    '''
    def __init__(self, logger, message, *args):
        super().__init__(message)
        self.args = args
        logger.error(message)

class Broker(ABC):
    '''
    Abstract base class for brokers.

    :param logger: the logger instance.
    :type logger: Logger
    :param host: The broker host.
    :type host: str
    :param port: The broker port.
    :type port: int
    '''
    def __init__(
        self,
        logger: Logger,
        host: str = 'localhost',
        port: int = 6379
    ):
        self._host = host
        self._port = port
        self._logger = logger
        self._is_connected = False
        self._broker = None

    def is_connected(self):
        '''
        Check if the broker is connected.

        :return: a boolean if connected
        '''
        return self._is_connected

    def set_connected(self):
        '''
        Set the broker as connected
        '''
        self._is_connected = True

    def set_disconnected(self):
        '''
        Set the broker as disconnected
        '''
        self._is_connected = False
        self._broker = None

    def check_connected(self):
        '''
        Check if the broker is connected and raise an exeption if not.
        '''
        if not self.is_connected():
            raise BrokerNotConnectedException(
                self._logger,
                f'Producer is not connected at {self._host}:{self._port}.')

    @abstractmethod
    def connect(self):
        '''Connect to the broker'''
        pass

class Producer(Broker):
    '''
    Producer class for sending messages to a broker.

    :param host: The broker host
    :type host: str
    :param port: The broker port
    :type port: int
    :param logger: The logger instance
    :type logger: Logger
    '''
    def __init__(self, host, port, logger):
        super().__init__(host=host, port=port, logger=logger)
        self.connect()

    def connect(self, retry_n=10, retry_sleep=5):
        '''
        Connect to the broker

        :param retry_n: Number of retry attempts
        :type retry_n: int
        :param retry_sleep: Sleep time between retries in seconds
        :type retry_sleep: int
        '''
        try:
            self._broker =  KafkaProducer(
                bootstrap_servers=f'{self._host}:{self._port}',
                value_serializer=lambda m: json.dumps(m).encode('ascii')
            )
            self.set_connected()
        except NoBrokersAvailable as e:
            self.set_disconnected()
            if retry_n > 0:
                self._logger.warning(f"No broker available at {self._host}:{self._port}.")
                self._logger.warning(f"Retrying {retry_n} time(s).")
                time.sleep(retry_sleep)
                self.connect(retry_n=retry_n-1, retry_sleep=retry_sleep)
            else:
                raise BrokerNotConnectedException(
                    self._logger,
                    f'No broker available at {self._host}:{self._port}'
                ) from e

    def send(self, message, topic):
        '''
        Send a message to a topic.

         :param message: The message to send.
         :type message: str
         :param topic: The topic to send the message to.
         :type topic: str
        '''
        try:
            self.check_connected()
            future = self._broker.send(topic, message)
            # TODO: check response
            try:
                rec = future.get(timeout=10)
                # self._logger.info(f"Message sent successfully to {rec.topic} partition {rec.partition} at offset {rec.offset}")
            except Exception as e:
                self._logger.error(f"Error sending message to {topic}: {e}")
        except BrokerNotConnectedException as e:
            self.set_disconnected()
            raise

    @staticmethod
    def from_conf(name, conf_broker, conf_log):
        '''
        A static method that create a Producer instance from configuration settings.

        :param name: The name of the producer.
        :type name: str
        :param conf_broker: The broker configuration dictionary
        :type conf_broker: dict
        :param conf_log: The logger configuration dictionary.
        :return: A producer instance
        '''
        return Producer(
            logger = Logger.from_conf(name, conf_log),
            host = conf_broker.host,
            port = conf_broker.port
        )

class Consumer(Broker, ABC):
    '''
    Abstract base class for consumers.

    :param host: The broker host
    :type host: str
    :param port: The broker port
    :type port: int
    :param logger: The logger instance
    :type logger: Logger
    '''
    def __init__(self, host, port, logger):
        super().__init__(host=host, port=port, logger=logger)
        self.connect()

    def connect(self):
        '''
        Connect to the broker and raise an Exception if the connection fails.
        '''
        try:
            self._broker =  KafkaConsumer(
                bootstrap_servers=f'{self._host}:{self._port}')
            self.set_connected()
        except NoBrokersAvailable as e:
            self.set_disconnected()
            raise BrokerNotConnectedException(
                self._logger,
                f'No broker available at {self._host}:{self._port}'
            ) from e

    def subscribe(self, topics):
        '''
        Subscribe to multiple topics.
        :param topics: The topics to subscribe to
        :type topics: list
        '''
        self._broker.subscribe(topics)

    @abstractmethod
    def retrieve(self):
        '''
        retrieve message from the broker.
        '''
        pass

class ConsumerPrint(Consumer):
    '''
    Consumer class for printing messages from a broker.
    '''
    def retrieve(self):
        '''
        Retrieve messages from the broker and print them.
        '''
        if self.is_connected():
            for message in self._broker:
                print(f'{datetime.now()} {message.topic}: {message.value.decode("utf-8")}')
        else:
            self._logger.error('Consumer is not connected. Connect first!')

class ConsumerFlink(Broker):
    '''
    Consumer class for Flink and Kafka connector.

    :param host: The broker host
    :type host: str
    :param port: the broker port
    :type port: int
    :param logger: the logger instance
    :type logger: Logger
    :param type_info: The type info for deserialization
    :type type_info: str
    :param topics: The topics to consume
    :host topics: list
    '''
    def __init__(self, host, port, logger, type_info, topics, num_partitions=1, replication_factor=1):
        super().__init__(host=host, port=port, logger=logger)
        self._type_info = type_info
        self._topics = topics
        self._num_partitions = num_partitions
        self._replication_factor = replication_factor
        # Create topics if not exist
        admin = KafkaAdminClient(
            bootstrap_servers=f'{self._host}:{self._port}'
        )
        for topic in self._topics:
            if topic not in admin.list_topics():
                admin.create_topics([NewTopic(
                    name=topic,
                    num_partitions=self._num_partitions,
                    replication_factor=self._replication_factor)])
        #
        self._deserializer = JsonRowDeserializationSchema \
            .builder() \
            .type_info(type_info=self._type_info)\
            .build()
        # self._deserializer = SimpleStringSchema()
        self._props = {
            'bootstrap.servers': f'{self._host}:{self._port}',
        }
        self._consumer = FlinkKafkaConsumer(
            topics=self._topics,
            deserialization_schema=self._deserializer,
            properties=self._props
        )

    def connect(self):
        '''
        Connect method is not implemented for ConsumerFlink.
        '''
        self._logger.error('This object is intended to use as Flink Source!')

    def get_consumer(self):
        '''
        Get the Flink Kafka Consumer object.
        :return: The Flink Kafka Consumer object
        '''
        return self._consumer

    @staticmethod
    def from_conf(name, conf_broker, conf_log, conf_parser, types):
        '''
        Create a ConsumerFlink instance from configuration settings.

        :param name: The name of the consumer.
        :type name: str
        :param conf_broker: The broker configuration dictionary.
        :type conf_broker: dict
        :param conf_log: The logger configuration dictionary.
        :type conf_log: dict
        :param conf_parser: The parser configuration dictionary.
        :type conf_parser: dict
        :param types: The type information for serialization.
        :type types: str
        :return: ConsumerFlink instance
        '''
        return ConsumerFlink(
            logger = Logger.from_conf(name, conf_log),
            host = conf_broker.host,
            port = conf_broker.port,
            type_info = types,
            topics=list(conf_parser.source.topics)
        )

class ProducerFlink(Broker):
    '''
    Producer class for Flink Kafka connector

    :param host: The broker host
    :type host: str
    :param port: the broker port
    :type port: int
    :param logger: the logger instance
    :type logger: Logger
    :param type_info: The type info for deserialization
    :type type_info: str
    :param topic: The topic to produce
    :host topic: list
    '''
    def __init__(self, host, port, logger, type_info, topic):
        super().__init__(host=host, port=port, logger=logger)
        self._type_info = type_info
        self._topic = topic
        self._serializer = JsonRowSerializationSchema \
            .builder() \
            .with_type_info(type_info=self._type_info)\
            .build()
        # self._serializer = SimpleStringSchema()
        self._props = {
            'bootstrap.servers': f'{self._host}:{self._port}',
        }
        self._producer = FlinkKafkaProducer(
            topic=self._topic,
            serialization_schema=self._serializer,
            producer_config=self._props
        )

    def connect(self):
        '''
        Connect method is not implemented for ProducerFlink.
        '''
        self._logger.error('This object is intended to use as Flink Source!')

    def get_producer(self):
        '''
        Get the Flink Kafka Producer object

        :return: The Flink Kafka Producer object
        '''
        return self._producer

    @staticmethod
    def from_conf(name, conf_broker, conf_log, conf_parser, types):
        '''
        Create a ProducerFlink instance from configuration setings.

        :param name: The name of the producer.
        :type name: str
        :param conf_broker: The broker configuration dictionary.
        :type conf_broker: dict
        :param conf_log: The logger configuration dictionary.
        :type conf_log: dict
        :param conf_parser: The parser configuration dictionary.
        :type conf_parser: dict
        :param types: The type information for serialization.
        :type types: str
        :return: ProducerFlink instance

        '''
        return ProducerFlink(
            logger = Logger.from_conf(name, conf_log),
            host = conf_broker.host,
            port = conf_broker.port,
            type_info = types,
            topic=conf_parser.target.topic
        )
