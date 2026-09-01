# ============================================================
# VALIDADORES
# Funciones de validacion que se reutilizan en todo el backend.
# Son la segunda barrera: la primera es el navegador y la
# tercera son las restricciones CHECK de PostgreSQL.
# ============================================================
import re
from datetime import date

from app.utils.excepciones import ErrorValidacion

REGEX_EMAIL = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$")
REGEX_CEDULA = re.compile(r"^[0-9]{10}$")
REGEX_TELEFONO = re.compile(r"^[0-9+\-\s]{7,15}$")
REGEX_POSTAL = re.compile(r"^[0-9]{6}$")
REGEX_CODIGO_PRODUCTO = re.compile(r"^RGE-[A-Z]{3}-[0-9]{3}$")
REGEX_CODIGO_PEDIDO = re.compile(r"^RGE-[0-9]{4}-[0-9]{4}$")

PROVINCIAS_VALIDAS = tuple(range(1, 25)) + (30,)
COEFICIENTES_CEDULA = (2, 1, 2, 1, 2, 1, 2, 1, 2)



# ---------------- Limpiar espacios sobrantes ----------------
def texto_limpio(valor):
    return "" if valor is None else str(valor).strip()



# ---------------- Largo de un texto ----------------
def validar_longitud(campo, valor, minimo, maximo=None):
    texto = texto_limpio(valor)
    if len(texto) < minimo:
        raise ErrorValidacion(campo, f"Debe tener al menos {minimo} caracteres")
    if maximo is not None and len(texto) > maximo:
        raise ErrorValidacion(campo, f"No puede superar los {maximo} caracteres")
    return texto



# ---------------- Correo electronico ----------------
def validar_email(valor, campo="email"):
    texto = texto_limpio(valor).lower()
    if not REGEX_EMAIL.match(texto):
        raise ErrorValidacion(campo, "El correo no tiene un formato valido")
    if len(texto) > 120:
        raise ErrorValidacion(campo, "El correo no puede superar los 120 caracteres")
    return texto


def cedula_valida(cedula):
    texto = texto_limpio(cedula)
    if not REGEX_CEDULA.match(texto):
        return False
    if int(texto[:2]) not in PROVINCIAS_VALIDAS:
        return False
    if int(texto[2]) >= 6:
        return False
    suma = 0
    for digito, coeficiente in zip(texto[:9], COEFICIENTES_CEDULA):
        producto = int(digito) * coeficiente
        suma += producto - 9 if producto > 9 else producto
    return (10 - suma % 10) % 10 == int(texto[9])



# ---------------- Cedula ecuatoriana ----------------
def validar_cedula(valor, campo="cedula", obligatoria=True):
    texto = texto_limpio(valor)
    if not texto:
        if obligatoria:
            raise ErrorValidacion(campo, "La cedula es obligatoria")
        return None
    if not REGEX_CEDULA.match(texto):
        raise ErrorValidacion(campo, "La cedula debe tener exactamente 10 digitos")
    if not cedula_valida(texto):
        raise ErrorValidacion(campo, "La cedula no es valida segun el digito verificador")
    return texto



# ---------------- Telefono ----------------
def validar_telefono(valor, campo="telefono", obligatorio=False):
    texto = texto_limpio(valor)
    if not texto:
        if obligatorio:
            raise ErrorValidacion(campo, "El telefono es obligatorio")
        return None
    if not REGEX_TELEFONO.match(texto):
        raise ErrorValidacion(campo, "El telefono debe tener entre 7 y 15 digitos")
    return texto



# ---------------- Contrasena ----------------
def validar_password(valor, campo="password", minimo=8):
    texto = "" if valor is None else str(valor)
    if len(texto) < minimo:
        raise ErrorValidacion(campo, f"La contrasena debe tener al menos {minimo} caracteres")
    if len(texto) > 128:
        raise ErrorValidacion(campo, "La contrasena no puede superar los 128 caracteres")
    return texto



# ---------------- Numeros enteros ----------------
def validar_entero(valor, campo, minimo=None, maximo=None):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise ErrorValidacion(campo, "Debe ser un numero entero")
    if minimo is not None and numero < minimo:
        raise ErrorValidacion(campo, f"Debe ser mayor o igual a {minimo}")
    if maximo is not None and numero > maximo:
        raise ErrorValidacion(campo, f"Debe ser menor o igual a {maximo}")
    return numero



# ---------------- Cantidad de un pedido ----------------
def validar_cantidad(valor, campo="cantidad"):
    return validar_entero(valor, campo, minimo=1, maximo=999)



# ---------------- Fecha de nacimiento ----------------
def validar_fecha_nacimiento(valor, campo="fecha_nacimiento", obligatoria=False):
    texto = texto_limpio(valor)
    if not texto:
        if obligatoria:
            raise ErrorValidacion(campo, "La fecha de nacimiento es obligatoria")
        return None
    try:
        fecha = date.fromisoformat(texto)
    except ValueError:
        raise ErrorValidacion(campo, "La fecha debe tener el formato AAAA-MM-DD")
    if fecha >= date.today():
        raise ErrorValidacion(campo, "La fecha de nacimiento no puede ser futura")
    return fecha


def validar_codigo_producto(valor, campo="codigo"):
    texto = texto_limpio(valor).upper()
    if not REGEX_CODIGO_PRODUCTO.match(texto):
        raise ErrorValidacion(campo, "El codigo debe tener el formato RGE-XXX-000")
    return texto


def validar_codigo_pedido(valor, campo="codigo_pedido"):
    texto = texto_limpio(valor).upper()
    if not REGEX_CODIGO_PEDIDO.match(texto):
        raise ErrorValidacion(campo, "El codigo debe tener el formato RGE-AAAA-0000")
    return texto


def validar_codigo_postal(valor, campo="codigo_postal", obligatorio=False):
    texto = texto_limpio(valor)
    if not texto:
        if obligatorio:
            raise ErrorValidacion(campo, "El codigo postal es obligatorio")
        return None
    if not REGEX_POSTAL.match(texto):
        raise ErrorValidacion(campo, "El codigo postal debe tener 6 digitos")
    return texto



# ---------------- Que el valor este en una lista permitida ----------------
def validar_opcion(valor, campo, opciones):
    texto = texto_limpio(valor)
    if texto not in opciones:
        raise ErrorValidacion(campo, f"Debe ser uno de: {', '.join(opciones)}")
    return texto


def validar_campos_obligatorios(datos, campos):
    faltantes = [c for c in campos if not texto_limpio(datos.get(c))]
    if faltantes:
        raise ErrorValidacion(faltantes[0], f"Falta el campo obligatorio: {faltantes[0]}")
    return True