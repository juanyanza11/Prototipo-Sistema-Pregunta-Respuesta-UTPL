import csv
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import pandas as pd
import wikipedia


def obtener_fecha_modificacion(pageId, idioma='en'):
    import requests
    from datetime import datetime
    
    url = f"https://{idioma}.wikipedia.org/w/api.php"
    parametros = {
        'action': 'query',
        'prop': 'revisions',
        'pageids': pageId,
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
                        print(f"Sección: {seccion['title']}")
                        print(f"Contenido: {seccion['content']}\n")
                    # Guardar el contenido actualizado en el mismo archivo CSV
                    contenido_actualizado = "\n".join(
                        [f"{seccion['title']}\n{seccion['content']}\n" for seccion in contenido_actual])
                    contenido_text = seccion['content'] 
                    guardar_contenido_actualizado(
                        csv_file, pageid, contenido_text, index)
                    
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

def guardar_contenido_actualizado(csv_file, pageid, contenido_actualizado, index):
    # Leer el archivo CSV en un DataFrame de Pandas
    df = pd.read_csv(csv_file)

    # Buscar el índice de la fila que coincide con el 'WikipageID'
    # index = df[df['WikipageID'] == pageid].index

    if not index:
        # Actualizar la fila con el contenido actualizado
        df.at[index, 'Contenido'] = contenido_actualizado
        df.at[index, 'LastModified'] = obtener_fecha_modificacion(pageid)

        # Guardar el DataFrame actualizado en el mismo archivo CSV
        df.to_csv('data/updated.csv', encoding='utf-8', index=False)
        print(f"Contenido actualizado para la página con WikipageID {pageid} en el archivo {csv_file}.")
    else:
        print(f"No se encontró una fila con WikipageID {pageid} en el archivo {csv_file}.")


def obtener_contenido_wikipedia_por_pageid(page_id, lang='en'):
    # Define the Wikipedia API endpoint
    wikipedia_url = f"https://{lang}.wikipedia.org/w/api.php"

    # Define the parameters for the API request
    api_params = {
        'action': 'query',
        'pageids': page_id,
        'prop': 'revisions',
        'rvprop': 'timestamp',
        'format': 'json'
    }

    # Get the Wikipedia page object
    page = wikipedia.page(pageid=page_id, auto_suggest=False)
    title = page.title
    page_url = page.url
    wikipage_id = page.pageid

    # Make a request to the Wikipedia API
    response = requests.get(wikipedia_url, params=api_params)
    response.raise_for_status()
    api_data = response.json()

    # Extract the timestamps of the latest and creation revisions
    page_data = api_data['query']['pages'][str(page_id)]
    latest_revision = page_data['revisions'][0]
    creation_revision = page_data['revisions'][-1]
    creation_date = creation_revision['timestamp']
    last_modified = latest_revision['timestamp']
    wikipedia.set_lang(lang)

    # Split the page content into sections
    content = page.content.split('\n')

    sections = []
    current_section = None
    sub_section = None
    exclude_sections = ["== See also ==", "== References ==", "== External links =="]

    for line in content:
        if line:
            line = line.strip()
        else:
            continue

        if line.startswith("===") and line.endswith("===") and line not in exclude_sections:
            sub_section = line.strip("=")
        elif line.startswith("==") and line.endswith("=="):
            current_section = line.strip("=")
        else:
            if current_section not in exclude_sections:
                if sections and sections[-1]['section'] == sub_section and sections[-1]['creation_date'] == current_section:
                    # sections[-1] = (page_url, title, creation_date, sections[-1][3], sections[-1][4], sections[-1][5] + " " + line, wikipage_id, last_modified)
                    sections[-1] = {
                        'page_url': page_url,
                        'title': title,
                        'creation_date': creation_date,
                        'section': sections[-1]['section'],
                        'sub_section': sections[-1]['sub_section'],
                        'content': sections[-1]['content'] + " " + line,
                        'wikipage_id': wikipage_id,
                        'last_modified': last_modified
                    }
                else:
                    sections.append({
                        'page_url': page_url,
                        'title': title,
                        'creation_date': creation_date,
                        'section': current_section,
                        'sub_section': sub_section,
                        'content': line,
                        'wikipage_id': wikipage_id,
                        'last_modified': last_modified
                    })
            elif current_section is None:
                sections.append((page_url, title, creation_date, None, None, line, wikipage_id, last_modified))
    
    print(f"Se obtuvieron {len(sections)} secciones.")
    return sections