from decimal import Decimal, ROUND_HALF_UP

from app.models.producto import Producto


class Hoodie(Producto):

    GRAMAJE_PREMIUM = 400
    RECARGO_PREMIUM = Decimal("0.10")

    def __init__(self, id_producto, codigo, nombre, descripcion, precio,
                 imagen_principal, material=None, gramaje=380,
                 tipo_capucha="Forrada", genero="Unisex",
                 precio_oferta=None, activo=True, destacado=False):
        super().__init__(id_producto, codigo, nombre, descripcion, precio,
                         imagen_principal, "Hoodies", material, genero,
                         precio_oferta, activo, destacado)
        self._gramaje = int(gramaje)
        self._tipo_capucha = tipo_capucha

    @property
    def gramaje(self):
        return self._gramaje

    @property
    def tipo_capucha(self):
        return self._tipo_capucha

    @property
    def es_premium(self):
        return self._gramaje >= self.GRAMAJE_PREMIUM

    def calcular_precio_final(self):
        base = self.precio_venta
        if self.es_premium:
            base = base * (Decimal("1") + self.RECARGO_PREMIUM)
        return base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def descripcion_corta(self):
        etiqueta = "premium" if self.es_premium else "estándar"
        return f"Hoodie {self.nombre} · {self._gramaje} gsm ({etiqueta}) · capucha {self._tipo_capucha.lower()}"

    def tipo(self):
        return "Hoodie"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "gramaje": self._gramaje,
            "tipo_capucha": self._tipo_capucha,
            "es_premium": self.es_premium,
        })
        return datos