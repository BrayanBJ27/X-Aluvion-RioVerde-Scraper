# X (Twitter) Scraper

## Descripción
**Twitter Scraper** es una herramienta en Python que utiliza Playwright para automatizar la extracción de tweets en Twitter basados en un query de búsqueda. El scraper realiza lo siguiente:

- Carga los tweets existentes desde un archivo CSV para evitar duplicados.
- Realiza una búsqueda en Twitter con el query proporcionado.
- Extrae información de los tweets, incluyendo:
    - Texto del tweet.
    - Enlace al tweet.
    - Usuario.
    - Número de likes.
    - Número de retweets.
    - Número de vistas.
    - Hashtags.
    - Comentarios.
- Guarda los datos extraídos en un archivo CSV (`tweets.csv`).
- Guarda el estado de las cookies en un archivo (`twitter_cookies.json`) para mantener la sesión.

## Requisitos

- **Python 3.7+**
- **Playwright**

Instalarlo con:

```bash
pip install playwright
playwright install
```

Los módulos csv, os y re forman parte de la biblioteca estándar de Python.

## Instalación

Clonar el repositorio:

```bash
git clone https://github.com/BrayanBJ27/X-Aluvion-RioVerde-Scraper.git
cd twitter-scraper
```

Crear un entorno virtual (opcional, pero recomendado):

```bash
python -m venv venv
```

En Linux/Mac:

```bash
source venv/bin/activate
```

En Windows:

```bash
venv\Scripts\activate
```

Instalar las dependencias (crea un archivo requirements.txt y luego instala):

```bash
pip install -r requirements.txt
```

## Configuración

El scraper utiliza un archivo de cookies (`twitter_cookies.json`) para mantener el estado de sesión.
Si este archivo no existe, se creará automáticamente al ejecutar el script.
Puedes modificar el query de búsqueda directamente en el código o adaptarlo para que se lea desde variables de entorno.

## Ejecución

Para ejecutar el scraper:

```bash
python twitter_scraper.py
```

## Advertencias

- **Uso Ético**: Este scraper es para fines educativos. Asegúrate de cumplir con los Términos y Condiciones de Twitter y de utilizarlo de forma responsable.
- **Manejo de Cookies**: El archivo `twitter_cookies.json` se utiliza para mantener la sesión. Mantenlo seguro.
- **Limitaciones**: Los tiempos de espera y otros parámetros pueden necesitar ajustes según la velocidad de conexión y la respuesta del sitio.

## Estructura del Proyecto

```bash
twitter-scraper/
│
├── twitter_scraper.py       # Script principal del scraper.
├── requirements.txt         # Dependencias del proyecto.
└── README.md                # Documentación del proyecto.
```