import os
import sys
from datetime import date
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models import (Persona, Cliente, Administrador, Producto, Hoodie,
                        Pantalon, Accesorio, Categoria, Talla, ProductoTalla,
                        Direccion, Carrito, DetallePedido, Pedido, Mensaje)
from app.utils.excepciones import (ErrorValidacion, StockInsuficiente,
                                   PermisoDenegado, TransicionInvalida, CarritoVacio)

TOTAL = 0
FALLOS = 0


def comprobar(descripcion, condicion):
    global TOTAL, FALLOS
    TOTAL += 1
    if condicion:
        print(f"  [OK]    {descripcion}")
    else:
        FALLOS += 1
        print(f"  [FALLO] {descripcion}")


def titulo(texto):
    print()
    print("=" * 66)
    print(f"  {texto}")
    print("=" * 66)


def construir_catalogo():
    return [
        Hoodie(1, "RGE-HOO-001", "SUPERNOVA",
               "Hoodie oversize con estampado frontal de gran formato",
               35.00, "assets/img/productos/Hoodie1.png",
               material="Algodon 80% poliester 20%", gramaje=380),
        Hoodie(2, "RGE-HOO-004", "COLD SPIRIT",
               "Hoodie de gramaje pesado pensado para clima frio",
               35.00, "assets/img/productos/Hoodie4.png",
               material="Algodon 80% poliester 20%", gramaje=400),
        Pantalon(3, "RGE-PAN-001", "GRAVITY Baggy Denim",
                 "Pantalon baggy en denim rigido con caida amplia",
                 29.99, "assets/img/productos/Pantalones1.png",
                 material="Denim 100% algodon", tipo_corte="Baggy"),
        Pantalon(4, "RGE-PAN-003", "UTILITY Carpenter Blue",
                 "Pantalon carpintero con presilla y doble costura",
                 29.99, "assets/img/productos/Pantalones3.png",
                 material="Denim 100% algodon", tipo_corte="Carpenter"),
        Accesorio(5, "RGE-ACC-004", "Gorra Los Angeles Dodgers MLB Floral",
                  "Gorra snapback con bordado y forro interior floral",
                  79.00, "assets/img/productos/Accesorios4.png",
                  material="Poliester 100%", tipo_accesorio="Gorra"),
        Accesorio(6, "RGE-ACC-002", "Collar cubano estilo Miami",
                  "Collar de eslabon cubano con cierre de seguridad",
                  15.00, "assets/img/productos/Accesorios2.png",
                  material="Acero inoxidable 316L", tipo_accesorio="Collar"),
    ]


def probar_abstraccion():
    titulo("ABSTRACCION")
    try:
        Producto(1, "X", "Nombre", "Descripcion larga", 10, "img", "cat")
        comprobar("Producto no se puede instanciar", False)
    except TypeError:
        comprobar("Producto es abstracta y no se puede instanciar", True)
    try:
        Persona(1, "Ana", "Lopez", "ana@test.com")
        comprobar("Persona no se puede instanciar", False)
    except TypeError:
        comprobar("Persona es abstracta y no se puede instanciar", True)


def probar_polimorfismo():
    titulo("POLIMORFISMO")
    catalogo = construir_catalogo()
    print()
    for producto in catalogo:
        print(f"  {producto.tipo():10} {producto.codigo:14} "
              f"lista=${producto.precio:>6}  final=${producto.calcular_precio_final():>6}")
        print(f"             {producto.descripcion_corta()}")
    print()
    comprobar("Hoodie estandar sin recargo", catalogo[0].calcular_precio_final() == Decimal("35.00"))
    comprobar("Hoodie premium con 10% de recargo", catalogo[1].calcular_precio_final() == Decimal("38.50"))
    comprobar("Pantalon sin refuerzos sin recargo", catalogo[2].calcular_precio_final() == Decimal("29.99"))
    comprobar("Pantalon carpenter con 5% de recargo", catalogo[3].calcular_precio_final() == Decimal("31.49"))
    comprobar("Accesorio gama alta con 5% de descuento", catalogo[4].calcular_precio_final() == Decimal("75.05"))
    comprobar("Accesorio gama baja sin descuento", catalogo[5].calcular_precio_final() == Decimal("15.00"))
    tipos = {p.tipo() for p in catalogo}
    comprobar("Tres implementaciones distintas del mismo metodo", len(tipos) == 3)


