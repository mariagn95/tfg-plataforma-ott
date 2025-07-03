
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.link import TCLink
from mininet.term import makeTerm
from mininet.cli import CLI
from mininet.log import setLogLevel
from time import sleep
import os

class OTTTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')
        h1 = self.addHost('h1', ip='10.0.0.1')  # Servidor HLS
        h2 = self.addHost('h2', ip='10.0.0.2')  # Cliente adaptativo

        self.addLink(h1, s1)
        self.addLink(h2, s1, cls=TCLink, bw=0.4)  # Ancho inicial bajo

def run():
    net = Mininet(topo=OTTTopo(), controller=RemoteController, link=TCLink)
    net.start()
    h1, h2 = net.get('h1'), net.get('h2')
    sleep(3)

    # Abrir terminales del servidor y cliente
    makeTerm(h1, title="Servidor HLS", term="xterm")
    makeTerm(h2, title="Cliente Adaptativo", term="xterm")

    # Lanzar tcpdump en h2
    print("Iniciando captura con tcpdump en h2...")
    h2.cmd("tcpdump -i h2-eth0 -w captura_h2.pcap &")

    # Anchos de banda simulados que coinciden con el controlador
    bw_list = [400, 800, 1600]  # en kbps

    for bw in bw_list:
        print(f"Lanzando cliente_adaptativo.py con BW = {bw} kbps...")
        h2.cmd(f"python3 cliente_adaptativo.py {bw} &")
        sleep(30)  # tiempo total: 20s reproducción + 10s margen

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    run()
