#!/usr/bin/env python3
"""
cliente.py

Uso:
  python3 cliente.py <reproductor> [master]

- <reproductor>: vlc | ffplay | ffmpeg (se aceptan variaciones: "VLC", "ffplay", etc.)
- [master] (opcional): si se indica, se solicita directamente master.m3u8.
  Si no se indica, se mantiene el comportamiento actual: selección de playlist
  según el ancho de banda leído de 'reporte_anchos_banda.txt'.

Este script también inicia una captura con tcpdump durante la reproducción/descarga
y la guarda en un .pcap (uno por ejecución).
"""

import os
import re
import sys
import socket
import subprocess
from datetime import datetime
from typing import Optional, Tuple


SERVER_IP = "10.0.0.1"
SERVER_PORT = 8080

BW_REPORT_FILE = "reporte_anchos_banda.txt"   # Debe existir en el host cliente (h2/h3/h4)
MASTER_NAME = "master.m3u8"

# Nombres de playlists por calidad (según tu convención: <calidad>_playlist.m3u8)
PLAYLIST_360 = "360p_playlist.m3u8"
PLAYLIST_480 = "480p_playlist.m3u8"
PLAYLIST_720 = "720p_playlist.m3u8"


def _get_local_ip_towards_server() -> str:
    """Obtiene la IP local usada para alcanzar el servidor (útil para identificar el host)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect((SERVER_IP, SERVER_PORT))
        return s.getsockname()[0]
    finally:
        s.close()


def _read_bw_for_ip(ip_local: str) -> Tuple[Optional[str], Optional[float]]:
    """
    Lee el archivo de anchos y devuelve (host, bw_mbps) para la IP local.
    Formato esperado en cada línea (ejemplo):
      Host: h2 | IP: 10.0.0.2 | Ancho de Banda: 0.8 Mbps
    """
    if not os.path.exists(BW_REPORT_FILE):
        return None, None

    with open(BW_REPORT_FILE, "r", encoding="utf-8", errors="ignore") as f:
        for linea in f:
            if f"IP: {ip_local}" not in linea:
                continue

            host_match = re.search(r"Host:\s*(h\d+)", linea)
            bw_match = re.search(r"Ancho de Banda:\s*([\d.]+)\s*Mbps", linea)

            host = host_match.group(1) if host_match else None
            bw = float(bw_match.group(1)) if bw_match else None
            return host, bw

    return None, None


def _select_playlist_from_bw(bw_mbps: float) -> str:
    """Selecciona playlist según el ancho de banda (mantiene la lógica original)."""
    if bw_mbps <= 0.5:
        return PLAYLIST_360
    if bw_mbps <= 1.0:
        return PLAYLIST_480
    return PLAYLIST_720


def _infer_capture_iface() -> str:
    """
    Intenta inferir la interfaz de salida hacia el servidor.
    En Mininet suele ser hX-eth0.
    """
    try:
        out = subprocess.check_output(["sh", "-lc", f"ip route get {SERVER_IP} | head -n1"], text=True)
        m = re.search(r"\bdev\s+(\S+)", out)
        if m:
            return m.group(1)
    except Exception:
        pass
    return "any"  # fallback


def _start_tcpdump(pcap_file: str) -> subprocess.Popen:
    iface = _infer_capture_iface()
    # Capturamos tráfico HTTP hacia/desde el servidor en el puerto configurado.
    cmd = ["tcpdump", "-i", iface, "host", SERVER_IP, "and", "port", str(SERVER_PORT), "-w", pcap_file]
    # Silencioso: stdout/stderr a /dev/null
    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _run_player(player: str, url: str) -> None:
    p = player.lower()

    if "vlc" in p:
        # --no-audio: sin audio
        # --play-and-exit: cierra al finalizar
        subprocess.run(["vlc-wrapper", "--no-audio", "--play-and-exit", url], check=False)

    elif "ffplay" in p:
        # -autoexit: cierra al terminar
        subprocess.run(["ffplay", "-autoexit", url], check=False)

    elif "ffmpeg" in p:
        # Descarga/lectura sin reproducir (útil para validación)
        subprocess.run(["ffmpeg", "-i", url, "-c", "copy", "-f", "null", "-"], check=False)

    else:
        raise ValueError("Reproductor no soportado. Usa: vlc | ffplay | ffmpeg")


def main() -> int:
    if len(sys.argv) < 2:
        print("Uso: python3 cliente.py <reproductor> [master]")
        return 1

    reproductor = sys.argv[1]
    modo_master = (len(sys.argv) >= 3 and sys.argv[2].lower() == "master")

    ip_local = _get_local_ip_towards_server()
    host, bw = _read_bw_for_ip(ip_local)

    if host is None:
        # fallback: si no se puede leer el host, usamos la IP como identificador
        host = ip_local.replace(".", "_")

    # Selección del recurso a solicitar
    if modo_master:
        recurso = MASTER_NAME
        modo = "master"
    else:
        if bw is None:
            print(f"[WARN] No se encontró BW para {ip_local} en {BW_REPORT_FILE}. Se usará 720p por defecto.")
            recurso = PLAYLIST_720
        else:
            recurso = _select_playlist_from_bw(bw)
        modo = "auto"

    url = f"http://{SERVER_IP}:{SERVER_PORT}/{recurso}"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = recurso.replace(".m3u8", "")
    pcap_file = f"{host}_{modo}_{base}_{timestamp}.pcap"

    print(f"[INFO] Reproductor: {reproductor}")
    print(f"[INFO] Modo: {modo} | URL: {url}")
    print(f"[INFO] Captura: {pcap_file}")

    tcpdump_proc = None
    try:
        tcpdump_proc = _start_tcpdump(pcap_file)
        _run_player(reproductor, url)
    finally:
        if tcpdump_proc and tcpdump_proc.poll() is None:
            tcpdump_proc.terminate()
            try:
                tcpdump_proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                tcpdump_proc.kill()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
