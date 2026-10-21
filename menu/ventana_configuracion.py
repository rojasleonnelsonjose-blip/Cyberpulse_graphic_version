"""Ventana editable de configuración de correo."""
from PyQt6 import QtWidgets, QtCore
from configuracion_correo import ConfiguracionCorreo


class VentanaConfiguracionCorreo(QtWidgets.QDialog):
    nombre_guardado = QtCore.pyqtSignal(str)

    def __init__(self, parent=None, almacen=None):
        super().__init__(parent)
        self.almacen = almacen or ConfiguracionCorreo()
        self.setWindowTitle("Configuración — CyberPulse")
        self.resize(490, 410)
        layout = QtWidgets.QVBoxLayout(self)
        ayuda = QtWidgets.QLabel("Personaliza tu nombre y configura la cuenta de Gmail que enviará los informes.")
        ayuda.setWordWrap(True)
        layout.addWidget(ayuda)
        formulario = QtWidgets.QFormLayout()
        self.nombre = QtWidgets.QLineEdit()
        self.nombre.setMaxLength(60)
        self.nombre.setPlaceholderText("Nombre que aparecerá en la pantalla principal")
        formulario.addRow("Nombre de usuario:", self.nombre)
        self.remitente = QtWidgets.QLineEdit()
        self.remitente.setPlaceholderText("tu.correo@gmail.com")
        formulario.addRow("Correo remitente:", self.remitente)
        self.clave = QtWidgets.QLineEdit()
        self.clave.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.clave.setPlaceholderText("Contraseña de aplicación de Gmail")
        formulario.addRow("Clave de envío:", self.clave)
        mostrar = QtWidgets.QCheckBox("Mostrar clave")
        mostrar.toggled.connect(lambda visible: self.clave.setEchoMode(
            QtWidgets.QLineEdit.EchoMode.Normal if visible else QtWidgets.QLineEdit.EchoMode.Password))
        formulario.addRow("", mostrar)
        self.destinatarios = QtWidgets.QPlainTextEdit()
        self.destinatarios.setPlaceholderText("Un correo por línea, o separados por coma o punto y coma")
        self.destinatarios.setMaximumHeight(100)
        formulario.addRow("Correos receptores:", self.destinatarios)
        layout.addLayout(formulario)
        self.estado = QtWidgets.QLabel()
        self.estado.setWordWrap(True)
        layout.addWidget(self.estado)
        botones = QtWidgets.QDialogButtonBox()
        self.guardar_boton = botones.addButton("Guardar", QtWidgets.QDialogButtonBox.ButtonRole.AcceptRole)
        botones.addButton("Cancelar", QtWidgets.QDialogButtonBox.ButtonRole.RejectRole)
        botones.accepted.connect(self.guardar)
        botones.rejected.connect(self.reject)
        layout.addWidget(botones)
        try:
            datos = self.almacen.cargar()
            self.remitente.setText(datos["remitente"])
            self.clave.setText(datos["clave"])
            self.destinatarios.setPlainText("\n".join(datos["destinatarios"]))
            self.estado.setText("Los datos se conservan al cerrar la aplicación. Puedes modificarlos aquí.")
        except ValueError as exc:
            self.estado.setText(str(exc))
        try:
            self.nombre.setText(self.almacen.cargar_nombre())
        except (ValueError, OSError) as exc:
            self.estado.setText(str(exc))

    def guardar(self):
        try:
            if any((self.remitente.text().strip(), self.clave.text(), self.destinatarios.toPlainText().strip())):
                self.almacen.guardar(self.remitente.text(), self.clave.text(), self.destinatarios.toPlainText())
            self.almacen.guardar_nombre(self.nombre.text())
        except ValueError as exc:
            self.estado.setText(str(exc))
            return
        except OSError as exc:
         self.estado.setText(
         f"No se pudo guardar la configuración: {exc}"
        )
         return
        self.nombre_guardado.emit(self.nombre.text().strip() or "usuario")
        QtWidgets.QMessageBox.information(self, "Configuración", "Configuración guardada correctamente.")
        self.accept()
