import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication
from index import Ui_CYBERPULSE
from Modulos.Tools_Cyberpulse import Ui_Dialog as Ui_ToolsCyberpulse
from Modulos.Tools_Redes.Tool_redes import Ui_Dialog as Ui_ToolRedes
from Modulos.Tools_Redes.Funciones.scaner.Scaner import Ui_Dialog as Ui_Scaner
import socket 

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

        self.cambiar_pagina(self.main_page)

    def cambiar_pagina(self, pagina):
        self.stack.setCurrentWidget(pagina)

    def abrir_tools(self):
        self.cambiar_pagina(self.tools_page)

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

        self.ui.label_ip.setText(f"IP local: {obtener_ip_local()}")

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

        print(segmento, tipo, herramienta, modo)


    def volver_atras(self):
        self.main_window.cambiar_pagina(self.main_window.network_audit_page)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = CyberPulseApp()
    window.show()
    sys.exit(app.exec())



    