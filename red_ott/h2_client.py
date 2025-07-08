#!/usr/bin/env python3
import subprocess
import time
import os

def obtener_bw(ruta="/tmp/bw.txt"):
    try:
        with open(ruta, "r") as f:
            bw_str = f.read().strip()
            return float(bw_str)
    except Exception as e:
        print("Error al obtener BW desde archivo:", e)
        return None

def elegir_calidad(bw):
    if bw is None:
        return None
    if bw < 0.6:
        return "360p"
    elif bw < 1.0:
        return "480p"
    else:
        return "720p"

def descargar_contenido(url):
    print(f"Descargando contenido '{url}'")
    subprocess.run(['ffmpeg', url])

if __name__ == '__main__':
    bw = obtener_bw()
    print(f"Ancho de banda recibido: {bw} Mbps")
    calidad = elegir_calidad(bw)
    if calidad:
        url = f"ffmpeg http://10.0.0.1:8080/playlist_{calidad}.m3u8"
        descargar_contenido(url)
    else:
        print("No se pudo determinar la calidad adecuada.")
