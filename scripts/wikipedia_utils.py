import requests
import os
from bs4 import BeautifulSoup

def obtener_paginas_categoria(categoria, idioma='en', limite=5):
    url = f"https://{idioma}.wikipedia.org/w/api.php"
    parametros = {
        'action': 'query',
        'list': 'categorymembers',
        'cmtitle': f"Category:{categoria}",
        'cmlimit': limite,
        'format': 'json'
    }

    try:
        respuesta = requests.get(url, params=parametros)
        respuesta.raise_for_status()
        datos = respuesta.json()
        paginas = [pagina['title'] for pagina in datos['query']['categorymembers']]
        return paginas
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la lista de páginas en la categoría: {str(e)}")
        return None
    


def obtener_fecha_modificacion(articulo, idioma='en'):
    url = f"https://{idioma}.wikipedia.org/w/api.php"
    parametros = {
        'action': 'query',
        'prop': 'revisions',
        'titles': articulo,
        'rvlimit': 1,
        'rvprop': 'timestamp',
        'format': 'json'
    }

    try:
        respuesta = requests.get(url, params=parametros)
        respuesta.raise_for_status()
        datos = respuesta.json()
        pagina = next(iter(datos['query']['pages'].values()))
        if 'revisions' in pagina:
            fecha_modificacion = pagina['revisions'][0]['timestamp']
            return fecha_modificacion
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener la fecha de modificación: {str(e)}")
        return None
    
    
def obtener_contenido_wikipedia(articulo, idioma='en'):
    url = f"https://{idioma}.wikipedia.org/w/api.php"
    parametros = {
        'action': 'parse',
        'page': articulo,
        'prop': 'text',
        'format': 'json'
    }

    try:
        respuesta = requests.get(url, params=parametros)
        respuesta.raise_for_status()
        datos = respuesta.json()
        contenido_bruto = datos['parse']['text']['*']
        # Utiliza BeautifulSoup para analizar el contenido HTML
        soup = BeautifulSoup(contenido_bruto, 'html.parser')
        # Extrae párrafos y títulos
        contenido_limpio = []
        contenido_actual = {'titulo': '', 'contenido': ''}  # Almacena el contenido actual
        for elemento in soup.find_all(['p', 'h2', 'h3']):
            if elemento.name == 'h2' or elemento.name == 'h3':
                # Guarda el contenido anterior si existe
                if contenido_actual['contenido']:
                    contenido_limpio.append(contenido_actual)
                # Establece el nuevo título
                titulo_actual = elemento.get_text().replace("[edit]", "")
                contenido_actual = {'titulo': titulo_actual, 'contenido': ''}
            else:
                # Añade el párrafo al contenido actual si contiene texto
                texto_parrafo = elemento.get_text().strip()
                if texto_parrafo:
                    contenido_actual['contenido'] += ' ' + texto_parrafo
        # Añade el último contenido actual
        if contenido_actual['contenido']:
            contenido_limpio.append(contenido_actual)
        return contenido_limpio
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el contenido de Wikipedia: {str(e)}")
        return None
    
def guardar_contenido_txt(articulo, contenido, directorio):
    if not os.path.exists(directorio):
        os.makedirs(directorio)

    archivo = os.path.join(directorio, f"{articulo}.txt")
    with open(archivo, 'w', encoding='utf-8') as f:
        for seccion in contenido:
            f.write(seccion['titulo'] + '\n\n')
            f.write(seccion['contenido'] + '\n\n')
    print(f"Contenido guardado en {archivo}")
    
def verificar_y_actualizar_contenido(articulo, contenido_actual, directorio):
    archivo_guardado = os.path.join("contenido_wikipedia", f"{articulo}.txt")

    if os.path.exists(archivo_guardado):
        # Obtiene la fecha de modificación actual de Wikipedia
        fecha_modificacion_actual = obtener_fecha_modificacion(articulo)

        if fecha_modificacion_actual:
            # Lee el archivo guardado
            with open(archivo_guardado, 'r', encoding='utf-8') as f:
                contenido_guardado = f.read()

            # Si el contenido actual es diferente al contenido guardado, actualiza el archivo
            if contenido_actual != contenido_guardado:
                print(f"El contenido de '{articulo}' ha cambiado.")
                guardar_contenido_txt(articulo, contenido_actual)
            else:
                print(f"El contenido de '{articulo}' sigue siendo el mismo.")
        else:
            print(f"No se pudo obtener la fecha de modificación actual de '{articulo}'.")
    else:
        # Si el archivo guardado no existe, lo crea
        guardar_contenido_txt(articulo, contenido_actual, directorio)
        print(f"Contenido de '{articulo}' guardado por primera vez.")