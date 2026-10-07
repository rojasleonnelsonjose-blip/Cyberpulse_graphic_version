"""Tabla educativa de riesgos sugeridos, proporcionada para CyberPulse."""
from PyQt6 import QtCore, QtGui, QtWidgets


# Puerto, servicio, uso, riesgo sugerido, principal riesgo, color de referencia.
RIESGOS = [
    ("20/21", "FTP", "Transferencia de archivos", "Alto", "Credenciales/datos sin cifrar", "rojo"),
    ("22", "SSH / SFTP", "Administración / archivos", "Alto", "Acceso remoto privilegiado", "naranja"),
    ("23", "Telnet", "Administración remota", "Crítico", "Comunicación y credenciales sin cifrar", "rojo"),
    ("25", "SMTP", "Correo", "Alto", "Relay, spoofing y abuso si está mal configurado", "naranja"),
    ("53", "DNS", "Resolución de nombres", "Alto", "Amplificación, tunneling, transferencia de zona", "naranja"),
    ("67/68", "DHCP", "Asignación IP", "Medio", "Servidores DHCP no autorizados", "amarillo"),
    ("69", "TFTP", "Transferencia simple", "Alto", "Sin autenticación ni cifrado", "rojo"),
    ("80", "HTTP", "Web", "Alto", "Comunicación sin cifrar", "naranja"),
    ("88", "Kerberos", "Autenticación", "Alto", "Servicio crítico de autenticación", "naranja"),
    ("110", "POP3", "Correo", "Alto", "Puede transmitir credenciales sin cifrado", "rojo"),
    ("123", "NTP", "Sincronización horaria", "Medio", "Amplificación/manipulación si se expone", "amarillo"),
    ("135", "MS RPC", "Servicios Windows", "Alto", "Enumeración y superficie RPC", "rojo"),
    ("137-139", "NetBIOS", "Compartición Windows", "Alto", "Enumeración y movimiento lateral", "rojo"),
    ("143", "IMAP", "Correo", "Alto", "Comunicación sin cifrar si no usa TLS", "naranja"),
    ("161/162", "SNMP", "Monitoreo", "Alto", "Exposición de información; versiones antiguas débiles", "rojo"),
    ("389", "LDAP", "Directorio", "Alto", "LDAP sin TLS puede exponer credenciales/datos", "rojo"),
    ("443", "HTTPS", "Web segura", "Medio", "Riesgo depende de aplicación, TLS y exposición", "amarillo"),
    ("445", "SMB", "Archivos Windows", "Crítico", "Movimiento lateral, ransomware y explotación SMB", "rojo"),
    ("465/587", "SMTP TLS/Submission", "Correo", "Medio", "Abuso de autenticación/configuración", "amarillo"),
    ("636", "LDAPS", "Directorio seguro", "Medio", "Servicio sensible aunque esté cifrado", "amarillo"),
    ("1433", "Microsoft SQL Server", "Base de datos", "Crítico", "Acceso directo a BD", "rojo"),
    ("1521", "Oracle", "Base de datos", "Crítico", "Exposición directa de Oracle", "rojo"),
    ("2049", "NFS", "Archivos Unix/Linux", "Alto", "Acceso a recursos compartidos", "rojo"),
    ("3306", "MySQL/MariaDB", "Base de datos", "Crítico", "Exposición directa de BD", "rojo"),
    ("3389", "RDP", "Escritorio remoto", "Crítico", "Ataques de credenciales y acceso remoto", "rojo"),
    ("5432", "PostgreSQL", "Base de datos", "Crítico", "Exposición directa de BD", "rojo"),
    ("5900", "VNC", "Escritorio remoto", "Crítico", "Acceso remoto al equipo", "rojo"),
    ("5985", "WinRM HTTP", "Administración Windows", "Alto", "Administración remota sin TLS", "rojo"),
    ("5986", "WinRM HTTPS", "Administración Windows", "Alto", "Administración remota privilegiada", "naranja"),
    ("6379", "Redis", "Base de datos/cache", "Crítico", "Instancias mal protegidas pueden permitir acceso a datos", "rojo"),
    ("8080", "HTTP alternativo", "Web/API", "Alto", "Aplicaciones o consolas administrativas", "naranja"),
    ("8443", "HTTPS alternativo", "Web/API", "Alto", "Puede alojar consolas administrativas", "naranja"),
    ("9200", "Elasticsearch", "API/BD", "Crítico", "Consulta/exposición de datos", "rojo"),
    ("27017", "MongoDB", "Base de datos", "Crítico", "Acceso directo a BD", "rojo"),
    ("3200+", "SAP Dispatcher", "SAP GUI", "Alto", "Acceso a instancia SAP", "rojo"),
    ("3300+", "SAP Gateway", "RFC/CPIC", "Alto", "Comunicación RFC y superficie Gateway", "rojo"),
    ("3600+", "SAP Message Server", "SAP", "Alto", "Servicio interno sensible", "rojo"),
    ("30013+", "SAP HANA", "Base de datos", "Crítico", "Acceso a infraestructura HANA", "rojo"),
]


