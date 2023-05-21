import json
from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import NoBrokersAvailable
from utils import Logger

class Broker:
    def __init__(self, host, port, logger):
        self._host = host
        self._port = port
        self._is_connected = False
        self._logger = logger

    def is_connected(self):
        return self._is_connected

class Producer(Broker):
    def __init__(self, host, port, logger):
        super().__init__(host, port, logger)
        try:
            self._producer =  KafkaProducer(
                bootstrap_servers=f'{self._host}:{self._port}',
                value_serializer=lambda m: json.dumps(m).encode('ascii')
            )
            self._is_connected = True
        except NoBrokersAvailable:
            self._logger.error(
                f'No broker available at {self._host}:{self._port}')
            self.consumer = None

    def send(self, message, topic):
        if self.is_connected():
            self._producer.send(topic, message)
        else:
            self._logger.error('Producer is not connected. Connect first!')

class Consumer(Broker):
    def __init__(self, host, port, topic, logger):
        super().__init__(host, port, logger)
        self.topic = topic

        try:
            self._consumer =  KafkaConsumer(
                self.topic, bootstrap_servers=f'{self._host}:{self._port}')
            self._is_connected = True
        except NoBrokersAvailable:
            self._logger.error(
                f'No broker available at {self._host}:{self._port}')
            self.consumer = None

    def retrieve(self):
        if self.is_connected():
            for message in self._consumer:
                print(message.value.decode('utf-8'))
        else:
            self._logger.error('Consumer is not connected. Connect first!')
