from decimal import Decimal, ROUND_HALF_UP

from app.models.producto import Producto


class Accesorio(Producto):

    TIPOS = ("Gorra", "Gorro", "Collar", "Cadena")
    UMBRAL_VOLUMEN = Decimal("70.00")
    DESCUENTO_VOLUMEN = Decimal("0.05")

    def __init__(self, id_producto, codigo, nombre, descripcion, precio,
                 imagen_principal, material=None, tipo_accesorio="Gorra",
                 ajustable=True, genero="Unisex",
                 precio_oferta=None, activo=True, destacado=False):
        super().__init__(id_producto, codigo, nombre, descripcion, precio,
                         imagen_principal, "Accesorios", material, genero,
                         precio_oferta, activo, destacado)
        self._tipo_accesorio = tipo_accesorio
        self._ajustable = bool(ajustable)

    @property
    def tipo_accesorio(self):
        return self._tipo_accesorio

    @property
    def ajustable(self):
        return self._ajustable

    @property
    def es_talla_unica(self):
        return True

    @property
    def aplica_descuento_gama_alta(self):
        return self.precio_venta >= self.UMBRAL_VOLUMEN

    def calcular_precio_final(self):
        base = self.precio_venta
        if self.aplica_descuento_gama_alta:
            base = base * (Decimal("1") - self.DESCUENTO_VOLUMEN)
        return base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def descripcion_corta(self):
        ajuste = "ajustable" if self._ajustable else "talla fija"
        return f"{self._tipo_accesorio} {self.nombre} · talla única · {ajuste}"

    def tipo(self):
        return "Accesorio"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "tipo_accesorio": self._tipo_accesorio,
            "ajustable": self._ajustable,
            "talla_unica": self.es_talla_unica,
        })
        return datos