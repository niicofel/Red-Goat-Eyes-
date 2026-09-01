# ============================================================
# AUTH SERVICE
# Iniciar sesion y registrar usuarios.
# Las contrasenas se guardan con bcrypt, que es de un solo
# sentido: se puede comprobar pero no se puede recuperar.
# ============================================================
import bcrypt

from app.config import Config
from app.repositories.usuario_repository import UsuarioRepository
from app.utils.excepciones import CredencialesInvalidas, UsuarioDuplicado
from app.utils.validadores import (validar_cedula, validar_email, validar_entero,
                                   validar_fecha_nacimiento, validar_longitud,
                                   validar_password, validar_telefono)



# ---------------- La clase ----------------
class AuthService:

    def __init__(self, repositorio=None):
        self._repo = repositorio or UsuarioRepository()


# ---------------- Convertir la contrasena en hash ----------------
# 12 rondas de bcrypt. Cada vez da un resultado distinto por la sal aleatoria
    def hashear(self, password):
        semilla = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
        return bcrypt.hashpw(password.encode("utf-8"), semilla).decode("utf-8")


# ---------------- Comprobar si la contrasena coincide ----------------
    def verificar(self, password, hash_guardado):
        try:
            return bcrypt.checkpw(password.encode("utf-8"),
                                  hash_guardado.encode("utf-8"))
        except (ValueError, TypeError):
            return False


# ---------------- Iniciar sesion ----------------
# Si el correo o la clave estan mal, el mensaje es el mismo para no dar pistas
    def iniciar_sesion(self, email, password):
        correo = validar_email(email)
        clave = validar_password(password, minimo=1)

        credenciales = self._repo.obtener_credenciales(correo)
        if credenciales is None:
            raise CredencialesInvalidas()
        if not credenciales["activo"]:
            raise CredencialesInvalidas()
        if not self.verificar(clave, credenciales["password_hash"]):
            raise CredencialesInvalidas()

        self._repo.registrar_acceso(credenciales["id_usuario"])
        return self._repo.obtener_por_id(credenciales["id_usuario"])


# ---------------- Registrar un cliente nuevo ----------------
# Valida todo antes de tocar la base de datos
    def registrar(self, datos):
        correo = validar_email(datos.get("email"))
        clave = validar_password(datos.get("password"))
        nombres = validar_longitud("nombres", datos.get("nombres"), 3, 60)
        apellidos = validar_longitud("apellidos", datos.get("apellidos"), 3, 60)
        cedula = validar_cedula(datos.get("cedula"))
        telefono = validar_telefono(datos.get("telefono"))
        id_ciudad = validar_entero(datos.get("id_ciudad"), "id_ciudad", minimo=1)
        nacimiento = validar_fecha_nacimiento(datos.get("fecha_nacimiento"))

        if self._repo.email_existe(correo):
            raise UsuarioDuplicado(correo)

        hash_clave = self.hashear(clave)
        return self._repo.registrar_cliente(correo, hash_clave, nombres, apellidos,
                                            cedula, telefono, id_ciudad, nacimiento)


# ---------------- Catalogos y direcciones ----------------
    def obtener_ciudades(self):
        return self._repo.obtener_ciudades()

    def obtener_direcciones(self, id_cliente):
        return [d.a_diccionario() for d in self._repo.obtener_direcciones(id_cliente)]

    def crear_direccion(self, id_cliente, datos):
        id_ciudad = validar_entero(datos.get("id_ciudad"), "id_ciudad", minimo=1)
        calle = validar_longitud("calle_principal", datos.get("calle_principal"), 5, 120)
        return self._repo.crear_direccion(
            id_cliente, id_ciudad, calle,
            datos.get("calle_secundaria"), datos.get("numeracion"),
            datos.get("referencia"), datos.get("codigo_postal") or None,
            bool(datos.get("es_principal")))