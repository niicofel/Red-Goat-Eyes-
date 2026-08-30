import re

from app.utils.excepciones import ErrorValidacion


class Categoria:

    REGEX_SLUG = re.compile(r"^[a-z0-9-]+$")

    def __init__(self, id_categoria, nombre, slug, descripcion=None,
                 imagen_portada=None, activa=True):
        self._id_categoria = id_categoria
        self.nombre = nombre
        self.slug = slug
        self._descripcion = descripcion
        self._imagen_portada = imagen_portada
        self._activa = bool(activa)
        self._productos = []

    @property
    def id_categoria(self):
        return self._id_categoria

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        texto = str(valor).strip()
        if len(texto) < 3:
            raise ErrorValidacion("nombre", "El nombre debe tener al menos 3 caracteres")
        self._nombre = texto

    @property
    def slug(self):
        return self._slug

    @slug.setter
    def slug(self, valor):
        texto = str(valor).strip().lower()
        if not self.REGEX_SLUG.match(texto):
            raise ErrorValidacion("slug", "El slug solo admite minúsculas, números y guiones")
        self._slug = texto

    @property
    def descripcion(self):
        return self._descripcion

    @property
    def imagen_portada(self):
        return self._imagen_portada

    @property
    def activa(self):
        return self._activa

    @property
    def productos(self):
        return tuple(self._productos)

    @property
    def total_productos(self):
        return len(self._productos)

    @property
    def total_activos(self):
        return len(self.listar_activos())

    def agregar_producto(self, producto):
        if producto in self._productos:
            return False
        self._productos.append(producto)
        return True

    def quitar_producto(self, codigo):
        antes = len(self._productos)
        self._productos = [p for p in self._productos if p.codigo != codigo]
        return len(self._productos) < antes

    def listar_activos(self):
        return [p for p in self._productos if p.activo]

    def listar_destacados(self):
        return [p for p in self._productos if p.activo and p.destacado]

    def listar_en_oferta(self):
        return [p for p in self._productos if p.activo and p.en_oferta]

    def ordenar_por_precio(self, descendente=False):
        return sorted(self.listar_activos(), reverse=descendente)

    def precio_minimo(self):
        activos = self.listar_activos()
        return min(p.calcular_precio_final() for p in activos) if activos else None

    def precio_maximo(self):
        activos = self.listar_activos()
        return max(p.calcular_precio_final() for p in activos) if activos else None

    def desactivar(self):
        self._activa = False

    def a_diccionario(self):
        return {
            "id_categoria": self._id_categoria,
            "nombre": self._nombre,
            "slug": self._slug,
            "descripcion": self._descripcion,
            "imagen_portada": self._imagen_portada,
            "activa": self._activa,
            "total_productos": self.total_productos,
            "total_activos": self.total_activos,
        }

    def __str__(self):
        return f"{self._nombre} ({self.total_activos} productos activos)"

    def __repr__(self):
        return f"Categoria(slug='{self._slug}', productos={self.total_productos})"

    def __len__(self):
        return len(self._productos)

    def __iter__(self):
        return iter(self._productos)

    def __contains__(self, producto):
        return producto in self._productos