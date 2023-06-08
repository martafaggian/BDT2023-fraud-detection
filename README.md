# BTD2023-fraud-detection

## Introduction

![workflow demo](./img/workflow.gif)

## Streamers

![kafka demo](./img/kafka_ui.png)

## Pipeline

![flink demo](./img/flink_dash.png)

## Data Modeling

The data modeling flow followed the instructions proposed by
[cassandra](https://cassandra.apache.org/doc/latest/cassandra/data_modeling.html)

### Conceptual Model
![conceptual model](img/1_conceptual_model.drawio.png)

### Query Model

#### User Stories

* As a user, I want to see:
    * my details
    * the details of my accounts
    * all my transactions
    * the transactions of one of my accounts
    * if there are some anomalous transactions
    * the details of the transactions

----

* As a bank, I want to see:
    * my details
    * the details of the accounts
    * the details of the users
    * all transactions of the bank
    * the details of the transactions
    * all transactions of a user
    * all transactions of an account
    * all the fraudulent transactions

----

* As the fraud detector system, I want to see:
    * all transactions available
    * all transactions of a user
    * all transactions of an account
    
#### Final Query Model

![query model](img/2_query_model.drawio.png)

### Logical Model

![logical model](img/3_logical_model.drawio.png)

### Physical Model

![physical model](img/4_physical_model.drawio.png)

Note: a further refinement of the physical model is usually needed in
order to define possible bucketing and partitioning techniques based
on the estimated data flow.
For more information, see [here](https://cassandra.apache.org/doc/latest/cassandra/data_modeling/data_modeling_refining.html)

## Database

### Add entities

![add entities demo](./img/insert_bank.gif)

## Visualization

![grafana demo](./img/grafana.gif)

## TODOs

### General
- [ ] Write README.md
- [x] Dockerize the software
- [ ] Write documentation
- [x] Add utils scripts:
    - [x] start/enable/stop/interrupt_streamers.sh
    - [x] add user/account/bank to cassandra
    - [x] simple interface for adding entities
- [x] start.sh for starting all pipeline

### Data Modeling
- [x] Conceptual model
- [x] Query model
    - [x] Define user stories
- [x] Logical model
- [x] Physical model

### Streamer
- [x] Start/enable/stop/interrupt streamers
- [ ] Save current streamer state to redis (e.g. config, last row sent)
- [x] Handle multiple streamers in parallel

### Pipeline
- [x] Fraud detection phase
    - [ ] Better-refine fraud-detection algorithms
        - [ ] Integrate Benford-Law for fraud detection
- [ ] Use redis as intermediate persistance layer
    - (Py)Flink missing redis connector
- [x] Update account balances real-time

### Database
- [x] Initialize Cassandra DB on docker startup
- [x] Simulate cassandra cluster with multiple nodes

### Visualization
- [x] Integrate grafana for banks generic views
- [x] Integrate user-based interface with dash
    - [x] Interact with DB via Flask defined APIs
