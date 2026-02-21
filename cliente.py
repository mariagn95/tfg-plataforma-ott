import sys
import subprocess
import re
import socket
import os

def obtener_datos_por_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.0.0.1", 8080))
        ip_local = s.getsockname()[0]
        s.close()
    except Exception:
        sys.exit(1)

    try:
        with open("reporte_anchos_banda.txt", "r") as f:
            for linea in f:
                if f"IP: {ip_local}" in linea:
                    nombre = re.search(r"Host: (h\d+)", linea).group(1)
                    bw = float(re.search(r"Ancho de Banda: ([\d.]+) Mbps", linea).group(1))
                    return nombre, bw, ip_local
    except Exception:
        sys.exit(1)
    return None, None, ip_local

if len(sys.argv) < 2:
    sys.exit(1)

reproductor = sys.argv[1]
host, bw, ip = obtener_datos_por_ip()

if host is None:
    sys.exit(1)

if bw <= 0.5:
    playlist = "360p_playlist.m3u8"
elif bw <= 1.0:
    playlist = "480p_playlist.m3u8"
else:
    playlist = "720p_playlist.m3u8"

url = f"http://10.0.0.1:8080/{playlist}"
pcap_file = f"{host}_{playlist.replace('.m3u8', '')}.pcap"

# 1. Iniciar captura silenciosa (esto no se ve en el terminal)
tcpdump_cmd = f"tcpdump -i any port 8080 -w {pcap_file} > /dev/null 2>&1 &"
subprocess.Popen(tcpdump_cmd, shell=True)

try:
    if "vlc" in reproductor.lower():
        # VLC necesita esta bandera para cerrarse solo
        subprocess.run(["vlc-wrapper", url, "--play-and-exit"])
    
    elif "ffplay" in reproductor.lower():
        # FFplay también tiene su propia bandera para cerrarse al terminar
        subprocess.run(["ffplay", "-autoexit", url])

    elif "ffmpeg" in reproductor.lower():
        # Lanzamos: ffmpeg -i http://... -c copy -f null -
        print(f" Lanzando descarga de prueba con FFmpeg: {url}")
        subprocess.run(["ffmpeg", "-i", url, "-c", "copy", "-f", "null", "-"])

finally:
    # Este bloque SOLO se ejecuta cuando el comando de arriba termina.
    # Si el reproductor se queda abierto, el tcpdump sigue capturando.
    subprocess.run(f"pkill -f {pcap_file}", shell=True)
