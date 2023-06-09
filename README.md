# BTD2023-fraud-detection

## Live Demo

For navigating the live demo (final [grafana dashboard](#visualization)), you can visit:
> URL: **[bdt.davidecalza.com](https://bdt.davidecalza.com)**
> <br />User: **guest**
> <br />Password: **BDT2023**

> **Warning** due to recently frequent disconnections from my ISP, the website may not be always reachable, since DNS cache takes some minutes to refresh after a change of my server's public IP. 

## Initial setup

The workflow requires an initial data sources location in the path:
```
./data/sources/
```
And some flink libraries in:
```
./lib/
```

The sources zip can be downloaded [here](https://drive.google.com/file/d/13Po01RVLYdbDWWEvDPSfqElstoX_aX1g/view?usp=sharing).
The lib zip can be downloaded[here](https://drive.google.com/file/d/1cBIjjZTNSo9UqNsf9Hq3LvYaWSyWuvoz/view?usp=drive_link)

Afterwards, it is sufficient to run:
```sh
./start.sh
```

The most critical parameters can be set via the proposed [config.yaml](config.yaml) file. 

> **Note**: regarding the final [grafana dashboard](#visualization), it is necessary to upload the provided config file **./conf/grafana.json** in the grafana after adding the cassandra and redis sources. Some queries may not be set by default in the panel, but are included in the conf.json.  

### Prerequirements

* docker
* python 3.10
```
pip install -r requirements.txt
```
> **Warning** for systems with less than 8GB of RAM, it is recommended to run only one cassandra node and set parallel processes of flink to 1. 

> **Warning** for low memory systems, it is also recommended to run flink natively instead of running the dockerized version (see [here](https://nightlies.apache.org/flink/flink-docs-master/docs/deployment/resource-providers/standalone/overview/)). The installing procedure can be found in the relative [Dockerfile](./app/pipeline/Dockerfile), and a pointer to kafka host from localhost is needed in /etc/hosts. Further tweaks may be required. 

## 1. Introduction

The project requirement was the following:
> Create an intelligent fraud detection platform leveraging Big Data technologies. Your system would ingest transactional data from various sources (e.g., credit cards, bank accounts, investment portfolios), process unlimited events per second, perform statistical analyses of transactions, compare them against historic norms, and flag suspicious activities in milliseconds (or slightly more, well..).

The pipeline design is the following:

<img src="./img/pipeline_design.jpg" alt="pipeline design" width="70%"/>

## 2. Data Modeling

The data modeling process was performed by following the indications proposed by
[cassandra](https://cassandra.apache.org/doc/latest/cassandra/data_modeling.html) for a correct modeling of the data structure.
> **Warning**
> data modeling for cassandra requires a **query oriented** approach, different from the typical relational data modeling.

Overall, the data modeling workflow is:
1. Define a [conceptual model](#conceptual-model)
2. Define a [query model](#query-model)
3. Merge conceptual and query models into a [logical model](#logical-model)
4. Derive a [physical model](#physical-model) from the logical

<img src="./img/data_modeling.png" alt="data processing workflow" width="70%"/>

### 2.1. Conceptual Model

The conceptual model aims at defining the entities present in the data model and the relationships that may be present between each other.
This example proposes a conceptual model for a fraud detection system using the Peter Chen's entity-relationship model:

<img src="img/1_conceptual_model.drawio.png" alt="conceptual model" width="70%"/>

### 2.2. Query Model

The second step consists in defining a query model. This is particularly promoted by the cassandra query-oriented approach.
This consists in defining the possible end queries that the system will perform to the db, in order to provide a robust and
efficient model.

#### 2.2.1. User Stories

A preliminary step useful for defining the possible end queries is the definition of the so-called user stories:

----

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
    
#### 2.2.2. Final Query Model

After the definition of the user stories, it is possible to define the query model:

<img src="img/2_query_model.drawio.png" alt="query model" width="70%"/>

### 2.3. Logical Model

Conceptual and query models are then combined into a logical model:

<img src="img/3_logical_model.drawio.png" alt="logical model" width="70%"/>

The definition of the logical model for Cassandra data model is a critical phase because it determines how the data will be structured and organized to fit the specific queries and data access patterns of the application.

### 2.4. Physical Model

The definition of the physical model is a simple task after the definition of a logical model:

<img src="img/4_physical_model.png" alt="physical model" width="70%"/>

> **Warning**
> a further refinement of the physical model is usually needed in order to define possible bucketing and partitioning techniques based on the estimated data flow. Being this project a prototype, this step has been neglected. For more information, see [here](https://cassandra.apache.org/doc/latest/cassandra/data_modeling/data_modeling_refining.html)

## 3. Streamers

In order to simulate a possible real case of real-time transactions, several streaming utilities have been included.
The concept is to add an input source (like the ones proposed in the introduction section) and stream all the data to a kafka broker, defined in the config file.
As multiple sources can be present, a streams manager is included, which will handle the different streamers using multiple threads.

![kafka demo](./img/kafka_ui.png)

The source format is not relevant, as the system was designed to provide several parsers with the aim of convert the source formats to the target one.
Parsers are part of the [flink pipeline](#data-processing).
Each streamer stores its status (active, enabled, interrupted) in a redis cache.
Useful commands for handling the streamers are:

```sh
./stream_start.sh # Start streamers when interrupt/at the first run
```
```sh
./stream_disable.sh # Disable streamers but keep running.
```
```sh
./stream_enable.sh # Enable streamers.
```
```sh
./stream_interrupt.sh # Interrupt all streamers. Requires a new start afterwards.
```

A configuration example is the following:

```yaml
 streamers:
  - name: streamer1 # Streamer name
    file: ./data/synthetic_financial_datasets.csv # Source file to stream
    topic: raw-streamer1 # Target Kafka topic for publishing the messages
    status_key: streamer1.active # Streamer status key in the redis cache
    messages_per_second: 1 # How many messages should be sent per second
    sleep_disabled: 10 # How much time to wait for checking the status when disabled
```

## 3. Data Processing

![flink demo](./img/flink_dash.png)

## Database

### Add entities

![add entities demo](./img/insert_bank.gif)

## Visualization

![grafana demo](./img/grafana.gif)

## Interfaces

The following interfaces can be accessed:
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
