import time
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
    print(f'Ruta de documentos de scopus: {file_path}')
    
    # Borra todos los nodos y relaciones
    DELETE = '''
    MATCH (n)
    DETACH DELETE n
    '''
    
    UPLOAD = '''
    LOAD CSV WITH HEADERS FROM
    "https://raw.githubusercontent.com/juanyanza11/Prototipo-Sistema-Pregunta-Respuesta-UTPL/main/data/pollutionScopus.csv" AS line
    WITH line LIMIT 4000

    MERGE (title:Document {id: line.eid})
    ON CREATE SET 
                title.title = line.title,
                title.description = line.description,
                title.subtypeDescription = line.subtypeDescription,
                title.name = line.title

    MERGE (creator:Creator {name: COALESCE(line.creator, 'N.D.')})
    MERGE (title)-[:CREATED_BY]->(creator)

    FOREACH (keyword IN split(line.authkeywords, '|') |
    MERGE (k:Keyword {value: keyword})
    MERGE (title)-[:HAS_KEYWORD]->(k)
    )

    FOREACH (description IN CASE WHEN line.description IS NOT NULL THEN [line.description] ELSE [] END |
    MERGE (desc:Description {value: description})
    MERGE (title)-[:HAS_DESCRIPTION]->(desc)
    )

    MERGE (type:TypeArticle {value: line.subtypeDescription})
    MERGE (title)-[:HAS_TYPE]->(type)

    MERGE (institution:Institution {name: COALESCE(line.affilname, 'N.D.')})
    MERGE (title)-[:AFFILIATED_WITH]->(institution)

    MERGE (city:City {name: COALESCE(line.affiliation_city, 'N.D.')})
    MERGE (institution)-[:LOCATED_IN]->(city)

    MERGE (country:Country {name: COALESCE(line.affiliation_country, 'N.D.')})
    MERGE (city)-[:LOCATED_IN]->(country)
    '''
    
    query_sequence_execution = [
        (DELETE, "Borrando nodos y relaciones"),
        (UPLOAD, "Subiendo nodos y relaciones")        
    ]
    
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        with driver.session() as session:
            for query in query_sequence_execution:
                time.sleep(2)
                start_time = time.time()
                session.run(query[0])
                elapsed_time = time.time() - start_time
                print(f'{query[1]} en {elapsed_time} segundos.')
            session.close()
            