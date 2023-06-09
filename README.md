# BTD2023-fraud-detection 
📦APP <br />  
 ┣ 📂INFRASTRUCTURE <br /> The "Infrastructure" folder contains three codes for working with different components. The "Broker" sends messages to a Kafka broker using the "KafkaProducer" class. The "Cache" interacts with a Redis cache, providing key-value storage and retrieval.
"Database" offers a database abstraction layer for connecting to and working with a Cassandra database.
These codes simplify interactions with the Kafka broker, Redis cache, and Cassandra database, providing convenient interfaces for integration. A better explanation is provided in the documentation of the code. <br />
 ┃ ┣ 📜broker.py <br />
 ┃ ┣ 📜cache.py <br />
 ┃ ┣ 📜database.py <br />
 ┃ ┗ 📜__init__.py <br />
 ┣ 📂MODEL <br />    
 ┃ ┣ 📜account.py <br />
 ┃ ┣ 📜bank.py <br />
 ┃ ┣ 📜main.py <br />
 ┃ ┣ 📜transaction.py <br />
 ┃ ┣ 📜user.py <br />
 ┃ ┗ 📜__init__.py <br />
 ┣ 📂PIPELINE <br /> 
 ┃ ┣ 📜Dockerfile <br />
 ┃ ┣ 📜fraud_detection.py <br />
 ┃ ┣ 📜main.py <br />
 ┃ ┣ 📜parser.py <br />
 ┃ ┣ 📜stream_entities.py <br />
 ┃ ┣ 📜stream_transactions.py <br />
 ┃ ┗ 📜__init__.py <br />
 ┣ 📂STREAM <br />   
 ┃ ┣ 📜Dockerfile <br />
 ┃ ┣ 📜main.py <br />
 ┃ ┣ 📜streamer.py <br />
 ┃ ┣ 📜streamers_manager.py <br />
 ┃ ┗ 📜__init__.py <br />
 ┗ 📂UTILS <br />    
 ┃ ┣ 📜logger.py <br />
 ┃ ┗ 📜__init__.py <br />
