# ============================================================
# MENSAJE REPOSITORY
# Mensajes del formulario de contacto.
# Detalle importante: la aplicacion puede ESCRIBIR mensajes pero
# no leerlos, por eso listar() usa la conexion administrativa.
# ============================================================
from app.database import consultar_todos_admin
from app.repositories.base_repository import BaseRepository



# ---------------- La clase ----------------
class MensajeRepository(BaseRepository):

    @property
    def tabla(self):
        return "mensaje_contacto"

    @property
    def clave_primaria(self):
        return "id_mensaje"

    def a_objeto(self, fila):
        if fila is None:
            return None
        datos = dict(fila)
        if fila.get("fecha_envio"):
            datos["fecha_envio"] = fila["fecha_envio"].isoformat()
        return datos


# ---------------- Guardar un mensaje nuevo ----------------
# Sin RETURNING, porque el rol de la app no tiene permiso de lectura aqui
    def registrar(self, asunto, id_ciudad, nombre, email, descripcion,
                  id_cliente=None, url_foto=None):
        return self._ejecutar("""
            INSERT INTO mensaje_contacto
                (id_asunto, id_ciudad, id_cliente, nombre, email, descripcion, url_foto)
            VALUES ((SELECT id_asunto FROM asunto_contacto WHERE nombre = %s),
                    %s, %s, %s, %s, %s, %s)
        """, (asunto, id_ciudad, id_cliente, nombre, email, descripcion, url_foto)) > 0


# ---------------- Listar mensajes para el panel ----------------
# Usa consultar_todos_admin porque hace falta el rol rge_panel
    def listar(self, limite=100):
        filas = consultar_todos_admin("""
            SELECT m.id_mensaje, m.fecha_envio, m.nombre, m.email, m.descripcion,
                   m.leido, m.fecha_respuesta, a.nombre AS asunto,
                   ci.nombre AS ciudad
            FROM   mensaje_contacto m
            JOIN   asunto_contacto a ON a.id_asunto = m.id_asunto
            JOIN   ciudad ci ON ci.id_ciudad = m.id_ciudad
            ORDER  BY m.fecha_envio DESC
            LIMIT  %s
        """, (limite,))
        salida = []
        for fila in filas:
            datos = dict(fila)
            datos["fecha_envio"] = fila["fecha_envio"].isoformat()
            datos["estado"] = "Respondido" if fila["fecha_respuesta"] else (
                "Leido" if fila["leido"] else "Pendiente")
            datos.pop("fecha_respuesta", None)
            salida.append(datos)
        return salida


# ---------------- Nombre de una ciudad por su id ----------------
    def nombre_ciudad(self, id_ciudad):
        fila = self._consultar_uno(
            "SELECT nombre FROM ciudad WHERE id_ciudad = %s", (id_ciudad,))
        return fila["nombre"] if fila else ""



# ---------------- Los asuntos disponibles ----------------
    def obtener_asuntos(self):
        return self._consultar_todos(
            "SELECT id_asunto, nombre FROM asunto_contacto WHERE activo = TRUE ORDER BY id_asunto")