def probar_encapsulamiento():
    titulo("ENCAPSULAMIENTO")
    hoodie = construir_catalogo()[0]
    try:
        hoodie.precio = -5
        comprobar("Precio negativo rechazado", False)
    except ErrorValidacion:
        comprobar("Precio negativo rechazado", True)
    try:
        hoodie.precio_oferta = 99
        comprobar("Oferta mayor que el precio rechazada", False)
    except ErrorValidacion:
        comprobar("Oferta mayor que el precio rechazada", True)
    try:
        hoodie.nombre = "AB"
        comprobar("Nombre demasiado corto rechazado", False)
    except ErrorValidacion:
        comprobar("Nombre demasiado corto rechazado", True)
    try:
        hoodie.genero = "Otro"
        comprobar("Genero fuera del catalogo rechazado", False)
    except ErrorValidacion:
        comprobar("Genero fuera del catalogo rechazado", True)
    hoodie.aplicar_oferta(20)
    comprobar("Oferta del 20% calculada", hoodie.precio_oferta == Decimal("28.00"))
    comprobar("Porcentaje de descuento correcto", hoodie.descuento_porcentaje == 20)
    hoodie.quitar_oferta()
    comprobar("Oferta retirada", not hoodie.en_oferta)


def probar_herencia():
    titulo("HERENCIA")
    cliente = Cliente(10, "Maria Fernanda", "Torres Vega", "  MARIA@Example.COM ",
                      cedula="1712345675", telefono="0991234567",
                      fecha_nacimiento="2001-04-18", ciudad="Quito")
    admin = Administrador(20, "Felipe Nicolas", "Campos Cisneros",
                          "admin@redgoateyes.com",
                          cargo="Administrador general", nivel_acceso=3)
    print()
    print(f"  {cliente}")
    print(f"  {admin}")
    print()
    comprobar("Cliente hereda de Persona", isinstance(cliente, Persona))
    comprobar("Administrador hereda de Persona", isinstance(admin, Persona))
    comprobar("El correo se normaliza a minusculas", cliente.email == "maria@example.com")
    comprobar("nombre_completo heredado funciona", cliente.nombre_completo == "Maria Fernanda Torres Vega")
    comprobar("iniciales heredadas funcionan", cliente.iniciales == "MT")
    comprobar("Cada clase declara su propio rol",
              cliente.obtener_rol() == "cliente" and admin.obtener_rol() == "administrador")
    comprobar("La edad se calcula", cliente.edad is not None and cliente.es_mayor_de_edad)


def probar_cedula():
    titulo("VALIDACION DE CEDULA ECUATORIANA")
    casos = [("1712345675", True), ("1712345678", False),
             ("9912345675", False), ("1762345675", False), ("12345", False)]
    for numero, esperado in casos:
        try:
            Cliente(99, "Test", "Prueba", "t@test.com", cedula=numero)
            valida = True
        except ErrorValidacion:
            valida = False
        etiqueta = "aceptada" if esperado else "rechazada"
        comprobar(f"Cedula {numero} {etiqueta}", valida == esperado)


def probar_permisos():
    titulo("PERMISOS POR NIVEL DE ACCESO")
    consulta = Administrador(30, "Solo", "Consulta", "consulta@rge.com", nivel_acceso=1)
    total = Administrador(31, "Felipe", "Campos", "admin@rge.com", nivel_acceso=3)
    comprobar("Nivel 1 no gestiona productos", not consulta.puede_gestionar_productos())
    comprobar("Nivel 3 gestiona productos", total.puede_gestionar_productos())
    comprobar("Nivel 1 tiene menos permisos", len(consulta.permisos()) < len(total.permisos()))
    try:
        consulta.exigir("reponer_stock")
        comprobar("Nivel 1 bloqueado al reponer stock", False)
    except PermisoDenegado:
        comprobar("Nivel 1 bloqueado al reponer stock", True)
    comprobar("Nivel 3 autorizado a reponer stock", total.exigir("reponer_stock"))


def probar_inventario():
    titulo("INVENTARIO")
    talla = Talla(7, "U", "Talla unica", 7)
    hoodie = construir_catalogo()[0]
    inventario = ProductoTalla(1, hoodie, talla, stock=5, stock_minimo=3)
    comprobar("La talla U es unica", talla.es_unica)
    comprobar("Hay stock suficiente para 3", inventario.hay_stock(3))
    comprobar("No hay stock para 10", not inventario.hay_stock(10))
    inventario.descontar(3)
    comprobar("Stock descontado correctamente", inventario.stock == 2)
    comprobar("Nivel critico detectado", inventario.en_nivel_critico)
    try:
        inventario.descontar(10)
        comprobar("Venta sin stock rechazada", False)
    except StockInsuficiente:
        comprobar("Venta sin stock rechazada", True)
    inventario.reponer(20)
    comprobar("Stock repuesto correctamente", inventario.stock == 22)
    comprobar("Fuera de nivel critico", not inventario.en_nivel_critico)


