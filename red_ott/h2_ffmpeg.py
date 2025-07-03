#!/usr/bin/env python3
import subprocess
import time
import os

def obtener_bw(host='10.0.0.1', puerto=9999):
    try:
        resultado = subprocess.run(['nc', host, str(puerto)], capture_output=True, text=True, timeout=5)
        bw_str = resultado.stdout.strip()
        return float(bw_str)
    except Exception as e:
        print("Error al obtener BW:", e)
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

def reproducir_con_ffplay(url):
    print(f"Reproduciendo {url} con ffplay...")
    subprocess.run(['ffplay', url])

if __name__ == '__main__':
    bw = obtener_bw()
    print(f"Ancho de banda recibido: {bw} Mbps")

    calidad = elegir_calidad(bw)
    if calidad:
        url = f"http://10.0.0.1/hls/{calidad}.m3u8"
        reproducir_con_ffplay(url)
    else:
        print("No se pudo determinar la calidad adecuada.")
