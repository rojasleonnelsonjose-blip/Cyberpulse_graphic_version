"""Informes Nmap: cada bloque de equipo conserva sus propios puertos."""
from pathlib import Path
from xml.sax.saxutils import escape
import re
import textwrap

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether


def analizar_nmap(contenido):
    equipos = []
    actual = None
    patron_puerto = re.compile(r"^(\d{1,5})/(tcp|udp|sctp)\s+(open\|filtered|closed\|filtered|open|closed|filtered|unfiltered)\s+(\S+)(?:\s+(.*))?$")
    for linea in contenido.splitlines():
        if linea.startswith("Nmap scan report for "):
            destino = linea[len("Nmap scan report for "):].strip()
            nombre = ""
            direccion = destino
            coincidencia = re.fullmatch(r"(.+)\s+\(([^()]+)\)", destino)
            if coincidencia:
                nombre, direccion = coincidencia.groups()
            actual = {"direccion": direccion, "nombre": nombre, "puertos": [], "notas": []}
            equipos.append(actual)
            continue
        if actual is None:
            continue
        puerto = patron_puerto.fullmatch(linea)
        if puerto and 1 <= int(puerto.group(1)) <= 65535:
            numero, protocolo, estado, servicio, version = puerto.groups()
            actual["puertos"].append({"puerto": f"{numero}/{protocolo}", "estado": estado,
                                       "servicio": servicio, "version": version or "No informada"})
        elif linea.startswith(("Host is ", "All ", "Not shown:", "MAC Address:", "Service Info:", "OS details:", "Running:", "Device type:")):
            actual["notas"].append(linea)
    return equipos


