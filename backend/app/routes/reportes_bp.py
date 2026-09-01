# ============================================================
# RUTAS DE REPORTES
# Los 4 reportes del panel. Todas piden ser administrador.
# ============================================================
from flask import Blueprint, jsonify, request

from app.routes.sesion import requiere_admin
from app.services.reporte_service import ReporteService

reportes_bp = Blueprint("reportes", __name__, url_prefix="/api/reportes")
_servicio = ReporteService()



# ---------------- Numeros generales del panel ----------------
@reportes_bp.get("/resumen")
@requiere_admin()
def resumen():
    return jsonify(_servicio.resumen())



# ---------------- Reporte 1: ventas por categoria ----------------
@reportes_bp.get("/ventas")
@requiere_admin()
def ventas():
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    datos = _servicio.ventas_por_categoria(desde, hasta)
    return jsonify({"total": len(datos), "filas": datos})



# ---------------- Reporte 2: ranking de clientes ----------------
@reportes_bp.get("/clientes")
@requiere_admin()
def clientes():
    datos = _servicio.top_clientes(request.args.get("limite", 20, type=int))
    return jsonify({"total": len(datos), "filas": datos})



# ---------------- Reporte 3: stock critico ----------------
@reportes_bp.get("/stock")
@requiere_admin()
def stock():
    datos = _servicio.stock_critico()
    return jsonify({"total": len(datos), "filas": datos})



# ---------------- Reporte 4: mensajes de contacto ----------------
@reportes_bp.get("/mensajes")
@requiere_admin()
def mensajes():
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")
    datos = _servicio.mensajes(desde, hasta)
    return jsonify({"total": len(datos), "filas": datos})