# Importación de librerías para gestión de red y temporización
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
from mininet.node import RemoteController
from time import sleep                       # Permite pausar la ejecución para simular eventos temporales
from mininet.cli import CLI

# Definición de la clase para el escenario de red dinámica (QoS Variable)
class DynamicTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')
        # h1 actúa como origen del contenido multimedia
        h1 = self.addHost('h1', ip='10.0.0.1')
        # h2 es el cliente que experimentará variaciones de ancho de banda en tiempo real
        h2 = self.addHost('h2', ip='10.0.0.2')
        
        self.addLink(h1, s1)
        # Se establece un enlace inicial de 2.0 Mbps utilizando TCLink
        self.addLink(h2, s1, cls=TCLink, bw=2.0)

def run():
    # Creación del entorno dinámico conectado al controlador Ryu
    net = Mininet(topo=DynamicTopo(), link=TCLink, controller=RemoteController)
    net.start()
    
    # IMPORTANTE: Obtenemos h1, h2 y s1.
    # Necesitamos el objeto del switch (s1) para que la función linksBetween 
    # identifique el enlace físico-virtual específico que queremos modificar.
    h1, h2, s1 = net.get('h1', 'h2', 's1')
    enlace = net.linksBetween(h2, s1)[0]

    # Arranque del servidor multimedia en h1 (puerto 8080), sirviendo la carpeta hls
    print("[INFO] Abriendo terminal del SERVIDOR en h1...")
    h1.cmd('xterm -T "SERVIDOR HTTP (h1)" -e "cd hls && python3 -m http.server 8080" &')

    # Lanzamiento del cliente en h2 pidiendo el archivo maestro
    # Se utiliza xterm para visualizar los logs del script cliente.py en tiempo real
    print("[INFO] Lanzando cliente h2 en modo Adaptive Bitrate (Master)...")
    h2.cmd('xterm -T "CLIENTE DINAMICO h2" -e "python3 cliente.py; bash" &')
    
    # Espera inicial para permitir que el cliente arranque y llene buffer
    print("[INFO] Esperando 15 segundos para estabilizar la reproducción inicial...")
    sleep(15)
    
    # --- INICIO DEL CICLO DE VARIACIÓN DE RED ---
    print(">>> Fase 1: Reproducción del contenido en condiciones moderadas durante 15 segundos")
    print("Ancho de banda actual:")
    print(h2.cmd("tc class show dev h2-eth0"))
    sleep(15)
    
    print(">>> Fase 2: Reducción drástica de ancho de banda durante 30 segundos")
    enlace.intf1.config(bw=0.4)
    enlace.intf2.config(bw=0.4)
    print("Ancho de banda actual:")
    print(h2.cmd("tc class show dev h2-eth0"))
    sleep(30)
    
    print(">>> Fase 3: Recuperación parcial de la red durante 30 segundos")
    enlace.intf1.config(bw=0.9)
    enlace.intf2.config(bw=0.9)
    print("Ancho de banda actual:")
    print(h2.cmd("tc class show dev h2-eth0"))
    sleep(30)

    print("\n[OK] Simulación de red dinámica completada.")
    CLI(net)       # Acceso a la consola para inspección final
    net.stop()     # Limpieza y cierre de la topología

if __name__ == '__main__':
    run()
