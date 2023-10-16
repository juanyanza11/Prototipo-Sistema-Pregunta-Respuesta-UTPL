from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import requests
import pandas as pd
import wikipedia
from difflib import SequenceMatcher


def obtener_fecha_modificacion(pageId, idioma='en'):

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
    df = pd.read_csv(csv_file)
    cambios = []

    def process_page(pageid, contenido_actual, group):
        for index, row in group.iterrows():
            for parrafo in contenido_actual:
                similarity = SequenceMatcher(
                    None, row['Contenido'], parrafo).ratio()

                if 0.7 < similarity < 1:
                    indice = df[df['Contenido'] == row['Contenido']].index[0]
                    guardar_contenido_actualizado(
                        csv_file, pageid, parrafo, indice, fecha_modificacion_actual)
                    cambios.append(
                        (pageid, row['Contenido'], parrafo, row['Title']))
                    print(f"Contenido con cambios: {parrafo} ({similarity})")
                    print(
                        f"Contenido anterior: {row['Contenido']} ({similarity})")

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        df_grouped = df.groupby('WikipageID')
        for pageid, group in df_grouped:
            last_modified = group['LastModified'].max()
            fecha_modificacion_actual = obtener_fecha_modificacion(pageid)

            if fecha_modificacion_actual:
                if fecha_modificacion_actual > last_modified:
                    print(
                        f"Ultima modificacion: {last_modified} - Fecha actual de modificacion: {fecha_modificacion_actual}")
                    contenido_actual = obtener_contenido_wikipedia_por_pageid(
                        pageid)
                    list_contenido_actual = [c['content']
                                             for c in contenido_actual if str(c['content'])]

                    future = executor.submit(
                        process_page, pageid, list_contenido_actual, group)
                    futures.append(future)
                else:
                    print(
                        f"La página con WikipageID {pageid} está actualizada.")
            else:
                print(
                    f"No se pudo obtener la fecha de modificación para WikipageID {pageid}.")

        for future in futures:
            future.result()

    generar_informe_cambios(cambios)


def generar_informe_cambios(cambios):
    if not cambios:
        print("No se encontraron cambios.")
        return

    informe = "Informe de Cambios en el Contenido:\n\n"
    informe += f"Total de cambios detectados: {len(cambios)}\n\n"

    for pageid, original, actualizado, title in cambios:
        informe += f"Cambios para {title} - {pageid} : \n\nParrafo original:\n{original} \n\nParrafo actualizado:\n{actualizado} \n\n"

    informe_file = "report/informe_cambios.txt"
    with open(informe_file, 'w', encoding="utf-8") as f:
        f.write(informe)

    print(f"Informe generado y guardado en {informe_file}.")


def guardar_contenido_actualizado(csv_file, pageid, contenido_actualizado, index, fecha_modificacion=None):
    df = pd.read_csv(csv_file)

    if index:
        df.at[index, 'Contenido'] = contenido_actualizado
        df.at[index, 'LastModified'] = fecha_modificacion

        df.to_csv('data/updated.csv', encoding='utf-8', index=False)
        print(
            f"Contenido actualizado para la página con WikipageID {pageid} en el archivo {csv_file}.")
    else:
        print(
            f"No se encontró una fila con WikipageID {pageid} en el archivo {csv_file}.")


def obtener_contenido_wikipedia_por_pageid(page_id, lang='en'):
    wikipedia_url = f"https://{lang}.wikipedia.org/w/api.php"

    api_params = {
        'action': 'query',
        'pageids': page_id,
        'prop': 'revisions',
        'rvprop': 'timestamp',
        'format': 'json'
    }

    page = wikipedia.page(pageid=page_id, auto_suggest=False)
    title = page.title
    page_url = page.url
    wikipage_id = page.pageid

    response = requests.get(wikipedia_url, params=api_params)
    response.raise_for_status()
    api_data = response.json()

    page_data = api_data['query']['pages'][str(page_id)]
    latest_revision = page_data['revisions'][0]
    creation_revision = page_data['revisions'][-1]
    creation_date = creation_revision['timestamp']
    last_modified = latest_revision['timestamp']
    wikipedia.set_lang(lang)

    content = page.content.split('\n')

    sections = []
    current_section = None
    sub_section = None
    exclude_sections = ["== See also ==",
                        "== References ==", "== External links =="]

    for line in content:
        if line:
            line = line.strip()
        else:
            continue

        if line.startswith("===") and line.endswith("===") and line not in exclude_sections:
            sub_section = line.strip("=")
        elif line.startswith("==") and line.endswith("=="):
            section = line.strip("=")
            current_section = section

        else:
            if current_section not in exclude_sections:
                if sections and sections[-1]['sub_section'] == sub_section and sections[-1]['section'] == current_section:
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
                sections.append((page_url, title, creation_date,
                                None, None, line, wikipage_id, last_modified))

    print(f"Se obtuvieron {len(sections)} secciones para {page_id}.")
    return sections
