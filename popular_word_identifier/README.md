# Popular Word Identifier

## Descripcón del proyecto

El objetivo de este proyecto es proporcionar una herramienta que extraiga las palabras más utilizadas para nombrar funciones y métodos en proyectos Python y Java dentro de github. Para ello, se procedera a obtener y procesar las palabras obtenidas de repositorios ordenados de manera decendente considerando su cantidad de estrellas, procesar el nombre de las funciones y métodos para obtener las palabras naturales y finalmente, se mostrará un top que se actualiza en tiempo real entre más palabras entregue el componente miner.

## Herrramientas a utilizar

- Para el componente **miner** se utilizará **Python** para obtener los enlaces de los repositorios, los archivos .java y .py de estos, y finalmente extraer las palabras de los nombres de las funciones y métodos.
- Para el componente **visualizer** se utilizará **Javascript** para mostrar un top de cantidad configurable de las palabras más utilizadas que se actualiza en tiempo real entre más palabras entregue el componente miner.

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