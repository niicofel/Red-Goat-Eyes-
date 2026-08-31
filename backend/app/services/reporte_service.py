from app.repositories.reporte_repository import ReporteRepository


class ReporteService:

    def __init__(self, repositorio=None):
        self._repo = repositorio or ReporteRepository()

    def ventas_por_categoria(self, desde=None, hasta=None):
        return self._repo.ventas_por_categoria(desde or None, hasta or None)

    def top_clientes(self, limite=20):
        return self._repo.top_clientes(limite)

    def stock_critico(self):
        return self._repo.stock_critico()

    def mensajes(self, desde=None, hasta=None):
        return self._repo.mensajes_contacto(desde or None, hasta or None)

    def resumen(self):
        datos = self._repo.resumen_general()
        return dict(datos) if datos else {}

    def todos(self):
        return {
            "resumen": self.resumen(),
            "ventas_por_categoria": self.ventas_por_categoria(),
            "top_clientes": self.top_clientes(10),
            "stock_critico": self.stock_critico(),
            "mensajes": self.mensajes(),
        }