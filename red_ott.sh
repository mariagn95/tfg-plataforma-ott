#!bin/bash


# Iniciar el controlador ryu
echo "Iniciando el controlador ryu (controlador_adaptativo.py)"
genome-terminal -- bash -c "ryu-manager controlador_adaptativo.py" &
