from app.routes.auth_bp import auth_bp
from app.routes.categorias_bp import categorias_bp
from app.routes.contacto_bp import contacto_bp
from app.routes.pedidos_bp import pedidos_bp
from app.routes.productos_bp import productos_bp
from app.routes.reportes_bp import reportes_bp

TODOS = (productos_bp, categorias_bp, auth_bp, pedidos_bp, contacto_bp, reportes_bp)


def registrar_blueprints(app):
    for blueprint in TODOS:
        app.register_blueprint(blueprint)
    return app


__all__ = ["registrar_blueprints", "TODOS"]