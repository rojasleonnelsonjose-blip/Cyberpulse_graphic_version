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
import shutil
from pathlib import Path
from datetime import datetime
from escaneo_metasploit import (PUERTOS_BASICOS, validar_destino, comandos_escaneo,
    limpiar_salida, escaneo_correcto, generar_pdf_metasploit)
import os
from Modulos.Reports.Report_pdf import ReportePDFNmap
from correo_escaneo_basico_v2 import CorreoEscaneoBasico
from configuracion_correo import ConfiguracionCorreo, validar_configuracion
from ventana_configuracion import VentanaConfiguracionCorreo
from ventana_pentesting import VentanaPentesting
from tabla_riesgos import VentanaTablaRiesgos





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
        self.ui.pushButton_7.setText("Pentesting")
        self.ui.pushButton_7.clicked.connect(self.abrir_pentesting)
        if not sys.platform.startswith("linux"):
            self.ui.pushButton_7.setEnabled(False)
            self.ui.pushButton_7.setToolTip("Pentesting está disponible en Linux.")
        self.ui.exit_tc.clicked.connect(QApplication.quit)

    def volver_inicio(self):
        self.main_window.cambiar_pagina(self.main_window.main_page)

    def abrir_network_audit(self):
        self.main_window.cambiar_pagina(self.main_window.network_audit_page)

    def abrir_pentesting(self):
        VentanaPentesting(
            self.main_window,
            self.main_window.scaner_page.localizar_metasploit,
            Path(__file__).resolve().parent.parent / "Results",
        ).exec()


