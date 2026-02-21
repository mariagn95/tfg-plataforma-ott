#  Importación de módulos
from mininet.topo import Topo                # Permite definir topologías personalizadas
from mininet.net import Mininet              # Crea y gestiona la red virtual de Mininet
from mininet.node import RemoteController    # Permite conectar la red a un controlador SDN externo
from mininet.term import makeTerms           # Abre terminales xterm para los hosts
from mininet.cli import CLI                  # Proporciona una CLI interactiva para controlar la red
from mininet.link import TCLink              # Permite estrablecer enlaces con parametros como ancho de banda, retardo o perdida
from mininet.log import setLogLevel          # Permite definir el nivel de detalle de los mensajes del sistema
from time import sleep                       # Proporciona pausas temporales durante la ejecución

# Definición de la topología
class VideoStreamingTopo(Topo):
    def build(self):
        s1 = self.addSwitch('s1')                 # Crea un switch virtual llamado s1        
        h1 = self.addHost('h1', ip='10.0.0.1')  # Crea el host h1 con IP fija como servidor
        h2 = self.addHost('h2', ip='10.0.0.2')  # Crea el host h2 con IP fija como cliente 720p
        h3 = self.addHost('h3', ip='10.0.0.3')  # Crea el host h3 con IP fija como cliente 480p
        h4 = self.addHost('h4', ip='10.0.0.4')  # Crea el host h4 con IP fija como cliente 360p

        # Establece enlaces punto a punto entre los hosts y el switch
        self.addLink(h1, s1)
        self.addLink(h2, s1, cls=TCLink, bw=1.6)
        self.addLink(h3, s1, cls=TCLink, bw=0.8)
        self.addLink(h4, s1, cls=TCLink, bw=0.4)

# Inicialización de la red y terminales xterm
def run():
    net = Mininet(topo=VideoStreamingTopo(), controller=RemoteController)                        # Inicializa la red con la topología definida y un controlador externo
    net.start()                                                                    # Arranca la red virtual
    sleep(5)                                                                       # Pausa de 5 segundos para asegurar que todo esté inicializado
    
    # --- BLOQUE NUEVO PARA GENERAR EL TXT ---
    with open("reporte_anchos_banda.txt", "w") as f:
        f.write("REPORTE DE RED SDN - TFG\n")
        f.write("========================\n")
        for h_name in ['h2', 'h3', 'h4']:
            host = net.get(h_name)
            # Obtenemos el BW de la interfaz conectada al switch
            bw = host.intf().params.get('bw', 'No definido')
            f.write(f"Host: {h_name} | IP: {host.IP()} | Ancho de Banda: {bw} Mbps\n")
    # ---------------------------------------
    
    makeTerms([net.get('h1'), net.get('h2'), net.get('h3'), net.get('h4')],'host')    # Abre terminales xterm para los tres hosts
    print("Topología iniciada...")
    CLI(net)                                                                          # Inicia una interfaz de línea de comandos interactiva de Mininet
    net.stop()                                                                        # Detiene la red al salir de la CLI

# Ejecucion de la topologia definida
if __name__ == '__main__':
    setLogLevel('info')    # Define el nivel de detalle de los mensajes en consola
    run()                  # Ejecuta la función principal para iniciar la topología
