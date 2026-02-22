# Desarrollo de una plataforma OTT sobre una red SDN - Trabajo de Fin de Grado

Este repositorio contiene los archivos y scripts utilizados para el diseño, simulación y análisis de una plataforma de video Over-The-Top (OTT) desplegada sobre una red definida por software (SDN).

## 📂 Estructura del Repositorio

* **`hls/`**: Directorio que contiene los segmentos de video (.ts) y la lista de reproducción (.m3u8) preparados para el protocolo HTTP Live Streaming.
* **`media/`**: Directorio que contiene los archivos de vídeo originales antes de ser procesados o segmentados para el protocolo HLS.
* **`topo_sdn_video_streaming.py`**: Script de Python que define la topología de red en Mininet.
* **`topo_sdn_video_streaming_dynamic_qos.py`**: Variante de la topología que incluye gestión dinámica de Calidad de Servicio (QoS).
* **`cliente.py`**: Script para simular las peticiones de un cliente OTT y medir el rendimiento.
* **`run_experiments.sh`**: Script de Bash para automatizar la ejecución de múltiples pruebas de streaming, facilitando la recolección de datos y capturas de tráfico de forma secuencial.
* **`ejecutar el entorno.txt`**: Guía rápida con los comandos necesarios para levantar el escenario.

## 🛠️ Requisitos Técnicos

Para ejecutar este proyecto, es necesario contar con:
1.  **Mininet** (Simulador de red).
2.  Un controlador SDN (como **Ryu** o el controlador nativo de Mininet).
3.  **Python 3.8.10**.
4.  Servidor HTTP (módulo `http.server` de Python) para servir el contenido HLS.
