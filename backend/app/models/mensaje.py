import re
from datetime import datetime

from app.utils.excepciones import ErrorValidacion


class Mensaje:

    REGEX_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
    ASUNTOS_VALIDOS = ("Consulta", "Reclamo", "Sugerencia")

    def __init__(self, id_mensaje, asunto, ciudad, nombre, email, descripcion,
                 id_cliente=None, url_foto=None, fecha_envio=None, leido=False):
        self._id_mensaje = id_mensaje
        self.asunto = asunto
        self._ciudad = ciudad
        self.nombre = nombre
        self.email = email
        self.descripcion = descripcion
        self._id_cliente = id_cliente
        self._url_foto = url_foto
        self._fecha_envio = fecha_envio or datetime.now()
        self._leido = bool(leido)
        self._respondido_por = None
        self._fecha_respuesta = None

    @property
    def id_mensaje(self):
        return self._id_mensaje

    @property
    def asunto(self):
        return self._asunto

    @asunto.setter
    def asunto(self, valor):
        texto = str(valor).strip().capitalize()
        if texto not in self.ASUNTOS_VALIDOS:
            raise ErrorValidacion("asunto", f"El asunto debe ser uno de {self.ASUNTOS_VALIDOS}")
        self._asunto = texto

    @property
    def ciudad(self):
        return self._ciudad

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        texto = str(valor).strip()
        if len(texto) < 3:
            raise ErrorValidacion("nombre", "El nombre debe tener al menos 3 caracteres")
        self._nombre = texto

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        texto = str(valor).strip().lower()
        if not self.REGEX_EMAIL.match(texto):
            raise ErrorValidacion("email", "El correo no tiene un formato válido")
        self._email = texto

    @property
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor):
        texto = str(valor).strip()
        if len(texto) < 10:
            raise ErrorValidacion("descripcion", "El mensaje debe tener al menos 10 caracteres")
        self._descripcion = texto

    @property
    def id_cliente(self):
        return self._id_cliente

    @property
    def url_foto(self):
        return self._url_foto

    @property
    def fecha_envio(self):
        return self._fecha_envio

    @property
    def leido(self):
        return self._leido

    @property
    def respondido_por(self):
        return self._respondido_por

    @property
    def fecha_respuesta(self):
        return self._fecha_respuesta

    @property
    def respondido(self):
        return self._fecha_respuesta is not None

    @property
    def es_de_visitante(self):
        return self._id_cliente is None

    @property
    def es_urgente(self):
        return self._asunto == "Reclamo" and not self.respondido

    @property
    def horas_sin_responder(self):
        if self.respondido:
            return 0
        delta = datetime.now() - self._fecha_envio
        return round(delta.total_seconds() / 3600, 1)

    @property
    def horas_de_respuesta(self):
        if not self.respondido:
            return None
        delta = self._fecha_respuesta - self._fecha_envio
        return round(delta.total_seconds() / 3600, 1)

    def marcar_leido(self):
        self._leido = True

    def responder(self, administrador):
        if not administrador.activo:
            raise ErrorValidacion("administrador", "El administrador no está activo")
        self._respondido_por = administrador.id_usuario
        self._fecha_respuesta = datetime.now()
        self._leido = True
        return True

    def resumen(self, longitud=60):
        texto = self._descripcion.replace("\n", " ")
        if len(texto) <= longitud:
            return texto
        return texto[:longitud].rsplit(" ", 1)[0] + "..."

    def a_diccionario(self):
        return {
            "id_mensaje": self._id_mensaje,
            "asunto": self._asunto,
            "ciudad": self._ciudad,
            "nombre": self._nombre,
            "email": self._email,
            "descripcion": self._descripcion,
            "resumen": self.resumen(),
            "url_foto": self._url_foto,
            "fecha_envio": self._fecha_envio.isoformat(),
            "leido": self._leido,
            "respondido": self.respondido,
            "es_de_visitante": self.es_de_visitante,
            "es_urgente": self.es_urgente,
            "horas_sin_responder": self.horas_sin_responder,
        }

    def __str__(self):
        estado = "respondido" if self.respondido else ("leído" if self._leido else "pendiente")
        return f"[{self._asunto}] {self._nombre}: {self.resumen(40)} ({estado})"

    def __repr__(self):
        return f"Mensaje(id={self._id_mensaje}, asunto='{self._asunto}')"