"""Configuración por usuario; la clave se protege con Windows DPAPI."""
import base64
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import re
import tempfile


def validar_configuracion(remitente, clave, destinatarios):
    remitente = remitente.strip()
    if isinstance(destinatarios, str):
        destinatarios = re.split(r"[;,\s]+", destinatarios.strip())
    destinatarios = list(dict.fromkeys(d.strip() for d in destinatarios if d.strip()))
    patron = r"[^\s@<>;,]+@[^\s@<>;,]+\.[^\s@<>;,]+"
    if not re.fullmatch(patron, remitente):
        raise ValueError("Introduce un correo remitente válido.")
    if not clave or not clave.strip():
        raise ValueError("Introduce la clave de envío del correo.")
    if not destinatarios or any(not re.fullmatch(patron, d) for d in destinatarios):
        raise ValueError("Introduce al menos un destinatario y revisa sus direcciones.")
    return {"remitente": remitente, "clave": clave, "destinatarios": destinatarios}


def _proteger(datos, descifrar=False):
    if os.name != "nt":
        raise OSError("El almacenamiento seguro de la clave requiere Windows.")

    class Blob(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("data", ctypes.POINTER(ctypes.c_ubyte))]

    buffer = (ctypes.c_ubyte * len(datos)).from_buffer_copy(datos)
    entrada = Blob(len(datos), buffer)
    salida = Blob()
    crypt = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    funcion = crypt.CryptUnprotectData if descifrar else crypt.CryptProtectData
    funcion.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p,
                        ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    funcion.restype = wintypes.BOOL
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    if not funcion(ctypes.byref(entrada), None, None, None, None, 1, ctypes.byref(salida)):
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return ctypes.string_at(salida.data, salida.size)
    finally:
        kernel.LocalFree(salida.data)


class ConfiguracionCorreo:
    def __init__(self, ruta=None):
        self.ruta = Path(ruta) if ruta else Path(os.environ.get("LOCALAPPDATA", Path.home())) / "CyberPulse" / "correo.json"

    def cargar_nombre(self):
        ruta = self.ruta.with_name("perfil.json")
        if not ruta.exists():
            return ""
        try:
            nombre = json.loads(ruta.read_text(encoding="utf-8"))["nombre"]
            if not isinstance(nombre, str):
                raise ValueError("Nombre inválido")
            return nombre.strip()
        except (ValueError, KeyError, TypeError) as exc:
            raise ValueError("No se pudo leer el nombre guardado. Puedes volver a configurarlo.") from exc

    def guardar_nombre(self, nombre):
        nombre = nombre.strip()
        if len(nombre) > 60:
            raise ValueError("El nombre debe tener un máximo de 60 caracteres.")
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.ruta.parent, delete=False) as archivo:
                temporal = Path(archivo.name)
                json.dump({"nombre": nombre}, archivo, ensure_ascii=False)
            os.replace(temporal, self.ruta.with_name("perfil.json"))
        finally:
            if temporal and temporal.exists():
                temporal.unlink()

    def cargar(self):
        if not self.ruta.exists():
            return {"remitente": "", "clave": "", "destinatarios": []}
        try:
            datos = json.loads(self.ruta.read_text(encoding="utf-8"))
            clave = _proteger(base64.b64decode(datos["clave_protegida"], validate=True), True).decode("utf-8")
            return validar_configuracion(datos["remitente"], clave, datos["destinatarios"])
        except Exception as exc:
            raise ValueError("No se pudo leer la configuración de correo. Vuelve a introducir los datos y guárdalos.") from exc

    def guardar(self, remitente, clave, destinatarios):
        datos = validar_configuracion(remitente, clave, destinatarios)
        datos["clave_protegida"] = base64.b64encode(_proteger(datos.pop("clave").encode("utf-8"))).decode("ascii")
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.ruta.parent, delete=False) as archivo:
                temporal = Path(archivo.name)
                json.dump(datos, archivo, ensure_ascii=False, indent=2)
            os.replace(temporal, self.ruta)
        finally:
            if temporal and temporal.exists():
                temporal.unlink()
