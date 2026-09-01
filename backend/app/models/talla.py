# ============================================================
# TALLA y PRODUCTO_TALLA
# Talla es el catalogo de tallas (XS a XXL y U de unica).
# ProductoTalla une un producto con una talla y guarda su stock.
# Es la pieza clave del inventario: el stock no vive en Producto.
# ============================================================
from app.utils.excepciones import ErrorValidacion



# ---------------- Catalogo de tallas ----------------
class Talla:

    CODIGOS_VALIDOS = ("XS", "S", "M", "L", "XL", "XXL", "U")

    def __init__(self, id_talla, codigo, descripcion, orden):
        self._id_talla = id_talla
        self.codigo = codigo
        self._descripcion = descripcion
        self.orden = orden

    @property
    def id_talla(self):
        return self._id_talla

    @property
    def codigo(self):
        return self._codigo

    @codigo.setter
    def codigo(self, valor):
        texto = str(valor).strip().upper()
        if texto not in self.CODIGOS_VALIDOS:
            raise ErrorValidacion("codigo", f"La talla debe ser una de {self.CODIGOS_VALIDOS}")
        self._codigo = texto

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def orden(self):
        return self._orden

    @orden.setter
    def orden(self, valor):
        numero = int(valor)
        if numero <= 0:
            raise ErrorValidacion("orden", "El orden debe ser mayor que cero")
        self._orden = numero

    @property
    def es_unica(self):
        return self._codigo == "U"

    def a_diccionario(self):
        return {
            "id_talla": self._id_talla,
            "codigo": self._codigo,
            "descripcion": self._descripcion,
            "orden": self._orden,
            "es_unica": self.es_unica,
        }

    def __str__(self):
        return self._codigo

    def __repr__(self):
        return f"Talla('{self._codigo}')"

    def __eq__(self, otra):
        if not isinstance(otra, Talla):
            return NotImplemented
        return self._codigo == otra._codigo

    def __hash__(self):
        return hash(self._codigo)

    def __lt__(self, otra):
        return self._orden < otra._orden



# ---------------- Inventario de una talla concreta ----------------
class ProductoTalla:

    def __init__(self, id_producto_talla, producto, talla, stock=0, stock_minimo=3):
        self._id_producto_talla = id_producto_talla
        self._producto = producto
        self._talla = talla
        self.stock = stock
        self.stock_minimo = stock_minimo

    @property
    def id_producto_talla(self):
        return self._id_producto_talla

    @property
    def producto(self):
        return self._producto

    @property
    def talla(self):
        return self._talla

    @property

# ---------------- Stock con validacion ----------------
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, valor):
        cantidad = int(valor)
        if cantidad < 0:
            raise ErrorValidacion("stock", "El stock no puede ser negativo")
        self._stock = cantidad

    @property
    def stock_minimo(self):
        return self._stock_minimo

    @stock_minimo.setter
    def stock_minimo(self, valor):
        cantidad = int(valor)
        if cantidad < 0:
            raise ErrorValidacion("stock_minimo", "El stock mínimo no puede ser negativo")
        self._stock_minimo = cantidad

    @property

# ---------------- Estado del inventario ----------------
# critico cuando el stock baja del minimo, agotado cuando llega a cero
    def disponible(self):
        return self._stock > 0

    @property
    def en_nivel_critico(self):
        return self._stock <= self._stock_minimo

    @property
    def agotado(self):
        return self._stock == 0


# ---------------- Comprobar, descontar y reponer unidades ----------------
    def hay_stock(self, cantidad):
        return self._stock >= cantidad

    def descontar(self, cantidad):
        if cantidad <= 0:
            raise ErrorValidacion("cantidad", "La cantidad debe ser mayor que cero")
        if not self.hay_stock(cantidad):
            from app.utils.excepciones import StockInsuficiente
            raise StockInsuficiente(self._producto.nombre, cantidad, self._stock)
        self._stock -= cantidad
        return self._stock

    def reponer(self, cantidad):
        if cantidad <= 0:
            raise ErrorValidacion("cantidad", "La cantidad a reponer debe ser mayor que cero")
        self._stock += cantidad
        return self._stock

    def a_diccionario(self):
        return {
            "id_producto_talla": self._id_producto_talla,
            "producto": self._producto.nombre,
            "codigo": self._producto.codigo,
            "talla": self._talla.codigo,
            "stock": self._stock,
            "stock_minimo": self._stock_minimo,
            "disponible": self.disponible,
            "nivel_critico": self.en_nivel_critico,
        }

    def __str__(self):
        return f"{self._producto.codigo} talla {self._talla.codigo}: {self._stock} unidades"