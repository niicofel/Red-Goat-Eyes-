from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from app.utils.excepciones import ErrorValidacion, StockInsuficiente, CarritoVacio


class Carrito:

    IVA = Decimal("0.15")

    def __init__(self, id_carrito, id_cliente, fecha_creacion=None):
        self._id_carrito = id_carrito
        self._id_cliente = id_cliente
        self._fecha_creacion = fecha_creacion or datetime.now()
        self._fecha_actualizacion = self._fecha_creacion
        self._items = {}

    @property
    def id_carrito(self):
        return self._id_carrito

    @property
    def id_cliente(self):
        return self._id_cliente

    @property
    def fecha_creacion(self):
        return self._fecha_creacion

    @property
    def fecha_actualizacion(self):
        return self._fecha_actualizacion

    @property
    def items(self):
        return tuple(self._items.values())

    @property
    def vacio(self):
        return len(self._items) == 0

    @property
    def total_lineas(self):
        return len(self._items)

    @property
    def total_unidades(self):
        return sum(cantidad for _, cantidad in self._items.values())

    def _tocar(self):
        self._fecha_actualizacion = datetime.now()

    def agregar(self, producto_talla, cantidad=1):
        if cantidad <= 0:
            raise ErrorValidacion("cantidad", "La cantidad debe ser mayor que cero")

        clave = producto_talla.id_producto_talla
        actual = self._items[clave][1] if clave in self._items else 0
        solicitada = actual + cantidad

        if not producto_talla.hay_stock(solicitada):
            raise StockInsuficiente(producto_talla.producto.nombre,
                                    solicitada, producto_talla.stock)

        self._items[clave] = (producto_talla, solicitada)
        self._tocar()
        return solicitada

    def actualizar_cantidad(self, id_producto_talla, cantidad):
        if id_producto_talla not in self._items:
            return False
        if cantidad <= 0:
            return self.eliminar(id_producto_talla)

        producto_talla = self._items[id_producto_talla][0]
        if not producto_talla.hay_stock(cantidad):
            raise StockInsuficiente(producto_talla.producto.nombre,
                                    cantidad, producto_talla.stock)

        self._items[id_producto_talla] = (producto_talla, cantidad)
        self._tocar()
        return True

    def eliminar(self, id_producto_talla):
        if id_producto_talla not in self._items:
            return False
        del self._items[id_producto_talla]
        self._tocar()
        return True

    def vaciar(self):
        self._items.clear()
        self._tocar()

    def contiene(self, id_producto_talla):
        return id_producto_talla in self._items

    def calcular_subtotal(self):
        total = sum(
            (pt.producto.calcular_precio_final() * cantidad
             for pt, cantidad in self._items.values()),
            Decimal("0")
        )
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calcular_iva(self):
        return (self.calcular_subtotal() * self.IVA).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calcular_total(self):
        return (self.calcular_subtotal() + self.calcular_iva()).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)

    def validar_para_pago(self):
        if self.vacio:
            raise CarritoVacio()
        for producto_talla, cantidad in self._items.values():
            if not producto_talla.hay_stock(cantidad):
                raise StockInsuficiente(producto_talla.producto.nombre,
                                        cantidad, producto_talla.stock)
        return True

    def a_lista_items(self):
        return [
            {"id_producto_talla": pt.id_producto_talla, "cantidad": cantidad}
            for pt, cantidad in self._items.values()
        ]

    def a_diccionario(self):
        return {
            "id_carrito": self._id_carrito,
            "id_cliente": self._id_cliente,
            "lineas": self.total_lineas,
            "unidades": self.total_unidades,
            "subtotal": float(self.calcular_subtotal()),
            "iva": float(self.calcular_iva()),
            "total": float(self.calcular_total()),
            "items": [
                {
                    "id_producto_talla": pt.id_producto_talla,
                    "codigo": pt.producto.codigo,
                    "producto": pt.producto.nombre,
                    "talla": pt.talla.codigo,
                    "precio": float(pt.producto.calcular_precio_final()),
                    "cantidad": cantidad,
                    "subtotal": float(pt.producto.calcular_precio_final() * cantidad),
                }
                for pt, cantidad in self._items.values()
            ],
        }

    def __len__(self):
        return len(self._items)

    def __bool__(self):
        return not self.vacio

    def __iter__(self):
        return iter(self._items.values())

    def __str__(self):
        return f"Carrito de {self._id_cliente}: {self.total_unidades} unidades, ${self.calcular_total()}"