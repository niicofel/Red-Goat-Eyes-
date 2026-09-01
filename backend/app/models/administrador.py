# ============================================================
# ADMINISTRADOR
# Hereda de Persona. Anade cargo y nivel de acceso (1 a 3).
# El nivel decide que puede hacer.
# ============================================================
from app.models.persona import Persona
from app.utils.excepciones import ErrorValidacion, PermisoDenegado



# ---------------- La clase ----------------
class Administrador(Persona):


# ---------------- Los tres niveles ----------------
    NIVEL_CONSULTA = 1
    NIVEL_GESTION = 2
    NIVEL_TOTAL = 3

    NOMBRES_NIVEL = {
        NIVEL_CONSULTA: "Consulta",
        NIVEL_GESTION: "Gestión",
        NIVEL_TOTAL: "Total",
    }


# ---------------- Constructor ----------------
    def __init__(self, id_usuario, nombres, apellidos, email,
                 cargo="Operador", nivel_acceso=NIVEL_CONSULTA, activo=True):
        super().__init__(id_usuario, nombres, apellidos, email, activo)
        self.cargo = cargo
        self.nivel_acceso = nivel_acceso

    @property

# ---------------- Cargo y nivel con validacion ----------------
    def cargo(self):
        return self._cargo

    @cargo.setter
    def cargo(self, valor):
        texto = str(valor).strip()
        if len(texto) < 3:
            raise ErrorValidacion("cargo", "El cargo debe tener al menos 3 caracteres")
        self._cargo = texto

    @property
    def nivel_acceso(self):
        return self._nivel_acceso

    @nivel_acceso.setter
    def nivel_acceso(self, valor):
        nivel = int(valor)
        if nivel not in self.NOMBRES_NIVEL:
            raise ErrorValidacion("nivel_acceso", "El nivel de acceso debe estar entre 1 y 3")
        self._nivel_acceso = nivel

    @property
    def nombre_nivel(self):
        return self.NOMBRES_NIVEL[self._nivel_acceso]


# ---------------- Que puede hacer segun su nivel ----------------
    def puede_ver_reportes(self):
        return self.activo

    def puede_gestionar_productos(self):
        return self.activo and self._nivel_acceso >= self.NIVEL_GESTION

    def puede_reponer_stock(self):
        return self.activo and self._nivel_acceso >= self.NIVEL_GESTION

    def puede_cambiar_estado_pedido(self):
        return self.activo and self._nivel_acceso >= self.NIVEL_GESTION

    def puede_gestionar_usuarios(self):
        return self.activo and self._nivel_acceso >= self.NIVEL_TOTAL


# ---------------- Comprobar un permiso ----------------
# Si no tiene nivel suficiente lanza PermisoDenegado
    def exigir(self, accion):
        comprobaciones = {
            "ver_reportes": self.puede_ver_reportes,
            "gestionar_productos": self.puede_gestionar_productos,
            "reponer_stock": self.puede_reponer_stock,
            "cambiar_estado_pedido": self.puede_cambiar_estado_pedido,
            "gestionar_usuarios": self.puede_gestionar_usuarios,
        }
        comprobacion = comprobaciones.get(accion)
        if comprobacion is None:
            raise ErrorValidacion("accion", f"Acción desconocida: {accion}")
        if not comprobacion():
            raise PermisoDenegado(accion, self.NIVEL_GESTION)
        return True


# ---------------- Rol y permisos del administrador ----------------
    def obtener_rol(self):
        return "administrador"

    def permisos(self):
        base = ["ver_catalogo", "ver_reportes", "ver_mensajes"]
        if self._nivel_acceso >= self.NIVEL_GESTION:
            base += ["gestionar_productos", "reponer_stock",
                     "cambiar_estado_pedido", "responder_mensajes"]
        if self._nivel_acceso >= self.NIVEL_TOTAL:
            base += ["gestionar_usuarios", "ver_auditoria"]
        return tuple(base)

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos.update({
            "cargo": self._cargo,
            "nivel_acceso": self._nivel_acceso,
            "nombre_nivel": self.nombre_nivel,
            "permisos": list(self.permisos()),
        })
        return datos