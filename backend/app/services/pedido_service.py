from decimal import Decimal, ROUND_HALF_UP

from app.config import Config
from app.repositories.pedido_repository import PedidoRepository
from app.repositories.producto_repository import ProductoRepository
from app.repositories.usuario_repository import UsuarioRepository
from app.utils.excepciones import (CarritoVacio, ErrorValidacion, PermisoDenegado, StockInsuficiente)
from app.utils.validadores import validar_cantidad, validar_email, validar_entero


class PedidoService:

    IVA = Decimal(str(Config.IVA_PORCENTAJE))

    def __init__(self, pedido_repo=None, producto_repo=None, usuario_repo=None):
        self._pedidos = pedido_repo or PedidoRepository()
        self._productos = producto_repo or ProductoRepository()
        self._usuarios = usuario_repo or UsuarioRepository()

    def calcular_totales(self, items):
        subtotal = Decimal("0")
        detalle = []

        for item in items:
            id_pt = validar_entero(item.get("id_producto_talla"), "id_producto_talla", minimo=1)
            cantidad = validar_cantidad(item.get("cantidad"))
            inventario = self._productos.obtener_inventario(id_pt)

            if not inventario.hay_stock(cantidad):
                raise StockInsuficiente(inventario.producto.nombre,
                                        cantidad, inventario.stock)

            precio = inventario.producto.calcular_precio_final()
            linea = (precio * cantidad).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            subtotal += linea

            detalle.append({
                "id_producto_talla": id_pt,
                "codigo": inventario.producto.codigo,
                "producto": inventario.producto.nombre,
                "talla": inventario.talla.codigo,
                "cantidad": cantidad,
                "precio_unitario": float(precio),
                "subtotal_linea": float(linea),
            })

        subtotal = subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        iva = (subtotal * self.IVA).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        return {
            "items": detalle,
            "subtotal": float(subtotal),
            "iva": float(iva),
            "costo_envio": 0.0,
            "total": float(subtotal + iva),
        }

    def registrar(self, id_cliente, datos):
        items = datos.get("items") or []
        if not items:
            raise CarritoVacio()

        comprador = self._usuarios.obtener_por_id(id_cliente)

        if comprador is None or comprador.obtener_rol() != "cliente":
            raise PermisoDenegado(
                "realizar compras con una cuenta administrativa. "
                "Inicie sesion con una cuenta de cliente")

        validar_email(datos.get("email"))

        id_direccion = datos.get("id_direccion")
        if not id_direccion:
            id_direccion = self._resolver_direccion(id_cliente, datos)

        id_metodo = validar_entero(datos.get("id_metodo_pago"), "id_metodo_pago", minimo=1)

        limpios = [{"id_producto_talla": validar_entero(i.get("id_producto_talla"),
                                                        "id_producto_talla", minimo=1),
                    "cantidad": validar_cantidad(i.get("cantidad"))}
                   for i in items]

        codigo = self._pedidos.registrar(id_cliente, id_direccion, id_metodo,
                                         limpios, datos.get("observaciones"))
        if codigo is None:
            raise ErrorValidacion("pedido", "No se pudo registrar el pedido")

        self._pedidos.cambiar_estado(codigo, "Pagado")
        return self._pedidos.obtener_por_codigo(codigo)

    def _resolver_direccion(self, id_cliente, datos):
        existentes = self._usuarios.obtener_direcciones(id_cliente)
        calle = (datos.get("direccion") or "").strip()

        if not calle and existentes:
            return existentes[0].id_direccion
        if not calle:
            raise ErrorValidacion("direccion", "Debe indicar una direccion de entrega")

        for direccion in existentes:
            if direccion.calle_principal.lower() == calle.lower():
                return direccion.id_direccion

        cliente = self._usuarios.obtener_por_id(id_cliente)
        id_ciudad = datos.get("id_ciudad") or self._id_ciudad_por_nombre(cliente.ciudad)
        return self._usuarios.crear_direccion(
            id_cliente, id_ciudad, calle,
            referencia=datos.get("referencia"),
            es_principal=not existentes)

    def _id_ciudad_por_nombre(self, nombre):
        for ciudad in self._usuarios.obtener_ciudades():
            if ciudad["nombre"] == nombre:
                return ciudad["id_ciudad"]
        raise ErrorValidacion("id_ciudad", "No se pudo determinar la ciudad de entrega")

    def obtener(self, codigo):
        return self._pedidos.obtener_por_codigo(codigo)

    def historial(self, id_cliente, limite=20):
        return self._pedidos.obtener_por_cliente(id_cliente, limite)

    def listar_todos(self, limite=100):
        return self._pedidos.obtener_todos(limite)

    def metodos_pago(self):
        return self._pedidos.obtener_metodos_pago()

    def cambiar_estado(self, codigo, nuevo_estado, id_administrador=None):
        return self._pedidos.cambiar_estado(codigo, nuevo_estado, id_administrador)