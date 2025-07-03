#!/bin/bash

# ----------------------------
# Script para iniciar el entorno OTT sobre SDN:
# 1. Limpia procesos y caché anteriores
# 2. Lanza el controlador Ryu
# 3. Lanza Mininet con la topología definida
# 4. Finaliza todo al cerrar Mininet
# ----------------------------

echo "🧹 Limpiando procesos anteriores de VLC y caché..."

# Cerrar instancias de VLC y vlc-wrapper previas
pkill -9 vlc 2>/dev/null
pkill -9 vlc-wrapper 2>/dev/null

# Borrar caché de VLC para evitar que recuerde decisiones anteriores
rm -rf ~/.cache/vlc

# Limpiar cualquier resto de redes anteriores de Mininet
sudo mn -c > /dev/null

echo "✅ Limpieza completada."

echo "🚀 Iniciando el controlador Ryu (simple_switch)..."

# Lanzar el controlador Ryu en un nuevo terminal
gnome-terminal -- bash -c "ryu-manager ryu.app.simple_switch; exec bash" &
CONTROLADOR_PID=$!

# Esperar unos segundos para asegurar que el controlador está activo
sleep 3

echo "🌐 Ejecutando la topología de Mininet..."

# Lanzar el script de topología en otra terminal
gnome-terminal -- bash -c "sudo python3 topo_sdn.py; exec bash" &
MININET_PID=$!

# Esperar a que el usuario cierre Mininet
wait $MININET_PID

echo "🛑 Cerrando entorno..."

# Terminar el controlador Ryu
kill $CONTROLADOR_PID 2>/dev/null

# Cerrar las ventanas xterm que Mininet abrió para los hosts
pkill -f "xterm -title host" 2>/dev/null

echo "✅ Entorno cerrado correctamente."





