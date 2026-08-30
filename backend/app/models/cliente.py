from datetime import date

from app.models.persona import Persona
from app.utils.excepciones import ErrorValidacion


class Cliente(Persona):

    PROVINCIAS_VALIDAS = tuple(range(1, 25)) + (30,)
    COEFICIENTES = (2, 1, 2, 1, 2, 1, 2, 1, 2)

    def __init__(self, id_usuario, nombres, apellidos, email, cedula=None,
                 telefono=None, fecha_nacimiento=None, ciudad=None,
                 id_ciudad=None, activo=True):
        super().__init__(id_usuario, nombres, apellidos, email, activo)
        self.cedula = cedula
        self.telefono = telefono
        self.fecha_nacimiento = fecha_nacimiento
        self._ciudad = ciudad
        self._id_ciudad = id_ciudad
        self._direcciones = []

    @property
    def cedula(self):
        return self._cedula

    @cedula.setter
    def cedula(self, valor):
        if valor is None:
            self._cedula = None
            return
        texto = str(valor).strip()
        if not texto.isdigit() or len(texto) != 10:
            raise ErrorValidacion("cedula", "La cédula debe tener exactamente 10 dígitos")
        if not self._cedula_valida(texto):
            raise ErrorValidacion("cedula", "La cédula no es válida según el dígito verificador")
        self._cedula = texto

    @classmethod
    def _cedula_valida(cls, cedula):
        provincia = int(cedula[:2])
        if provincia not in cls.PROVINCIAS_VALIDAS:
            return False
        if int(cedula[2]) >= 6:
            return False
        suma = 0
        for digito, coeficiente in zip(cedula[:9], cls.COEFICIENTES):
            producto = int(digito) * coeficiente
            suma += producto - 9 if producto > 9 else producto
        verificador = (10 - suma % 10) % 10
        return verificador == int(cedula[9])

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        if valor is None or str(valor).strip() == "":
            self._telefono = None
            return
        texto = str(valor).strip()
        limpio = texto.replace("+", "").replace("-", "").replace(" ", "")
        if not limpio.isdigit() or not 7 <= len(limpio) <= 15:
            raise ErrorValidacion("telefono", "El teléfono debe tener entre 7 y 15 dígitos")
        self._telefono = texto

    @property
    def fecha_nacimiento(self):
        return self._fecha_nacimiento

    @fecha_nacimiento.setter
    def fecha_nacimiento(self, valor):
        if valor is None:
            self._fecha_nacimiento = None
            return
        if isinstance(valor, str):
            valor = date.fromisoformat(valor)
        if valor >= date.today():
            raise ErrorValidacion("fecha_nacimiento", "La fecha de nacimiento no puede ser futura")
        self._fecha_nacimiento = valor

    @property
    def edad(self):
        if self._fecha_nacimiento is None:
            return None
        hoy = date.today()
        años = hoy.year - self._fecha_nacimiento.year
        if (hoy.month, hoy.day) < (self._fecha_nacimiento.month, self._fecha_nacimiento.day):
            años -= 1
        return años

    @property
    def es_mayor_de_edad(self):
        edad = self.edad
        return edad is not None and edad >= 18

    @property
    def ciudad(self):
        return self._ciudad

    @property
    def id_ciudad(self):
        return self._id_ciudad

    @property
    def direcciones(self):
        return tuple(self._direcciones)

    @property
    def direccion_principal(self):
        for direccion in self._direcciones:
            if direccion.es_principal:
                return direccion
        return self._direcciones[0] if self._direcciones else None

    def agregar_direccion(self, direccion):
        if direccion in self._direcciones:
            return False
        if direccion.es_principal:
            for existente in self._direcciones:
                existente.quitar_principal()
        elif not self._direcciones:
            direccion.marcar_principal()
        self._direcciones.append(direccion)
        return True

    def eliminar_direccion(self, id_direccion):
        antes = len(self._direcciones)
        self._direcciones = [d for d in self._direcciones if d.id_direccion != id_direccion]
        return len(self._direcciones) < antes

    def puede_comprar(self):
        return self.activo and self._cedula is not None and len(self._direcciones) > 0

    def obtener_rol(self):
        return "cliente"

    def permisos(self):
        return ("ver_catalogo", "gestionar_carrito", "crear_pedido",
                "ver_pedidos_propios", "enviar_mensaje")

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "cedula": self._cedula,
            "telefono": self._telefono,
            "fecha_nacimiento": self._fecha_nacimiento.isoformat() if self._fecha_nacimiento else None,
            "edad": self.edad,
            "ciudad": self._ciudad,
            "id_ciudad": self._id_ciudad,
            "direcciones": len(self._direcciones),
        })
        return datos