# ============================================================
# RUTAS DE PEDIDOS
# Calcular totales, registrar la compra y consultar pedidos.
# ============================================================
from flask import Blueprint, jsonify, request

from app.routes.sesion import requiere_admin, requiere_sesion, usuario_actual
from app.services.correo_service import CorreoService
from app.services.pedido_service import PedidoService

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/api/pedidos")
_servicio = PedidoService()
_correo = CorreoService()



# ---------------- Calcular totales del carrito ----------------
# Publico: se puede calcular sin tener sesion
@pedidos_bp.post("/calcular")
def calcular():
    datos = request.get_json(silent=True) or {}
    return jsonify(_servicio.calcular_totales(datos.get("items") or []))



# ---------------- Metodos de pago disponibles ----------------
@pedidos_bp.get("/metodos-pago")
def metodos_pago():
    return jsonify({"metodos": _servicio.metodos_pago()})



# ---------------- Registrar un pedido ----------------
# Despues de crearlo, lanza el envio del recibo en segundo plano
@pedidos_bp.post("")
@requiere_sesion
def crear():
    actual = usuario_actual()
    datos = request.get_json(silent=True) or {}
    pedido = _servicio.registrar(actual["id_usuario"], datos)
    _correo.enviar_pendientes_en_segundo_plano()
    return jsonify({"mensaje": "Pedido registrado", "pedido": pedido}), 201



# ---------------- Pedidos del cliente conectado ----------------
@pedidos_bp.get("/mios")
@requiere_sesion
def mios():
    actual = usuario_actual()
    datos = _servicio.historial(actual["id_usuario"])
    return jsonify({"total": len(datos), "pedidos": datos})



# ---------------- Todos los pedidos (solo admin) ----------------
@pedidos_bp.get("/todos")
@requiere_admin()
def todos():
    limite = request.args.get("limite", 100, type=int)
    datos = _servicio.listar_todos(limite)
    return jsonify({"total": len(datos), "pedidos": datos})



# ---------------- Estado del correo (solo admin) ----------------
@pedidos_bp.get("/correos/estado")
@requiere_admin()
def correos_estado():
    return jsonify(_correo.probar_conexion())



# ---------------- Procesar la cola de correos ----------------
@pedidos_bp.post("/correos/procesar")
@requiere_admin()
def correos_procesar():
    limite = request.args.get("limite", 20, type=int)
    return jsonify(_correo.enviar_pendientes(limite))



# ---------------- Detalle de un pedido ----------------
# Un cliente solo puede ver los suyos: si no, responde 403
@pedidos_bp.get("/<codigo>")
@requiere_sesion
def detalle(codigo):
    pedido = _servicio.obtener(codigo)
    if pedido is None:
        return jsonify({"error": "NO_ENCONTRADO",
                        "mensaje": "No existe el pedido"}), 404
    actual = usuario_actual()
    if actual["rol"] != "administrador" and pedido["email"] != actual["email"]:
        return jsonify({"error": "PERMISO_DENEGADO",
                        "mensaje": "Este pedido no le pertenece"}), 403
    return jsonify(pedido)



# ---------------- Cambiar el estado (admin nivel 2) ----------------
@pedidos_bp.patch("/<codigo>/estado")
@requiere_admin(nivel_minimo=2)
def cambiar_estado(codigo):
    actual = usuario_actual()
    datos = request.get_json(silent=True) or {}
    _servicio.cambiar_estado(codigo, datos.get("estado"), actual["id_usuario"])
    return jsonify({"mensaje": "Estado actualizado", "pedido": _servicio.obtener(codigo)})