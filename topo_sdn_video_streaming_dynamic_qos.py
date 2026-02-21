#!/usr/bin/python3
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.node import RemoteController
from mininet.log import setLogLevel
from time import sleep
import os
import sys # Importante para leer el argumento del .sh

class VideoStreamingDynamicQoSTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1', ip='10.0.0.1')
        h2 = self.addHost('h2', ip='10.0.0.2')
        self.addLink(h1, s1)
        # Enlace inicial a 2.0 Mbps
        self.addLink(h2, s1, cls=TCLink, bw=2.0)

def run():
    setLogLevel('info')
    
    # --- LÓGICA DE SELECCIÓN DE REPRODUCTOR ---
    # Leemos el argumento enviado por el .sh (sys.argv[1])
    reproductor = sys.argv[1] if len(sys.argv) > 1 else "vlc"
    url = "http://10.0.0.1:8080/master.m3u8"
    
    if reproductor == "vlc":
        cmd_player = f"vlc-wrapper {url} --play-and-exit"
        pkill_cmd = "pkill -f vlc-wrapper"
    elif reproductor == "ffplay":
        # -autoexit cierra al terminar, -infbuf ayuda a ver cambios de red rápido
        cmd_player = f"ffplay -i {url} -autoexit -window_title 'FFplay_HLS'"
        pkill_cmd = "pkill -f ffplay"
    elif reproductor == "ffmpeg":
        # -f null no muestra video, solo procesa datos para diagnóstico
        cmd_player = f"ffmpeg -i {url} -f null -"
        pkill_cmd = "pkill -f ffmpeg"

    net = Mininet(topo=VideoStreamingDynamicQoSTopo(), link=TCLink, controller=RemoteController)
    net.start()
    
    h1 = net.get('h1')
    h2 = net.get('h2')
    s1 = net.get('s1')
    enlace = net.linksBetween(h2, s1)[0]

    # 1. Iniciar captura de tráfico
    print(f"\n[INFO] Iniciando captura en h2 para análisis de {reproductor.upper()}...")
    h2.cmd(
        'tcpdump -U -s 0 -i h2-eth0 '
        '-w /tmp/captura-h2.pcap '
        '> /tmp/tcpdump-h2.log 2>&1 & echo $! > /tmp/tcpdump-h2.pid'
    )
    sleep(2)

    # 2. Servidor HTTP en h1
    print("[INFO] Abriendo servidor HLS en h1...")
    h1.cmd('xterm -T "SERVIDOR HTTP (h1)" -e "cd hls && python3 -m http.server 8080" &')
    sleep(5)

    # 3. Cliente con el reproductor seleccionado
    print(f"[INFO] Lanzando cliente h2 con {reproductor.upper()}...")
    h2.cmd(f'xterm -T "CLIENTE {reproductor.upper()}" -e "{cmd_player}; bash" &')
    
    # --- SIMULACIÓN DE RED DINÁMICA ---
    print("\n>>> Fase 1: Enlace estable (2.0 Mbps) - 30 segundos")
    sleep(30) 
    
    print("\n>>> Fase 2: Degradación de red SDN (Bajando a 0.4 Mbps)")
    enlace.intf1.config(bw=0.4)
    sleep(30) 
    
    print("\n>>> Fase 3: Recuperación de red SDN (Subiendo a 0.9 Mbps)")
    enlace.intf1.config(bw=0.9)
    sleep(30)
    
    # --- CIERRE DE PROCESOS AUTOMÁTICOS ---
    
    # Detenmos la captura de trafico
    print("[INFO] Deteniendo captura tcpdump...")
    h2.cmd('kill $(cat /tmp/tcpdump-h2.pid)')
    sleep(3)
    
    # Guardamos el pcap con el nombre del reproductor para no sobrescribir
    pcap_final = f"/home/maria/mi_proyecto/captura_dinamica_{reproductor}.pcap"
    h2.cmd(f'cp /tmp/captura-h2.pcap {pcap_final}')
    print(f"[OK] Captura guardada como: {pcap_final}")
    sleep(3)

    
    # Abrir CLI por si el usuario quiere hacer pruebas manuales extra
    print("\n*** Entrando en CLI de Mininet (escribe 'exit' para cerrar todo) ***")
    CLI(net)

    net.stop()

if __name__ == '__main__':
    run()
