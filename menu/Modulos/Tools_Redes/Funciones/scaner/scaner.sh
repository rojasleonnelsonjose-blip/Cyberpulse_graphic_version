#!/bin/bash

segmento=$1
tipo=$2
herramienta=$3
modo=$4

# Obtener la ruta del directorio actual y buscar el directorio "CYBERPULSE_APPQT6"

current="$PWD"

while [[ "$(basename "$current")" != "CYBERPULSE_APPQT6" && "$current" != "/" ]]; do
    current="$(dirname "$current")"
done

ruta="$current/menu/Modulos/Tools_Redes/Funciones/Results"

echo "$ruta"

echo "Iniciando escaneo..."
echo "Segmento: $segmento"
echo "Tipo: $tipo"
echo "Herramienta: $herramienta"
echo "Modo: $modo"
echo "--------------------------------"

if [ "$herramienta" = "nmap" ]; then

    NombreArchivo="nmap_${tipo}_${modo}_${segmento}.txt"

    if [ "$tipo" = "basic" ] && [ "$modo" = "silent" ]; then
        echo "Ejecutando Nmap básico silencioso..."
        nmap -sn "$segmento" -oN "$ruta/$NombreArchivo"

    elif [ "$tipo" = "basic" ] && [ "$modo" = "noisy" ]; then
        echo "Ejecutando Nmap básico ruidoso..."
        nmap -sV "$segmento" -oN "$ruta/$NombreArchivo"

    elif [ "$tipo" = "complete" ] && [ "$modo" = "silent" ]; then
        echo "Ejecutando Nmap completo silencioso..."
        nmap -sS -T2 "$segmento" -oN "$ruta/$NombreArchivo"

    elif [ "$tipo" = "complete" ] && [ "$modo" = "noisy" ]; then
        echo "Ejecutando Nmap completo ruidoso..."
        nmap -A -T4 "$segmento" -oN "$ruta/$NombreArchivo"

    else
        echo "Combinación no válida para Nmap"
        exit 1
    fi

elif [ "$herramienta" = "metasploit" ]; then

    if [ "$tipo" = "basic" ]; then
        echo "Metasploit básico seleccionado"
        echo "Aquí puedes llamar un script .rc básico de Metasploit"

    elif [ "$tipo" = "complete" ]; then
        echo "Metasploit completo seleccionado"
        echo "Aquí puedes llamar un script .rc completo de Metasploit"

    else
        echo "Combinación no válida para Metasploit"
        exit 1
    fi

else
    echo "Herramienta no válida"
    exit 1
fi

echo "--------------------------------"
echo "Escaneo finalizado correctamente"