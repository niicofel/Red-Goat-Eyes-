from flask import Blueprint, jsonify, request

from app.services.producto_service import ProductoService

productos_bp = Blueprint("productos", __name__, url_prefix="/api/productos")
_servicio = ProductoService()


@productos_bp.get("")
def listar():
    slug = request.args.get("categoria")
    busqueda = request.args.get("q")
    if busqueda:
        datos = _servicio.buscar(busqueda)
    else:
        datos = _servicio.catalogo(slug)
    return jsonify({"total": len(datos), "productos": datos})


@productos_bp.get("/destacados")
def destacados():
    datos = _servicio.destacados()
    return jsonify({"total": len(datos), "productos": datos})


@productos_bp.get("/<codigo>")
def detalle(codigo):
    return jsonify(_servicio.detalle(codigo))


@productos_bp.get("/disponibilidad/<int:id_producto_talla>")
def disponibilidad(id_producto_talla):
    cantidad = request.args.get("cantidad", 1, type=int)
    return jsonify({
        "id_producto_talla": id_producto_talla,
        "cantidad": cantidad,
        "disponible": _servicio.verificar_disponibilidad(id_producto_talla, cantidad),
    })