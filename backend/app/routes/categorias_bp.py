from flask import Blueprint, jsonify

from app.services.auth_service import AuthService
from app.services.producto_service import ProductoService

categorias_bp = Blueprint("categorias", __name__, url_prefix="/api")
_productos = ProductoService()
_auth = AuthService()


@categorias_bp.get("/categorias")
def categorias():
    datos = _productos.categorias()
    return jsonify({"total": len(datos), "categorias": datos})


@categorias_bp.get("/ciudades")
def ciudades():
    datos = _auth.obtener_ciudades()
    return jsonify({"total": len(datos), "ciudades": datos})