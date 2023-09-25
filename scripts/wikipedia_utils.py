import csv
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import os
import re
import pandas as pd

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
            # Convertir la fecha al formato legible con guiones bajos
            fecha_legible = datetime.strptime(fecha_modificacion, '%Y-%m-%dT%H:%M:%SZ')
            fecha_formateada = fecha_legible.strftime('%Y-%m-%d-%H-%M-%S')
            return fecha_formateada
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
        # Encuentra y elimina las notas de cita (contenido entre corchetes)
        for nota_cita in soup.find_all("sup", class_="reference"):
            nota_cita.extract()  # Elimina el elemento del contenido

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
                # Reemplaza [update] por una cadena vacía en el texto del párrafo
                texto_parrafo = re.sub(r'\[update\]', '', texto_parrafo)
                if texto_parrafo:
                    contenido_actual['contenido'] += ' ' + texto_parrafo
        # Añade el último contenido actual
        if contenido_actual['contenido']:
            contenido_limpio.append(contenido_actual)
        return contenido_limpio
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener el contenido de Wikipedia: {str(e)}")
        return None
    
def guardar_contenido_txt(articulo, contenido, directorio, fecha_modificacion):
    if not os.path.exists(directorio):
        os.makedirs(directorio)
        
    articulo = articulo.replace(' ', '_')
    archivo = os.path.join(directorio, f"{fecha_modificacion}_{articulo}.txt")
    with open(archivo, 'w', encoding='utf-8') as f:
        for seccion in contenido:
            f.write(seccion['titulo'] + '\n\n')
            f.write(seccion['contenido'] + '\n\n')
    print(f"Contenido guardado en {archivo}")
    
def guardar_contenido_csv(articulo, contenido, fecha_modificacion):
    archivo_csv = 'data/contenido_wikipedia.csv'

    # Verificar si el archivo CSV ya existe
    if not os.path.isfile(archivo_csv):
        # Si no existe, crear el archivo y escribir la cabecera
        with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow(['Pagina', 'Topic', 'Contenido', 'Fecha_Modificacion'])

    # Guardar el contenido en el archivo CSV
    with open(archivo_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='|')
        for seccion in contenido:
            writer.writerow([articulo, seccion['titulo'], seccion['contenido'], fecha_modificacion])
    print(f"Contenido de '{articulo}' guardado en {archivo_csv}")
    
def verificar_y_actualizar_contenido(articulo, contenido_actual, directorio):
    fecha_modificacion_actual = obtener_fecha_modificacion(articulo)
    fecha_modificacion_actual_time = datetime.strptime(fecha_modificacion_actual, '%Y-%m-%d-%H-%M-%S')
    
    if fecha_modificacion_actual:
        # Verifica si el archivo CSV existe
        archivo_csv = directorio
        if os.path.isfile(archivo_csv):
            # Lee el archivo CSV en un DataFrame de Pandas
            df = pd.read_csv(archivo_csv,  delimiter='|', encoding='utf-8')
            # Filtra las filas correspondientes al artículo actual
            filas_articulo = df[df['Pagina'] == articulo]
            if not filas_articulo.empty:
                # Obtiene la fecha de modificación guardada en el CSV
                fecha_guardada_str = filas_articulo['Fecha_Modificacion'].iloc[0]
                fecha_guardada_datetime = datetime.strptime(fecha_guardada_str, '%Y-%m-%d-%H-%M-%S')
                
                print(f"Fecha de modificación actual: {fecha_modificacion_actual}")
                print(f"Fecha de modificación guardada: {fecha_guardada_str}")
                
                # Compara las fechas
                if fecha_modificacion_actual_time > fecha_guardada_datetime:
                    print(f"El contenido de '{articulo}' ha cambiado.")
                    guardar_contenido_csv(articulo, contenido_actual, fecha_modificacion_actual)
                else:
                    print(f"El contenido de '{articulo}' sigue siendo el mismo.")
            else:
                # Si no hay datos en el DataFrame para el artículo, guarda el contenido por primera vez
                guardar_contenido_csv(articulo, contenido_actual, fecha_modificacion_actual)
                print(f"Contenido de '{articulo}' guardado por primera vez.")
        else:
            # Si el archivo CSV no existe, guarda el contenido por primera vez
            guardar_contenido_csv(articulo, contenido_actual, fecha_modificacion_actual)
            print(f"Contenido de '{articulo}' guardado por primera vez.")
    else:
        print(f"No se pudo obtener la fecha de modificación actual de '{articulo}'.")
