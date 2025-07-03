#!/bin/bash


# Iniciar el controlador el controlador Ryu en un terminal
echo "Iniciando el controlador Ryu (simple_switch)..."
gnome-terminal -- bash -c "ryu-manager ryu.app.simple_switch; exec bash" &

# Esperar unos segundos para asegurarse de que el controlador está listo
sleep 3

# Iniciar la topología de Mininet en otro terminal
echo "Ejecutando la topologia de Mininet..."
gnome-terminal -- bash -c "sudo python3 topo_sdn.py" &
