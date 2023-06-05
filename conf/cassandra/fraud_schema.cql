SELECT * FROM system_schema.keyspaces;

DROP KEYSPACE IF EXISTS fraud_detection;
CREATE KEYSPACE IF NOT EXISTS fraud_detection
    WITH REPLICATION = {
        'class' : 'NetworkTopologyStrategy',
        'dc1' : 3
        };

-- DROP MATERIALIZED VIEW IF EXISTS fraud_detection.transactions_by_account;
-- DROP MATERIALIZED VIEW IF EXISTS fraud_detection.transactions_by_bank;
-- DROP MATERIALIZED VIEW IF EXISTS fraud_detection.transactions_by_user;
-- DROP TABLE IF EXISTS fraud_detection.transactions;
--
-- DROP MATERIALIZED VIEW IF EXISTS fraud_detection.accounts_by_bank;
-- DROP MATERIALIZED VIEW IF EXISTS fraud_detection.accounts_by_user;
-- DROP TABLE IF EXISTS fraud_detection.accounts;
-- DROP TABLE IF EXISTS fraud_detection.banks;
-- DROP TABLE IF EXISTS fraud_detection.users;

-- NOTE: all ids are of type TEXT and not UUID due to flink unable
--       to cast UUID types!
--       It is sufficient to cast uuid to text:
--       CAST(uuid() AS TEXT)
-- ################## TRANSACTIONS ################## --

CREATE TABLE IF NOT EXISTS fraud_detection.transactions (
    transaction_id TEXT,
    timestamp TIMESTAMP,
    user_id TEXT,
    account_id TEXT,
    bank_id TEXT,
    balance_before DOUBLE,
    balance_after DOUBLE,
    account_type TEXT,
    counterparty_account_id TEXT,
    counterparty_isinternal BOOLEAN,
    counterparty_name TEXT,
    counterparty_type TEXT,
    amount DOUBLE,
    direction TEXT,
    status TEXT,
    source_location TUPLE<FLOAT, FLOAT>,
    is_fraud BOOLEAN,
    fraud_confidence FLOAT,
    PRIMARY KEY ((transaction_id), timestamp))
    WITH CLUSTERING ORDER BY(timestamp DESC);

CREATE MATERIALIZED VIEW IF NOT EXISTS fraud_detection.transactions_by_bank AS
    SELECT * FROM fraud_detection.transactions
    WHERE bank_id IS NOT NULL AND
          transaction_id IS NOT NULL AND
          timestamp IS NOT NULL
    PRIMARY KEY ((bank_id, transaction_id), timestamp)
    WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE MATERIALIZED VIEW IF NOT EXISTS fraud_detection.transactions_by_user AS
    SELECT * FROM fraud_detection.transactions
    WHERE user_id IS NOT NULL AND
          transaction_id IS NOT NULL AND
          timestamp IS NOT NULL
    PRIMARY KEY ((user_id, transaction_id), timestamp)
    WITH CLUSTERING ORDER BY (timestamp DESC);

CREATE MATERIALIZED VIEW IF NOT EXISTS fraud_detection.transactions_by_account AS
    SELECT * FROM fraud_detection.transactions
    WHERE account_id IS NOT NULL AND
          transaction_id IS NOT NULL AND
          timestamp IS NOT NULL
    PRIMARY KEY ((account_id, transaction_id), timestamp)
    WITH CLUSTERING ORDER BY (timestamp DESC);

-- ################## TRANSACTIONS ################## --

CREATE TABLE IF NOT EXISTS fraud_detection.accounts(
    account_id text,
    user_id text,
    bank_id text,
    type TEXT,
    balance DOUBLE,
    PRIMARY KEY (account_id)
);

CREATE MATERIALIZED VIEW IF NOT EXISTS fraud_detection.accounts_by_user AS
    SELECT * FROM fraud_detection.accounts
    WHERE account_id IS NOT NULL AND
          user_id IS NOT NULL
    PRIMARY KEY ((user_id), account_id)
    WITH CLUSTERING ORDER BY (account_id ASC);

CREATE MATERIALIZED VIEW IF NOT EXISTS fraud_detection.accounts_by_bank AS
    SELECT * FROM fraud_detection.accounts
    WHERE account_id IS NOT NULL AND
          bank_id IS NOT NULL
    PRIMARY KEY ((bank_id), account_id)
    WITH CLUSTERING ORDER BY (account_id ASC);

-- ################## BANKS ################## --

CREATE TABLE IF NOT EXISTS fraud_detection.banks(
    bank_id TEXT,
    name TEXT,
    address TEXT,
    phone TEXT,
    PRIMARY KEY (bank_id)
);

-- ################## USERS ################## --

CREATE TABLE IF NOT EXISTS fraud_detection.users(
    user_id TEXT,
    name TEXT,
    ssn TEXT,
    email TEXT,
    birthdate DATE,
    registration_date DATE,
    PRIMARY KEY (user_id)
);