import argparse
import time
from scripts.embeddings_store import *
from scripts.wikipedia_utils import *


class WikipediaCrawler:
    def __init__(self, dir, index, save):
        self.dir = dir
        self.index = index
        self.save = save

    def crawl_wikipedia(self):
        print('Verificando actualizaciones...')
        start_time = time.time()
        verificar_actualizaciones(self.dir)
        elapsed_time = time.time() - start_time
        print(f'Actualizaciones verificadas en {elapsed_time} segundos.')

        if self.save:
            print('Almacenando embeddings...')
            almacenar_embeddings_dbscan(self.index, self.dir)


def main():
    parser = argparse.ArgumentParser(description='Wikipedia Crawler')
    parser.add_argument('--dir', default=f'data/dominio3.csv',
                        help='Directorio de almacenamiento')
    parser.add_argument('--index', default='pollution', help='Índice')
    parser.add_argument('--save', default=False,
                        action='store_true', help='Almacenar embeddings')

    args = parser.parse_args()

    crawler = WikipediaCrawler(args.dir, args.index, args.save)
    crawler.crawl_wikipedia()


if __name__ == "__main__":
    main()