def probar_carrito():
    titulo("CARRITO (agregacion)")
    talla = Talla(7, "U", "Talla unica", 7)
    catalogo = construir_catalogo()
    pt_hoodie = ProductoTalla(1, catalogo[0], talla, stock=18)
    pt_pantalon = ProductoTalla(2, catalogo[2], talla, stock=17)
    pt_gorra = ProductoTalla(3, catalogo[4], talla, stock=1)

    carrito = Carrito(1, 10)
    comprobar("El carrito nace vacio", carrito.vacio and not bool(carrito))
    try:
        carrito.validar_para_pago()
        comprobar("Carrito vacio no permite pagar", False)
    except CarritoVacio:
        comprobar("Carrito vacio no permite pagar", True)

    carrito.agregar(pt_hoodie, 2)
    carrito.agregar(pt_pantalon, 1)
    print()
    print(f"  subtotal = ${carrito.calcular_subtotal()}")
    print(f"  IVA 15%  = ${carrito.calcular_iva()}")
    print(f"  total    = ${carrito.calcular_total()}")
    print()
    comprobar("Subtotal correcto", carrito.calcular_subtotal() == Decimal("99.99"))
    comprobar("IVA del 15% correcto", carrito.calcular_iva() == Decimal("15.00"))
    comprobar("Total correcto", carrito.calcular_total() == Decimal("114.99"))
    comprobar("Dos lineas y tres unidades",
              carrito.total_lineas == 2 and carrito.total_unidades == 3)

    carrito.agregar(pt_hoodie, 1)
    comprobar("Repetir producto suma cantidad sin crear linea",
              carrito.total_lineas == 2 and carrito.total_unidades == 4)
    try:
        carrito.agregar(pt_gorra, 5)
        comprobar("Agregar por encima del stock rechazado", False)
    except StockInsuficiente:
        comprobar("Agregar por encima del stock rechazado", True)

    comprobar("Formato de items para el procedimiento",
              carrito.a_lista_items() == [{"id_producto_talla": 1, "cantidad": 3},
                                          {"id_producto_talla": 2, "cantidad": 1}])
    carrito.vaciar()
    comprobar("El carrito se vacia", carrito.vacio)


def probar_pedido():
    titulo("PEDIDO (composicion y maquina de estados)")
    talla = Talla(7, "U", "Talla unica", 7)
    catalogo = construir_catalogo()
    pt_hoodie = ProductoTalla(1, catalogo[0], talla, stock=18)
    pt_pantalon = ProductoTalla(2, catalogo[2], talla, stock=17)

    cliente = Cliente(10, "Maria Fernanda", "Torres Vega", "maria@example.com",
                      cedula="1712345675", ciudad="Quito")
    direccion = Direccion(1, 10, "Quito", "Av. 12 de Octubre",
                          "Vicente Ramon Roca", "N24-593",
                          "Frente al parque El Arbolito", "170525", True)
    cliente.agregar_direccion(direccion)
    comprobar("La direccion se asocia al cliente", len(cliente.direcciones) == 1)
    comprobar("Direccion principal detectada", cliente.direccion_principal is direccion)

    pedido = Pedido(1, "RGE-2026-0006", cliente, direccion, metodo_pago="Deuna")
    pedido.agregar_detalle(DetallePedido(1, pt_hoodie, 2))
    pedido.agregar_detalle(DetallePedido(2, pt_pantalon, 1))
    print()
    print(f"  {pedido}")
    print(f"  subtotal = ${pedido.calcular_subtotal()}")
    print(f"  IVA 15%  = ${pedido.calcular_iva()}")
    print(f"  total    = ${pedido.calcular_total()}")
    print()
    comprobar("Subtotal del pedido correcto", pedido.calcular_subtotal() == Decimal("99.99"))
    comprobar("Total del pedido correcto", pedido.calcular_total() == Decimal("114.99"))

    pedido.agregar_detalle(DetallePedido(3, pt_hoodie, 1))
    comprobar("Producto repetido suma cantidad en la linea existente",
              len(pedido) == 2 and pedido.total_unidades == 4)

    comprobar("El pedido nace Pendiente", pedido.estado == "Pendiente")
    try:
        pedido.cambiar_estado("Entregado")
        comprobar("Transicion Pendiente a Entregado bloqueada", False)
    except TransicionInvalida:
        comprobar("Transicion Pendiente a Entregado bloqueada", True)

    pedido.marcar_pagado()
    comprobar("Transicion a Pagado permitida", pedido.estado == "Pagado")
    comprobar("El pedido consta como pagado", pedido.esta_pagado)
    pedido.cambiar_estado("En preparacion")
    pedido.cambiar_estado("Enviado")
    pedido.cambiar_estado("Entregado")
    comprobar("Ruta completa hasta Entregado", pedido.estado == "Entregado")
    comprobar("Entregado es estado final", pedido.es_final)
    try:
        pedido.cancelar()
        comprobar("No se cancela un pedido entregado", False)
    except TransicionInvalida:
        comprobar("No se cancela un pedido entregado", True)
    comprobar("El historial registra los 5 estados", len(pedido.historial) == 5)
    comprobar("Correo del recibo correcto", pedido.correo_destinatario() == "maria@example.com")


