#!/usr/bin/env python3
import sys
import socket
import subprocess
import os
from datetime import datetime

SERVER_IP = "10.0.0.1"
SERVER_PORT = 8080

def _get_host_name():
    #Identifica el host cliente (h2, h3, etc.) basándose en su IP local
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((SERVER_IP, SERVER_PORT))
        ip = s.getsockname()[0]
        return f"h{ip.split('.')[-1]}"
    except:
        return "host"
    finally:
        s.close()

def main():
    # Parámetro único: calidad (720p, 480p, 360p). Si no hay, usa el archivo maestro
    calidad_input = sys.argv[1] if len(sys.argv) > 1 else "master"

    if calidad_input in ["720p", "480p", "360p"]:
        recurso = f"{calidad_input}_playlist.m3u8"
        calidad_tag = calidad_input
    else:
        recurso = "master.m3u8"
        calidad_tag = "master"

    url = f"http://{SERVER_IP}:{SERVER_PORT}/{recurso}"
    host = _get_host_name()
    timestamp = datetime.now().strftime("%H%M%S")
    
    # Formato de captura de tráfico
    pcap_file = f"{host}_{calidad_tag}_{timestamp}.pcap"
    
    # Comando del reproductor
    vlc_cmd = ["vlc-wrapper", "--no-audio", "--no-qt-privacy-ask", "--play-and-exit", url]

    # Salida por consola detallada
    print(f"[INFO] {host} reproduciendo {recurso}.")
    print(f"[INFO] Captura: {pcap_file}")
    print(f"[INFO] URL: {' '.join(vlc_cmd)}")

    # Iniciar captura tcpdump
    tcp_cmd = ["tcpdump", "-n", "-i", "any", "host", SERVER_IP, "and", "port", str(SERVER_PORT), "-w", pcap_file]
    
    tcpdump_proc = None
    try:
        # Ejecución de la captura de tráfico
        tcpdump_proc = subprocess.Popen(tcp_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Ejecución del reproductor (bloquea hasta que VLC cierra)
        subprocess.run(vlc_cmd)
        
    finally:
        # Bloque robusto de cierre
        if tcpdump_proc and tcpdump_proc.poll() is None:
            tcpdump_proc.terminate()
            try:
                tcpdump_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                tcpdump_proc.kill()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