class ReportePDFNmap:
    def generar_pdf_desde_txt(self, ruta_txt, ruta_pdf, ruta_logo=None):
        ruta_txt = Path(ruta_txt)
        if not ruta_txt.is_file():
            raise FileNotFoundError(f"No existe el archivo TXT: {ruta_txt}")
        contenido = ruta_txt.read_text(encoding="utf-8", errors="replace")
        equipos = analizar_nmap(contenido)
        doc = SimpleDocTemplate(str(ruta_pdf), pagesize=letter, rightMargin=1.8*cm, leftMargin=1.8*cm,
                                topMargin=1.6*cm, bottomMargin=1.7*cm,
                                title="Reporte Nmap - CyberPulse", author="CyberPulse")
        base = getSampleStyleSheet()
        normal = ParagraphStyle("Cuerpo", parent=base["Normal"], fontSize=9, leading=12, spaceAfter=4)
        pequeno = ParagraphStyle("Celda", parent=normal, fontSize=8, leading=10, spaceAfter=0)
        blanco = ParagraphStyle("Cabecera", parent=pequeno, textColor=colors.white, fontName="Helvetica-Bold")
        titulo = ParagraphStyle("Titulo", parent=base["Title"], fontSize=19, leading=23, textColor=colors.HexColor("#0B3D91"), alignment=0)
        h2 = ParagraphStyle("Seccion", parent=base["Heading2"], fontSize=12, leading=16,
                            textColor=colors.HexColor("#0B3D91"), spaceBefore=13, spaceAfter=7, keepWithNext=True)
        registro = ParagraphStyle("Registro", parent=normal, fontName="Courier", fontSize=7, leading=9, spaceAfter=1)

        def parrafo(texto, estilo=pequeno):
            return Paragraph(escape(str(texto)), estilo)

        def tabla(cabeceras, filas, proporciones):
            celdas = [[parrafo(c, blanco) for c in cabeceras]]
            celdas += [[parrafo(c) for c in fila] for fila in filas]
            resultado = Table(celdas, colWidths=[doc.width*p for p in proporciones], repeatRows=1, hAlign="LEFT")
            resultado.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0B3D91")),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#F1F5F9"), colors.white]),
                ("GRID", (0,0), (-1,-1), 0.4, colors.HexColor("#CBD5E1")),
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6),
                ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ]))
            return resultado

        elementos = []
        if ruta_logo and Path(ruta_logo).is_file():
            from io import BytesIO
            from PIL import Image as ImagenPIL
            with ImagenPIL.open(ruta_logo) as original:
                miniatura = original.copy()
                miniatura.thumbnail((220, 220))
                memoria = BytesIO()
                miniatura.save(memoria, format="PNG")
            memoria.seek(0)
            logo = Image(memoria, width=1.5*cm, height=1.5*cm)
            encabezado = Table([[logo, parrafo("Reporte de escaneo Nmap", titulo)]], colWidths=[1.9*cm, doc.width-1.9*cm])
            encabezado.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE"), ("LEFTPADDING", (0,0), (-1,-1), 0)]))
            elementos.append(encabezado)
        else:
            elementos.append(parrafo("Reporte de escaneo Nmap", titulo))
        elementos.append(parrafo("CyberPulse | Resultados organizados por equipo", normal))
        elementos.append(Spacer(1, 8))
        total_abiertos = sum(p["estado"] == "open" for e in equipos for p in e["puertos"])
        elementos.append(tabla(["Información", "Valor"], [
            ["Archivo de origen", ruta_txt.name],
            ["Equipos con bloque de resultado", str(len(equipos))],
            ["Puertos listados con estado open", str(total_abiertos)],
        ], [0.37, 0.63]))
        final = next((l for l in reversed(contenido.splitlines()) if l.startswith(("# Nmap done", "Nmap done:"))), "")
        if final:
            elementos.append(Spacer(1, 6))
            elementos.append(parrafo(final.lstrip("# "), pequeno))
        elementos.append(parrafo("Resumen por equipo", h2))
        if equipos:
            filas = []
            for equipo in equipos:
                abiertos = [p["puerto"] for p in equipo["puertos"] if p["estado"] == "open"]
                resumen = ", ".join(abiertos) if abiertos else "Ninguno listado con estado open"
                filas.append([equipo["direccion"], equipo["nombre"] or "No informado", resumen])
            elementos.append(tabla(["Dirección", "Nombre", "Puertos abiertos listados"], filas, [0.26, 0.26, 0.48]))
        else:
            elementos.append(parrafo("No se encontraron bloques de equipos. Revisa el registro: puede tratarse de un destino sin respuesta, un error de ejecución o un formato no reconocido.", normal))
        elementos.append(Spacer(1, 6))
        elementos.append(parrafo("Se muestran los estados informados por Nmap. La ausencia de puertos listados no implica que se hayan examinado todos los puertos; un puerto abierto no confirma una vulnerabilidad.", pequeno))

        # Página independiente para las tablas, sin separar la cabecera del primer dato.
        if equipos:
            elementos.append(PageBreak())
        for numero, equipo in enumerate(equipos, 1):
            elementos.append(parrafo(f"Equipo {numero} | {equipo['direccion']}", h2))
            if equipo["nombre"]:
                elementos.append(parrafo("Nombre: " + equipo["nombre"], normal))
            notas = [parrafo(nota, pequeno) for nota in equipo["notas"]]
            if notas:
                elementos.append(KeepTogether(notas))
                elementos.append(Spacer(1, 6))
            if equipo["puertos"]:
                filas = [[p["puerto"], p["estado"], p["servicio"], p["version"]] for p in equipo["puertos"]]
                elementos.append(tabla(["Puerto", "Estado", "Servicio", "Versión / identificación"], filas, [0.16, 0.19, 0.23, 0.42]))
            else:
                elementos.append(tabla(["Puertos", "Resultado"], [["Sin filas individuales", "Nmap no listó puertos individuales para este equipo. Consulta las notas anteriores para conocer el alcance y los estados resumidos."]], [0.27, 0.73]))
            elementos.append(Spacer(1, 10))

        elementos.append(PageBreak())
        elementos.append(parrafo("Anexo | Registro completo del escaneo", h2))
        elementos.append(parrafo("Contenido del TXT de origen. Las líneas largas se dividen únicamente para ajustarlas a la página.", pequeno))
        elementos.append(Spacer(1, 8))
        for linea in contenido.splitlines():
            for fragmento in textwrap.wrap(linea, width=112, replace_whitespace=False, drop_whitespace=False) or [" "]:
                elementos.append(parrafo(fragmento, registro))

        def pie(canvas, documento):
            canvas.saveState()
            canvas.setStrokeColor(colors.HexColor("#CBD5E1"))
            canvas.line(doc.leftMargin, 1.15*cm, letter[0]-doc.rightMargin, 1.15*cm)
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(colors.HexColor("#475569"))
            canvas.drawString(doc.leftMargin, 0.7*cm, "CyberPulse | Reporte Nmap")
            canvas.drawRightString(letter[0]-doc.rightMargin, 0.7*cm, f"Página {documento.page}")
            canvas.restoreState()

        doc.build(elementos, onFirstPage=pie, onLaterPages=pie)
        return str(ruta_pdf)
