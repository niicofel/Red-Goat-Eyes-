# Planteamiento del Problema

**Proyecto Integrador — Segundo Nivel**  
PUCE TEC · Unidad Académica de Formación Técnica y Tecnológica  
Asignaturas: Base de Datos I · Programación Orientada a Objetos · Desarrollo Web Frontend UX/UI

**Equipo:** Felipe Nicolás Campos Cisneros · Elian Emanuel Valenzuela Álvarez · Rafael Chiriboga  
**Fecha:** Agosto 2026  
**Repositorio:** https://github.com/niicofel/Red-Goat-Eyes-

---

## 1. Contexto

En Quito, una gran parte de las marcas pequeñas de ropa urbana utiliza las redes sociales como su principal medio para mostrar y vender productos. Generalmente publican sus prendas en Instagram y terminan la venta mediante mensajes directos. Esta forma de trabajo puede ser suficiente cuando existen pocos pedidos, pero empieza a generar dificultades cuando la cantidad de clientes aumenta.

Red Goat Eyes es una marca de ropa urbana que cuenta con 24 productos organizados en tres categorías: hoodies, pantalones y accesorios.

## 2. Problema identificado

Al manejar las ventas principalmente por mensajes se presentan varios problemas que afectan tanto a la marca como a sus clientes.

### 2.1 Falta de control del inventario

Cuando el stock se controla de memoria o mediante registros separados, existe el riesgo de ofrecer prendas que ya no se encuentran disponibles. Esto puede provocar cancelaciones después de haber confirmado una compra y generar una mala experiencia para el cliente.

El problema se agrava cuando una misma prenda existe en varias tallas, porque el vendedor debe recordar cuántas unidades quedan de cada una.

### 2.2 Falta de un historial de ventas

Las ventas realizadas mediante conversaciones no permiten mantener la información organizada en un solo lugar. Por esta razón, resulta difícil conocer datos importantes para el negocio, por ejemplo:

- qué categoría tiene mayores ventas;
- cuáles son los clientes que compran con mayor frecuencia;
- qué productos están próximos a quedarse sin stock.

### 2.3 Ausencia de un comprobante

En una venta realizada únicamente por chat no siempre existe un documento que respalde la operación. Si ocurre un reclamo, puede resultar complicado comprobar qué productos se compraron, cuál fue su precio o qué método de pago se seleccionó.

### 2.4 Cálculo manual de valores

El IVA del 15 % puede calcularse manualmente durante cada venta. Al repetir este proceso muchas veces pueden aparecer errores de cálculo o de redondeo que terminan afectando el valor final del pedido.

### 2.5 Poco seguimiento de los pedidos

El cliente necesita conocer en qué etapa se encuentra su compra. Sin un sistema, debe preguntar por mensaje si el pedido ya fue pagado, preparado o enviado, lo que también genera trabajo adicional para la marca.

### 2.6 Consultas dispersas

Las preguntas de los clientes llegan por distintos canales y no quedan registradas. Un reclamo puede perderse entre otros mensajes y no recibir respuesta.

## 3. Necesidad

A partir de estos problemas se identificó la necesidad de desarrollar una plataforma web que permita:

1. mostrar el catálogo utilizando el stock real por talla y evitar compras cuando no existen unidades disponibles;
2. almacenar las ventas para poder consultarlas posteriormente;
3. generar un comprobante de manera automática;
4. calcular el IVA de forma consistente;
5. consultar el estado de los pedidos;
6. reponer inventario de forma controlada y auditada;
7. registrar y responder las consultas de los clientes;
8. proporcionar reportes que ayuden al administrador a tomar decisiones.

## 4. Solución propuesta

La solución consiste en una tienda en línea organizada en tres capas principales:

| Capa | Tecnología | Responsabilidad |
|------|------------|-----------------|
| Presentación | HTML5, CSS3 y JavaScript | Interfaz, catálogo, carrito, formularios y panel administrativo |
| Lógica | Python 3 y Flask | Validaciones, autenticación, reglas del negocio y generación de recibos |
| Datos | PostgreSQL 18 | Almacenamiento, relaciones, reglas críticas y reportes |

Esta separación permite que cada tecnología se encargue de una responsabilidad concreta y facilita el mantenimiento del sistema.

## 5. Justificación de la solución

### 5.1 Respuesta a los problemas encontrados

Cada problema identificado se relaciona con una función implementada en el sistema:

