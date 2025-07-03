#!/bin/bash


# Iniciar el controlador Ryu en un terminal
echo "Iniciando el controlador Ryu (controlador_adaptativo.py)..."
gnome-terminal -- bash -c "ryu-manager controlador_adaptativo.py; exec bash" &

# Esperar unos segundos para asegurarse de que el controlador está listo
sleep 3

# Iniciar la topología de Mininet en otro terminal
echo "Ejecutando la topologia de Mininet..."
gnome-terminal -- bash -c "sudo python3 topo_ott.py" &
