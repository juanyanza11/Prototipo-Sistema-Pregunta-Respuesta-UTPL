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
        paginas = [pagina['title']
                   for pagina in datos['query']['categorymembers']]
        return paginas
    except requests.exceptions.RequestException as e:
        print(
            f"Error al obtener la lista de páginas en la categoría: {str(e)}")
        return None


import requests
from datetime import datetime

def obtener_fecha_modificacion(pageId, idioma='en'):
    url = f"https://{idioma}.wikipedia.org/w/api.php"
    parametros = {
        'action': 'query',
        'prop': 'revisions',
        'titles': pageId,
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
            fecha_legible = datetime.strptime(
                fecha_modificacion, '%Y-%m-%dT%H:%M:%SZ')
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
            nota_cita.extract()

        # Elimina todas las imágenes con etiqueta <img>
        for img in soup.find_all('img'):
            img.extract()

        # Elimina todas las tablas
        for table in soup.find_all('table'):
            table.extract()

        # Elimina el contenido de las etiquetas span con clase mwe-math-element
        for span in soup.find_all('span', class_='mwe-math-element'):
            span.extract()

        # Extrae párrafos y títulos
        contenido_limpio = []
        # Almacena el contenido actual
        contenido_actual = {'titulo': '', 'contenido': ''}
        for elemento in soup.find_all(['p', 'h2', 'h3', 'h4', 'ul', 'li']):
            if elemento.name in ['h2', 'h3', 'h4']:
                # Guarda el contenido anterior si existe
                if contenido_actual['contenido']:
                    contenido_limpio.append(contenido_actual)
                # Establece el nuevo título
                titulo_actual = elemento.get_text(
                ).strip().replace("[edit]", "")
                contenido_actual = {'titulo': titulo_actual, 'contenido': ''}
            else:
                # Si el contenido es un ul, extrae todos los li en el texto_parrafo
                # Añade el párrafo al contenido actual si contiene texto
                texto_parrafo = elemento.get_text().strip()
                if elemento.name == 'ul':
                    texto_parrafo = ''
                    for li in elemento.find_all('li'):
                        texto_parrafo += ' ' + li.get_text().strip()
                    # Añade el párrafo al contenido actual si contiene texto
                    if texto_parrafo:
                        contenido_actual['contenido'] += ' ' + texto_parrafo
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
    

def verificar_actualizaciones(csv_file):
    # Leer el archivo CSV en un DataFrame de Pandas
    df = pd.read_csv(csv_file)
    cambios = []  # Lista para almacenar información sobre los cambios

    for index, row in df.iterrows():
        pageid = row['WikipageID']
        last_modified = row['LastModified']

        # Obtener la fecha de modificación actual de la página de Wikipedia
        fecha_modificacion_actual = obtener_fecha_modificacion(pageid)

        if fecha_modificacion_actual:
            # Compara las fechas
            if last_modified < fecha_modificacion_actual:
                print(f"Fecha de modificación actual: {fecha_modificacion_actual} - Fecha de modificación guardada: {last_modified}")
                print(f"La página con WikipageID {pageid} necesita actualización.")
                contenido_actual = obtener_contenido_wikipedia_por_pageid(pageid)
                if contenido_actual:
                    print("Cambios en el contenido:")
                    for seccion in contenido_actual:
                        print(f"Sección: {seccion['titulo']}")
                        print(f"Contenido: {seccion['contenido']}\n")
                    # Guardar el contenido actualizado en el mismo archivo CSV
                    contenido_actualizado = "\n".join(
                        [f"{seccion['titulo']}\n{seccion['contenido']}\n" for seccion in contenido_actual])
                    guardar_contenido_actualizado(
                        csv_file, pageid, contenido_actualizado)
                    
                     # Registrar los cambios en la lista
                    cambios.append((pageid, len(contenido_actual)))
                else:
                    print(f"No se pudo obtener el nuevo contenido para WikipageID {pageid}.")
            else:
                print(f"La página con WikipageID {pageid} está actualizada.")
        else:
            print(f"No se pudo obtener la fecha de modificación para WikipageID {pageid}.")
        # Generar el informe de cambios
    generar_informe_cambios(cambios)
    
def generar_informe_cambios(cambios):
    if not cambios:
        print("No se encontraron cambios.")
        return

    informe = "Informe de Cambios en el Contenido:\n\n"
    informe += f"Total de cambios detectados: {len(cambios)}\n\n"

    for pageid, cambios_contenido in cambios:
        informe += f"Página con WikipageID {pageid}: {cambios_contenido} palabras cambiadas\n"

    informe_file = "report/informe_cambios.txt"
    with open(informe_file, 'w') as f:
        f.write(informe)

    print(f"Informe generado y guardado en {informe_file}.")

            
def guardar_contenido_actualizado(csv_file, pageid, contenido_actualizado):
    # Leer el archivo CSV en un DataFrame de Pandas
    df = pd.read_csv(csv_file)

    index = df[df['WikipageID'] == pageid].index

    if not index.empty:
        index = index[0]
        # Actualizar la fila con el contenido actualizado
        df.at[index, 'Contenido'] = contenido_actualizado
        df.at[index, 'LastModified'] = obtener_fecha_modificacion(pageid)

        # Guardar el DataFrame actualizado en el mismo archivo CSV
        df.to_csv(f"data/wikipedia_content_updated.csv", index=False)
        print(f"Contenido actualizado para la página con WikipageID {pageid} en el archivo {csv_file}.")
    else:
        print(f"No se encontró una fila con WikipageID {pageid} en el archivo {csv_file}.")

def obtener_contenido_wikipedia_por_pageid(pageid, idioma='en'):
    url = f"https://{idioma}.wikipedia.org/w/api.php"
    parametros = {
        'action': 'parse',
        'pageid': pageid,  # Usar pageid en lugar de page
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
            nota_cita.extract()

        # Elimina todas las imágenes con etiqueta <img>
        for img in soup.find_all('img'):
            img.extract()

        # Elimina todas las tablas
        for table in soup.find_all('table'):
            table.extract()

        # Elimina el contenido de las etiquetas span con clase mwe-math-element
        for span in soup.find_all('span', class_='mwe-math-element'):
            span.extract()

        # Extrae párrafos y títulos
        contenido_limpio = []
        # Almacena el contenido actual
        contenido_actual = {'titulo': '', 'contenido': ''}
        for elemento in soup.find_all(['p', 'h2', 'h3', 'h4', 'ul', 'li']):
            if elemento.name in ['h2', 'h3', 'h4']:
                # Guarda el contenido anterior si existe
                if contenido_actual['contenido']:
                    contenido_limpio.append(contenido_actual)
                # Establece el nuevo título
                titulo_actual = elemento.get_text(
                ).strip().replace("[edit]", "")
                contenido_actual = {'titulo': titulo_actual, 'contenido': ''}
            else:
                # Si el contenido es un ul, extrae todos los li en el texto_parrafo
                # Añade el párrafo al contenido actual si contiene texto
                texto_parrafo = elemento.get_text().strip()
                if elemento.name == 'ul':
                    texto_parrafo = ''
                    for li in elemento.find_all('li'):
                        texto_parrafo += ' ' + li.get_text().strip()
                    # Añade el párrafo al contenido actual si contiene texto
                    if texto_parrafo:
                        contenido_actual['contenido'] += ' ' + texto_parrafo
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

def guardar_contenido_csv(articulo, contenido, fecha_modificacion, directorio):
    archivo_csv = directorio

    # Verificar si el archivo CSV ya existe
    if not os.path.isfile(archivo_csv):
        # Si no existe, crear el archivo y escribir la cabecera
        with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerow(
                ['Pagina', 'Topic', 'Contenido', 'Fecha_Modificacion'])

    # Guardar el contenido en el archivo CSV
    with open(archivo_csv, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='|')
        for seccion in contenido:
            titulo = seccion['titulo'] if seccion['titulo'].strip(
            ) != '' else 'General'
            writer.writerow(
                [articulo, titulo, seccion['contenido'], fecha_modificacion])
    print(f"Contenido de '{articulo}' guardado en {archivo_csv}")


def verificar_y_actualizar_contenido(articulo, contenido_actual, directorio):
    fecha_modificacion_actual = obtener_fecha_modificacion(articulo)
    fecha_modificacion_actual_time = datetime.strptime(
        fecha_modificacion_actual, '%Y-%m-%d-%H-%M-%S')

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
                fecha_guardada_datetime = datetime.strptime(
                    fecha_guardada_str, '%Y-%m-%d-%H-%M-%S')

                print(
                    f"Fecha de modificación actual: {fecha_modificacion_actual}")
                print(f"Fecha de modificación guardada: {fecha_guardada_str}")

                # Compara las fechas
                if fecha_modificacion_actual_time > fecha_guardada_datetime:
                    print(f"El contenido de '{articulo}' ha cambiado.")
                    guardar_contenido_csv(
                        articulo, contenido_actual, fecha_modificacion_actual, directorio)
                else:
                    print(
                        f"El contenido de '{articulo}' sigue siendo el mismo.")
            else:
                # Si no hay datos en el DataFrame para el artículo, guarda el contenido por primera vez
                guardar_contenido_csv(
                    articulo, contenido_actual, fecha_modificacion_actual, directorio)
                print(f"Contenido de '{articulo}' guardado por primera vez.")
        else:
            # Si el archivo CSV no existe, guarda el contenido por primera vez
            guardar_contenido_csv(articulo, contenido_actual,
                                  fecha_modificacion_actual, directorio)
            print(f"Contenido de '{articulo}' guardado por primera vez.")
    else:
        print(
            f"No se pudo obtener la fecha de modificación actual de '{articulo}'.")
