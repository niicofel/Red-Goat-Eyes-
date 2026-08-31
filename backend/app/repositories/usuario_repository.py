from app.models.administrador import Administrador
from app.models.cliente import Cliente
from app.models.direccion import Direccion
from app.repositories.base_repository import BaseRepository
from app.utils.excepciones import UsuarioDuplicado

SELECT_USUARIO = """
    SELECT id_usuario, email, rol, activo, ultimo_acceso,
           nombres, apellidos, cedula, telefono, ciudad,
           cargo, nivel_acceso
    FROM   v_usuario_seguro
"""


class UsuarioRepository(BaseRepository):

    @property
    def tabla(self):
        return "usuario"

    @property
    def clave_primaria(self):
        return "id_usuario"

    def a_objeto(self, fila):
        if fila is None:
            return None
        if fila["rol"] == "administrador":
            return Administrador(
                fila["id_usuario"], fila["nombres"], fila["apellidos"],
                fila["email"], fila["cargo"] or "Operador",
                fila["nivel_acceso"] or 1, fila["activo"])
        return Cliente(
            fila["id_usuario"], fila["nombres"], fila["apellidos"],
            fila["email"], fila["cedula"], fila["telefono"],
            None, fila["ciudad"], None,
            fila["activo"])

    def obtener_por_id(self, id_usuario):
        fila = self._consultar_uno(SELECT_USUARIO + " WHERE id_usuario = %s",
                                   (id_usuario,))
        return self.a_objeto(fila)

    def obtener_por_email(self, email):
        fila = self._consultar_uno(SELECT_USUARIO + " WHERE LOWER(email) = LOWER(%s)",
                                   (email,))
        return self.a_objeto(fila)

    def obtener_credenciales(self, email):
        return self._consultar_uno(
            "SELECT id_usuario, email, password_hash, rol, activo "
            "FROM usuario WHERE LOWER(email) = LOWER(%s)", (email,))

    def email_existe(self, email):
        return self._consultar_uno(
            "SELECT 1 AS existe FROM usuario WHERE LOWER(email) = LOWER(%s)",
            (email,)) is not None

    def registrar_cliente(self, email, password_hash, nombres, apellidos,
                          cedula, telefono, id_ciudad, fecha_nacimiento=None):
        if self.email_existe(email):
            raise UsuarioDuplicado(email)

        from app.database import obtener_conexion

        with obtener_conexion() as con:
            with con.cursor() as cur:
                cur.execute(
                    "CALL sp_registrar_cliente(%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (email, password_hash, nombres, apellidos, cedula,
                     telefono, id_ciudad, fecha_nacimiento, None))
                salida = cur.fetchone()
                con.commit()

        id_cliente = salida.get("p_id_cliente") if salida else None
        return self.obtener_por_id(id_cliente) if id_cliente else self.obtener_por_email(email)

    def registrar_acceso(self, id_usuario):
        return self._ejecutar(
            "UPDATE usuario SET ultimo_acceso = CURRENT_TIMESTAMP WHERE id_usuario = %s",
            (id_usuario,)) > 0

    def obtener_direcciones(self, id_cliente):
        filas = self._consultar_todos("""
            SELECT d.id_direccion, d.id_cliente, d.calle_principal,
                   d.calle_secundaria, d.numeracion, d.referencia,
                   d.codigo_postal, d.es_principal, ci.nombre AS ciudad
            FROM   direccion_envio d
            JOIN   ciudad ci ON ci.id_ciudad = d.id_ciudad
            WHERE  d.id_cliente = %s
            ORDER  BY d.es_principal DESC, d.id_direccion
        """, (id_cliente,))
        return [Direccion(f["id_direccion"], f["id_cliente"], f["ciudad"],
                          f["calle_principal"], f["calle_secundaria"],
                          f["numeracion"], f["referencia"],
                          f["codigo_postal"], f["es_principal"]) for f in filas]

    def crear_direccion(self, id_cliente, id_ciudad, calle_principal,
                        calle_secundaria=None, numeracion=None,
                        referencia=None, codigo_postal=None, es_principal=False):
        fila = self._ejecutar("""
            INSERT INTO direccion_envio
                (id_cliente, id_ciudad, calle_principal, calle_secundaria,
                 numeracion, referencia, codigo_postal, es_principal)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id_direccion
        """, (id_cliente, id_ciudad, calle_principal, calle_secundaria,
              numeracion, referencia, codigo_postal, es_principal), devolver=True)
        return fila["id_direccion"] if fila else None

    def obtener_ciudades(self):
        return self._consultar_todos("""
            SELECT ci.id_ciudad, ci.nombre, p.nombre AS provincia
            FROM   ciudad ci
            JOIN   provincia p ON p.id_provincia = ci.id_provincia
            ORDER  BY ci.nombre
        """)