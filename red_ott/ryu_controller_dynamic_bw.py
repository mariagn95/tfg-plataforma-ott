from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ether_types
from ryu.lib import hub
import subprocess
import os  # Añadido para guardar el BW

class DynamicBandwidthSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DynamicBandwidthSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.h2_interface = "s1-eth2"
        self.monitor_thread = hub.spawn(self._monitor_bandwidth)

    def guardar_bw(self, bw):
        try:
            with open("/tmp/bw.txt", "w") as f:
                f.write(str(bw))
        except Exception as e:
            self.logger.error("Error al guardar ancho de banda: %s", e)

    def _monitor_bandwidth(self):
        rates_mbps = [0.4, 0.8, 1.6]
        idx = 0
        while True:
            current_rate = rates_mbps[idx]
            rate_str = f"{int(current_rate * 1000)}kbit"
            subprocess.call(["tc", "qdisc", "del", "dev", self.h2_interface, "root"], stderr=subprocess.DEVNULL)
            burst = "32kbit"
            latency = "50ms"
            self.logger.info("Cambiando ancho de banda de %s a %s (%.1f Mbps)",
                             self.h2_interface, rate_str, current_rate)
            subprocess.call([
                "tc", "qdisc", "add", "dev", self.h2_interface, "root", "tbf",
                "rate", rate_str, "burst", burst, "latency", latency
            ])
            self.guardar_bw(current_rate)
            hub.sleep(30)
            idx = (idx + 1) % len(rates_mbps)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)]
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(datapath=datapath, priority=0, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            return
        dst = eth.dst
        src = eth.src
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD
        actions = [parser.OFPActionOutput(out_port)]
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst)
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                flow_mod = parser.OFPFlowMod(datapath=datapath, buffer_id=msg.buffer_id,
                                             priority=1, match=match,
                                             instructions=[parser.OFPInstructionActions(
                                                 ofproto.OFPIT_APPLY_ACTIONS, actions)])
                datapath.send_msg(flow_mod)
                return
            else:
                flow_mod = parser.OFPFlowMod(datapath=datapath, priority=1, match=match,
                                             instructions=[parser.OFPInstructionActions(
                                                 ofproto.OFPIT_APPLY_ACTIONS, actions)])
                datapath.send_msg(flow_mod)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)
