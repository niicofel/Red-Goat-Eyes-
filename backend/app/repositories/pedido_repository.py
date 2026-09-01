# ============================================================
# PEDIDO REPOSITORY
# Consultas de pedidos, sus detalles y la cola de correos.
# ============================================================
import json

from app.repositories.base_repository import BaseRepository
from app.utils.excepciones import CarritoVacio


# ---------------- Consulta base de pedidos ----------------
# Une pedido con estado, metodo de pago, cliente y direccion
SELECT_PEDIDO = """
    SELECT p.id_pedido, p.codigo_pedido, p.fecha_pedido, p.subtotal, p.iva,
           p.costo_envio, p.total, p.observaciones,
           e.nombre AS estado, m.nombre AS metodo_pago,
           c.nombres, c.apellidos, u.email,
           d.calle_principal, d.calle_secundaria, d.numeracion,
           d.referencia, ci.nombre AS ciudad
    FROM   pedido p
    JOIN   estado_pedido e ON e.id_estado = p.id_estado
    LEFT JOIN metodo_pago m ON m.id_metodo = p.id_metodo_pago
    JOIN   cliente c ON c.id_cliente = p.id_cliente
    JOIN   usuario u ON u.id_usuario = c.id_cliente
    JOIN   direccion_envio d ON d.id_direccion = p.id_direccion
    JOIN   ciudad ci ON ci.id_ciudad = d.id_ciudad
"""



# ---------------- La clase ----------------
class PedidoRepository(BaseRepository):

    @property
    def tabla(self):
        return "pedido"

    @property
    def clave_primaria(self):
        return "id_pedido"


# ---------------- Convertir la fila en diccionario ----------------
# Los montos pasan a float para que la API pueda mandarlos como JSON
    def a_objeto(self, fila):
        if fila is None:
            return None
        datos = dict(fila)
        datos["subtotal"] = float(fila["subtotal"])
        datos["iva"] = float(fila["iva"])
        datos["total"] = float(fila["total"])
        datos["costo_envio"] = float(fila["costo_envio"])
        datos["fecha_pedido"] = fila["fecha_pedido"].isoformat()
        datos["direccion"] = self._formato_direccion(fila)
        datos["cliente"] = f"{fila['nombres']} {fila['apellidos']}"
        return datos

    @staticmethod

# ---------------- Armar la direccion como texto ----------------
    def _formato_direccion(fila):
        partes = [fila["calle_principal"]]
        if fila.get("numeracion"):
            partes.append(fila["numeracion"])
        if fila.get("calle_secundaria"):
            partes.append("y " + fila["calle_secundaria"])
        texto = " ".join(partes)
        if fila.get("ciudad"):
            texto += ", " + fila["ciudad"]
        return texto


# ---------------- Registrar un pedido ----------------
# Llama a sp_registrar_pedido: crea el pedido y sus detalles de una sola vez
    def registrar(self, id_cliente, id_direccion, id_metodo_pago, items,
                  observaciones=None):
        if not items:
            raise CarritoVacio()

        from app.database import obtener_conexion

        with obtener_conexion() as con:
            with con.cursor() as cur:
                cur.execute(
                    "CALL sp_registrar_pedido(%s, %s, %s, %s::jsonb, %s, %s)",
                    (id_cliente, id_direccion, id_metodo_pago,
                     json.dumps(items), observaciones, None))
                salida = cur.fetchone()
                con.commit()

        return salida.get("p_codigo_pedido") if salida else None


# ---------------- Buscar un pedido con sus lineas ----------------
    def obtener_por_codigo(self, codigo):
        fila = self._consultar_uno(SELECT_PEDIDO + " WHERE p.codigo_pedido = %s",
                                   (codigo,))
        pedido = self.a_objeto(fila)
        if pedido:
            pedido["detalles"] = self.obtener_detalles(fila["id_pedido"])
        return pedido


# ---------------- Lineas de un pedido ----------------
    def obtener_detalles(self, id_pedido):
        filas = self._consultar_todos("""
            SELECT d.id_detalle, d.cantidad, d.precio_unitario, d.descuento,
                   d.subtotal_linea, pr.codigo, pr.nombre, t.codigo AS talla
            FROM   detalle_pedido d
            JOIN   producto_talla pt ON pt.id_producto_talla = d.id_producto_talla
            JOIN   producto pr ON pr.id_producto = pt.id_producto
            JOIN   talla t ON t.id_talla = pt.id_talla
            WHERE  d.id_pedido = %s
            ORDER  BY d.id_detalle
        """, (id_pedido,))
        return [{"codigo": f["codigo"], "producto": f["nombre"], "talla": f["talla"],
                 "cantidad": f["cantidad"],
                 "precio_unitario": float(f["precio_unitario"]),
                 "descuento": float(f["descuento"]),
                 "subtotal_linea": float(f["subtotal_linea"])} for f in filas]


# ---------------- Historial de un cliente ----------------
    def obtener_por_cliente(self, id_cliente, limite=20):
        filas = self._consultar_todos(
            SELECT_PEDIDO + " WHERE p.id_cliente = %s ORDER BY p.fecha_pedido DESC LIMIT %s",
            (id_cliente, limite))
        return [self.a_objeto(f) for f in filas]


# ---------------- Todos los pedidos (panel de administracion) ----------------
    def obtener_todos(self, limite=100):
        filas = self._consultar_todos(
            SELECT_PEDIDO + " ORDER BY p.fecha_pedido DESC LIMIT %s", (limite,))
        return [self.a_objeto(f) for f in filas]


# ---------------- Cambiar el estado de un pedido ----------------
# El procedimiento valida que la transicion sea permitida
    def cambiar_estado(self, codigo_pedido, nuevo_estado, id_administrador=None):
        from app.database import llamar_procedimiento
        llamar_procedimiento("sp_cambiar_estado_pedido",
                             (codigo_pedido, nuevo_estado, id_administrador))
        return True


# ---------------- Catalogos de apoyo ----------------
    def obtener_metodos_pago(self):
        return self._consultar_todos(
            "SELECT id_metodo, nombre FROM metodo_pago WHERE activo = TRUE ORDER BY id_metodo")

    def obtener_estados(self):
        return self._consultar_todos(
            "SELECT id_estado, nombre, descripcion FROM estado_pedido ORDER BY orden")


# ---------------- Cola de correos ----------------
# Los correos que el trigger dejo pendientes de enviar
    def correos_pendientes(self, limite=20):
        return self._consultar_todos("""
            SELECT e.id_envio, e.id_pedido, e.destinatario, e.asunto, e.intentos,
                   p.codigo_pedido
            FROM   envio_correo e
            JOIN   pedido p ON p.id_pedido = e.id_pedido
            WHERE  e.estado = 'pendiente' AND e.intentos < 5
            ORDER  BY e.fecha_creado
            LIMIT  %s
        """, (limite,))


# ---------------- Marcar el resultado del envio ----------------
    def marcar_correo_enviado(self, id_envio):
        return self._ejecutar("""
            UPDATE envio_correo
            SET    estado = 'enviado', fecha_enviado = CURRENT_TIMESTAMP,
                   intentos = intentos + 1
            WHERE  id_envio = %s
        """, (id_envio,)) > 0

    def marcar_correo_fallido(self, id_envio, detalle):
        return self._ejecutar("""
            UPDATE envio_correo
            SET    estado = CASE WHEN intentos + 1 >= 5 THEN 'fallido' ELSE 'pendiente' END,
                   intentos = intentos + 1,
                   error_detalle = %s
            WHERE  id_envio = %s
        """, (detalle[:500], id_envio)) > 0