#!/bin/bash
# 1. Limpieza inicial del entorno Mininet y procesos previos
echo "=================================================="
echo "   PREPARANDO ENTORNO DE EXPERIMENTACIÓN SDN      "
echo "=================================================="
sudo mn -c > /dev/null 2>&1
sudo pkill -f python3
sudo pkill -f ryu-manager
sleep 1

2. Selección de ESCENARIO con límite de reintentos
intentos=0
seleccion_valida=false

while [ $intentos -lt 3 ]; do
    echo ">>> SELECCIONE EL ESCENARIO"
    echo "1) Escenario estático (h1 servidor, h2-h4 clientes)"
    echo "2) Escenario dinámico (h1 servidor, h2 cliente dinámico)"
    read -p "Opción: " escenario

    if [ "$escenario" == "1" ] || [ "$escenario" == "2" ]; then
        seleccion_valida=true
        break
    else
        intentos=$((intentos + 1))
        if [ $intentos -lt 3 ]; then
            echo -e "\n[!] Opción no válida. Le queda 1 intento.\n"
        fi
    fi
done

# 3. Lógica de ejecución (Solo si la selección fue correcta)
if [ "$seleccion_valida" = true ]; then
    # Lanzamiento del controlador Ryu solo tras elegir escenario
    gnome-terminal --title="Controlador Ryu" -- bash -c "ryu-manager ryu.app.simple_switch_13; exec bash" &
    sleep 5

    # Lanzamiento el escenario
    if [ "$escenario" == "1" ]; then
        echo ">>> EJECUTANDO ESCENARIO ESTÁTICO..."
        sudo python3 topo_sdn_video_streaming_static.py 
    else
        echo ">>> EJECUTANDO ESCENARIO DINÁMICO..."
        sudo python3 topo_sdn_video_streaming_dynamic.py
    fi
else
    echo -e "\n[ERROR] Segundo intento fallido. No se ejecutará ninguna topología."
fi

#4. Limpieza final (Se ejecuta tras cerrar Mininet)
echo -e "\n=================================================="
echo "   SALIENDO - LIMPIANDO ENTORNO                   "
echo "=================================================="

# Matamos específicamente los procesos que suelen quedar abiertos
sudo pkill -f http.server    # Mata el servidor de Python en h1
sudo pkill -f vlc-wrapper    # Cierra cualquier VLC que se haya quedado colgado
sudo pkill -f tcpdump        # Asegura que no queden capturas zombis
sudo pkill -f xterm          # Cierra todas las ventanas xterm abiertas
sudo pkill -f ryu-manager    # Cierra el controlador

sudo mn -c > /dev/null 2>&1
echo "[OK] Proceso finalizado. Entorno limpio."
