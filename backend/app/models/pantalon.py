# ============================================================
# PANTALON
# Los cortes Carpenter y Workwear llevan refuerzos y
# cuestan 5% mas.
# ============================================================
from decimal import Decimal, ROUND_HALF_UP

from app.models.producto import Producto



# ---------------- La clase ----------------
class Pantalon(Producto):

    CORTES_REFORZADOS = ("Carpenter", "Workwear")
    RECARGO_REFUERZO = Decimal("0.05")

    def __init__(self, id_producto, codigo, nombre, descripcion, precio,
                 imagen_principal, material=None, tipo_corte="Baggy",
                 tiro="Alto", genero="Unisex",
                 precio_oferta=None, activo=True, destacado=False):
        super().__init__(id_producto, codigo, nombre, descripcion, precio,
                         imagen_principal, "Pantalones", material, genero,
                         precio_oferta, activo, destacado)
        self._tipo_corte = tipo_corte
        self._tiro = tiro

    @property
    def tipo_corte(self):
        return self._tipo_corte

    @property
    def tiro(self):
        return self._tiro

    @property
    def lleva_refuerzos(self):
        return any(c.lower() in self._tipo_corte.lower() for c in self.CORTES_REFORZADOS)


# ---------------- Precio con recargo por refuerzos ----------------
    def calcular_precio_final(self):
        base = self.precio_venta
        if self.lleva_refuerzos:
            base = base * (Decimal("1") + self.RECARGO_REFUERZO)
        return base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def descripcion_corta(self):
        extra = " con refuerzos" if self.lleva_refuerzos else ""
        return f"Pantalón {self.nombre} · corte {self._tipo_corte} · tiro {self._tiro.lower()}{extra}"

    def tipo(self):
        return "Pantalón"

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "tipo_corte": self._tipo_corte,
            "tiro": self._tiro,
            "lleva_refuerzos": self.lleva_refuerzos,
        })
        return datos