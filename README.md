# Proyecto de Obtención y Almacenamiento de Contenido de Wikipedia

Este proyecto permite obtener páginas de Wikipedia pertenecientes a una categoría específica, obtener información sobre su fecha de modificación y almacenar su contenido en archivos de texto. Además, verifica si el contenido de una página ha cambiado desde la última vez que se obtuvo y, en caso afirmativo, actualiza el archivo de texto correspondiente.
áá# Wikipedia Crawler

Este script en Python funciona como un rastreador de Wikipedia que te permite actualizar contenido, almacenar embeddings y subir documentos a Neo4j.

## Uso

```bash
python wikipedia_crawler.py [--dir DIR] [--index INDEX] [--save] [--update UPDATE] [--neo4j]
```

### Opciones

- `--dir DIR`: Especifica el directorio de almacenamiento. El valor predeterminado es 'data/dominio3.csv'.
- `--index INDEX`: Establece el índice. El valor predeterminado es 'pollution'.
- `--save`: Bandera para almacenar embeddings. Si se proporciona, se almacenarán los embeddings.
- `--update UPDATE`: Especifica si se debe actualizar el contenido. Si se proporciona, se actualizará el contenido.
- `--neo4j`: Bandera para subir documentos a Neo4j. Si se proporciona, se subirán los documentos.

## Requisitos

Asegúrate de tener las dependencias necesarias instaladas. Puedes instalarlas con:

```bash
pip install -r requirements.txt
```

## Funcionalidades

### Actualizar Contenido

Si se proporciona la bandera `--update`, el script actualizará el contenido. Verifica las actualizaciones e imprime el tiempo transcurrido.

```bash
python wikipedia_crawler.py --update
```

### Almacenar Embeddings

Si se proporciona la bandera `--save`, el script almacenará embeddings. Requiere un índice y un directorio.

```bash
python wikipedia_crawler.py --save --index mi_indice --dir mi_directorio
```

### Subir a Neo4j

Si se proporciona la bandera `--neo4j`, el script subirá documentos a Neo4j. Requiere un directorio.

```bash
python wikipedia_crawler.py --neo4j --dir mi_directorio
```

## Ejemplo

```bash
python wikipedia_crawler.py --dir data/mis_datos.csv --index mi_indice --save --update --neo4j
```

Este comando actualizará el contenido, almacenará embeddings y subirá documentos a Neo4j utilizando el directorio e índice especificados.

## Estructura de Archivos y Carpetas
- **scripts/**: Contiene módulos de utilidad para interactuar con Wikipedia y gestionar el almacenamiento de contenido.
- **doc/**: Documentación relacionada con el proyecto.
- **main.py**: Punto de entrada principal del proyecto.
