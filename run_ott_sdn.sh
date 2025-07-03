#!/bin/bash


# 1. Limpiar entorno previo de Mininet
echo "🧹 Limpiando Mininet..."
sudo mn -c

# 2. Lanzar el controlador Ryu con aumento de ancho de banda tras 60s
echo "🚦 Iniciando controlador Ryu (dynamic bandwidth)..."
gnome-terminal -- bash -c "ryu-manager ryu_controller_dynamic_bw.py; exec bash"

# 3. Esperar unos segundos para asegurar que el controlador está en marcha
sleep 3

# 4. Lanzar la topología que simula la adaptación desde un cliente único
echo "🧪 Ejecutando topología OTT adaptativa con Mininet..."
gnome-terminal -- bash -c "sudo python3 topo_sdn_adaptacion.py; exec bash"
