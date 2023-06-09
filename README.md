# BTD2023-fraud-detection 
📦APP <br />  

 ┣ 📂INFRASTRUCTURE <br /> The "Infrastructure" folder contains three codes for working with different components. The "Broker" sends messages to a Kafka broker using the "KafkaProducer" class. The "Cache" interacts with a Redis cache, providing key-value storage and retrieval.
"Database" offers a database abstraction layer for connecting to and working with a Cassandra database.
These codes simplify interactions with the Kafka broker, Redis cache, and Cassandra database, providing convenient interfaces for integration. A better explanation is provided in the documentation of the code. <br />

 ┃ ┣ 📜broker.py <br />
 ┃ ┣ 📜cache.py <br />
 ┃ ┣ 📜database.py <br />
 ┃ ┗ 📜__init__.py <br />
 
 ┣ 📂MODEL <br /> The folder contains several Python files that form the core of an application. The files include "main.py," which serves as the entry point and orchestrates the overall functionality. "account.py" defines a class for account entities, "bank.py" handles bank-related operations, "transaction.py" manages transaction data, and "user.py" handles user-related functionalities. Together, these files enable the creation, management, and interaction with entities such as accounts, banks, transactions, and users within the application. <br />
 
 ┃ ┣ 📜account.py <br />
 ┃ ┣ 📜bank.py <br />
 ┃ ┣ 📜main.py <br />
 ┃ ┣ 📜transaction.py <br />
 ┃ ┣ 📜user.py <br />
 ┃ ┗ 📜__init__.py <br />
 
 ┣ 📂PIPELINE <br /> The folder contains multiple Python files for a fraud detection system using Apache Flink. The "fraud_detection.py" file implements the "FraudDetection" class, which performs fraud detection on a data stream. The "main.py" file serves as the main entry point for executing streaming processes for transactions and entities using Apache Flink. The "parser.py" file provides a parser for transforming data from a source format to a target format using Apache Flink. The "stream_entities.py" file defines the "StreamEntities" class, responsible for handling the streaming of various entities (e.g., user, account, bank) using Apache Flink and interacting with components like Kafka, Cassandra, and the application's infrastructure. The "stream_transactions.py" file includes the "StreamTransactions" class, which handles the streaming of transactions using Apache Flink. It integrates with components such as Kafka, Cassandra, and the application's infrastructure, and utilizes a parser and fraud detection for processing transactions.  <br />
 
 ┃ ┣ 📜Dockerfile <br />
 ┃ ┣ 📜fraud_detection.py <br />
 ┃ ┣ 📜main.py <br />
 ┃ ┣ 📜parser.py <br />
 ┃ ┣ 📜stream_entities.py <br />
 ┃ ┣ 📜stream_transactions.py <br />
 ┃ ┗ 📜__init__.py <br />
 
 ┣ 📂STREAM <br /> Overall, the folder's code provides a framework for managing and controlling multiple streamers for data streaming tasks. It enables simultaneous execution of multiple streamers, allows for dynamic enablement/disabling, and handles interruptions gracefully. It can serve as a foundation for building more complex streaming applications or systems that involve multiple streamers working together. <br />
 
 ┃ ┣ 📜Dockerfile <br />
 ┃ ┣ 📜main.py <br />
 ┃ ┣ 📜streamer.py <br />
 ┃ ┣ 📜streamers_manager.py <br />
 ┃ ┗ 📜__init__.py <br />
 
 ┗ 📂UTILS <br />  The folder contains a Python file that provides a set of classes for logging messages with different levels to various files and streams.
 
 ┃ ┣ 📜logger.py <br />
 ┃ ┗ 📜__init__.py <br />
