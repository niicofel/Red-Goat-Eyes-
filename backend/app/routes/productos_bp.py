# ============================================================
# RUTAS DE PRODUCTOS
# Catalogo, detalle, disponibilidad, inventario y reposicion.
# OJO con el orden: /<codigo> va al final, porque si no
# capturaria /inventario como si fuera un codigo de producto.
# ============================================================
from flask import Blueprint, jsonify, request

from app.routes.sesion import requiere_admin, usuario_actual
from app.services.producto_service import ProductoService

productos_bp = Blueprint("productos", __name__, url_prefix="/api/productos")
_servicio = ProductoService()



# ---------------- Listar el catalogo ----------------
@productos_bp.get("")
def listar():
    slug = request.args.get("categoria")
    busqueda = request.args.get("q")
    if busqueda:
        datos = _servicio.buscar(busqueda)
    else:
        datos = _servicio.catalogo(slug)
    return jsonify({"total": len(datos), "productos": datos})



# ---------------- Productos destacados ----------------
@productos_bp.get("/destacados")
def destacados():
    datos = _servicio.destacados()
    return jsonify({"total": len(datos), "productos": datos})



# ---------------- Inventario completo (solo admin) ----------------
@productos_bp.get("/inventario")
@requiere_admin()
def inventario():
    datos = _servicio.inventario_completo()
    return jsonify({
        "total": len(datos),
        "criticos": sum(1 for d in datos if d["critico"]),
        "agotados": sum(1 for d in datos if d["agotado"]),
        "inventario": datos,
    })



# ---------------- Reponer stock (admin nivel 2) ----------------
@productos_bp.post("/reponer")
@requiere_admin(nivel_minimo=2)
def reponer():
    actual = usuario_actual()
    datos = request.get_json(silent=True) or {}

    resultado = _servicio.reponer_stock(
        datos.get("codigo_producto"),
        datos.get("codigo_talla"),
        datos.get("cantidad"),
        actual["id_usuario"])

    return jsonify({"mensaje": "Stock repuesto", "producto": resultado})



# ---------------- Comprobar stock de una talla ----------------
@productos_bp.get("/disponibilidad/<int:id_producto_talla>")
def disponibilidad(id_producto_talla):
    cantidad = request.args.get("cantidad", 1, type=int)
    return jsonify({
        "id_producto_talla": id_producto_talla,
        "cantidad": cantidad,
        "disponible": _servicio.verificar_disponibilidad(id_producto_talla, cantidad),
    })



# ---------------- Detalle de un producto ----------------
# Va al final para no capturar las rutas de arriba
@productos_bp.get("/<codigo>")
def detalle(codigo):
    return jsonify(_servicio.detalle(codigo))