class ToolRedes(QtWidgets.QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.ui = Ui_ToolRedes()
        self.ui.setupUi(self)
        self.main_window = main_window

        self.ui.Back_tr.clicked.connect(self.volver_inicio)
        self.ui.exit_tr.clicked.connect(QApplication.quit)
        self.ui.Scaner.clicked.connect(self.abrir_scaner)
        self.ui.risk_table.clicked.connect(self.abrir_tabla_riesgos)

    def volver_inicio(self):
        self.main_window.cambiar_pagina(self.main_window.tools_page)

    def abrir_scaner(self):
        self.main_window.cambiar_pagina(self.main_window.scaner_page)

    def abrir_tabla_riesgos(self):
        VentanaTablaRiesgos(self).exec()


class CyberPulseApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CyberPulse")
        self.resize(780, 620)
        self.setMinimumSize(700, 540)

        self.stack = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.stack)

        self.main_page = MainPage()
        self.main_page.ui.user.setTextFormat(QtCore.Qt.TextFormat.PlainText)
        self.main_page.ui.user.setWordWrap(True)
        try:
            self.main_page.ui.user.setText(ConfiguracionCorreo().cargar_nombre() or "usuario")
        except (ValueError, OSError):
            self.main_page.ui.user.setText("usuario")
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
        self.main_page.ui.config_i.setToolTip("Configurar nombre de usuario y correo")
        self.main_page.ui.config_i.clicked.connect(self.abrir_configuracion)

        self.cambiar_pagina(self.main_page)

    def cambiar_pagina(self, pagina):
        self.stack.setCurrentWidget(pagina)

    def abrir_tools(self):
        self.cambiar_pagina(self.tools_page)

    def abrir_configuracion(self):
        ventana = VentanaConfiguracionCorreo(self)
        ventana.nombre_guardado.connect(self.main_page.ui.user.setText)
        return ventana.exec()

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

        self.grupos = []
        for botones in ((self.ui.Nmap, self.ui.Metasploit), (self.ui.Basic, self.ui.Complete), (self.ui.silent, self.ui.Noysi)):
            grupo = QtWidgets.QButtonGroup(self)
            grupo.setExclusive(True)
            for boton in botones:
                grupo.addButton(boton)
            botones[0].setChecked(True)
            self.grupos.append(grupo)
        self.ui.imput_red.clear()
        self.ui.imput_red.setPlaceholderText("IP o red CIDR: 192.168.1.0/24")
        self.ui.Noysi.setText("Normal")
        self.ui.silent.setText("Pausado")
        self.ui.silent.setToolTip("Menor concurrencia en Metasploit; no hace invisible el escaneo.")
        self.puertos = QtWidgets.QLineEdit(PUERTOS_BASICOS)
        self.puertos.setToolTip("Metasploit: Basic propone puertos comunes; Complete, 1-65535. Puedes editarlos.")
        self.ui.gridLayout.addWidget(QtWidgets.QLabel("Puertos Metasploit:"), 6, 0, 1, 2)
        self.ui.gridLayout.addWidget(self.puertos, 6, 2, 1, 4)
        self.puertos.setEnabled(False)
        self.ui.Metasploit.toggled.connect(self.puertos.setEnabled)
        if not sys.platform.startswith("linux"):
            self.ui.Metasploit.setEnabled(False)
            self.ui.Metasploit.setToolTip("Disponible al ejecutar CyberPulse en Linux.")
        self.ui.Basic.toggled.connect(lambda basico: self.puertos.setText(PUERTOS_BASICOS if basico else "1-65535"))
        self.salida_visible = QtWidgets.QPlainTextEdit()
        self.salida_visible.setReadOnly(True)
        self.salida_visible.setMaximumBlockCount(3000)
        self.salida_visible.setPlaceholderText("Aquí aparecerá el progreso del escaneo.")
        self.ui.gridLayout.addWidget(self.salida_visible, 7, 0, 1, 6)
        self.texto_proceso = ""
        self.herramienta_actual = "nmap"
        self.ruta_txt = None

        # Mostrar IP
        self.ui.label_ip.setText(f"IP local: {obtener_ip_local()}")

        # Crear proceso
        self.process = QtCore.QProcess(self)

        # Eventos del proceso
        self.process.started.connect(self.nmap_iniciado)
        self.process.finished.connect(self.nmap_finalizado)
        self.process.readyReadStandardOutput.connect(self.leer_salida)
        self.process.readyReadStandardError.connect(self.leer_error)

        self.process.errorOccurred.connect(self.error_proceso)

        # Botones
        self.ui.Back_s.clicked.connect(self.volver_atras)
        self.ui.exit_s.clicked.connect(QApplication.quit)
        self.ui.Start_s.clicked.connect(self.iniciar_scan)

    def volver_atras(self):
        self.main_window.cambiar_pagina(self.main_window.network_audit_page)

    def iniciar_scan(self):
        if self.process.state() != QtCore.QProcess.ProcessState.NotRunning:
            return
        try:
            segmento = validar_destino(self.ui.imput_red.text())
            tipo = "basic" if self.ui.Basic.isChecked() else "complete"
            herramienta = "nmap" if self.ui.Nmap.isChecked() else "metasploit"
            pausado = self.ui.silent.isChecked()
            programa = "nmap"
            if herramienta == "metasploit":
                comandos = comandos_escaneo(segmento, self.puertos.text(), pausado)
                programa = self.localizar_metasploit()
                if not programa:
                    return
                args = ["-q", "-x", comandos]
            else:
                opciones = {
                    ("basic", True): ["-sn"], ("basic", False): ["-sV"],
                    ("complete", True): ["-sS", "-T2"], ("complete", False): ["-A", "-T4"],
                }
                args = opciones[tipo, pausado] + [segmento]
            carpeta = Path(__file__).resolve().parent.parent / "Results"
            carpeta.mkdir(parents=True, exist_ok=True)
            identificador = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            self.ruta_txt = carpeta / f"{herramienta}_{identificador}.txt"
            self.ruta_pdf = self.ruta_txt.with_suffix(".pdf")
            self.herramienta_actual = herramienta
            self.destino_actual = segmento
            self.puertos_actuales = self.puertos.text().strip()
            if herramienta == "nmap":
                args += ["-oN", str(self.ruta_txt)]
            self.texto_proceso = ""
            self.salida_visible.clear()
            self.salida_visible.appendPlainText(f"Iniciando {herramienta} sobre {segmento}...")
            self.ui.Start_s.setEnabled(False)
            self.process.start(programa, args)
        except (ValueError, OSError) as exc:
            self.ui.Start_s.setEnabled(True)
            QtWidgets.QMessageBox.warning(self, "Escaneo", str(exc))

    def localizar_metasploit(self):
        if not sys.platform.startswith("linux"):
            raise ValueError("Metasploit y Pentesting se ejecutan en Linux. En Windows puedes utilizar los escaneos de Nmap.")
        ajustes = QtCore.QSettings("CyberPulse", "CyberPulse")
        ruta = ajustes.value("metasploit/ejecutable", "")
        if ruta and Path(ruta).is_file() and os.access(ruta, os.X_OK) and Path(ruta).name == "msfconsole":
            return ruta
        ruta = shutil.which("msfconsole")
        if ruta:
            return ruta
        QtWidgets.QMessageBox.information(self, "Metasploit no disponible", "No se encontró msfconsole. En Linux/Docker, instala Metasploit en el mismo entorno donde se ejecuta CyberPulse y añade msfconsole al PATH. Si ya tienes una instalación local, selecciona su ejecutable; de lo contrario, cancela.")
        ruta, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Seleccionar msfconsole", "", "Metasploit (msfconsole);;Todos los archivos (*)")
        if ruta:
            if Path(ruta).name != "msfconsole" or not os.access(ruta, os.X_OK):
                raise ValueError("Selecciona msfconsole con permiso de ejecución en Linux.")
            ajustes.setValue("metasploit/ejecutable", ruta)
        return ruta

    def error_proceso(self, error):
        if error == QtCore.QProcess.ProcessError.FailedToStart:
            self.ui.Start_s.setEnabled(True)
            self.ui.progressBar.setRange(0, 100)
            self.ui.progressBar.setValue(0)
            QtWidgets.QMessageBox.warning(self, "No se pudo iniciar", "Comprueba que la herramienta esté instalada y su ruta sea correcta. " + self.process.errorString())

    # Barra en ejecución
    def nmap_iniciado(self):
        self.ui.progressBar.setRange(0, 0)

    # Cuando termina
    def nmap_finalizado(self, codigo, estado):
        self.leer_salida()
        self.leer_error()
        self.ui.progressBar.setRange(0, 100)
        self.ui.Start_s.setEnabled(True)
        texto = limpiar_salida(self.texto_proceso)
        try:
            if self.herramienta_actual == "metasploit":
                self.ruta_txt.write_text(texto, encoding="utf-8")
            correcto = codigo == 0 and estado == QtCore.QProcess.ExitStatus.NormalExit
            if self.herramienta_actual == "metasploit":
                correcto = correcto and escaneo_correcto(texto)
            if not correcto:
                self.ui.progressBar.setValue(0)
                QtWidgets.QMessageBox.warning(self, "Escaneo incompleto", "La herramienta no terminó correctamente. Revisa el registro de la pantalla. No se enviará un informe.")
                return
            ruta_txt, ruta_pdf = str(self.ruta_txt), str(self.ruta_pdf)
            if self.herramienta_actual == "metasploit":
                generar_pdf_metasploit(ruta_txt, ruta_pdf, self.destino_actual, self.puertos_actuales)
            else:
                ruta_logo = str(Path(__file__).resolve().parent.parent / "Resources" / "logo_cyberpulse.png")
                ReportePDFNmap().generar_pdf_desde_txt(ruta_txt, ruta_pdf, ruta_logo)
        except Exception as exc:
            self.ui.progressBar.setValue(0)
            QtWidgets.QMessageBox.warning(self, "Reporte", "No se pudo guardar el reporte: " + str(exc))
            return
        self.ui.progressBar.setValue(100)
        QtWidgets.QMessageBox.information(self, "Reporte generado", "El PDF fue generado correctamente.\n" + ruta_pdf)

        try:
            datos = ConfiguracionCorreo().cargar()
            validar_configuracion(datos["remitente"], datos["clave"], datos["destinatarios"])
        except (ValueError, OSError):
            QtWidgets.QMessageBox.warning(
                self, "Configura el correo",
                "El PDF está guardado. Para enviarlo, configura el remitente, la clave y los destinatarios."
            )
            if self.main_window.abrir_configuracion() != QtWidgets.QDialog.DialogCode.Accepted:
                return
            try:
                datos = ConfiguracionCorreo().cargar()
                validar_configuracion(datos["remitente"], datos["clave"], datos["destinatarios"])
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
        self.texto_proceso += salida
        if salida:
            self.salida_visible.appendPlainText(limpiar_salida(salida))

    # Leer errores
    def leer_error(self):
        error = self.process.readAllStandardError().data().decode(errors="ignore")
        self.texto_proceso += error
        if error:
            self.salida_visible.appendPlainText(limpiar_salida(error))



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CyberPulseApp()
    window.show()
    sys.exit(app.exec())



    
