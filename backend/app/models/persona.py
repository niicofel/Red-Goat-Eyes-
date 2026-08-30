from abc import ABC, abstractmethod
from datetime import date
import re

from app.utils.excepciones import ErrorValidacion


class Persona(ABC):

    REGEX_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")

    def __init__(self, id_usuario, nombres, apellidos, email, activo=True):
        self._id_usuario = id_usuario
        self.nombres = nombres
        self.apellidos = apellidos
        self.email = email
        self._activo = activo

    @property
    def id_usuario(self):
        return self._id_usuario

    @property
    def nombres(self):
        return self._nombres

    @nombres.setter
    def nombres(self, valor):
        texto = str(valor).strip()
        if len(texto) < 3:
            raise ErrorValidacion("nombres", "Los nombres deben tener al menos 3 caracteres")
        self._nombres = texto

    @property
    def apellidos(self):
        return self._apellidos

    @apellidos.setter
    def apellidos(self, valor):
        texto = str(valor).strip()
        if len(texto) < 3:
            raise ErrorValidacion("apellidos", "Los apellidos deben tener al menos 3 caracteres")
        self._apellidos = texto

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
    def activo(self):
        return self._activo

    @property
    def nombre_completo(self):
        return f"{self._nombres} {self._apellidos}"

    @property
    def iniciales(self):
        return f"{self._nombres[0]}{self._apellidos[0]}".upper()

    def desactivar(self):
        self._activo = False

    def reactivar(self):
        self._activo = True

    @abstractmethod
    def obtener_rol(self):
        pass

    @abstractmethod
    def permisos(self):
        pass

    def a_diccionario(self):
        return {
            "id_usuario": self._id_usuario,
            "nombres": self._nombres,
            "apellidos": self._apellidos,
            "nombre_completo": self.nombre_completo,
            "email": self._email,
            "rol": self.obtener_rol(),
            "activo": self._activo,
        }

    def __str__(self):
        return f"{self.nombre_completo} <{self._email}> ({self.obtener_rol()})"

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self._id_usuario}, email='{self._email}')"

    def __eq__(self, otro):
        if not isinstance(otro, Persona):
            return NotImplemented
        return self._id_usuario == otro._id_usuario

    def __hash__(self):
        return hash(self._id_usuario)