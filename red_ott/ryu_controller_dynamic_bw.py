from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types
from ryu.lib import hub
import subprocess

class DynamicBandwidthSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DynamicBandwidthSwitch, self).__init__(*args, **kwargs)
        # Tabla MAC para comportamiento de switch de aprendizaje
        self.mac_to_port = {}
        # Nombre de la interfaz del switch conectada a h2 (asumiendo topología simple con switch s1)
        self.h2_interface = "s1-eth2"
        # Iniciar un hilo separado para cambiar el ancho de banda periódicamente
        self.monitor_thread = hub.spawn(self._monitor_bandwidth)

    def _monitor_bandwidth(self):
        """Hilo de monitoreo para cambiar el ancho de banda de h2 cíclicamente."""
        # Ciclo de valores de ancho de banda en Mbps
        rates_mbps = [0.4, 0.8, 1.6]  # valores cíclicos de ancho de banda
        idx = 0
        while True:
            current_rate = rates_mbps[idx]
            # Formatear el valor de tasa para tc (usar kbit para evitar decimales)
            if current_rate < 1:
                rate_str = f"{int(current_rate * 1000)}kbit"   # ej: 0.4 -> "400kbit"
            else:
                rate_str = f"{int(current_rate * 1000)}kbit"   # ej: 1.6 -> "1600kbit"
            # Aplicar el límite de ancho de banda usando tc (Token Bucket Filter)
            # Eliminar configuración previa (qdisc root) si existe, para evitar conflicto:contentReference[oaicite:1]{index=1}
            subprocess.call(
                ["tc", "qdisc", "del", "dev", self.h2_interface, "root"],
                stderr=subprocess.DEVNULL
            )
            # Añadir nueva regla tbf con la tasa actual
            burst = "32kbit"    # tamaño de ráfaga
            latency = "50ms"    # latencia máxima de cola
            self.logger.info("Cambiando ancho de banda de %s a %s (%.1f Mbps)",
                              self.h2_interface, rate_str, current_rate)
            subprocess.call(
                ["tc", "qdisc", "add", "dev", self.h2_interface, "root", "tbf",
                 "rate", rate_str, "burst", burst, "latency", latency]
            )
            # Esperar 30 segundos antes de aplicar el siguiente cambio
            hub.sleep(30)
            # Avanzar al siguiente valor en la lista (cíclico)
            idx = (idx + 1) % len(rates_mbps)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """Maneja el evento de características del switch (negociación OF)."""
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        # Instalar flujo por defecto (table-miss) para enviar paquetes desconocidos al controlador
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=0,
                                 match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        """Maneja eventos PacketIn (paquetes que llegan al controlador)."""
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        # Analizar el paquete recibido para obtener campos Ethernet
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # Ignorar paquetes LLDP (utilizados por descubrimiento de topología)
            return

        dst = eth.dst
        src = eth.src

        # Aprender la dirección MAC de origen con el puerto asociado
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        # Decidir puerto de salida basado en la tabla MAC
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD  # desconocido: inundar

        # Crear acciones de salida (enviar el paquete al puerto determinado)
        actions = [parser.OFPActionOutput(out_port)]

        # Si el destino es conocido (no flood), agregar un flujo para agilizar futuros paquetes
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            # Instalar flujo de reenvío solo si el switch no almacenó el paquete (no buffer)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                flow_mod = parser.OFPFlowMod(datapath=datapath, buffer_id=msg.buffer_id,
                                             priority=1, match=match,
                                             instructions=[parser.OFPInstructionActions(
                                                 ofproto.OFPIT_APPLY_ACTIONS, actions)])
                datapath.send_msg(flow_mod)
                return  # El paquete ya fue enviado por el switch desde el buffer
            else:
                # Sin buffer: enviar flujo junto con el paquete
                flow_mod = parser.OFPFlowMod(datapath=datapath, priority=1,
                                             match=match, instructions=[
                                                 parser.OFPInstructionActions(
                                                     ofproto.OFPIT_APPLY_ACTIONS, actions)])
                datapath.send_msg(flow_mod)

        # Enviar el paquete recibido al puerto de salida correspondiente (PacketOut)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
