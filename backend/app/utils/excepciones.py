class ErrorRedGoatEyes(Exception):

    def __init__(self, mensaje, codigo=None):
        super().__init__(mensaje)
        self.mensaje = mensaje
        self.codigo = codigo or self.__class__.__name__

    def a_diccionario(self):
        return {"error": self.codigo, "mensaje": self.mensaje}

    def __str__(self):
        return f"[{self.codigo}] {self.mensaje}"


class ErrorValidacion(ErrorRedGoatEyes):

    def __init__(self, campo, mensaje):
        super().__init__(mensaje, "VALIDACION")
        self.campo = campo

    def a_diccionario(self):
        datos = super().a_diccionario()
        datos["campo"] = self.campo
        return datos


class StockInsuficiente(ErrorRedGoatEyes):

    def __init__(self, producto, solicitado, disponible):
        mensaje = (f"Stock insuficiente para '{producto}': "
                   f"se solicitan {solicitado} unidades y solo hay {disponible}")
        super().__init__(mensaje, "STOCK_INSUFICIENTE")
        self.producto = producto
        self.solicitado = solicitado
        self.disponible = disponible


class ProductoNoEncontrado(ErrorRedGoatEyes):

    def __init__(self, identificador):
        super().__init__(f"No existe el producto {identificador}", "PRODUCTO_NO_ENCONTRADO")
        self.identificador = identificador


class CredencialesInvalidas(ErrorRedGoatEyes):

    def __init__(self):
        super().__init__("El correo o la contraseña no son correctos", "CREDENCIALES_INVALIDAS")


class UsuarioDuplicado(ErrorRedGoatEyes):

    def __init__(self, email):
        super().__init__(f"Ya existe una cuenta con el correo {email}", "USUARIO_DUPLICADO")
        self.email = email


class PermisoDenegado(ErrorRedGoatEyes):

    def __init__(self, accion, nivel_requerido=None):
        mensaje = f"No tiene permisos para {accion}"
        if nivel_requerido is not None:
            mensaje += f" (nivel requerido: {nivel_requerido})"
        super().__init__(mensaje, "PERMISO_DENEGADO")


class TransicionInvalida(ErrorRedGoatEyes):

    def __init__(self, estado_actual, estado_destino):
        mensaje = f"No se puede pasar del estado '{estado_actual}' a '{estado_destino}'"
        super().__init__(mensaje, "TRANSICION_INVALIDA")
        self.estado_actual = estado_actual
        self.estado_destino = estado_destino


class CarritoVacio(ErrorRedGoatEyes):

    def __init__(self):
        super().__init__("El carrito no contiene productos", "CARRITO_VACIO")