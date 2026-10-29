

#!/bin/bash


set -e


CONTENEDOR="cyberpulse-dev-v4"
PROYECTO="$HOME/Cyberpulse_graphic_version"
AUTH_DEST="$HOME/.local/share/cyberpulse/x11/docker.xauth"
LOG="$HOME/.local/share/cyberpulse/inicio.log"


mkdir -p "$(dirname "$LOG")"


exec >> "$LOG" 2>&1

echo "=================================="
echo "       INICIANDO CYBERPULSE"
echo "=================================="


# Comprobar la sesion grafica
if [ -z "${DISPLAY:-}" ]; then
    echo "[ERROR] DISPLAY no esta definido."
    exit 1
fi


# Obtener la autorizacion X11 actual
AUTH_SRC="${XAUTHORITY:-$HOME/.Xauthority}"


if [ ! -f "$AUTH_SRC" ]; then
    echo "[ERROR] No existe XAUTHORITY: $AUTH_SRC"
    exit 1
fi


# Actualizar credenciales sin sustituir
# el archivo montado por Docker
mkdir -p "$(dirname "$AUTH_DEST")"


if [ ! -f "$AUTH_DEST" ]; then
    touch "$AUTH_DEST"
fi


chmod 600 "$AUTH_DEST"
cat "$AUTH_SRC" > "$AUTH_DEST"


echo "[OK] Autorizacion X11 actualizada."


# Comprobar Docker
if ! docker info >/dev/null 2>&1; then
    echo "[ERROR] Docker no esta disponible."
    exit 1
fi


# Comprobar el contenedor
if ! docker container inspect "$CONTENEDOR" >/dev/null 2>&1; then
    echo "[ERROR] No existe $CONTENEDOR"
    exit 1
fi


# Comprobar la red host
RED=$(docker inspect -f \
    '{{.HostConfig.NetworkMode}}' "$CONTENEDOR")


if [ "$RED" != "host" ]; then
    echo "[ERROR] El contenedor no usa red host."
    exit 1
fi


# Iniciar si esta detenido
if [ "$(docker inspect -f '{{.State.Running}}' "$CONTENEDOR")" != "true" ]; then
    echo "[INFO] Iniciando contenedor..."
    docker start "$CONTENEDOR"
fi


# Confirmar funcionamiento
if [ "$(docker inspect -f '{{.State.Running}}' "$CONTENEDOR")" != "true" ]; then
    echo "[ERROR] El contenedor no permanece activo."
    exit 1
fi


echo "[OK] Contenedor disponible."
echo "[INFO] Abriendo CYBERPULSE..."


# Iniciar interfaz grafica
docker exec \
    -e DISPLAY="$DISPLAY" \
    -e XAUTHORITY=/tmp/cyberpulse.Xauthority \
    -w /app/menu \
    "$CONTENEDOR" \
    python3 main.py
