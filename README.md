This code reads an XML file and extracts data from it to create nodes and relationships in a Neo4j graph database. It uses the py2neo library to connect to the database and the xmltodict library to parse the XML file.

The ingest_data function performs the following steps:

-**Reads the contents of the XML file and loads it into a dictionary using xmltodict.**

-**Connects to the Neo4j graph database using the Graph class from py2neo.**

-**Deletes all existing nodes and relationships in the graph.**

-**Creates nodes and relationships for each protein in the XML file.**

-**Creates nodes and relationships for each feature in the XML file.**

-**Creates nodes and relationships for each gene in the XML file.**

-**Creates nodes and relationships for each organism in the XML file.**

-**Creates nodes and relationships for each reference in the XML file.**

The validate_data function is a helper function that checks if a key exists in a dictionary and returns its value if it does, or None if it doesn't.

The code also sets up a scheduler using the apscheduler library to run the ingest_data function every hour.

If more time was available, airflow could be used to schedule and monitor the data ingestion process. Airflow is an open-source platform to programmatically author, schedule and monitor workflows. It can be used to create complex data pipelines that can handle dependencies, retry failed tasks, and provide alerts and notifications in case of errors.

To use Airflow, the ingest_data function could be refactored into a PythonOperator and added to a DAG (Directed Acyclic Graph). The DAG would define the dependencies between tasks and schedule the execution of the DAG at a specific interval. Airflow provides a web interface to monitor the status of the DAG and its tasks and provides a rich set of tools to handle errors, notifications, and retries.



***How To Run:***

1- install the required libraries by running *pip install -r requirements*
2- Create the Graph Database (I used the docker method mentioned in coding challenge)
3- Connect to the default neo4j (in the script I'm using the following connection details: 
  url: bolt://localhost:7687
  username: neo4j
  password: weavebio)
  NOTE: You need to change neo4j password (the default one is neo4j but it won't work
4- run the script using python script.py

