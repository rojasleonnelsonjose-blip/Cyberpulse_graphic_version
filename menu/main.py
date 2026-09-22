import sys
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtWidgets import QApplication
from index import Ui_CYBERPULSE
from Modulos.Tools_Cyberpulse import Ui_Dialog as Ui_ToolsCyberpulse
from Modulos.Tools_Redes.Tool_redes import Ui_Dialog as Ui_ToolRedes
from Modulos.Tools_Redes.Funciones.scaner.Scaner import Ui_Dialog as Ui_Scaner
import socket 
import subprocess
import os
from Modulos.Reports.Report_pdf import ReportePDFNmap
from correo_escaneo_basico_v2 import CorreoEscaneoBasico
from configuracion_correo import ConfiguracionCorreo, validar_configuracion
from ventana_configuracion import VentanaConfiguracionCorreo





class MainPage(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_CYBERPULSE()
        self.ui.setupUi(self)


class ToolsPage(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.ui = Ui_ToolsCyberpulse()
        self.ui.setupUi(self)
        self.main_window = main_window

        self.ui.Back_tc.clicked.connect(self.volver_inicio)
        self.ui.Netwok_audit.clicked.connect(self.abrir_network_audit)
        self.ui.exit_tc.clicked.connect(QApplication.quit)

    def volver_inicio(self):
        self.main_window.cambiar_pagina(self.main_window.main_page)

    def abrir_network_audit(self):
        self.main_window.cambiar_pagina(self.main_window.network_audit_page)


class ToolRedes(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.ui = Ui_ToolRedes()
        self.ui.setupUi(self)
        self.main_window = main_window

        self.ui.Back_tr.clicked.connect(self.volver_inicio)
        self.ui.exit_tr.clicked.connect(QApplication.quit)
        self.ui.Scaner.clicked.connect(self.abrir_scaner)

    def volver_inicio(self):
        self.main_window.cambiar_pagina(self.main_window.tools_page)

    def abrir_scaner(self):
        self.main_window.cambiar_pagina(self.main_window.scaner_page)


class CyberPulseApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberPulse")
        self.setFixedSize(500, 400)

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.main_page = MainPage()
        self.tools_page = ToolsPage(self)
        self.network_audit_page = ToolRedes(self)
        self.scaner_page = ScanerPage(self)

        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.tools_page)
        self.stack.addWidget(self.network_audit_page)
        self.stack.addWidget(self.scaner_page)

        self.main_page.ui.Start_i.clicked.connect(self.abrir_tools)
        self.main_page.ui.Informacion.clicked.connect(self.informacion)
        self.main_page.ui.exit_i.clicked.connect(self.close)
        self.main_page.ui.config_i.setText("Configuración")
        self.main_page.ui.config_i.setToolTip("Configurar remitente, clave y destinatarios")
        self.main_page.ui.config_i.clicked.connect(self.abrir_configuracion)

        self.cambiar_pagina(self.main_page)

    def cambiar_pagina(self, pagina):
        self.stack.setCurrentWidget(pagina)

    def abrir_tools(self):
        self.cambiar_pagina(self.tools_page)

    def abrir_configuracion(self):
        VentanaConfiguracionCorreo(self).exec()

    def informacion(self):
        QtWidgets.QMessageBox.information(
            self,
            "Información",
            "Aplicación CyberPulse v1.0"
        )
def obtener_ip_local():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "No disponible"

class ScanerPage(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.ui = Ui_Scaner()
        self.ui.setupUi(self)
        self.main_window = main_window

        # Mostrar IP
        self.ui.label_ip.setText(f"IP local: {obtener_ip_local()}")

        # Crear proceso
        self.process = QtCore.QProcess(self)

        # Eventos del proceso
        self.process.started.connect(self.nmap_iniciado)
        self.process.finished.connect(self.nmap_finalizado)
        self.process.readyReadStandardOutput.connect(self.leer_salida)
        self.process.readyReadStandardError.connect(self.leer_error)

        # Botones
        self.ui.Back_s.clicked.connect(self.volver_atras)
        self.ui.exit_s.clicked.connect(QApplication.quit)
        self.ui.Start_s.clicked.connect(self.iniciar_scan)

    def volver_atras(self):
        self.main_window.cambiar_pagina(self.main_window.network_audit_page)

    def iniciar_scan(self):
        segmento = self.ui.imput_red.text()

        tipo = "basic" if self.ui.Basic.isChecked() else "complete"
        herramienta = "nmap" if self.ui.Nmap.isChecked() else "metasploit"
        modo = "silent" if self.ui.silent.isChecked() else "noisy"

        ruta = "Results"
        archivo = "scan.txt"

        # Crear carpeta si no existe
        os.makedirs(ruta, exist_ok=True)

        if herramienta != "nmap":
            QtWidgets.QMessageBox.warning(self, "Error", "Solo Nmap está soportado por ahora")
            return

        # Construir argumentos
        if tipo == "basic" and modo == "silent":
            args = ["-sn", segmento, "-oN", f"{ruta}/{archivo}"]

        elif tipo == "basic" and modo == "noisy":
            args = ["-sV", segmento, "-oN", f"{ruta}/{archivo}"]

        elif tipo == "complete" and modo == "silent":
            args = ["-sS", "-T2", segmento, "-oN", f"{ruta}/{archivo}"]

        elif tipo == "complete" and modo == "noisy":
            args = ["-A", "-T4", segmento, "-oN", f"{ruta}/{archivo}"]

        else:
            QtWidgets.QMessageBox.warning(self, "Error", "Configuración inválida")
            return

        # Ejecutar Nmap
        self.process.start("nmap", args)

    # Barra en ejecución
    def nmap_iniciado(self):
        self.ui.progressBar.setRange(0, 0)

    # Cuando termina
    def nmap_finalizado(self):
        self.ui.progressBar.setRange(0, 100)
        self.ui.progressBar.setValue(100)

        ruta_txt = "Results/scan.txt"
        ruta_pdf = "Results/reporte_nmap.pdf"
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        ruta_logo = os.path.join(
            base_dir,
            "resources",
            "logo_cyberpulse.png"
        )

        ruta_logo = os.path.normpath(ruta_logo)
        reporte = ReportePDFNmap()
        reporte.generar_pdf_desde_txt(ruta_txt, ruta_pdf, ruta_logo)

        QtWidgets.QMessageBox.information(
            self,
            "Reporte generado",
            "El PDF fue generado correctamente."
        )

        try:
            datos = ConfiguracionCorreo().cargar()
            validar_configuracion(datos["remitente"], datos["clave"], datos["destinatarios"])
        except (ValueError, OSError):
            QtWidgets.QMessageBox.warning(
                self, "Configura el correo",
                "El PDF está guardado. Para enviarlo, configura el remitente, la clave y los destinatarios."
            )
            if VentanaConfiguracionCorreo(self).exec() != QtWidgets.QDialog.DialogCode.Accepted:
                return
            try:
                datos = ConfiguracionCorreo().cargar()
            except (ValueError, OSError):
                QtWidgets.QMessageBox.warning(self, "Correo", "No se pudo leer la configuración guardada.")
                return

        correo = CorreoEscaneoBasico(
            remitente=datos["remitente"],
            destinatarios=datos["destinatarios"],
            smtp_password=datos["clave"]
        )

        enviado = correo.enviar_correo_con_informe(ruta_txt, ruta_pdf)

        if enviado:
            QtWidgets.QMessageBox.information(self, "Correo", "Enviado correctamente")
        else:
            QtWidgets.QMessageBox.warning(self, "Error", "No se pudo enviar el correo")

    # Leer salida
    def leer_salida(self):
        salida = self.process.readAllStandardOutput().data().decode(errors="ignore")
        print(salida)

    # Leer errores
    def leer_error(self):
        error = self.process.readAllStandardError().data().decode(errors="ignore")
        print(error)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CyberPulseApp()
    window.show()
    sys.exit(app.exec())



    