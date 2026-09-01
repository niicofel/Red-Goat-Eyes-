# ============================================================
# RUTAS DE AUTENTICACION
# Iniciar sesion, registrarse, cerrar sesion y direcciones.
# ============================================================
from flask import Blueprint, jsonify, request

from app.routes.sesion import (abrir_sesion, cerrar_sesion, requiere_sesion,
                               usuario_actual)
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
_servicio = AuthService()



# ---------------- Iniciar sesion ----------------
@auth_bp.post("/login")
def login():
    datos = request.get_json(silent=True) or {}
    usuario = _servicio.iniciar_sesion(datos.get("email"), datos.get("password"))
    abrir_sesion(usuario)
    return jsonify({"mensaje": "Sesion iniciada", "usuario": usuario.a_diccionario()})



# ---------------- Crear una cuenta ----------------
@auth_bp.post("/registro")
def registro():
    datos = request.get_json(silent=True) or {}
    usuario = _servicio.registrar(datos)
    abrir_sesion(usuario)
    return jsonify({"mensaje": "Cuenta creada", "usuario": usuario.a_diccionario()}), 201



# ---------------- Cerrar sesion ----------------
@auth_bp.post("/logout")
def logout():
    cerrar_sesion()
    return jsonify({"mensaje": "Sesion cerrada"})



# ---------------- Saber quien esta conectado ----------------
# El JavaScript la usa al cargar cada pagina
@auth_bp.get("/sesion")
def sesion():
    actual = usuario_actual()
    return jsonify({"autenticado": actual is not None, "usuario": actual})



# ---------------- Direcciones del cliente ----------------
@auth_bp.get("/direcciones")
@requiere_sesion
def direcciones():
    actual = usuario_actual()
    datos = _servicio.obtener_direcciones(actual["id_usuario"])
    return jsonify({"total": len(datos), "direcciones": datos})


@auth_bp.post("/direcciones")
@requiere_sesion
def crear_direccion():
    actual = usuario_actual()
    datos = request.get_json(silent=True) or {}
    id_direccion = _servicio.crear_direccion(actual["id_usuario"], datos)
    return jsonify({"mensaje": "Direccion creada", "id_direccion": id_direccion}), 201