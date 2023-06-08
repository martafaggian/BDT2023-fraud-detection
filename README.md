# BTD2023-fraud-detection

## Initial setup

The workflow requires an initial data sources location in the path:
```
./data/sources
```
And some flink libraries in:
```
./lib
```

The sources zip can be downloaded [here](https://drive.google.com/file/d/13Po01RVLYdbDWWEvDPSfqElstoX_aX1g/view?usp=sharing).
The lib zip can be downloaded[here](https://drive.google.com/file/d/1cBIjjZTNSo9UqNsf9Hq3LvYaWSyWuvoz/view?usp=drive_link)

Afterwards, it is sufficient to run:
```sh
./start.sh
```

### Prerequirements

* docker
* python 3.10
```
pip install -r requirements.txt
```
> **Warning** for systems with less than 8GB of RAM, it is recommended to run only one cassandra node and set parallel processes of flink to 1. 

## Introduction

![workflow demo](./img/workflow.gif)

## Streamers

![kafka demo](./img/kafka_ui.png)

## Pipeline

![flink demo](./img/flink_dash.png)

## Data Modeling

The data modeling flow followed the instructions proposed by
[cassandra](https://cassandra.apache.org/doc/latest/cassandra/data_modeling.html) for a correct modeling of the data structure.
> **Warning**
> data modeling for cassandra requires a **query oriented** approach, different from the typical relational data modeling.

Overall, the data modeling workflow is:
1. Define a [conceptual model](#conceptual-model)
2. Define a [query model](#query-model)
3. Merge conceptual and query models into a [logical model](#logical-model)
4. Derive a [physical model](#physical-model) from the logical

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

![physical model](img/4_physical_model.png)

> **Warning**
> a further refinement of the physical model is usually needed in order to define possible bucketing and partitioning techniques based on the estimated data flow. Being this project a prototype, this step has been neglected. For more information, see [here](https://cassandra.apache.org/doc/latest/cassandra/data_modeling/data_modeling_refining.html)

## Database

### Add entities

![add entities demo](./img/insert_bank.gif)

## Visualization

![grafana demo](./img/grafana.gif)

## Services

The following services can be accessed:
* **Grafana Dashboard**: localhost:**3000**
* **Flink Dashboard**: localhost:**8081**
* **Kafka-UI**: localhost:**8080**

## TODOs

### General
- [ ] Auto download libs from gdrive with gdown
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
