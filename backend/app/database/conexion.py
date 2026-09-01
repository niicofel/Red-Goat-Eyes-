# ============================================================
# CONEXION
# Maneja las conexiones a PostgreSQL con dos pools.
# Un pool es un grupo de conexiones ya abiertas y listas para usar,
# porque abrir una conexion cada vez seria lento.
# ============================================================
import atexit
import logging

import psycopg
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import Config
from app.utils.excepciones import ErrorRedGoatEyes

log = logging.getLogger(__name__)

_pool = None
_pool_admin = None



# ---------------- Error propio de base de datos ----------------
class ErrorBaseDatos(ErrorRedGoatEyes):

    def __init__(self, mensaje, original=None):
        super().__init__(mensaje, "ERROR_BASE_DATOS")
        self.original = original



# ---------------- Abrir el pool normal (rge_flask) ----------------
def iniciar_pool():
    global _pool
    if _pool is not None:
        return _pool

    _pool = ConnectionPool(
        conninfo=Config.cadena_conexion(),
        min_size=Config.DB_POOL_MIN,
        max_size=Config.DB_POOL_MAX,
        kwargs={"row_factory": dict_row},
        open=False,
        name="red_goat_eyes",
    )
    _pool.open(wait=True, timeout=10)
    log.info("Pool de conexiones abierto (%s-%s)", Config.DB_POOL_MIN, Config.DB_POOL_MAX)
    return _pool



# ---------------- Abrir el pool administrativo (rge_panel) ----------------
# Se necesita porque rge_flask no puede leer los reportes
def iniciar_pool_admin():
    global _pool_admin
    if _pool_admin is not None:
        return _pool_admin

    _pool_admin = ConnectionPool(
        conninfo=Config.cadena_conexion_admin(),
        min_size=1,
        max_size=3,
        kwargs={"row_factory": dict_row},
        open=False,
        name="red_goat_eyes_admin",
    )
    _pool_admin.open(wait=True, timeout=10)
    log.info("Pool administrativo abierto")
    return _pool_admin



# ---------------- Cerrar los pools al apagar ----------------
def cerrar_pool():
    global _pool, _pool_admin
    if _pool is not None:
        _pool.close()
        _pool = None
        log.info("Pool de conexiones cerrado")
    if _pool_admin is not None:
        _pool_admin.close()
        _pool_admin = None
        log.info("Pool administrativo cerrado")


atexit.register(cerrar_pool)



# ---------------- Pedir una conexion prestada ----------------
def obtener_conexion():
    if _pool is None:
        iniciar_pool()
    return _pool.connection()


def obtener_conexion_admin():
    if _pool_admin is None:
        iniciar_pool_admin()
    return _pool_admin.connection()



# ---------------- Consultas por el pool administrativo ----------------
def consultar_todos_admin(sql, parametros=None):
    try:
        with obtener_conexion_admin() as con:
            with con.cursor() as cur:
                cur.execute(sql, parametros or ())
                return cur.fetchall()
    except psycopg.Error as error:
        log.error("consultar_todos_admin fallo: %s", error)
        raise _traducir(error) from error


def consultar_uno_admin(sql, parametros=None):
    try:
        with obtener_conexion_admin() as con:
            with con.cursor() as cur:
                cur.execute(sql, parametros or ())
                return cur.fetchone()
    except psycopg.Error as error:
        log.error("consultar_uno_admin fallo: %s", error)
        raise _traducir(error) from error



# ---------------- Traducir errores de PostgreSQL ----------------
# Convierte errores tecnicos en mensajes que el usuario entienda
def _traducir(error):
    if isinstance(error, psycopg.errors.UniqueViolation):
        return ErrorBaseDatos("Ya existe un registro con esos datos", error)
    if isinstance(error, psycopg.errors.ForeignKeyViolation):
        return ErrorBaseDatos("El registro referenciado no existe", error)
    if isinstance(error, psycopg.errors.CheckViolation):
        return ErrorBaseDatos(_mensaje_limpio(error), error)
    if isinstance(error, psycopg.errors.RaiseException):
        return ErrorBaseDatos(_mensaje_limpio(error), error)
    if isinstance(error, psycopg.errors.InsufficientPrivilege):
        return ErrorBaseDatos("La aplicacion no tiene permisos para esta operacion", error)
    if isinstance(error, psycopg.OperationalError):
        return ErrorBaseDatos("No se pudo conectar con la base de datos", error)
    return ErrorBaseDatos("Error inesperado en la base de datos", error)


def _mensaje_limpio(error):
    texto = str(error).strip()
    return texto.split("\n")[0]



# ---------------- Consultas normales ----------------
def consultar_todos(sql, parametros=None):
    try:
        with obtener_conexion() as con:
            with con.cursor() as cur:
                cur.execute(sql, parametros or ())
                return cur.fetchall()
    except psycopg.Error as error:
        log.error("consultar_todos fallo: %s", error)
        raise _traducir(error) from error


def consultar_uno(sql, parametros=None):
    try:
        with obtener_conexion() as con:
            with con.cursor() as cur:
                cur.execute(sql, parametros or ())
                return cur.fetchone()
    except psycopg.Error as error:
        log.error("consultar_uno fallo: %s", error)
        raise _traducir(error) from error


def consultar_valor(sql, parametros=None):
    fila = consultar_uno(sql, parametros)
    if not fila:
        return None
    return next(iter(fila.values()))



# ---------------- INSERT, UPDATE y DELETE ----------------
def ejecutar(sql, parametros=None, devolver=False):
    try:
        with obtener_conexion() as con:
            with con.cursor() as cur:
                cur.execute(sql, parametros or ())
                resultado = cur.fetchone() if devolver else cur.rowcount
                con.commit()
                return resultado
    except psycopg.Error as error:
        log.error("ejecutar fallo: %s", error)
        raise _traducir(error) from error



# ---------------- Llamar a un procedimiento almacenado ----------------
def llamar_procedimiento(nombre, parametros=None):
    marcadores = ", ".join(["%s"] * len(parametros or ()))
    sql = f"CALL {nombre}({marcadores})"
    try:
        with obtener_conexion() as con:
            with con.cursor() as cur:
                cur.execute(sql, parametros or ())
                salida = cur.fetchone() if cur.description else None
                con.commit()
                return salida
    except psycopg.Error as error:
        log.error("llamar_procedimiento %s fallo: %s", nombre, error)
        raise _traducir(error) from error



# ---------------- Comprobar que la base responde ----------------
def probar_conexion():
    try:
        fila = consultar_uno("SELECT current_user AS usuario, version() AS motor")
        return {
            "conectado": True,
            "usuario": fila["usuario"],
            "motor": fila["motor"].split(",")[0],
        }
    except ErrorBaseDatos as error:
        return {"conectado": False, "error": error.mensaje}