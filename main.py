import argparse
import time
from scripts.embeddings_store import *
from scripts.wikipedia_utils import *
from scripts.upload_neo4j_documents import *


class WikipediaCrawler:
    def __init__(self, dir, index, save, update, neo4j):
        self.dir = dir
        self.index = index
        self.save = save
        self.update = update
        self.neo4j = neo4j

    def crawl_wikipedia(self):
        if self.update:
            print('Actualizando contenido...')
            start_time = time.time()
            verificar_actualizaciones(self.dir)
            elapsed_time = time.time() - start_time
            print(f'Contenido actualizado en {elapsed_time} segundos.')
            
        if self.save:
            print('Almacenando embeddings...')
            almacenar_embeddings_dbscan(self.index, self.dir)
        
        if self.neo4j:
            print('Subiendo documentos a Neo4j...')
            load_data_to_neo4j(self.dir)


def main():
    parser = argparse.ArgumentParser(description='Wikipedia Crawler')
    parser.add_argument('--dir', default=f'data/dominio3.csv',
                        help='Directorio de almacenamiento')
    parser.add_argument('--index', default='pollution', help='Índice')
    parser.add_argument('--save', default=False,
                        action='store_true', help='Almacenar embeddings')
    parser.add_argument('--update', default=False,
                        help='Actualizar contenido')
    parser.add_argument('--neo4j', default=False, help='Subir documentos a Neo4j', action='store_true')

    args = parser.parse_args()

    crawler = WikipediaCrawler(args.dir, args.index, args.save, args.update, args.neo4j)
    crawler.crawl_wikipedia()


if __name__ == "__main__":
    main()
