# ============================================================
# CREATE APP
# Arma la aplicacion Flask: configura las sesiones, abre la
# conexion a la base, registra las rutas y los manejadores de
# error. Tambien sirve el HTML, el CSS y las imagenes.
# ============================================================
import logging
from datetime import timedelta

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from app.config import Config, RAIZ_PROYECTO
from app.database import iniciar_pool, probar_conexion
from app.routes import registrar_blueprints
from app.utils.excepciones import ErrorRedGoatEyes

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(name)s  %(message)s",
    datefmt="%H:%M:%S")

log = logging.getLogger("red_goat_eyes")



# ---------------- Armar la aplicacion ----------------
def create_app():
    app = Flask(__name__,
                static_folder=Config.CARPETA_ESTATICA,
                static_url_path="/assets")

    app.config["SECRET_KEY"] = Config.SECRET_KEY
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_CONTENT_LENGTH
    app.config["JSON_SORT_KEYS"] = False
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=Config.SESION_DURACION_HORAS)
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_HTTPONLY"] = True

    CORS(app, supports_credentials=True)

    iniciar_pool()
    registrar_blueprints(app)
    _registrar_paginas(app)
    _registrar_errores(app)

    log.info("Aplicacion lista en %s", Config.resumen()["base_de_datos"])
    return app



# ---------------- Servir las paginas HTML ----------------
# Por eso todo corre en un solo servidor y las llamadas a /api funcionan
def _registrar_paginas(app):

    @app.get("/")
    def inicio():
        return send_from_directory(str(RAIZ_PROYECTO), "index.html")

    @app.get("/index.html")
    def inicio_alterno():
        return send_from_directory(str(RAIZ_PROYECTO), "index.html")

    @app.get("/pages/<path:archivo>")
    def pagina(archivo):
        return send_from_directory(Config.CARPETA_PAGINAS, archivo)

    @app.get("/api/salud")
    def salud():
        estado = probar_conexion()
        codigo = 200 if estado["conectado"] else 503
        return jsonify({"servicio": "Red Goat Eyes API",
                        "base_de_datos": estado}), codigo



# ---------------- Traducir errores a codigos HTTP ----------------
# Convierte las excepciones propias en 400, 403, 409, etc.
def _registrar_errores(app):

    @app.errorhandler(ErrorRedGoatEyes)
    def error_dominio(error):
        codigos = {
            "VALIDACION": 400,
            "CARRITO_VACIO": 400,
            "STOCK_INSUFICIENTE": 409,
            "TRANSICION_INVALIDA": 409,
            "USUARIO_DUPLICADO": 409,
            "CREDENCIALES_INVALIDAS": 401,
            "PERMISO_DENEGADO": 403,
            "PRODUCTO_NO_ENCONTRADO": 404,
            "ERROR_BASE_DATOS": 500,
        }
        estado = codigos.get(error.codigo, 400)
        log.warning("%s -> %s", error.codigo, error.mensaje)
        return jsonify(error.a_diccionario()), estado

    @app.errorhandler(404)
    def no_encontrado(error):
        return jsonify({"error": "NO_ENCONTRADO",
                        "mensaje": "El recurso solicitado no existe"}), 404

    @app.errorhandler(405)
    def metodo_no_permitido(error):
        return jsonify({"error": "METODO_NO_PERMITIDO",
                        "mensaje": "Metodo HTTP no permitido en esta ruta"}), 405

    @app.errorhandler(500)
    def error_interno(error):
        log.exception("Error interno no controlado")
        return jsonify({"error": "ERROR_INTERNO",
                        "mensaje": "Ocurrio un error inesperado"}), 500


__all__ = ["create_app"]