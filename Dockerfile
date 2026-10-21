FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Dependencias del sistema
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    nmap \
    iputils-ping \
    iproute2 \
    dnsutils \
    libglib2.0-0 \
    libgl1 \
    libx11-6 \
    libxcb1 \
    libxext6 \
    libxrender1 \
    libxkbcommon-x11-0 \
    libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*

# Copiar código del proyecto
COPY . /app

# Instalar dependencias Python si están declaradas
RUN if [ -f requirements.txt ]; then \
        pip install --no-cache-dir \
        -r requirements.txt; \
    fi

# Usuario sin privilegios
RUN useradd --create-home --shell /bin/bash cyberpulse \
    && mkdir -p /app/Results \
    && chown -R cyberpulse:cyberpulse /app

USER cyberpulse

# Punto de entrada inicial (pendiente validar GUI)
CMD ["python", "menu/main.py"]
