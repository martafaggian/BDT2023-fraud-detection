"""
NB: flink requires all code in one single file!
"""
from omegaconf import OmegaConf
from app.infrastructure import Database, Cache
from app.model import Account
from app.pipeline import StreamTransactions

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
    Account.cassandra_to_cache(cache, db)
    # Account.csv_to_cache(cache, conf.redis.accounts.file)
    stream_transactions = StreamTransactions(conf, cache_conf_args, db_conf_args)
    stream_transactions.submit_all()
