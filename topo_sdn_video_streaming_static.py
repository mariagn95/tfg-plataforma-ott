#  Importación de módulos necesarios de Mininet
from mininet.topo import Topo                # Clase base para definir topologías personalizadas
from mininet.net import Mininet              # Clase principal para crear y gestionar la red virtual
from mininet.node import RemoteController    # Nodo para conectar con el controlador SDN externo (Ryu)
from mininet.link import TCLink              # Permite configurar parámetros de red (BW, retardo, etc.)
from mininet.cli import CLI                  # Proporciona la consola interactiva de Mininet
from mininet.term import makeTerms           # Facilita la apertura automática de terminales xterm

# Definición de la clase para la topología estática
class StaticTopo(Topo):
    def build(self):
        # 1. Creación de la infraestructura de conmutación
        s1 = self.addSwitch('s1')        # Crea un switch OpenFlow virtual llamado s1
        
        # 2. Creación de los nodos (Hosts) con sus IPs correspondientes
        h1 = self.addHost('h1', ip='10.0.0.1')  # Nodo Servidor (Streaming Server)
        h2 = self.addHost('h2', ip='10.0.0.2')  # Nodo Cliente 1 (Alta calidad)
        h3 = self.addHost('h3', ip='10.0.0.3')  # Nodo Cliente 2 (Calidad media)
        h4 = self.addHost('h4', ip='10.0.0.4')  # Nodo Cliente 3 (Baja calidad)

        # 3. Establecimiento de enlaces con restricciones de ancho de banda (BW)
        # El servidor h1 tiene un enlace sin restricciones para no ser el cuello de botella
        self.addLink(h1, s1)
        # Los clientes tienen diferentes perfiles de red para probar el streaming
        self.addLink(h2, s1, cls=TCLink, bw=1.8) # Enlace de 1.8 Mbps
        self.addLink(h3, s1, cls=TCLink, bw=0.9) # Enlace de 0.9 Mbps
        self.addLink(h4, s1, cls=TCLink, bw=0.5) # Enlace de 0.5 Mbps

def run():
    # Inicialización de la red conectándola al controlador externo Ryu
    net = Mininet(topo=StaticTopo(), controller=RemoteController)
    net.start() # Arranca la red virtual y establece conexión con Ryu

    # E# Arranque del servidor multimedia en h1 (puerto 8080), sirviendo la carpeta hls
    h1 = net.get('h1')
    print("[INFO] Abriendo terminal del SERVIDOR en h1...")
    h1.cmd('xterm -T "SERVIDOR HTTP (h1)" -e "cd hls && python3 -m http.server 8080" &')
    
    print("\n[OK] Topología estática desplegada correctamente.")
    print("[INFO] Use las terminales abiertas para ejecutar 'python3 cliente.py [calidad]'")
    
    # Abre automáticamente terminales xterm para los clientes h2, h3 y h4
    makeTerms([net.get('h2'), net.get('h3'), net.get('h4')], 'Cliente')
    
    CLI(net)       # Inicia la interfaz de comandos para interacción manual
    net.stop()     # Detiene todos los nodos y enlaces al salir

if __name__ == '__main__':
    run()