class VentanaTablaRiesgos(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CyberPulse - Tabla de riesgos por puerto")
        self.resize(1120, 700)
        self.setMinimumSize(720, 440)
        layout = QtWidgets.QVBoxLayout(self)
        titulo = QtWidgets.QLabel("Puertos, servicios y riesgos sugeridos")
        fuente = titulo.font()
        fuente.setPointSize(15)
        fuente.setBold(True)
        titulo.setFont(fuente)
        layout.addWidget(titulo)
        aviso = QtWidgets.QLabel("Guía educativa de referencia. Un puerto abierto no confirma una vulnerabilidad: el riesgo real depende del servicio, su configuración y la exposición.")
        aviso.setWordWrap(True)
        layout.addWidget(aviso)
        filtros = QtWidgets.QHBoxLayout()
        self.busqueda = QtWidgets.QLineEdit()
        self.busqueda.setPlaceholderText("Buscar puerto, servicio, uso o riesgo...")
        self.busqueda.setClearButtonEnabled(True)
        self.busqueda.setAccessibleName("Buscar en la tabla de riesgos")
        filtros.addWidget(self.busqueda, 1)
        filtros.addWidget(QtWidgets.QLabel("Riesgo:"))
        self.filtro = QtWidgets.QComboBox()
        self.filtro.addItems(["Todos", "Crítico", "Alto", "Medio"])
        self.filtro.setAccessibleName("Filtrar por riesgo sugerido")
        filtros.addWidget(self.filtro)
        layout.addLayout(filtros)
        self.tabla = QtWidgets.QTableWidget(len(RIESGOS), 5)
        self.tabla.setHorizontalHeaderLabels(["Puerto", "Servicio común", "Uso", "Riesgo sugerido", "Principal riesgo"])
        self.tabla.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setWordWrap(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.horizontalHeader().setStretchLastSection(True)
        for columna, ancho in enumerate([85, 175, 185, 130, 440]):
            self.tabla.setColumnWidth(columna, ancho)
        colores = {"rojo": ("#FEE2E2", "#991B1B"), "naranja": ("#FFEDD5", "#9A3412"), "amarillo": ("#FEF9C3", "#713F12")}
        for fila, registro in enumerate(RIESGOS):
            for columna, valor in enumerate(registro[:5]):
                item = QtWidgets.QTableWidgetItem(valor)
                item.setToolTip(valor)
                if columna == 3:
                    fondo, texto = colores[registro[5]]
                    item.setBackground(QtGui.QColor(fondo))
                    item.setForeground(QtGui.QColor(texto))
                    fuente_riesgo = item.font()
                    fuente_riesgo.setBold(True)
                    item.setFont(fuente_riesgo)
                    item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                self.tabla.setItem(fila, columna, item)
        self.tabla.resizeRowsToContents()
        layout.addWidget(self.tabla, 1)
        self.contador = QtWidgets.QLabel()
        layout.addWidget(self.contador)
        nota = QtWidgets.QLabel("Se conserva la clasificación y los colores de la tabla proporcionada. Las referencias SAP con '+' no se interpretan como todos los puertos superiores; verifica el puerto concreto de la instancia.")
        nota.setWordWrap(True)
        layout.addWidget(nota)
        cerrar = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Close)
        cerrar.rejected.connect(self.reject)
        layout.addWidget(cerrar)
        self.busqueda.textChanged.connect(self.filtrar)
        self.filtro.currentTextChanged.connect(self.filtrar)
        self.filtrar()

    def filtrar(self, *_):
        consulta = self.busqueda.text().strip().casefold()
        nivel = self.filtro.currentText()
        visibles = 0
        for fila, registro in enumerate(RIESGOS):
            coincide = consulta in " ".join(registro[:5]).casefold() and (nivel == "Todos" or registro[3] == nivel)
            self.tabla.setRowHidden(fila, not coincide)
            visibles += int(coincide)
        self.contador.setText(f"{visibles} de {len(RIESGOS)} servicios" if visibles else "No hay resultados para estos filtros.")
