from scripts.embeddings_store import almacenar_embeddings
from scripts.wikipedia_utils import obtener_contenido_wikipedia, obtener_paginas_categoria, verificar_y_actualizar_contenido

def main():
    categoria_wikipedia = "Programming_languages"  # Categoria seleccionada
    idioma_wikipedia = "en"  # Cambiar el idioma si es necesario
    limite_paginas = 25   # Cambiar el límite de páginas
    directorio = "data/contenido_wikipedia.csv"
    index = "wikipedia"


    # paginas = obtener_paginas_categoria(categoria_wikipedia, idioma_wikipedia, limite_paginas)

    # if paginas:
    #     for pagina in paginas:
    #         contenido_actual = obtener_contenido_wikipedia(pagina, idioma_wikipedia)
    #         if contenido_actual:
    #             verificar_y_actualizar_contenido(pagina, contenido_actual, directorio)
    #         else:
    #             print(f"No se pudo obtener el contenido de '{pagina}'.")
    # else:
    #     print("No se pudieron obtener las páginas de la categoría.")
    
    almacenar_embeddings(index, directorio)

if __name__ == "__main__":
    main()