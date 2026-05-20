from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import os
import re


class ReportePDFNmap:

    def generar_pdf_desde_txt(self, ruta_txt, ruta_pdf, ruta_logo=None):
        if not os.path.isfile(ruta_txt):
            raise FileNotFoundError(f"No existe el archivo TXT: {ruta_txt}")

        with open(ruta_txt, "r", encoding="utf-8", errors="ignore") as file:
            contenido = file.read()

        doc = SimpleDocTemplate(
            ruta_pdf,
            pagesize=letter,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm
        )

        estilos = getSampleStyleSheet()

        titulo = ParagraphStyle(
            "TituloCyberPulse",
            parent=estilos["Title"],
            fontSize=18,
            textColor=colors.HexColor("#0B3D91"),
            spaceAfter=12
        )

        subtitulo = ParagraphStyle(
            "Subtitulo",
            parent=estilos["Heading2"],
            fontSize=12,
            textColor=colors.HexColor("#333333"),
            spaceBefore=10,
            spaceAfter=6
        )

        normal = ParagraphStyle(
            "NormalCyber",
            parent=estilos["Normal"],
            fontSize=9,
            leading=12
        )

        elementos = []

        # Logo
        if ruta_logo and os.path.isfile(ruta_logo):
            logo = Image(ruta_logo, width=4 * cm, height=4 * cm)
            elementos.append(logo)
            elementos.append(Spacer(1, 8))

        elementos.append(Paragraph("Reporte de Escaneo Nmap - CyberPulse", titulo))
        elementos.append(Paragraph("Resumen del análisis de red generado automáticamente.", normal))
        elementos.append(Spacer(1, 12))

        # IP escaneada
        ip_match = re.search(r"Nmap scan report for ([\d\.]+)", contenido)
        ip = ip_match.group(1) if ip_match else "No identificada"

        elementos.append(Paragraph("Información general", subtitulo))

        tabla_info = Table([
            ["Campo", "Valor"],
            ["Host escaneado", ip],
            ["Archivo origen", os.path.basename(ruta_txt)]
        ], colWidths=[5 * cm, 10 * cm])

        tabla_info.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3D91")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F4F6F8")),
        ]))

        elementos.append(tabla_info)
        elementos.append(Spacer(1, 14))

        # Puertos
        elementos.append(Paragraph("Puertos detectados", subtitulo))


        filas = [["Puerto", "Estado", "Servicio", "Versión"]]

        capturar = False
        for linea in contenido.splitlines():
            if linea.startswith("PORT"):
                capturar = True
                continue

            if capturar:
                if linea.strip() == "" or linea.startswith("Device type"):
                    break

                partes = linea.split()
                if len(partes) >= 3:
                    puerto = partes[0]
                    estado = partes[1]
                    servicio = partes[2]
                    version = " ".join(partes[3:]) if len(partes) > 3 else ""

                    filas.append([puerto, estado, servicio, version])

        tabla_puertos = Table(filas, colWidths=[3 * cm, 3 * cm, 4 * cm, 6 * cm])

        estilo_tabla = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]

        puertos_rojos = {"21", "23", "445", "3389"}
        puertos_amarillos = {"80", "139", "135"}

        for i, fila in enumerate(filas[1:], start=1):

            numero_puerto = fila[0].split("/")[0]

            # 🔴 Riesgo alto
            if numero_puerto in puertos_rojos:

                estilo_tabla.append((
                    "BACKGROUND",
                    (0, i),
                    (-1, i),
                    colors.HexColor("#FECACA")
                ))

                estilo_tabla.append((
                    "TEXTCOLOR",
                    (0, i),
                    (-1, i),
                    colors.HexColor("#991B1B")
                ))

            # 🟡 Riesgo medio
            elif numero_puerto in puertos_amarillos:

                estilo_tabla.append((
                    "BACKGROUND",
                    (0, i),
                    (-1, i),
                    colors.HexColor("#FEF3C7")
                ))

                estilo_tabla.append((
                    "TEXTCOLOR",
                    (0, i),
                    (-1, i),
                    colors.HexColor("#92400E")
                ))

            # 🟢 Riesgo bajo
            else:

                estilo_tabla.append((
                    "BACKGROUND",
                    (0, i),
                    (-1, i),
                    colors.HexColor("#DCFCE7")
                ))

                estilo_tabla.append((
                    "TEXTCOLOR",
                    (0, i),
                    (-1, i),
                    colors.HexColor("#166534")
                ))


        tabla_puertos.setStyle(TableStyle(estilo_tabla))
        elementos.append(tabla_puertos)
        elementos.append(Spacer(1, 14))

        # Contenido completo
        elementos.append(Paragraph("Detalle completo del escaneo", subtitulo))

        for linea in contenido.splitlines():
            texto = linea.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            elementos.append(Paragraph(texto, normal))

        doc.build(elementos)

        return ruta_pdf