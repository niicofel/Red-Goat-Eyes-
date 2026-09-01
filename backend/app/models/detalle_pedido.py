# ============================================================
# DETALLE PEDIDO
# Una linea del pedido. Lo importante: el precio se congela
# al comprar, asi el pedido no cambia si el producto sube manana.
# ============================================================
from decimal import Decimal, ROUND_HALF_UP

from app.utils.excepciones import ErrorValidacion



# ---------------- La clase ----------------
class DetallePedido:

    def __init__(self, id_detalle, producto_talla, cantidad,
                 precio_unitario=None, descuento=0):
        self._id_detalle = id_detalle
        self._producto_talla = producto_talla
        self.cantidad = cantidad
        self._precio_unitario = self._congelar_precio(precio_unitario)
        self.descuento = descuento


# ---------------- Congelar el precio de compra ----------------
    def _congelar_precio(self, precio_unitario):
        if precio_unitario is not None:
            monto = Decimal(str(precio_unitario))
        else:
            monto = self._producto_talla.producto.calcular_precio_final()
        if monto <= 0:
            raise ErrorValidacion("precio_unitario", "El precio unitario debe ser mayor que cero")
        return monto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def id_detalle(self):
        return self._id_detalle

    @property
    def producto_talla(self):
        return self._producto_talla

    @property
    def producto(self):
        return self._producto_talla.producto

    @property
    def talla(self):
        return self._producto_talla.talla

    @property

# ---------------- Cantidad y descuento con validacion ----------------
    def cantidad(self):
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor):
        numero = int(valor)
        if numero <= 0:
            raise ErrorValidacion("cantidad", "La cantidad debe ser mayor que cero")
        self._cantidad = numero

    @property
    def precio_unitario(self):
        return self._precio_unitario

    @property
    def descuento(self):
        return self._descuento

    @descuento.setter
    def descuento(self, valor):
        monto = Decimal(str(valor))
        if monto < 0:
            raise ErrorValidacion("descuento", "El descuento no puede ser negativo")
        bruto = self._precio_unitario * self._cantidad
        if monto >= bruto:
            raise ErrorValidacion("descuento", "El descuento no puede igualar ni superar el importe")
        self._descuento = monto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property

# ---------------- Calculo de la linea ----------------
    def importe_bruto(self):
        return (self._precio_unitario * self._cantidad).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)

    @property
    def subtotal_linea(self):
        return (self.importe_bruto - self._descuento).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------------- Subir y bajar la cantidad ----------------
    def aumentar(self, unidades=1):
        self.cantidad = self._cantidad + unidades
        return self._cantidad

    def disminuir(self, unidades=1):
        nueva = self._cantidad - unidades
        if nueva <= 0:
            return 0
        self.cantidad = nueva
        return self._cantidad

    def a_diccionario(self):
        return {
            "id_detalle": self._id_detalle,
            "codigo": self.producto.codigo,
            "producto": self.producto.nombre,
            "talla": self.talla.codigo,
            "cantidad": self._cantidad,
            "precio_unitario": float(self._precio_unitario),
            "descuento": float(self._descuento),
            "subtotal_linea": float(self.subtotal_linea),
        }

    def __str__(self):
        return f"{self.producto.nombre} x{self._cantidad} = ${self.subtotal_linea}"

    def __repr__(self):
        return f"DetallePedido(producto='{self.producto.codigo}', cantidad={self._cantidad})"