# Sistema de Análisis de Inversiones Inmobiliarias

Este proyecto es un sistema completo para el análisis de inversiones inmobiliarias que incluye web scraping en Python y un frontend en Java con PrimeFaces.

## Componentes

El sistema consta de dos componentes principales:

### 1. Backend de Web Scraping (Python)

- Extrae datos de propiedades de sitios web inmobiliarios españoles (idealista.com, fotocasa.es, etc.)
- Almacena los datos en MongoDB (con soporte de fallback para PostgreSQL)
- Realiza un seguimiento de listados nuevos y modificados
- Utiliza algoritmos de aprendizaje automático para identificar oportunidades de inversión

### 2. Frontend (Java PrimeFaces)

- Consume los datos del backend a través de una API
- Muestra oportunidades de inversión en mapas interactivos
- Permite filtrar por regiones seleccionadas
- Proporciona análisis detallado de cada propiedad

## Estructura del Proyecto

```
.
├── api/                       # API de Flask para acceder a los datos
│   ├── services/              # Servicios para análisis y gestión de propiedades
│   ├── static/                # Archivos estáticos
│   ├── templates/             # Plantillas HTML
│   ├── utils/                 # Utilidades, incluyendo conexión a BD
│   ├── app.py                 # Aplicación principal de Flask
│   ├── main.py                # Punto de entrada para la API
│   └── models.py              # Modelos de datos
├── scraper/                   # Web scraper basado en Scrapy
│   ├── realestate/            # Proyecto Scrapy
│   │   ├── spiders/           # Arañas para diferentes sitios web
│   │   ├── utils/             # Utilidades para el scraping
│   │   ├── items.py           # Definición de elementos a extraer
│   │   ├── middlewares.py     # Middlewares para manejar proxies, etc.
│   │   ├── pipelines.py       # Pipelines para procesar datos
│   │   └── settings.py        # Configuración del scraper
│   ├── main.py                # Punto de entrada para el scraper
│   └── scheduler.py           # Programador de tareas
├── java-frontend/             # Frontend Java con PrimeFaces (no incluido en el paquete actual)
├── main.py                    # Punto de entrada principal del sistema
├── pyproject.toml             # Configuración de Python
└── README.md                  # Este archivo
```

## Características

- **Detección de propiedades nuevas/modificadas**: El sistema identifica automáticamente nuevos listados y cambios en listados existentes.
- **Análisis de inversión**: Utiliza datos históricos para identificar propiedades con potencial de inversión.
- **Visualización geoespacial**: Muestra propiedades en mapas interactivos con filtrado por zona.
- **Conexión a base de datos flexible**: Utiliza MongoDB como base de datos principal con PostgreSQL como fallback.
- **Técnicas anti-detección**: Implementa rotación de proxies y user agents para evitar ser bloqueado durante el scraping.

## Requisitos

- Python 3.10+
- MongoDB o PostgreSQL
- Java 17+ (para el frontend)

## Configuración

1. Configura las variables de entorno:
   - `MONGODB_URI`: URL de conexión a MongoDB (opcional)
   - `MONGODB_DATABASE`: Nombre de la base de datos MongoDB (opcional)
   - `DATABASE_URL`: URL de conexión a PostgreSQL (opcional)

2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

3. Inicia la API:
   ```
   python main.py
   ```

## Licencia

Este proyecto está licenciado bajo la Licencia MIT.