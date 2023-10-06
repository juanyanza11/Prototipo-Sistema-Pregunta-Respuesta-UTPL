import argparse
from scripts.embeddings_store import *
from scripts.wikipedia_utils import *


class WikipediaCrawler:
    def __init__(self, categoria_wikipedia, idioma_wikipedia, limite_paginas, directorio, index, almacenar_embeddings):
        self.categoria_wikipedia = categoria_wikipedia
        self.idioma_wikipedia = idioma_wikipedia
        self.limite_paginas = limite_paginas
        self.directorio = directorio
        self.index = index
        self.almacenar_embeddings = almacenar_embeddings

    def crawl_wikipedia(self):
        # print("Obteniendo páginas de la categoría...")
        # paginas = obtener_paginas_categoria(
        #     self.categoria_wikipedia, self.idioma_wikipedia, self.limite_paginas)

        # if paginas:
        #     for pagina in paginas:
        #         contenido_actual = obtener_contenido_wikipedia(
        #             pagina, self.idioma_wikipedia)
        #         if contenido_actual:
        #             verificar_y_actualizar_contenido(
        #                 pagina, contenido_actual, self.directorio)
        #         else:
        #             print(f"No se pudo obtener el contenido de '{pagina}'.")
        # else:
        #     print("No se pudieron obtener las páginas de la categoría.")
        
        # print("Verificar actualizaciones...")
        # verificar_actualizaciones(self.directorio)

        if self.almacenar_embeddings:
            print("Almacenando embeddings...")
            almacenar_embeddings_dbscan(self.index, self.directorio)


def main():
    parser = argparse.ArgumentParser(description='Wikipedia Crawler')
    parser.add_argument('--categoria', default='Pollution',
                        help='Categoría de Wikipedia')
    parser.add_argument('--idioma', default='en', help='Idioma de Wikipedia')
    parser.add_argument('--limite', type=int, default=100,
                        help='Límite de páginas')
    parser.add_argument('--directorio', default=f'data/sample data.csv',
                        help='Directorio de almacenamiento')
    parser.add_argument('--index', default='pollution', help='Índice')
    parser.add_argument('--guardar', default=False,
                        action='store_true', help='Almacenar embeddings')

    args = parser.parse_args()

    crawler = WikipediaCrawler(args.categoria, args.idioma, args.limite,
                               args.directorio, args.index, args.guardar)
    crawler.crawl_wikipedia()


if __name__ == "__main__":
    main()
