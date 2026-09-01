# ============================================================
# EXCEPCIONES
# Errores propios del sistema. Cada uno tiene un codigo que
# app/__init__.py traduce a un numero HTTP (400, 403, 409...).
# ============================================================
# ---------------- Error base del que heredan todos ----------------
class ErrorRedGoatEyes(Exception):

    def __init__(self, mensaje, codigo=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo or self.__class__.__name__

    def a_diccionario(self):
        return {"error": self.codigo, "mensaje": self.mensaje}

    def __str__(self):
        return f"[{self.codigo}] {self.mensaje}"



# ---------------- Dato invalido (400) ----------------
# Guarda el nombre del campo para que el JavaScript sepa donde poner el mensaje
class ErrorValidacion(ErrorRedGoatEyes):

    def __init__(self, campo, mensaje):
        super().__init__(mensaje, "VALIDACION")
        self.campo = campo

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["campo"] = self.campo
        return datos



# ---------------- No hay unidades suficientes (409) ----------------
class StockInsuficiente(ErrorRedGoatEyes):

    def __init__(self, producto, solicitado, disponible):
        mensaje = (f"Stock insuficiente para '{producto}': "
                   f"se solicitan {solicitado} unidades y solo hay {disponible}")
        super().__init__(mensaje, "STOCK_INSUFICIENTE")
        self.producto = producto
        self.solicitado = solicitado
        self.disponible = disponible



# ---------------- Producto que no existe (404) ----------------
class ProductoNoEncontrado(ErrorRedGoatEyes):

    def __init__(self, identificador):
        super().__init__(f"No existe el producto {identificador}", "PRODUCTO_NO_ENCONTRADO")
        self.identificador = identificador



# ---------------- Usuario o clave incorrectos (401) ----------------
class CredencialesInvalidas(ErrorRedGoatEyes):

    def __init__(self):
        super().__init__("El correo o la contraseña no son correctos", "CREDENCIALES_INVALIDAS")



# ---------------- Correo ya registrado (409) ----------------
class UsuarioDuplicado(ErrorRedGoatEyes):

    def __init__(self, email):
        super().__init__(f"Ya existe una cuenta con el correo {email}", "USUARIO_DUPLICADO")
        self.email = email



# ---------------- Sin permisos para esa accion (403) ----------------
class PermisoDenegado(ErrorRedGoatEyes):

    def __init__(self, accion, nivel_requerido=None):
        mensaje = f"No tiene permisos para {accion}"
        if nivel_requerido is not None:
            mensaje += f" (nivel requerido: {nivel_requerido})"
        super().__init__(mensaje, "PERMISO_DENEGADO")



# ---------------- Cambio de estado no permitido (409) ----------------
class TransicionInvalida(ErrorRedGoatEyes):

    def __init__(self, estado_actual, estado_destino):
        mensaje = f"No se puede pasar del estado '{estado_actual}' a '{estado_destino}'"
        super().__init__(mensaje, "TRANSICION_INVALIDA")
        self.estado_actual = estado_actual
        self.estado_destino = estado_destino



# ---------------- Carrito sin productos (400) ----------------
class CarritoVacio(ErrorRedGoatEyes):

    def __init__(self):
        super().__init__("El carrito no contiene productos", "CARRITO_VACIO")