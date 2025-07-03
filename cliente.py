import sys
import subprocess

# Diccionario de BW por host
bw_map = {
    'h2': 1.6,
    'h3': 0.8,
    'h4': 0.4
}

# Comprobación de argumento
if len(sys.argv) != 2:
    print("Uso: python3 cliente.py <nombre_host>")
    sys.exit(1)

host = sys.argv[1]

if host not in bw_map:
    print(f"[INFO] El host {host} no tiene un BW asignado. Saliendo.")
    sys.exit(0)

bw = bw_map[host]
print(f"[INFO] Host {host} con BW asignado: {bw} Mbps")

# Selección de calidad según BW
if bw <= 0.5:
    playlist = "360p_playlist.m3u8"
elif bw <= 1.0:
    playlist = "480p_playlist.m3u8"
else:
    playlist = "720p_playlist.m3u8"

# TCPDUMP para capturar tráfico
pcap_file = f"{host}_{playlist}.pcap"
subprocess.Popen(f"tcpdump -i any -w {pcap_file}", shell=True)

# Reproducción con ffmpeg (puedes usar VLC si prefieres)
url = f"http://10.0.0.1:8080/{playlist}"
print(f"[INFO] Reproduciendo desde {url}")
subprocess.run(["ffmpeg", "-i", url, "-c", "copy", "-f", "null", "-"])
