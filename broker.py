import json
from kafka import KafkaProducer, KafkaConsumer

class Broker:
    def __init__(self, host, port):
        self.host = host
        self.port = port

class Producer(Broker):
    def __init__(self, host, port):
        super().__init__(host, port)
        self.producer =  KafkaProducer(
            bootstrap_servers=f'{self.host}:{self.port}',
            value_serializer=lambda m: json.dumps(m).encode('ascii')
        )

    def send(self, message, topic):
        self.producer.send(topic, message)

class Consumer(Broker):
    def __init__(self, host, port, topic):
        super().__init__(host, port)
        self.topic = topic
        self.consumer =  KafkaConsumer(self.topic, bootstrap_servers=f'{self.host}:{self.port}')

    def retrieve(self):
        for message in self.consumer:
            print(message.value.decode('utf-8'))
