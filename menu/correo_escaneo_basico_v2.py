import smtplib
import os
from email.message import EmailMessage


class CorreoEscaneoBasico:

    def __init__(self, remitente, destinatarios):
        self.remitente = remitente
        self.destinatarios = destinatarios
        #self.smtp_password = os.environ.get("SMTP_APP_PASSWORD")
        self.smtp_password = os.environ.get('SMTP_APP_PASSWORD', 'jualpulbnvmmvmkn')

        if not self.smtp_password:
            raise ValueError("No se encontró la variable SMTP_APP_PASSWORD")
            

    def enviar_correo_con_informe(self, ruta_archivo):

        try:
            # Validar archivo
            if not os.path.isfile(ruta_archivo):
                raise FileNotFoundError(f"No existe el archivo: {ruta_archivo}")

            # Leer contenido
            with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                contenido = f.read()

            # Crear email
            email = EmailMessage()
            email["From"] = self.remitente
            email["To"] = ", ".join(self.destinatarios)
            email["Subject"] = "CyberPulse - Reporte de Escaneo"

            email.set_content(f"""
Reporte generado por CyberPulse

Archivo: {os.path.basename(ruta_archivo)}

----------------------------------------

{contenido}
""")

            # Enviar correo
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(self.remitente, self.smtp_password)
                smtp.send_message(email)

            return True

        except Exception as e:
            print("Error enviando correo:", e)
            return False