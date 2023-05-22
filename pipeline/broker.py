from __future__ import annotations
import json
from abc import ABC, abstractmethod
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable
from utils import Logger

class BrokerNotConnectedException(Exception):
    def __init__(self, logger, message, *args):
        super().__init__(message)
        self.args = args
        logger.error(message)

class Broker(ABC):
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
        return self._is_connected

    def set_connected(self):
        self._is_connected = True

    def set_disconnected(self):
        self._is_connected = False
        self._broker = None

    def check_connected(self):
        if not self.is_connected():
            raise BrokerNotConnectedException(
                self._logger,
                f'Producer is not connected at {self._host}:{self._port}.')

    @abstractmethod
    def connect(self):
        pass

class Producer(Broker):
    def __init__(self, host, port, logger):
        super().__init__(host=host, port=port, logger=logger)
        self.connect()

    def connect(self):
        try:
            self._broker =  KafkaProducer(
                bootstrap_servers=f'{self._host}:{self._port}',
                value_serializer=lambda m: json.dumps(m).encode('ascii')
            )
            self.set_connected()
        except NoBrokersAvailable as e:
            self.set_disconnected()
            raise BrokerNotConnectedException(
                self._logger,
                f'No broker available at {self._host}:{self._port}'
            ) from e

    def send(self, message, topic):
        try:
            self.check_connected()
            self._broker.send(topic, message)
            # TODO: check response
        except BrokerNotConnectedException as e:
            self.set_disconnected()
            raise

    @staticmethod
    def from_conf(name, conf_broker, conf_log):
        return Producer(
            logger = Logger.from_conf(name, conf_log),
            host = conf_broker.host,
            port = conf_broker.port
        )

class Consumer(Broker, ABC):
    def __init__(self, host, port, topic, logger):
        super().__init__(host=host, port=port, logger=logger)
        self._topic = topic
        self.connect()

    def connect(self):
        try:
            self._broker =  KafkaConsumer(
                self._topic, bootstrap_servers=f'{self._host}:{self._port}')
            self.set_connected()
        except NoBrokersAvailable as e:
            self.set_disconnected()
            raise BrokerNotConnectedException(
                self._logger,
                f'No broker available at {self._host}:{self._port}'
            ) from e

    @abstractmethod
    def retrieve(self):
        pass

class ConsumerPrint(Consumer):
    def retrieve(self):
        if self.is_connected():
            for message in self._broker:
                print(f'{message.topic}: {message.value.decode("utf-8")}')
        else:
            self._logger.error('Consumer is not connected. Connect first!')
