# Proyecto de Obtención y Almacenamiento de Contenido de Wikipedia

Este proyecto permite obtener páginas de Wikipedia pertenecientes a una categoría específica, obtener información sobre su fecha de modificación y almacenar su contenido en archivos de texto. Además, verifica si el contenido de una página ha cambiado desde la última vez que se obtuvo y, en caso afirmativo, actualiza el archivo de texto correspondiente.

## Requisitos

Antes de ejecutar el proyecto, asegúrate de tener instalado Python en tu sistema. También debes instalar las bibliotecas requeridas. Puedes hacerlo ejecutando:

```bash
pip install requests beautifulsoup4
```

## Uso

- Para ejecutar el proyecto, sigue estos pasos:

- Clona o descarga este repositorio en tu máquina local.

- Abre una terminal y navega hasta el directorio del proyecto.

- Ejecuta el archivo main.py con el siguiente comando:

```bash
python main.py
```

El script main.py utiliza la función obtener_paginas_categoria para obtener una lista de páginas de Wikipedia pertenecientes a una categoría especificada. A continuación, verifica si el contenido de cada página ha cambiado desde la última vez que se obtuvo y, en caso afirmativo, actualiza el archivo de texto correspondiente en el directorio "contenido_wikipedia".

## Parámetros
Puedes personalizar el comportamiento del proyecto modificando los siguientes parámetros en el archivo main.py:

- **categoria_wikipedia**: La categoría de Wikipedia que deseas explorar.
- **idioma_wikipedia**: El idioma de Wikipedia que deseas utilizar (por defecto, 'en' para inglés).
- **limite_paginas**: El límite de páginas que deseas obtener.

## Estructura de Archivos y Carpetas
- **scripts/**: Contiene módulos de utilidad para interactuar con Wikipedia y gestionar el almacenamiento de contenido.
- **doc/**: Documentación relacionada con el proyecto.
- **main.py**: Punto de entrada principal del proyecto.