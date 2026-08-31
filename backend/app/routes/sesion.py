from functools import wraps

from flask import jsonify, session


def usuario_actual():
    if "id_usuario" not in session:
        return None
    return {
        "id_usuario": session["id_usuario"],
        "email": session.get("email"),
        "rol": session.get("rol"),
        "nombre": session.get("nombre"),
        "nivel_acceso": session.get("nivel_acceso", 0),
    }


def abrir_sesion(usuario):
    session.clear()
    session["id_usuario"] = usuario.id_usuario
    session["email"] = usuario.email
    session["rol"] = usuario.obtener_rol()
    session["nombre"] = usuario.nombre_completo
    session["nivel_acceso"] = getattr(usuario, "nivel_acceso", 0)
    session.permanent = True


def cerrar_sesion():
    session.clear()


def requiere_sesion(funcion):
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if usuario_actual() is None:
            return jsonify({"error": "SIN_SESION",
                            "mensaje": "Debe iniciar sesion"}), 401
        return funcion(*args, **kwargs)
    return envoltura


def requiere_admin(nivel_minimo=1):
    def decorador(funcion):
        @wraps(funcion)
        def envoltura(*args, **kwargs):
            actual = usuario_actual()
            if actual is None:
                return jsonify({"error": "SIN_SESION",
                                "mensaje": "Debe iniciar sesion"}), 401
            if actual["rol"] != "administrador" or actual["nivel_acceso"] < nivel_minimo:
                return jsonify({"error": "PERMISO_DENEGADO",
                                "mensaje": "No tiene permisos para esta operacion"}), 403
            return funcion(*args, **kwargs)
        return envoltura
    return decorador