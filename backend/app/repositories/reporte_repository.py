# ============================================================
# REPORTE REPOSITORY
# Los 4 reportes del panel.
# Todo pasa por la conexion administrativa (rge_panel), porque
# el rol normal de la aplicacion no tiene permiso sobre las vistas.
# ============================================================
from app.database import consultar_todos_admin, consultar_uno_admin
from app.repositories.base_repository import BaseRepository



# ---------------- La clase ----------------
class ReporteRepository(BaseRepository):

    @property
    def tabla(self):
        return "pedido"

    @property
    def clave_primaria(self):
        return "id_pedido"

    def a_objeto(self, fila):
        return dict(fila) if fila else None


# ---------------- Usar siempre la conexion administrativa ----------------
# Sobrescribe el metodo del padre para cambiar de rol
    def _consultar_todos(self, sql, parametros=None):
        return consultar_todos_admin(sql, parametros)

    def _consultar_uno(self, sql, parametros=None):
        return consultar_uno_admin(sql, parametros)

    @staticmethod

# ---------------- Convertir Decimal a float para el JSON ----------------
    def _numerico(filas, campos):
        salida = []
        for fila in filas:
            datos = dict(fila)
            for campo in campos:
                if datos.get(campo) is not None:
                    datos[campo] = float(datos[campo])
            salida.append(datos)
        return salida


# ---------------- Reporte 1: ventas por categoria ----------------
    def ventas_por_categoria(self, desde=None, hasta=None):
        filas = self._consultar_todos(
            "SELECT * FROM fn_rpt_ventas_por_categoria(%s, %s)", (desde, hasta))
        return self._numerico(filas, ("total_vendido", "ticket_promedio"))


# ---------------- Reporte 2: ranking de clientes ----------------
    def top_clientes(self, limite=20):
        filas = self._consultar_todos(
            "SELECT * FROM rpt_top_clientes LIMIT %s", (limite,))
        return self._numerico(filas, ("total_comprado", "ticket_promedio"))


# ---------------- Reporte 3: productos por agotarse ----------------
    def stock_critico(self):
        filas = self._consultar_todos("SELECT * FROM rpt_stock_critico")
        return self._numerico(filas, ("precio", "dias_de_cobertura"))


# ---------------- Reporte 4: mensajes de contacto ----------------
    def mensajes_contacto(self, desde=None, hasta=None):
        if desde or hasta:
            filas = self._consultar_todos(
                "SELECT * FROM fn_rpt_mensajes_periodo(%s, %s)", (desde, hasta))
        else:
            filas = self._consultar_todos("SELECT * FROM rpt_mensajes_contacto")
        return self._numerico(filas, ("porcentaje_respuesta", "horas_promedio_respuesta"))


# ---------------- Numeros para las tarjetas del panel ----------------
    def resumen_general(self):
        return self._consultar_uno("""
            SELECT (SELECT COUNT(*) FROM producto WHERE activo) AS productos,
                   (SELECT COUNT(*) FROM cliente) AS clientes,
                   (SELECT COUNT(*) FROM pedido) AS pedidos,
                   (SELECT COUNT(*) FROM mensaje_contacto WHERE NOT leido) AS mensajes_pendientes,
                   (SELECT COUNT(*) FROM rpt_stock_critico) AS alertas_stock
        """)