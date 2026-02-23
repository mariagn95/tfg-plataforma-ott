# Desarrollo de una plataforma OTT sobre una red SDN - Trabajo de Fin de Grado

Este repositorio contiene los archivos y scripts utilizados para el diseño, simulación y análisis de una plataforma de video Over-The-Top (OTT) desplegada sobre una red definida por software (SDN).

## 📂 Estructura del Repositorio

* **`hls/`**: Directorio que contiene los segmentos de vídeo en formato .ts y las listas de reproducción .m3u8 generados conforme al protocolo HLS. Este contenido es el que se sirve desde el host servidor durante la ejecución de los experimentos.
* **`media/`**: Directorio que almacena los archivos de vídeo originales y las versiones intermedias previas a la segmentación HLS. Su función es mantener separados los archivos fuente del contenido preparado para streaming.
* **`topo_sdn_video_streaming.py`**: Script de Python que define la topología de red del escenario estático en Mininet, incluyendo hosts, switch y enlaces con limitación fija de ancho de banda.
* **`topo_sdn_video_streaming_dynamic_qos.py`**: Variante de la topología que incluye gestión dinámica de ancho de banda, permitiendo simular variaciones de Calidad de Servicio (QoS) durante la ejecución.
* **`cliente.py`**: Script que simula el comportamiento de un cliente OTT, automatizando la selección de calidad y permitiendo realizar capturas de tráfico para el análisis experimental.
* **`run_experiments.sh`**: Script en Bash que automatiza la ejecución de los distintos escenarios, incluyendo el lanzamiento del controlador, la creación de la topología y la ejecución de las pruebas de streaming.
* **`guia_ejecucion_entorno.txt`**: Documento de apoyo que describe los comandos necesarios para desplegar manualmente el entorno experimental, incluyendo la ejecución del script principal y los requisitos de privilegios del sistema.

## 🛠️ Requisitos Técnicos

Para ejecutar este proyecto, es necesario contar con:
1.  **Mininet** (Simulador de red).
2.  Un controlador SDN (como **Ryu** o el controlador nativo de Mininet).
3.  **Python 3.8.10**.
