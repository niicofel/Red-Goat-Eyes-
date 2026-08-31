import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ_BACKEND = Path(__file__).resolve().parent.parent
RAIZ_PROYECTO = RAIZ_BACKEND.parent

load_dotenv(RAIZ_BACKEND / ".env")


def _entero(clave, defecto):
    try:
        return int(os.getenv(clave, defecto))
    except (TypeError, ValueError):
        return int(defecto)


def _booleano(clave, defecto=False):
    valor = os.getenv(clave)
    if valor is None:
        return defecto
    return valor.strip().lower() in ("1", "true", "si", "yes", "on")


def _decimal(clave, defecto):
    try:
        return float(os.getenv(clave, defecto))
    except (TypeError, ValueError):
        return float(defecto)


class Config:

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PUERTO = _entero("DB_PUERTO", 5432)
    DB_NOMBRE = os.getenv("DB_NOMBRE", "red_goat_eyes")
    DB_USUARIO = os.getenv("DB_USUARIO", "rge_flask")
    DB_CLAVE = os.getenv("DB_CLAVE", "")

    DB_ADMIN_USUARIO = os.getenv("DB_ADMIN_USUARIO", "rge_panel")
    DB_ADMIN_CLAVE = os.getenv("DB_ADMIN_CLAVE", "")

    DB_POOL_MIN = _entero("DB_POOL_MIN", 1)
    DB_POOL_MAX = _entero("DB_POOL_MAX", 10)

    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PUERTO = _entero("SMTP_PUERTO", 587)
    SMTP_USUARIO = os.getenv("SMTP_USUARIO", "")
    SMTP_CLAVE = os.getenv("SMTP_CLAVE", "")
    SMTP_REMITENTE = os.getenv("SMTP_REMITENTE", "Red Goat Eyes")
    SMTP_USAR_TLS = _booleano("SMTP_USAR_TLS", True)

    SECRET_KEY = os.getenv("SECRET_KEY", "clave-insegura-solo-para-desarrollo")
    BCRYPT_ROUNDS = _entero("BCRYPT_ROUNDS", 12)
    SESION_DURACION_HORAS = _entero("SESION_DURACION_HORAS", 8)

    IVA_PORCENTAJE = _decimal("IVA_PORCENTAJE", 0.15)
    MONEDA = os.getenv("MONEDA", "USD")
    TIENDA_NOMBRE = os.getenv("TIENDA_NOMBRE", "Red Goat Eyes")
    TIENDA_CIUDAD = os.getenv("TIENDA_CIUDAD", "Quito")

    FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")
    FLASK_PUERTO = _entero("FLASK_PUERTO", 5000)
    DEBUG = _booleano("FLASK_DEBUG", False)

    CARPETA_ESTATICA = str(RAIZ_PROYECTO / "assets")
    CARPETA_PAGINAS = str(RAIZ_PROYECTO / "pages")
    CARPETA_UPLOADS = str(RAIZ_PROYECTO / "assets" / "img" / "uploads")
    MAX_UPLOAD_MB = _entero("MAX_UPLOAD_MB", 2)
    MAX_CONTENT_LENGTH = MAX_UPLOAD_MB * 1024 * 1024

    @classmethod
    def cadena_conexion(cls):
        return (
            f"host={cls.DB_HOST} "
            f"port={cls.DB_PUERTO} "
            f"dbname={cls.DB_NOMBRE} "
            f"user={cls.DB_USUARIO} "
            f"password={cls.DB_CLAVE}"
        )

    @classmethod
    def cadena_conexion_admin(cls):
        return (
            f"host={cls.DB_HOST} "
            f"port={cls.DB_PUERTO} "
            f"dbname={cls.DB_NOMBRE} "
            f"user={cls.DB_ADMIN_USUARIO} "
            f"password={cls.DB_ADMIN_CLAVE}"
        )

    @classmethod
    def validar(cls):
        faltantes = []
        if not cls.DB_CLAVE:
            faltantes.append("DB_CLAVE")
        if cls.SECRET_KEY == "clave-insegura-solo-para-desarrollo":
            faltantes.append("SECRET_KEY")
        return faltantes

    @classmethod
    def resumen(cls):
        return {
            "base_de_datos": f"{cls.DB_USUARIO}@{cls.DB_HOST}:{cls.DB_PUERTO}/{cls.DB_NOMBRE}",
            "pool": f"{cls.DB_POOL_MIN}-{cls.DB_POOL_MAX}",
            "iva": cls.IVA_PORCENTAJE,
            "debug": cls.DEBUG,
            "smtp_configurado": bool(cls.SMTP_CLAVE and "PEGA_AQUI" not in cls.SMTP_CLAVE),
        }