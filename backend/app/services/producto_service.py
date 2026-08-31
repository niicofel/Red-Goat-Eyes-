from app.repositories.producto_repository import ProductoRepository
from app.utils.excepciones import ProductoNoEncontrado


class ProductoService:

    def __init__(self, repositorio=None):
        self._repo = repositorio or ProductoRepository()

    def catalogo(self, slug=None):
        return [self._formatear(f) for f in self._repo.catalogo_publico(slug)]

    @staticmethod
    def _formatear(fila):
        return {
            "id_producto_talla": fila["id_producto_talla"],
            "codigo": fila["codigo"],
            "nombre": fila["nombre"],
            "descripcion": fila["descripcion"],
            "categoria": fila["categoria"],
            "categoria_slug": fila["categoria_slug"],
            "precio": float(fila["precio"]),
            "precio_final": float(fila["precio_final"]),
            "descuento": int(fila["descuento_porcentaje"] or 0),
            "en_oferta": fila["precio_oferta"] is not None,
            "imagen": fila["imagen_principal"],
            "alt": fila["alt_text"],
            "material": fila["material"],
            "genero": fila["genero"],
            "talla": fila["talla"],
            "stock": fila["stock"],
            "disponible": fila["disponible"],
            "destacado": fila["destacado"],
        }

    def detalle(self, codigo):
        producto = self._repo.obtener_por_codigo(codigo)
        if producto is None:
            raise ProductoNoEncontrado(codigo)
        return producto.a_diccionario()

    def destacados(self, limite=8):
        return [p.a_diccionario() for p in self._repo.obtener_destacados(limite)]

    def buscar(self, texto):
        if not texto or len(texto.strip()) < 2:
            return []
        return [p.a_diccionario() for p in self._repo.buscar(texto.strip())]

    def categorias(self):
        salida = []
        for categoria in self._repo.obtener_categorias():
            datos = categoria.a_diccionario()
            datos["precio_minimo"] = float(categoria.precio_minimo() or 0)
            datos["precio_maximo"] = float(categoria.precio_maximo() or 0)
            salida.append(datos)
        return salida

    def verificar_disponibilidad(self, id_producto_talla, cantidad):
        return bool(self._repo.hay_stock(id_producto_talla, cantidad))

    def inventario(self, id_producto_talla):
        return self._repo.obtener_inventario(id_producto_talla).a_diccionario()