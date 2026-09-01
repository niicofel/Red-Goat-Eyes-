# ============================================================
# DIRECCION
# Direccion de entrega de un cliente. Un cliente puede tener
# varias, pero solo una es la principal.
# ============================================================
import re

from app.utils.excepciones import ErrorValidacion



# ---------------- La clase ----------------
class Direccion:

    REGEX_POSTAL = re.compile(r"^[0-9]{6}$")

    def __init__(self, id_direccion, id_cliente, ciudad, calle_principal,
                 calle_secundaria=None, numeracion=None, referencia=None,
                 codigo_postal=None, es_principal=False):
        self._id_direccion = id_direccion
        self._id_cliente = id_cliente
        self._ciudad = ciudad
        self.calle_principal = calle_principal
        self._calle_secundaria = calle_secundaria
        self._numeracion = numeracion
        self._referencia = referencia
        self.codigo_postal = codigo_postal
        self._es_principal = bool(es_principal)

    @property
    def id_direccion(self):
        return self._id_direccion

    @property
    def id_cliente(self):
        return self._id_cliente

    @property
    def ciudad(self):
        return self._ciudad

    @property
    def calle_principal(self):
        return self._calle_principal

    @calle_principal.setter
    def calle_principal(self, valor):
        texto = str(valor).strip()
        if len(texto) < 5:
            raise ErrorValidacion("calle_principal", "La dirección debe tener al menos 5 caracteres")
        self._calle_principal = texto

    @property
    def calle_secundaria(self):
        return self._calle_secundaria

    @property
    def numeracion(self):
        return self._numeracion

    @property
    def referencia(self):
        return self._referencia

    @property

# ---------------- Codigo postal con validacion ----------------
    def codigo_postal(self):
        return self._codigo_postal

    @codigo_postal.setter
    def codigo_postal(self, valor):
        if valor is None or str(valor).strip() == "":
            self._codigo_postal = None
            return
        texto = str(valor).strip()
        if not self.REGEX_POSTAL.match(texto):
            raise ErrorValidacion("codigo_postal", "El código postal debe tener 6 dígitos")
        self._codigo_postal = texto

    @property
    def es_principal(self):
        return self._es_principal


# ---------------- Marcar como principal ----------------
    def marcar_principal(self):
        self._es_principal = True

    def quitar_principal(self):
        self._es_principal = False


# ---------------- Armar la direccion como texto ----------------
    def formato_completo(self):
        partes = [self._calle_principal]
        if self._numeracion:
            partes.append(self._numeracion)
        if self._calle_secundaria:
            partes.append(f"y {self._calle_secundaria}")
        linea = " ".join(partes)
        if self._ciudad:
            linea += f", {self._ciudad}"
        if self._referencia:
            linea += f" ({self._referencia})"
        return linea

    def formato_corto(self):
        base = self._calle_principal
        if self._numeracion:
            base += f" {self._numeracion}"
        return f"{base}, {self._ciudad}" if self._ciudad else base

    def a_diccionario(self):
        return {
            "id_direccion": self._id_direccion,
            "id_cliente": self._id_cliente,
            "ciudad": self._ciudad,
            "calle_principal": self._calle_principal,
            "calle_secundaria": self._calle_secundaria,
            "numeracion": self._numeracion,
            "referencia": self._referencia,
            "codigo_postal": self._codigo_postal,
            "es_principal": self._es_principal,
            "formato_completo": self.formato_completo(),
        }

    def __str__(self):
        return self.formato_completo()

    def __eq__(self, otra):
        if not isinstance(otra, Direccion):
            return NotImplemented
        return self._id_direccion == otra._id_direccion

    def __hash__(self):
        return hash(self._id_direccion)