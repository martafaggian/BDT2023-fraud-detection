import argparse
from omegaconf import OmegaConf
from infrastructure import ConsumerPrint
from utils import Logger

def main(conf):
    logger = Logger.from_conf("kafka.consumer", conf.logs)
    consumer = ConsumerPrint(host=conf.kafka.host,
                             port=conf.kafka.port,
                             logger=logger)
    consumer.subscribe([stream.topic for stream in conf.streamers])
    while True:
        consumer.retrieve()

'''
    The main function for the Kafka consumer application. It initializes the logger,
    creates a ConsumerPrint object, subscribes to the specified topics, and continuously
    retrieves messages from the Kafka broker.

    param:
        conf (OmegaConf): The configuration object containing the application settings.
'''
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', help='YAML config file')
    args = parser.parse_args()
    conf = OmegaConf.load(args.conf)
    main(conf)
