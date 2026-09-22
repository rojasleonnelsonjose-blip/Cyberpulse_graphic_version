"""Planificación y lectura de escaneos TCP auxiliares de Metasploit."""
import ipaddress
import re

PUERTOS_BASICOS = "21,22,23,25,53,80,110,135,139,143,443,445,993,995,1433,1521,3306,3389,5432,5900,8000,8080,8443"


def validar_destino(texto):
    try:
        return str(ipaddress.ip_network(texto.strip(), strict=False)) if "/" in texto else str(ipaddress.ip_address(texto.strip()))
    except ValueError as exc:
        raise ValueError("Introduce una dirección IP o una red CIDR válida, por ejemplo 192.168.1.10 o 192.168.1.0/24.") from exc


def validar_puertos(texto):
    texto = texto.strip()
    if not re.fullmatch(r"\d+(?:-\d+)?(?:,\d+(?:-\d+)?)*", texto):
        raise ValueError("Indica puertos separados por comas o rangos, por ejemplo 22,80,443 o 1-1024.")
    for parte in texto.split(","):
        limites = [int(n) for n in parte.split("-")]
        if any(n < 1 or n > 65535 for n in limites) or limites[0] > limites[-1]:
            raise ValueError("Los puertos deben estar entre 1 y 65535 y los rangos en orden ascendente.")
    return texto


def comandos_escaneo(destino, puertos, pausado):
    destino = validar_destino(destino)
    puertos = validar_puertos(puertos)
    # Sólo valores normalizados entran en los comandos de msfconsole.
    return "; ".join([
        "use auxiliary/scanner/portscan/tcp",
        f"set RHOSTS {destino}", f"set PORTS {puertos}",
        f"set THREADS {1 if pausado else 4}",
        f"set CONCURRENCY {2 if pausado else 10}",
        f"set DELAY {150 if pausado else 0}",
        "set TIMEOUT 1000", "set VERBOSE false", "run", "exit -y",
    ])


def limpiar_salida(texto):
    return re.sub(r"\x1b\[[0-?]*[ -/]*[@-~]", "", texto).replace("\r", "")


def puertos_detectados(texto):
    resultado = set()
    for host, puerto in re.findall(r"([0-9a-fA-F:.]+):(\d+)\s+-\s+TCP OPEN", limpiar_salida(texto)):
        try:
            host = str(ipaddress.ip_address(host))
        except ValueError:
            continue
        resultado.add((host, int(puerto)))
    return sorted(resultado)


def escaneo_correcto(texto):
    texto = limpiar_salida(texto)
    return "Auxiliary module execution completed" in texto and not re.search(r"(?m)^\s*\[-\]", texto)


def generar_pdf_metasploit(ruta_txt, ruta_pdf, destino, puertos):
    from pathlib import Path
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    contenido = limpiar_salida(Path(ruta_txt).read_text(encoding="utf-8"))
    estilos = getSampleStyleSheet()
    elementos = [Paragraph("Escaneo TCP de Metasploit - CyberPulse", estilos["Title"]),
                 Paragraph("Destino: " + escape(destino), estilos["Normal"]),
                 Paragraph("Puertos solicitados: " + escape(puertos), estilos["Normal"]),
                 Paragraph("Módulo: auxiliary/scanner/portscan/tcp. Los puertos abiertos no implican por sí solos una vulnerabilidad ni identifican la versión del servicio.", estilos["Normal"]),
                 Spacer(1, 12)]
    encontrados = puertos_detectados(contenido)
    if encontrados:
        filas = [["Equipo", "Puerto TCP", "Estado"]] + [[host, str(port), "Abierto"] for host, port in encontrados]
        tabla = Table(filas, repeatRows=1, colWidths=[250, 90, 100])
        tabla.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3D91")),
                                  ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                  ("GRID", (0, 0), (-1, -1), 0.4, colors.grey)]))
        elementos.append(tabla)
    else:
        elementos.append(Paragraph("No se detectaron puertos TCP abiertos en el alcance solicitado.", estilos["Normal"]))
    elementos.extend([Spacer(1, 12), Paragraph("Registro del escaneo", estilos["Heading2"])])
    for linea in contenido.splitlines():
        if linea.strip():
            elementos.append(Paragraph(escape(linea), estilos["Normal"]))
    SimpleDocTemplate(str(ruta_pdf)).build(elementos)
