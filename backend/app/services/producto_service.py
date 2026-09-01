# ============================================================
# PRODUCTO SERVICE
# Reglas del catalogo, el detalle y la reposicion de stock.
# ============================================================
from app.repositories.producto_repository import ProductoRepository
from app.utils.excepciones import ErrorValidacion, ProductoNoEncontrado



# ---------------- La clase ----------------
class ProductoService:

    def __init__(self, repositorio=None):
        self._repo = repositorio or ProductoRepository()


# ---------------- Catalogo, busqueda y destacados ----------------
# Los tres devuelven la misma forma de datos para que el JavaScript no cambie
    def catalogo(self, slug=None):
        return [self._formatear(f) for f in self._repo.catalogo_publico(slug)]

    def buscar(self, texto):
        if not texto or len(texto.strip()) < 2:
            return []
        return [self._formatear(f) for f in self._repo.catalogo_buscar(texto.strip())]

    def destacados(self, limite=8):
        return [self._formatear(f) for f in self._repo.catalogo_destacados(limite)]


# ---------------- Preparar un producto para la API ----------------
# El precio sale del modelo, no de SQL, para que coincida con lo que se cobra
    def _formatear(self, fila):
        tallas = fila.get("tallas") or ""
        producto = self._repo.a_objeto(fila)
        return {
            "id_producto": fila["id_producto"],
            "id_producto_talla": fila["id_producto_talla"],
            "codigo": fila["codigo"],
            "nombre": fila["nombre"],
            "descripcion": fila["descripcion"],
            "categoria": fila["categoria"],
            "categoria_slug": fila["categoria_slug"],
            "precio": float(fila["precio"]),
            "precio_final": float(producto.calcular_precio_final()),
            "descuento": int(fila["descuento_porcentaje"] or 0),
            "en_oferta": fila["precio_oferta"] is not None,
            "imagen": fila["imagen_principal"],
            "alt": fila["alt_text"],
            "material": fila["material"],
            "genero": fila["genero"],
            "stock": int(fila["stock"] or 0),
            "disponible": bool(fila["disponible"]),
            "tallas": tallas.split(",") if tallas else [],
            "tallas_disponibles": int(fila["tallas_disponibles"] or 0),
            "destacado": fila["destacado"],
        }


# ---------------- Detalle de un producto con sus tallas ----------------
    def detalle(self, codigo):
        producto = self._repo.obtener_por_codigo(codigo)
        if producto is None:
            raise ProductoNoEncontrado(codigo)

        datos = producto.a_diccionario()
        datos["tallas"] = self._repo.obtener_tallas_por_producto(producto.id_producto)
        datos["stock"] = sum(t["stock"] for t in datos["tallas"])
        datos["disponible"] = datos["stock"] > 0
        datos["tallas_disponibles"] = sum(1 for t in datos["tallas"] if t["disponible"])
        return datos


# ---------------- Categorias con su rango de precios ----------------
    def categorias(self):
        salida = []
        for categoria in self._repo.obtener_categorias():
            datos = categoria.a_diccionario()
            datos["precio_minimo"] = float(categoria.precio_minimo() or 0)
            datos["precio_maximo"] = float(categoria.precio_maximo() or 0)
            salida.append(datos)
        return salida


# ---------------- Comprobar stock ----------------
    def verificar_disponibilidad(self, id_producto_talla, cantidad):
        return bool(self._repo.hay_stock(id_producto_talla, cantidad))

    def inventario(self, id_producto_talla):
        return self._repo.obtener_inventario(id_producto_talla).a_diccionario()


# ---------------- Inventario para el panel ----------------
    def inventario_completo(self):
        return self._repo.inventario_completo()


# ---------------- Reponer stock ----------------
# Valida la cantidad y despues llama al procedimiento de PostgreSQL
    def reponer_stock(self, codigo_producto, codigo_talla, cantidad, id_administrador):
        if not codigo_producto:
            raise ErrorValidacion("codigo_producto", "Indique el codigo del producto")
        if not codigo_talla:
            raise ErrorValidacion("codigo_talla", "Indique la talla a reponer")

        try:
            unidades = int(cantidad)
        except (TypeError, ValueError):
            raise ErrorValidacion("cantidad", "La cantidad debe ser un numero entero")

        if unidades <= 0:
            raise ErrorValidacion("cantidad", "La cantidad debe ser mayor que cero")
        if unidades > 1000:
            raise ErrorValidacion("cantidad", "No se pueden reponer mas de 1000 unidades a la vez")

        self._repo.reponer_stock(codigo_producto, codigo_talla, unidades, id_administrador)
        return self._repo.obtener_stock(codigo_producto, codigo_talla)