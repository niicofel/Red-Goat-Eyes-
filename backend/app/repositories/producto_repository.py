from app.models.accesorio import Accesorio
from app.models.categoria import Categoria
from app.models.hoodie import Hoodie
from app.models.pantalon import Pantalon
from app.models.talla import ProductoTalla, Talla
from app.repositories.base_repository import BaseRepository
from app.utils.excepciones import ProductoNoEncontrado

SELECT_PRODUCTO = """
    SELECT p.id_producto, p.codigo, p.nombre, p.descripcion, p.precio,
           p.precio_oferta, p.imagen_principal, p.material, p.genero,
           p.activo, p.destacado, c.nombre AS categoria, c.slug AS categoria_slug
    FROM   producto p
    JOIN   categoria c ON c.id_categoria = p.id_categoria
"""


class ProductoRepository(BaseRepository):

    @property
    def tabla(self):
        return "producto"

    @property
    def clave_primaria(self):
        return "id_producto"

    def a_objeto(self, fila):
        if fila is None:
            return None

        comunes = {
            "id_producto": fila["id_producto"],
            "codigo": fila["codigo"],
            "nombre": fila["nombre"],
            "descripcion": fila["descripcion"],
            "precio": fila["precio"],
            "imagen_principal": fila["imagen_principal"],
            "material": fila.get("material"),
            "genero": fila.get("genero") or "Unisex",
            "precio_oferta": fila.get("precio_oferta"),
            "activo": fila.get("activo", True),
            "destacado": fila.get("destacado", False),
        }

        categoria = fila.get("categoria")

        if categoria == "Hoodies":
            return Hoodie(**comunes, gramaje=self._gramaje(fila.get("material")))
        if categoria == "Pantalones":
            return Pantalon(**comunes, tipo_corte=self._corte(fila["nombre"]))
        if categoria == "Accesorios":
            return Accesorio(**comunes, tipo_accesorio=self._tipo_accesorio(fila["nombre"]))

        raise ProductoNoEncontrado(f"categoria desconocida: {categoria}")

    @staticmethod
    def _gramaje(material):
        if not material:
            return 380
        for token in material.replace(",", " ").split():
            if token.isdigit() and 200 <= int(token) <= 900:
                return int(token)
        return 380

    @staticmethod
    def _corte(nombre):
        for corte in ("Carpenter", "Workwear", "Baggy", "Loose", "Straight"):
            if corte.lower() in nombre.lower():
                return corte
        return "Baggy"

    @staticmethod
    def _tipo_accesorio(nombre):
        for tipo in ("Gorra", "Gorro", "Collar", "Cadena"):
            if tipo.lower() in nombre.lower():
                return tipo
        return "Gorra"

    def obtener_por_id(self, id_producto):
        fila = self._consultar_uno(SELECT_PRODUCTO + " WHERE p.id_producto = %s",
                                   (id_producto,))
        return self.a_objeto(fila)

    def obtener_por_codigo(self, codigo):
        fila = self._consultar_uno(SELECT_PRODUCTO + " WHERE p.codigo = %s", (codigo,))
        return self.a_objeto(fila)

    def obtener_activos(self):
        filas = self._consultar_todos(
            SELECT_PRODUCTO + " WHERE p.activo = TRUE ORDER BY p.codigo")
        return [self.a_objeto(f) for f in filas]

    def obtener_por_categoria(self, slug):
        filas = self._consultar_todos(
            SELECT_PRODUCTO + " WHERE c.slug = %s AND p.activo = TRUE ORDER BY p.codigo",
            (slug,))
        return [self.a_objeto(f) for f in filas]

    def obtener_destacados(self, limite=8):
        filas = self._consultar_todos(
            SELECT_PRODUCTO + " WHERE p.destacado = TRUE AND p.activo = TRUE "
            "ORDER BY p.codigo LIMIT %s", (limite,))
        return [self.a_objeto(f) for f in filas]

    def buscar(self, texto):
        patron = f"%{texto}%"
        filas = self._consultar_todos(
            SELECT_PRODUCTO + " WHERE p.activo = TRUE AND "
            "(p.nombre ILIKE %s OR p.descripcion ILIKE %s OR p.codigo ILIKE %s) "
            "ORDER BY p.codigo", (patron, patron, patron))
        return [self.a_objeto(f) for f in filas]

    def catalogo_publico(self, slug=None):
        sql = "SELECT * FROM v_catalogo_publico WHERE disponible = TRUE"
        parametros = ()
        if slug:
            sql += " AND categoria_slug = %s"
            parametros = (slug,)
        sql += " ORDER BY categoria, codigo"
        return self._consultar_todos(sql, parametros)

    def obtener_inventario(self, id_producto_talla):
        fila = self._consultar_uno("""
            SELECT pt.id_producto_talla, pt.stock, pt.stock_minimo,
                   t.id_talla, t.codigo AS talla_codigo, t.descripcion AS talla_descripcion,
                   t.orden AS talla_orden,
                   p.id_producto, p.codigo, p.nombre, p.descripcion, p.precio,
                   p.precio_oferta, p.imagen_principal, p.material, p.genero,
                   p.activo, p.destacado, c.nombre AS categoria
            FROM   producto_talla pt
            JOIN   producto p ON p.id_producto = pt.id_producto
            JOIN   categoria c ON c.id_categoria = p.id_categoria
            JOIN   talla t ON t.id_talla = pt.id_talla
            WHERE  pt.id_producto_talla = %s
        """, (id_producto_talla,))

        if fila is None:
            raise ProductoNoEncontrado(id_producto_talla)

        producto = self.a_objeto(fila)
        talla = Talla(fila["id_talla"], fila["talla_codigo"],
                      fila["talla_descripcion"], fila["talla_orden"])
        return ProductoTalla(fila["id_producto_talla"], producto, talla,
                             fila["stock"], fila["stock_minimo"])

    def hay_stock(self, id_producto_talla, cantidad):
        return self._consultar_valor("SELECT fn_verificar_stock(%s, %s) AS hay",
                                     (id_producto_talla, cantidad))

    def obtener_categorias(self):
        filas = self._consultar_todos("""
            SELECT c.id_categoria, c.nombre, c.slug, c.descripcion,
                   c.imagen_portada, c.activa
            FROM   categoria c
            WHERE  c.activa = TRUE
            ORDER  BY c.id_categoria
        """)
        categorias = []
        for fila in filas:
            categoria = Categoria(fila["id_categoria"], fila["nombre"], fila["slug"],
                                  fila["descripcion"], fila["imagen_portada"],
                                  fila["activa"])
            for producto in self.obtener_por_categoria(fila["slug"]):
                categoria.agregar_producto(producto)
            categorias.append(categoria)
        return categorias

    def obtener_tallas_por_producto(self, id_producto):
        filas = self._consultar_todos("""
            SELECT pt.id_producto_talla, pt.stock, pt.stock_minimo,
                   t.codigo AS nombre_talla, t.descripcion AS talla_descripcion
            FROM   producto_talla pt
            JOIN   talla t ON t.id_talla = pt.id_talla
            WHERE  pt.id_producto = %s
            ORDER  BY t.orden
        """, (id_producto,))
        return [
            {
                "id_producto_talla": f["id_producto_talla"],
                "nombre_talla": f["nombre_talla"],
                "descripcion": f["talla_descripcion"],
                "stock": f["stock"],
                "disponible": f["stock"] > 0,
            }
            for f in filas
        ]

    def catalogo_buscar(self, texto):
        patron = f"%{texto}%"
        return self._consultar_todos("""
            SELECT * FROM v_catalogo_publico
            WHERE  nombre ILIKE %s OR descripcion ILIKE %s OR codigo ILIKE %s
            ORDER  BY categoria, codigo
        """, (patron, patron, patron))

    def catalogo_destacados(self, limite=8):
        return self._consultar_todos("""
            SELECT * FROM v_catalogo_publico
            WHERE  destacado = TRUE AND disponible = TRUE
            ORDER  BY codigo
            LIMIT  %s
        """, (limite,))

    def inventario_completo(self):
        filas = self._consultar_todos("""
            SELECT p.codigo, p.nombre, c.nombre AS categoria,
                   t.codigo AS talla, t.orden AS talla_orden,
                   pt.id_producto_talla, pt.stock, pt.stock_minimo
            FROM   producto_talla pt
            JOIN   producto  p ON p.id_producto  = pt.id_producto
            JOIN   categoria c ON c.id_categoria = p.id_categoria
            JOIN   talla     t ON t.id_talla     = pt.id_talla
            WHERE  p.activo = TRUE
            ORDER  BY p.codigo, t.orden
        """)
        return [
            {
                "codigo": f["codigo"],
                "nombre": f["nombre"],
                "categoria": f["categoria"],
                "talla": f["talla"],
                "id_producto_talla": f["id_producto_talla"],
                "stock": f["stock"],
                "stock_minimo": f["stock_minimo"],
                "critico": f["stock"] <= f["stock_minimo"],
                "agotado": f["stock"] == 0,
            }
            for f in filas
        ]

    def obtener_stock(self, codigo_producto, codigo_talla):
        fila = self._consultar_uno("""
            SELECT p.codigo, p.nombre, t.codigo AS talla,
                   pt.id_producto_talla, pt.stock, pt.stock_minimo
            FROM   producto_talla pt
            JOIN   producto p ON p.id_producto = pt.id_producto
            JOIN   talla    t ON t.id_talla    = pt.id_talla
            WHERE  p.codigo = %s AND t.codigo = %s
        """, (codigo_producto, codigo_talla))
        return dict(fila) if fila else None

    def reponer_stock(self, codigo_producto, codigo_talla, cantidad, id_administrador):
        from app.database import llamar_procedimiento
        llamar_procedimiento("sp_reponer_stock",
                             (codigo_producto, codigo_talla, cantidad, id_administrador))
        return True