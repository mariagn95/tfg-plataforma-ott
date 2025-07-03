
import sys
import subprocess

# Diccionario con los BW máximos por calidad
calidades = {
    "360p": 600,   # kbps
    "480p": 800,   # kbps
    "720p": 1500   # kbps
}

def seleccionar_playlist(bw_kbps):
    if bw_kbps < calidades["360p"]:
        return None
    elif bw_kbps < calidades["480p"]:
        return "360p_playlist.m3u8"
    elif bw_kbps < calidades["720p"]:
        return "480p_playlist.m3u8"
    else:
        return "720p_playlist.m3u8"

if len(sys.argv) != 2:
    print("Uso: python3 cliente_adaptativo.py <bw_kbps>")
    sys.exit(1)

bw = int(sys.argv[1])
playlist = seleccionar_playlist(bw)

if playlist:
    url = f"http://10.0.0.1:8080/{playlist}"
    print(f"[CLIENTE] Ancho de banda: {bw} kbps → Usando playlist: {playlist}")
    subprocess.run(["ffmpeg", "-i", url, "-t", "6", "-c", "copy", "-f", "null", "-"])
else:
    print("[CLIENTE] Ancho de banda demasiado bajo para reproducir.")
