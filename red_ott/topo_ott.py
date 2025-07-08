#!/usr/bin/python3

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import RemoteController
from mininet.term import makeTerm
from mininet.log import setLogLevel
import os
import shutil

class OTTTopo(Topo):
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        s1 = self.addSwitch('s1')

        self.addLink(h1, s1)
        self.addLink(h2, s1, cls=TCLink, bw=0.4)  # BW inicial limitado

if __name__ == '__main__':
    setLogLevel('info')
    topo = OTTTopo()
    net = Mininet(topo=topo, link=TCLink, controller=RemoteController)
    net.start()

    h1 = net.get('h1')
    h2 = net.get('h2')

    # Copiar script Python al host h2
    local_script = 'h2_ffmpeg.py'
    remote_path = '/tmp/h2_ffmpeg.py'
    if os.path.exists(local_script):
        shutil.copy(local_script, '/tmp/')
        h2.cmd(f'cp {remote_path} .')
        h2.cmd('chmod +x h2_ffmpeg.py')

    # Lanzar servidor HTTP en h1
    hls_dir = '/home/maria/hls'
    h1.cmd(f'cd {hls_dir} && python3 -m http.server 80 &')

    print("Lanzando terminal para h2 con cliente FFmpeg y para h1 (servidor)...")
    makeTerm(h1, title="Servidor HLS (h1)")

    print("Iniciando captura de tráfico en h2...")
    h2.cmd('tcpdump -i h2-eth0 -w /tmp/captura_h2.pcap &')

    for i in range(3):
        print(f"\n--- Ejecución {i+1}/3 del cliente h2 ---")
        h2.cmd('python3 h2_ffmpeg.py')
        if i < 2:
            print("Esperando 30 segundos para siguiente ejecución...")
            import time; time.sleep(30)

    print("\nFinalizando captura de tráfico...")
    h2.cmd('pkill -f tcpdump')


    input("Presiona ENTER para finalizar la red...")
    net.stop()
