from dotenv import load_dotenv
from neo4j import GraphDatabase
import os
import pandas as pd
import py2neo

load_dotenv()
# Conexion a Neo4j Aura
uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

def load_data_to_neo4j(file_path):
    # Lee el archivo CSV con pandas
    graph = py2neo.Graph(uri, password=password, name = "neo4j", user=user)
    print(f'file path: {file_path}')
    df = pd.read_csv(file_path)
    
    query = '''
    LOAD CSV WITH HEADERS FROM
    "https://raw.githubusercontent.com/amaboura/panama-papers-dataset-2016/master/de.csv" AS row
    MERGE (n:Node {node_id:row.id}) ON CREATE SET n = row, n:de_node;
    ''' % file_path
    
    result = graph.run(query)
    # Cantidad de nodos insertados:
    print(result)