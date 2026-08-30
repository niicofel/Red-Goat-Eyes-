from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP

from app.utils.excepciones import ErrorValidacion


class Producto(ABC):

    IVA = Decimal("0.15")

    def __init__(self, id_producto, codigo, nombre, descripcion, precio,
                 imagen_principal, categoria, material=None, genero="Unisex",
                 precio_oferta=None, activo=True, destacado=False):
        self._id_producto = id_producto
        self._codigo = codigo
        self.nombre = nombre
        self.descripcion = descripcion
        self.__precio = None
        self.__precio_oferta = None
        self.precio = precio
        self.precio_oferta = precio_oferta
        self._imagen_principal = imagen_principal
        self._categoria = categoria
        self._material = material
        self.genero = genero
        self._activo = activo
        self._destacado = destacado

    @property
    def id_producto(self):
        return self._id_producto

    @property
    def codigo(self):
        return self._codigo

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
    def descripcion(self):
        return self._descripcion

    @descripcion.setter
    def descripcion(self, valor):
        texto = str(valor).strip()
        if len(texto) < 10:
            raise ErrorValidacion("descripcion", "La descripción debe tener al menos 10 caracteres")
        self._descripcion = texto

    @property
    def precio(self):
        return self.__precio

    @precio.setter
    def precio(self, valor):
        monto = Decimal(str(valor))
        if monto <= 0:
            raise ErrorValidacion("precio", "El precio debe ser mayor que cero")
        self.__precio = monto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def precio_oferta(self):
        return self.__precio_oferta

    @precio_oferta.setter
    def precio_oferta(self, valor):
        if valor is None:
            self.__precio_oferta = None
            return
        monto = Decimal(str(valor))
        if monto <= 0:
            raise ErrorValidacion("precio_oferta", "El precio de oferta debe ser mayor que cero")
        if monto >= self.__precio:
            raise ErrorValidacion("precio_oferta",
                                  "El precio de oferta debe ser menor que el precio de lista")
        self.__precio_oferta = monto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def genero(self):
        return self._genero

    @genero.setter
    def genero(self, valor):
        permitidos = ("Hombre", "Mujer", "Unisex")
        if valor not in permitidos:
            raise ErrorValidacion("genero", f"El género debe ser uno de {permitidos}")
        self._genero = valor

    @property
    def categoria(self):
        return self._categoria

    @property
    def material(self):
        return self._material

    @property
    def imagen_principal(self):
        return self._imagen_principal

    @property
    def activo(self):
        return self._activo

    @property
    def destacado(self):
        return self._destacado

    @property
    def en_oferta(self):
        return self.__precio_oferta is not None

    @property
    def precio_venta(self):
        return self.__precio_oferta if self.en_oferta else self.__precio

    @property
    def descuento_porcentaje(self):
        if not self.en_oferta:
            return 0
        diferencia = (self.__precio - self.__precio_oferta) / self.__precio * 100
        return int(diferencia.quantize(Decimal("1"), rounding=ROUND_HALF_UP))

    def calcular_iva(self):
        return (self.precio_venta * self.IVA).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def aplicar_oferta(self, porcentaje):
        if not 0 < porcentaje < 100:
            raise ErrorValidacion("porcentaje", "El descuento debe estar entre 1 y 99")
        nuevo = self.__precio * (Decimal("100") - Decimal(str(porcentaje))) / Decimal("100")
        self.precio_oferta = nuevo

    def quitar_oferta(self):
        self.__precio_oferta = None

    def desactivar(self):
        self._activo = False

    @abstractmethod
    def calcular_precio_final(self):
        pass

    @abstractmethod
    def descripcion_corta(self):
        pass

    @abstractmethod
    def tipo(self):
        pass

    def a_diccionario(self):
        return {
            "id_producto": self._id_producto,
            "codigo": self._codigo,
            "nombre": self._nombre,
            "descripcion": self._descripcion,
            "tipo": self.tipo(),
            "categoria": self._categoria,
            "precio": float(self.__precio),
            "precio_oferta": float(self.__precio_oferta) if self.en_oferta else None,
            "precio_final": float(self.calcular_precio_final()),
            "descuento_porcentaje": self.descuento_porcentaje,
            "material": self._material,
            "genero": self._genero,
            "imagen_principal": self._imagen_principal,
            "activo": self._activo,
            "destacado": self._destacado,
        }

    def __str__(self):
        return f"{self._codigo} - {self._nombre} (${self.calcular_precio_final()})"

    def __repr__(self):
        return f"{self.__class__.__name__}(codigo='{self._codigo}', precio={self.__precio})"

    def __eq__(self, otro):
        if not isinstance(otro, Producto):
            return NotImplemented
        return self._codigo == otro._codigo

    def __hash__(self):
        return hash(self._codigo)

    def __lt__(self, otro):
        return self.calcular_precio_final() < otro.calcular_precio_final()