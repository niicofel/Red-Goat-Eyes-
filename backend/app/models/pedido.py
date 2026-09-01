# ============================================================
# PEDIDO
# La compra completa. Contiene sus DetallePedido (composicion:
# una linea no existe sin su pedido).
# Tiene una maquina de estados que controla por donde puede pasar.
# ============================================================
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from app.utils.excepciones import ErrorValidacion, TransicionInvalida



# ---------------- La clase ----------------
class Pedido:

    IVA = Decimal("0.15")


# ---------------- Maquina de estados ----------------
# Este diccionario dice a que estado puede pasar cada estado
    TRANSICIONES = {
        "Pendiente":      ("Pagado", "Cancelado"),
        "Pagado":         ("En preparacion", "Cancelado"),
        "En preparacion": ("Enviado", "Cancelado"),
        "Enviado":        ("Entregado",),
        "Entregado":      (),
        "Cancelado":      (),
    }


# ---------------- Constructor ----------------
    def __init__(self, id_pedido, codigo_pedido, cliente, direccion,
                 estado="Pendiente", metodo_pago=None, fecha_pedido=None,
                 costo_envio=0, observaciones=None):
        self._id_pedido = id_pedido
        self._codigo_pedido = codigo_pedido
        self._cliente = cliente
        self._direccion = direccion
        self._estado = estado
        self._metodo_pago = metodo_pago
        self._fecha_pedido = fecha_pedido or datetime.now()
        self._costo_envio = Decimal(str(costo_envio)).quantize(Decimal("0.01"))
        self._observaciones = observaciones
        self._detalles = []
        self._historial = [(self._estado, self._fecha_pedido)]

    @property
    def id_pedido(self):
        return self._id_pedido

    @property
    def codigo_pedido(self):
        return self._codigo_pedido

    @property
    def cliente(self):
        return self._cliente

    @property
    def direccion(self):
        return self._direccion

    @property
    def estado(self):
        return self._estado

    @property
    def metodo_pago(self):
        return self._metodo_pago

    @property
    def fecha_pedido(self):
        return self._fecha_pedido

    @property
    def costo_envio(self):
        return self._costo_envio

    @property
    def observaciones(self):
        return self._observaciones

    @property
    def detalles(self):
        return tuple(self._detalles)

    @property
    def historial(self):
        return tuple(self._historial)

    @property
    def total_unidades(self):
        return sum(d.cantidad for d in self._detalles)

    @property
    def es_final(self):
        return len(self.TRANSICIONES.get(self._estado, ())) == 0

    @property
    def esta_pagado(self):
        return self._estado not in ("Pendiente", "Cancelado")


# ---------------- Agregar y quitar lineas ----------------
    def agregar_detalle(self, detalle):
        for existente in self._detalles:
            if existente.producto_talla.id_producto_talla == detalle.producto_talla.id_producto_talla:
                existente.aumentar(detalle.cantidad)
                return existente
        self._detalles.append(detalle)
        return detalle

    def quitar_detalle(self, id_producto_talla):
        antes = len(self._detalles)
        self._detalles = [
            d for d in self._detalles
            if d.producto_talla.id_producto_talla != id_producto_talla
        ]
        return len(self._detalles) < antes


# ---------------- Calculos del pedido ----------------
# Todo con Decimal para no perder centavos
    def calcular_subtotal(self):
        total = sum((d.subtotal_linea for d in self._detalles), Decimal("0"))
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calcular_iva(self):
        return (self.calcular_subtotal() * self.IVA).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)

    def calcular_total(self):
        return (self.calcular_subtotal() + self.calcular_iva() + self._costo_envio).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP)


# ---------------- Cambio de estado ----------------
# Rechaza cualquier transicion que no este en el diccionario
    def puede_pasar_a(self, nuevo_estado):
        return nuevo_estado in self.TRANSICIONES.get(self._estado, ())

    def cambiar_estado(self, nuevo_estado):
        if nuevo_estado == self._estado:
            return False
        if nuevo_estado not in self.TRANSICIONES:
            raise ErrorValidacion("estado", f"El estado '{nuevo_estado}' no existe")
        if not self.puede_pasar_a(nuevo_estado):
            raise TransicionInvalida(self._estado, nuevo_estado)
        self._estado = nuevo_estado
        self._historial.append((nuevo_estado, datetime.now()))
        return True

    def cancelar(self):
        return self.cambiar_estado("Cancelado")

    def marcar_pagado(self):
        return self.cambiar_estado("Pagado")


# ---------------- Datos para el correo del recibo ----------------
    def correo_destinatario(self):
        return self._cliente.email

    def asunto_recibo(self):
        return f"Recibo de tu pedido {self._codigo_pedido} | Red Goat Eyes"


# ---------------- Convertir a diccionario para la API ----------------
    def a_diccionario(self):
        return {
            "id_pedido": self._id_pedido,
            "codigo_pedido": self._codigo_pedido,
            "cliente": self._cliente.nombre_completo,
            "email": self._cliente.email,
            "direccion": self._direccion.formato_completo() if self._direccion else None,
            "estado": self._estado,
            "metodo_pago": self._metodo_pago,
            "fecha_pedido": self._fecha_pedido.isoformat(),
            "lineas": len(self._detalles),
            "unidades": self.total_unidades,
            "subtotal": float(self.calcular_subtotal()),
            "iva": float(self.calcular_iva()),
            "costo_envio": float(self._costo_envio),
            "total": float(self.calcular_total()),
            "observaciones": self._observaciones,
            "detalles": [d.a_diccionario() for d in self._detalles],
        }


# ---------------- Metodos especiales ----------------
# len(pedido) da el numero de lineas, y se puede recorrer con for
    def __len__(self):
        return len(self._detalles)

    def __iter__(self):
        return iter(self._detalles)

    def __str__(self):
        return f"{self._codigo_pedido} · {self._estado} · ${self.calcular_total()}"

    def __repr__(self):
        return f"Pedido(codigo='{self._codigo_pedido}', estado='{self._estado}')"

    def __eq__(self, otro):
        if not isinstance(otro, Pedido):
            return NotImplemented
        return self._codigo_pedido == otro._codigo_pedido

    def __hash__(self):
        return hash(self._codigo_pedido)