| Problema | Solución implementada |
|----------|----------------------|
| Falta de control de inventario | La tabla `producto_talla` almacena `stock` y `stock_minimo` por cada combinación de producto y talla, mientras `trg_validar_stock` evita registrar pedidos sin existencias |
| Falta de historial | `pedido` y `detalle_pedido` mantienen el registro de las compras y conservan el precio utilizado al momento de vender |
| Falta de comprobante | Se genera un recibo PDF y se envía al correo después de confirmar el pago |
| Cálculo manual del IVA | El 15 % se maneja de forma consistente en JavaScript, Python y PostgreSQL |
| Falta de seguimiento | Los estados del pedido son controlados mediante `sp_cambiar_estado_pedido` |
| Reposición sin control | El procedimiento `sp_reponer_stock` verifica el nivel del administrador y registra la operación en la auditoría |
| Consultas dispersas | El formulario de contacto guarda cada mensaje y además avisa por correo al administrador |

### 5.2 Integración de las tres asignaturas

El proyecto permite aplicar las tres materias sobre un mismo problema.

**Base de Datos I** se encarga principalmente de mantener la información íntegra. Las relaciones impiden registros incoherentes, el stock no puede quedar en valores negativos y varias validaciones también existen como restricciones `CHECK`. La vista `v_catalogo_publico` resuelve además un problema propio del modelo: como el inventario se guarda por talla, agrupa las filas para que el catálogo muestre un producto y no una entrada por cada talla.

**Programación Orientada a Objetos** permite representar las entidades del negocio. Por ejemplo, `Hoodie`, `Pantalon` y `Accesorio` son tipos de `Producto`, pero cada uno calcula su precio de forma diferente. De esta manera se aplica polimorfismo sobre una situación real del sistema, y ese mismo método es el que usan tanto el catálogo como el cobro, de modo que el precio mostrado y el cobrado siempre coinciden.

**Desarrollo Web Frontend UX/UI** se enfoca en la interacción con el usuario. La interfaz está preparada para dispositivos móviles, muestra los errores junto al campo correspondiente y permite construir el carrito antes de solicitar el inicio de sesión. La ficha de producto permite elegir talla y cantidad sin salir del catálogo.

### 5.3 Organización y posibilidad de crecimiento

En el backend se utiliza una estructura de rutas, servicios, repositorios y base de datos. Esta separación evita colocar toda la lógica en un mismo archivo. Además, el patrón Repository concentra el acceso a los datos y reduce el acoplamiento entre las consultas SQL y la lógica del sistema.

El modelo de datos ya contemplaba la venta por tallas desde su diseño, por lo que ampliar el catálogo de una talla única a cuatro tallas no requirió modificar ninguna tabla: bastó con agregar filas y ajustar la vista de consulta.

### 5.4 Seguridad

La aplicación no utiliza una cuenta de superusuario para conectarse a PostgreSQL. Se definieron roles con permisos diferentes y se limita el acceso a información sensible. Los datos de usuario que pueden consultarse desde la aplicación se exponen mediante una vista segura que no incluye el hash de la contraseña.

## 6. Alcance

### Incluido

- Catálogo público con 24 productos y 3 categorías.
- Catálogo por tallas: hoodies y pantalones en S, M, L y XL; accesorios en talla única.
- Ficha de producto con selección de talla y cantidad.
- Carrito con validación de stock por talla.
- Registro e inicio de sesión con contraseñas almacenadas mediante bcrypt.
- Proceso de pago con 4 métodos y cálculo automático de IVA.
- Generación y envío de recibos en PDF.
- Panel administrativo con reportes, inventario, pedidos y mensajes.
- Control de inventario por talla, con reposición auditada desde el panel.
- Formulario de contacto almacenado en la base de datos.
- Aviso por correo al administrador cuando llega un mensaje de contacto.

### No incluido

- Pasarela de pago real; los métodos se registran, pero no se realiza el cobro.
- Integración con una empresa transportadora.
- Aplicación móvil nativa.
- Devoluciones y cambios de talla en línea.

## 7. Beneficiarios

| Actor | Beneficio |
|-------|-----------|
| Cliente | Puede comprar sin intermediarios, elegir su talla conociendo la disponibilidad real y recibir su comprobante |
| Administrador | Puede revisar ventas, controlar el stock de cada talla, reponer inventario y atender los mensajes recibidos |
| Marca | Mantiene un registro permanente de sus operaciones y mejora la organización del proceso de venta |