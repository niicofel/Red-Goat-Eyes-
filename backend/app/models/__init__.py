from app.models.persona import Persona
from app.models.cliente import Cliente
from app.models.administrador import Administrador

from app.models.producto import Producto
from app.models.hoodie import Hoodie
from app.models.pantalon import Pantalon
from app.models.accesorio import Accesorio
from app.models.categoria import Categoria
from app.models.talla import Talla, ProductoTalla

from app.models.direccion import Direccion
from app.models.carrito import Carrito
from app.models.detalle_pedido import DetallePedido
from app.models.pedido import Pedido
from app.models.mensaje import Mensaje

__all__ = [
    "Persona", "Cliente", "Administrador",
    "Producto", "Hoodie", "Pantalon", "Accesorio",
    "Categoria", "Talla", "ProductoTalla",
    "Direccion", "Carrito", "DetallePedido", "Pedido", "Mensaje",
]

TIPOS_PRODUCTO = {
    "Hoodies": Hoodie,
    "Pantalones": Pantalon,
    "Accesorios": Accesorio,
}


def crear_producto(categoria, **datos):
    clase = TIPOS_PRODUCTO.get(categoria)
    if clase is None:
        raise ValueError(f"No existe una clase de producto para la categoria '{categoria}'")
    return clase(**datos)