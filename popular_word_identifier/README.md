# Popular Word Identifier

## Descripcón del proyecto

El objetivo de este proyecto es proporcionar una herramienta que extraiga las palabras más utilizadas para nombrar funciones y métodos en proyectos Python y Java dentro de github. Para ello, se procedera a obtener y procesar las palabras obtenidas de repositorios ordenados de manera decendente considerando su cantidad de estrellas, procesar el nombre de las funciones y métodos para obtener las palabras naturales y finalmente, se mostrará un top que se actualiza en tiempo real entre más palabras entregue el componente miner.

## Herrramientas a utilizar

- Para el componente **miner** se utilizará:
  - **Python** para la extracción principal de GitHub (archivos, enlaces y palabras de funciones y métodos).
  - **Flask** y **Flask-CORS** para la creación de la API REST que comunica al miner con el frontend de manera segura.
  - **Multithreading** y **Queue (Colas)** para lograr una ejecución concurrente entre el servidor y el proceso de minería, pasando mensajes libremente.
  - **Python-dotenv** para el manejo de credenciales mediante variables de entorno.
- Para el componente **visualizer** se utilizará:
  - **JavaScript** (Vanilla) y HTML/CSS para la interfaz de usuario.
  - **Chart.js** para la renderización de los gráficos de barras, mostrando las palabras más utilizadas.
  - **Server-Sent Events (SSE)** para mantener una conexión en tiempo real unidireccional, actualizando el "Top N" sin necesidad de recargar la página.

## Arquitectura del proyecto

    ├── compose.yml          # Orquestación de contenedores Miner y Visualizer
    ├── README.md                   # Documentación principal
    ├── /miner                  # Componente de Minería (Python)
    │   ├── /getter_repo        # Consulta a GitHub API (ordenado por estrellas)
    │   ├── /getter_files       # Descarga efímera de archivos .py y .java
    │   ├── /parser             # Extracción de identificadores mediante AST
    │   ├── /convert            # Tokenización (CamelCase/snake_case a Natural)
    │   └── /controller         # API REST (Control) y SSE Endpoint (Data Stream)
    └── /visualizer             # Componente de Visualización (JavaScript)
        ├── /interface          # UI para control de procesos y gráficas
        └── /word_processor     # Procesamiento de frecuencias y lógica de ranking