from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
import os
import time
import threading

class ControladorAdaptativo(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(ControladorAdaptativo, self).__init__(*args, **kwargs)
        self.aplicando = False
        threading.Thread(target=self.evolucionar_bw).start()

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Tabla por defecto: reenviar a controlador
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        mod = parser.OFPFlowMod(datapath=datapath,
                                 priority=priority,
                                 match=match,
                                 instructions=inst)
        datapath.send_msg(mod)

    def evolucionar_bw(self):
        if self.aplicando:
            return
        self.aplicando = True

        bw_h2 = [0.4, 0.8, 1.6]  # En Mbps
        for i, bw in enumerate(bw_h2):
            print(f"[CONTROLADOR] Aplicando ancho de banda: {bw} Mbps para h2")
            kbps = int(bw * 1000)
            cmd = f"tc class change dev s1-eth2 parent 1: classid 1:1 htb rate {kbps}kbit"
            os.system(cmd)
            time.sleep(30)
