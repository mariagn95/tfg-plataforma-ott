#!/bin/bash

# 1. Limpieza inicial
echo "=================================================="
echo "   PREPARANDO ENTORNO DE EXPERIMENTACIÓN SDN      "
echo "=================================================="
sudo mn -c > /dev/null 2>&1
sudo pkill -f python3
sudo pkill -f ryu-manager
sleep 1

# 2. Selección de ESCENARIO
echo ">>> SELECCIONE EL ESCENARIO"
echo "1) Escenario Estático (3 Clientes)"
echo "2) Escenario Dinámico (Adaptación QoS)"
echo "3) Salir"
read -p "Opción: " escenario

if [ $escenario -eq 3 ]; then exit 0; fi

# 3. Lógica de Escenarios
if [ $escenario -eq 1 ]; then
    # --- ESCENARIO 1 ---
    gnome-terminal --title="Controlador Ryu" -- bash -c "ryu-manager ryu.app.simple_switch_13; exec bash" &
    sleep 5
    echo ">>> EJECUTANDO ESCENARIO ESTÁTICO..."
    # AQUÍ NO HAY '&': El script se para aquí hasta que cierres Mininet
    sudo python3 topo_sdn_video_streaming.py 

elif [ $escenario -eq 2 ]; then
    # --- ESCENARIO 2 ---
    echo ">>> SELECCIONE REPRODUCTOR"
    echo "1) VLC"
    echo "2) FFplay"
    echo "3) FFmpeg"
    read -p "Opción: " rep_opcion

    case $rep_opcion in
        1) player="vlc" ;;
        2) player="ffplay" ;;
        3) player="ffmpeg" ;;
    esac

    gnome-terminal --title="Controlador Ryu" -- bash -c "ryu-manager ryu.app.simple_switch_13; exec bash" &
    sleep 5
    echo ">>> EJECUTANDO ESCENARIO DINÁMICO CON $player..."
    # AQUÍ TAMPOCO HAY '&': El script espera a que termines tus pruebas
    sudo python3 topo_sdn_video_streaming_dynamic_qos.py $player
fi

# 4. Limpieza final (SOLO se ejecuta tras cerrar Mininet)
echo -e "\n=================================================="
echo "   MININET CERRADO - LIMPIANDO TODO               "
echo "=================================================="
sudo pkill -f ryu-manager
sudo mn -c > /dev/null 2>&1
echo "[OK] Proceso finalizado."
