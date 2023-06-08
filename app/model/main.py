'''
The purpose of this code is to provide an interactive command-line interface for creating and 
submitting entities (User, Account, Bank) based on user input. It loads the entity structure 
from JSON files, prompts the user to input values for the entity attributes, and submits the 
entity to the corresponding Kafka topic using a Producer.
'''

import argparse
import json
import inquirer as iq
from omegaconf import OmegaConf
from app.infrastructure import Producer
from app.model import Account, Bank, User

def load_source(file):
    '''
    Load the JSON data from a file.
    
    :param file: The path to the JSON file
    :type file: str
    '''
    with open(file, 'r') as f:
        model = json.load(f)
    return model

def isnumber(answers, current):
    '''
    Validate if the user's input is a number.
    
    :param answer: The answer collected by the prompt 
    :param current: The current answer being validated 
    :return: True if the input is a number, false otherwise.
    '''
    return current.isnumeric()

def get_entity(model):
    '''
    Prompt the user to input values for creating an entity based on the given model.
    
    :param model: The model specifying the entity structure
    :param type: dict
    '''
    questions = []
    #
    validate = {
        "STRING": True,
        "INT": isnumber,
        "FLOAT": isnumber,
        "DOUBLE": isnumber
    }
    #
    for key, values in model.items():
        questions.append(iq.Text(
            key,
            message=f"Insert {key}",
            validate=validate[values]))
    answers = iq.prompt(questions)
    #
    entity = {}
    for key, value in answers.items():
        entity[key] = value

    return entity

def main(conf):
    '''
    Main function to interactively create a submit entities.
    
    :param conf: The configuration object
    '''
    questions = [
        iq.List(
            'entity',
            message='What would you like to do?',
            choices=[
                'Add new User',
                'Add new Account',
                'Add new Bank',
                'Exit'])
    ]

    answer = iq.prompt(questions)

    sources = {}
    topics = {}
    for src in conf.entities:
        sources[src.source.name] = src.source.file
        topics[src.source.name] = src.source.topics[0]

    if answer['entity'] == 'Add new User':
        model = load_source(sources['user'])
        args = get_entity(model)
        entity = User(**args)
        topic = topics['user']
    elif answer['entity'] == 'Add new Account':
        model = load_source(sources['account'])
        args = get_entity(model)
        entity = Account(**args)
        topic = topics['account']
    elif answer['entity'] == 'Add new Bank':
        model = load_source(sources['bank'])
        args = get_entity(model)
        entity = Bank(**args)
        topic = topics['bank']
    else:
        return

    broker = Producer.from_conf(
        name="entity-sender",
        conf_broker=conf.kafka,
        conf_log=conf.logs)

    print("Sending the following:")
    print(entity)

    questions = [iq.Confirm(
        'confirm',
        message='Do you want to submit this entity?',
        default=True)]
    answer = iq.prompt(questions)

    if answer['confirm']:
        entity.submit(broker, topic)

    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', help='YAML config file', required=True)

    #Parse the command-line arguments
    args = parser.parse_args()

    #Load the YAML configuration file
    conf = OmegaConf.load(args.conf)
    main(conf)