def probar_precio_congelado():
    titulo("PRECIO CONGELADO EN EL DETALLE")
    talla = Talla(7, "U", "Talla unica", 7)
    hoodie = construir_catalogo()[0]
    inventario = ProductoTalla(1, hoodie, talla, stock=10)
    detalle = DetallePedido(1, inventario, 2)
    precio_original = detalle.precio_unitario
    hoodie.precio = 50.00
    print()
    print(f"  precio al comprar        = ${precio_original}")
    print(f"  precio actual del producto = ${hoodie.calcular_precio_final()}")
    print(f"  precio en el detalle       = ${detalle.precio_unitario}")
    print()
    comprobar("El detalle conserva el precio historico",
              detalle.precio_unitario == Decimal("35.00"))
    comprobar("El producto si cambio de precio",
              hoodie.calcular_precio_final() == Decimal("50.00"))
    comprobar("El subtotal de la linea usa el precio congelado",
              detalle.subtotal_linea == Decimal("70.00"))


def probar_categoria():
    titulo("CATEGORIA (composicion)")
    categoria = Categoria(1, "Hoodies", "hoodies",
                          "Hoodies oversize de gramaje pesado",
                          "assets/img/categorias/Hoodie1Portada.png")
    catalogo = construir_catalogo()
    for producto in catalogo[:2]:
        categoria.agregar_producto(producto)
    comprobar("Dos productos agregados", len(categoria) == 2)
    comprobar("El operador in funciona", catalogo[0] in categoria)
    comprobar("Precio minimo correcto", categoria.precio_minimo() == Decimal("35.00"))
    comprobar("Precio maximo correcto", categoria.precio_maximo() == Decimal("38.50"))
    ordenados = categoria.ordenar_por_precio()
    comprobar("Orden por precio ascendente",
              ordenados[0].calcular_precio_final() <= ordenados[1].calcular_precio_final())
    try:
        categoria.slug = "Hoodies Con Espacios"
        comprobar("Slug invalido rechazado", False)
    except ErrorValidacion:
        comprobar("Slug invalido rechazado", True)


def probar_mensaje():
    titulo("MENSAJE DE CONTACTO")
    mensaje = Mensaje(1, "Reclamo", "Guayaquil", "Juan Carlos Ramirez",
                      "juan@example.com",
                      "Mi pedido llego con un dia de retraso respecto a la fecha estimada")
    comprobar("El mensaje nace sin leer", not mensaje.leido)
    comprobar("Un reclamo sin responder es urgente", mensaje.es_urgente)
    comprobar("El resumen se recorta", len(mensaje.resumen(30)) <= 33)
    try:
        Mensaje(2, "Otro", "Quito", "Ana", "ana@test.com", "Un mensaje suficientemente largo")
        comprobar("Asunto fuera del catalogo rechazado", False)
    except ErrorValidacion:
        comprobar("Asunto fuera del catalogo rechazado", True)
    try:
        Mensaje(3, "Consulta", "Quito", "Ana Lopez", "ana@test.com", "Corto")
        comprobar("Descripcion corta rechazada", False)
    except ErrorValidacion:
        comprobar("Descripcion corta rechazada", True)
    admin = Administrador(20, "Felipe", "Campos", "admin@rge.com", nivel_acceso=3)
    mensaje.responder(admin)
    comprobar("El mensaje queda respondido", mensaje.respondido and mensaje.leido)
    comprobar("Ya no es urgente", not mensaje.es_urgente)


def main():
    print()
    print("#" * 66)
    print("#  RED GOAT EYES - Pruebas de las clases del dominio")
    print("#" * 66)

    probar_abstraccion()
    probar_polimorfismo()
    probar_encapsulamiento()
    probar_herencia()
    probar_cedula()
    probar_permisos()
    probar_inventario()
    probar_carrito()
    probar_pedido()
    probar_precio_congelado()
    probar_categoria()
    probar_mensaje()

    print()
    print("=" * 66)
    print(f"  RESULTADO: {TOTAL - FALLOS} de {TOTAL} comprobaciones superadas")
    print("=" * 66)
    print()
    return 1 if FALLOS else 0


if __name__ == "__main__":
    sys.exit(main())