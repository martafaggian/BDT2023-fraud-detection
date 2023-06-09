'''
This code snippet is the main entry point for executing the streaming 
processes for transactions and entities using Apache Flink.
'''

from omegaconf import OmegaConf
from app.infrastructure import Database, Cache
from app.model import Account
from app.pipeline import StreamTransactions, StreamEntities

if __name__ == '__main__':
    conf = OmegaConf.load("config.yaml")
    cache_conf_args = {
        "name": "parser-cache",
        "conf_cache": conf.redis,
        "conf_log": conf.logs,
        "db" : conf.redis.accounts.db
    }
    db_conf_args = {
        "name": "parser-cassandra",
        "conf_db": conf.cassandra,
        "conf_log": conf.logs
    }
    cache = Cache.from_conf(**cache_conf_args)
    db = Database.from_conf(**db_conf_args)
    # Transfer account data from Cassandra to cache
    Account.cassandra_to_cache(cache, db)
    # Account.csv_to_cache(cache, conf.redis.accounts.file)
    #Start streaming transactions
    stream_transactions = StreamTransactions(conf, cache_conf_args, db_conf_args)
    stream_transactions.submit_all()
    #Start streaming entities
    stream_entities = StreamEntities(conf, db_conf_args)
    stream_entities.submit_all()
