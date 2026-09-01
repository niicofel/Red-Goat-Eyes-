# ============================================================
# BASE REPOSITORY
# Clase abstracta de la que heredan todos los repositorios.
# Un repositorio es la capa que traduce entre objetos de Python
# y consultas SQL. Los servicios piden objetos, no escriben SQL.
# ============================================================
from abc import ABC, abstractmethod

from app.database import consultar_todos, consultar_uno, consultar_valor, ejecutar



# ---------------- La clase base ----------------
class BaseRepository(ABC):

    @property

# ---------------- Lo que cada repositorio debe definir ----------------
# El nombre de su tabla, su clave primaria y como armar el objeto
    @abstractmethod
    def tabla(self):
        pass

    @property
    @abstractmethod
    def clave_primaria(self):
        pass

    @abstractmethod
    def a_objeto(self, fila):
        pass


# ---------------- Atajos a las funciones de conexion ----------------
    def _consultar_todos(self, sql, parametros=None):
        return consultar_todos(sql, parametros)

    def _consultar_uno(self, sql, parametros=None):
        return consultar_uno(sql, parametros)

    def _consultar_valor(self, sql, parametros=None):
        return consultar_valor(sql, parametros)

    def _ejecutar(self, sql, parametros=None, devolver=False):
        return ejecutar(sql, parametros, devolver)


# ---------------- Operaciones comunes a todos ----------------
# Al estar aqui, los 5 repositorios las heredan sin repetir codigo
    def contar(self):
        return self._consultar_valor(f"SELECT COUNT(*) AS n FROM {self.tabla}")

    def existe(self, identificador):
        sql = (f"SELECT 1 AS existe FROM {self.tabla} "
               f"WHERE {self.clave_primaria} = %s LIMIT 1")
        return self._consultar_uno(sql, (identificador,)) is not None

    def obtener_por_id(self, identificador):
        sql = f"SELECT * FROM {self.tabla} WHERE {self.clave_primaria} = %s"
        fila = self._consultar_uno(sql, (identificador,))
        return self.a_objeto(fila) if fila else None

    def obtener_todos(self, limite=None, desplazamiento=0):
        sql = f"SELECT * FROM {self.tabla} ORDER BY {self.clave_primaria}"
        parametros = []
        if limite is not None:
            sql += " LIMIT %s OFFSET %s"
            parametros = [limite, desplazamiento]
        return [self.a_objeto(f) for f in self._consultar_todos(sql, tuple(parametros))]

    def eliminar(self, identificador):
        sql = f"DELETE FROM {self.tabla} WHERE {self.clave_primaria} = %s"
        return self._ejecutar(sql, (identificador,)) > 0

    def __repr__(self):
        return f"{self.__class__.__name__}(tabla='{self.tabla}')"