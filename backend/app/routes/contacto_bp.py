from flask import Blueprint, jsonify, request

from app.repositories.mensaje_repository import MensajeRepository
from app.services.correo_service import CorreoService
from app.routes.sesion import requiere_admin, usuario_actual
from app.utils.validadores import (validar_email, validar_entero,
                                   validar_longitud, validar_opcion)

contacto_bp = Blueprint("contacto", __name__, url_prefix="/api/contacto")
_repo = MensajeRepository()
_correo = CorreoService()


@contacto_bp.get("/asuntos")
def asuntos():
    return jsonify({"asuntos": _repo.obtener_asuntos()})


@contacto_bp.get("/mensajes")
@requiere_admin()
def mensajes():
    limite = request.args.get("limite", 100, type=int)
    datos = _repo.listar(limite)
    return jsonify({"total": len(datos), "mensajes": datos})


@contacto_bp.post("")
def enviar():
    datos = request.get_json(silent=True) or {}
    asuntos_validos = [a["nombre"] for a in _repo.obtener_asuntos()]

    asunto = validar_opcion(datos.get("asunto"), "asunto", asuntos_validos)
    nombre = validar_longitud("nombre", datos.get("nombre"), 3, 60)
    email = validar_email(datos.get("email"))
    descripcion = validar_longitud("descripcion", datos.get("descripcion"), 10, 2000)
    id_ciudad = validar_entero(datos.get("id_ciudad"), "id_ciudad", minimo=1)

    actual = usuario_actual()
    id_cliente = actual["id_usuario"] if actual and actual["rol"] == "cliente" else None

    _repo.registrar(asunto, id_ciudad, nombre, email, descripcion, id_cliente)

    _correo.notificar_contacto_en_segundo_plano({
        "nombre": nombre,
        "email": email,
        "asunto": asunto,
        "ciudad": _repo.nombre_ciudad(id_ciudad),
        "descripcion": descripcion,
    })

    return jsonify({"mensaje": "Mensaje enviado"}), 201