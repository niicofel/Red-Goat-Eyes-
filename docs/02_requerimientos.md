# Especificación de Requerimientos

**Proyecto:** Red Goat Eyes — Tienda de ropa urbana  
**Versión:** 2.0 · Agosto 2026

---

## 1. Requerimientos funcionales

### RF-01 · Catálogo de productos

El sistema debe presentar únicamente los productos que se encuentren activos. Para cada producto se muestra su nombre, precio, imagen, stock total y las tallas disponibles.

El inventario se guarda por combinación de producto y talla, por lo que la vista `v_catalogo_publico` agrupa esas filas para devolver un registro por producto, con el stock sumado de todas sus tallas.

El usuario puede consultar todo el catálogo o aplicar una categoría y un texto de búsqueda. Esta funcionalidad se encuentra implementada mediante `GET /api/productos`.

### RF-02 · Búsqueda y filtrado

El catálogo permite buscar productos por nombre, descripción o código. También se puede filtrar por las categorías `hoodies`, `pantalones` y `accesorios`.

La API utiliza los parámetros `?categoria=` y `?q=` para recibir estos filtros.

### RF-03 · Ficha de producto

Al pulsar una tarjeta se abre una ficha que muestra la imagen, la descripción, cada talla con su stock individual y un selector de cantidad.

Las tallas sin unidades aparecen deshabilitadas. El selector de cantidad no permite superar el stock de la talla elegida.

Implementado en `GET /api/productos/<codigo>` y `assets/js/catalogo.js`.

### RF-04 · Carrito de compras

El usuario puede agregar productos, cambiar las cantidades y eliminar artículos del carrito.

Para mantener los datos correctos se aplican las siguientes reglas:

- cada combinación de producto y talla se maneja como una línea independiente;
- no se permite solicitar una cantidad mayor al stock de esa talla;
- los precios utilizados se consultan desde la base de datos y no se confía en un precio enviado por el navegador;
- el carrito se conserva entre visitas dentro del navegador.

Esta funcionalidad utiliza `assets/js/carrito.js` y el endpoint `GET /api/productos/disponibilidad/<id>`.

### RF-05 · Registro de usuarios

Para crear una cuenta se validan los siguientes datos:

| Campo | Validación |
|-------|------------|
| Nombres | Mínimo 3 caracteres |
| Apellidos | Mínimo 3 caracteres |
| Cédula | 10 dígitos y dígito verificador ecuatoriano válido |
| Correo | Formato válido y valor único |
| Teléfono | Entre 7 y 15 dígitos |
| Ciudad | Debe pertenecer al catálogo de 30 ciudades |
| Contraseña | Mínimo 8 caracteres y almacenamiento mediante bcrypt |

El registro se procesa mediante `POST /api/auth/registro` y `sp_registrar_cliente`.

### RF-06 · Autenticación

El sistema compara las credenciales ingresadas con el hash bcrypt almacenado. Si los datos son correctos, crea una sesión con duración limitada y actualiza la fecha del último acceso.

Al iniciar sesión, un administrador es dirigido al panel y un cliente al catálogo o a la pantalla de pago, según de dónde provenga.

Endpoint utilizado: `POST /api/auth/login`.

### RF-07 · Cálculo de totales

El servidor calcula los valores del pedido para evitar que puedan ser modificados desde el navegador.

| Concepto | Cálculo |
|----------|---------|
| Subtotal | Suma del precio final por la cantidad de cada línea |
| IVA | Subtotal × 0.15 |
| Envío | 0.00 |
| Total | Subtotal + IVA |

El precio final se obtiene siempre del método `calcular_precio_final()` del modelo, de modo que el valor mostrado en la tarjeta, en la ficha y en el cobro coincide en los 24 productos.

Esta operación se encuentra en `POST /api/pedidos/calcular`.

### RF-08 · Registro del pedido

Para registrar un pedido, el usuario debe estar autenticado con una cuenta de cliente y su carrito debe contener productos.

El sistema recibe los artículos, correo, dirección y método de pago. Antes de confirmar verifica nuevamente el stock de cada talla, conserva el precio unitario utilizado en ese momento y descuenta las existencias correspondientes.

Como resultado se genera un código con el formato `RGE-AAAA-NNNN`.

Implementación: `POST /api/pedidos` y procedimiento `sp_registrar_pedido`.

### RF-09 · Restricción de compra para administradores

Una cuenta administrativa no puede registrar pedidos, porque la tabla `pedido` referencia a `cliente` y un administrador no lo es.

El servicio comprueba el rol antes de procesar y responde con un error 403 acompañado de un mensaje que indica iniciar sesión con una cuenta de cliente.

### RF-10 · Envío del recibo

Después de confirmar el pedido, se genera un comprobante PDF que se envía al correo del cliente.

El proceso de correo se ejecuta de forma separada del registro de la venta. Por ello, si existe un problema al enviar el mensaje, el pedido no se pierde: queda registrado y el correo puede volver a intentarse.

Participan `correo_service.py`, `pdf_service.py` y el trigger `trg_encolar_correo`.

### RF-11 · Estados del pedido

El sistema maneja diferentes estados para representar el avance de una compra y permitir que tanto el cliente como el administrador puedan conocer su situación actual.

```
Pendiente → Pagado → En preparación → Enviado → Entregado
     ↓         ↓            ↓
             Cancelado
```

El sistema rechaza cualquier transición que no siga este orden. Cuando un pedido se cancela, el stock de sus productos se devuelve automáticamente al inventario.

Participan el procedimiento `sp_cambiar_estado_pedido` y el trigger `trg_devolver_stock_cancelacion`.

### RF-12 · Consulta de pedidos propios

El cliente puede revisar el historial de sus compras junto con el estado actual de cada una.

Por seguridad, un cliente no puede consultar el pedido de otra persona: el sistema responde con un error de permiso denegado.

Implementado en `GET /api/pedidos/mios` y `GET /api/pedidos/<codigo>`.

### RF-13 · Formulario de contacto

Cualquier visitante puede escribir a la tienda indicando nombre, correo, ciudad, asunto y el detalle de su mensaje.

Los asuntos disponibles son Consulta, Reclamo y Sugerencia. La descripción debe tener al menos 10 caracteres. Si el visitante tiene sesión abierta, el mensaje queda vinculado a su cuenta de cliente.

Implementado en `POST /api/contacto`.

### RF-14 · Aviso de mensajes al administrador

Al enviarse el formulario, además de guardarse en la base de datos se remite un correo al buzón de la tienda con los datos del remitente y el texto completo.

El correo incluye la cabecera `Reply-To` con la dirección del cliente, de modo que al responder la contestación llega directamente a él.

El envío ocurre en segundo plano: si el correo falla, el mensaje queda guardado igualmente y visible en el panel.

Implementado en `correo_service.notificar_mensaje_contacto()`.

### RF-15 · Panel administrativo

El panel está reservado para usuarios con rol de administrador y se organiza en cinco pestañas:

| Pestaña | Contenido |
|---------|-----------|
| Reportes | Indicadores generales, ventas por categoría y ranking de clientes |
| Productos | Los 24 productos con su precio y stock total |
| Inventario | Las 72 combinaciones de producto y talla, con formulario de reposición |
| Pedidos | Todos los pedidos registrados en el sistema |
| Mensajes | Buzón de contacto; al pulsar una fila se abre el mensaje completo |

El acceso al panel aparece en el menú de usuario únicamente cuando la sesión pertenece a un administrador, y se agrega desde JavaScript en las trece páginas.

Implementado en `pages/admin.html` y `assets/js/admin.js`.

### RF-16 · Reposición de stock

| Campo | Detalle |
|-------|---------|
| Precondición | Administrador de nivel 2 o superior |
| Entrada | Código de producto, talla y unidades a agregar |
| Salida | Stock resultante de esa combinación |
| Regla 1 | La cantidad debe estar entre 1 y 1000 |
| Regla 2 | El procedimiento vuelve a verificar el nivel de acceso dentro de PostgreSQL |
| Regla 3 | La operación queda registrada en la tabla de auditoría |

El inventario puede filtrarse para mostrar solo las combinaciones en nivel crítico o agotadas.

Implementado en `GET /api/productos/inventario`, `POST /api/productos/reponer` y el procedimiento `sp_reponer_stock`.

### RF-17 · Reportes

Se implementaron cuatro reportes que combinan varias tablas mediante consultas complejas.

| Reporte | Técnica SQL utilizada |
|---------|----------------------|
| Ventas por categoría | `RANK() OVER` en una función con parámetros de fecha |
| Ranking de clientes | CTE con `DENSE_RANK()` y segmentación mediante `CASE` |
| Stock crítico | Subconsulta correlacionada sobre la demanda de los últimos 30 días |
| Mensajes de contacto | Agregación con la cláusula `FILTER` |

Definidos en `database/05_views_reportes.sql` y expuestos en `GET /api/reportes/*`.

---

## 2. Requerimientos no funcionales

### RNF-01 · Diseño adaptable

La interfaz se ajusta a cuatro puntos de quiebre según el ancho del dispositivo.

| Ancho | Comportamiento |
|-------|----------------|
| ≤ 992 px | La rejilla de productos pasa a dos columnas |
| ≤ 768 px | Aparece el menú hamburguesa y la navegación se colapsa |
| ≤ 600 px | Los formularios se muestran en una sola columna |
| ≤ 480 px | Rejilla de una columna y tipografía reducida |

Se verificó el funcionamiento a 375 píxeles sin desbordamiento horizontal.

### RNF-02 · Mensajes de error comprensibles

Cada error se muestra debajo del campo que lo origina, redactado en español y en lenguaje natural. Los mensajes generados por el servidor se trasladan al formulario correspondiente.

Algunos ejemplos reales del sistema:

- "La cédula debe tener exactamente 10 dígitos."
- "Solo quedan 20 unidades de esa talla"
- "Stock insuficiente para 'COBALT BLOOM': se solicitan 500 unidades y solo hay 2"
- "No tiene permisos para realizar compras con una cuenta administrativa. Inicie sesion con una cuenta de cliente"

### RNF-03 · Seguridad

| Medida | Implementación |
|--------|----------------|
| Contraseñas | bcrypt con 12 rondas, nunca almacenadas en texto plano |
| Acceso a datos | 7 roles de PostgreSQL con permisos a nivel de columna |
| Credenciales | Fuera del repositorio, en `backend/.env` ignorado por Git |
| Sesiones | Cookie con `HttpOnly` y `SameSite=Lax` |
| Autorización | Verificada en tres capas: Flask, rol de conexión y permisos del motor |
| Construcción del DOM | Se emplea `textContent`, nunca `innerHTML` con datos del usuario |

### RNF-04 · Integridad de datos

| Mecanismo | Cantidad |
|-----------|----------|
| Restricciones `CHECK` | 56 |
| Claves foráneas | 24 |
| Restricciones `UNIQUE` | 19 |
| Índices | 21 |
| Triggers | 7 |
| Procedimientos almacenados | 4 |
| Combinaciones producto-talla | 72 |

De las 56 restricciones `CHECK`, trece replican exactamente una validación que también existe en el formulario. Si alguien envía datos sin pasar por el navegador, la base de datos los rechaza igualmente.

### RNF-05 · Precisión monetaria

Todos los montos se manejan con el tipo `Decimal` en Python y `NUMERIC` en PostgreSQL. No se utiliza punto flotante para representar dinero, ya que introduce errores de redondeo. El redondeo aplicado es `ROUND_HALF_UP` a dos decimales.

### RNF-06 · Coherencia de precios

El precio se calcula en un único lugar: el método `calcular_precio_final()` de cada subclase de `Producto`. El catálogo, la ficha de producto y el cobro utilizan ese mismo método, de modo que el importe mostrado y el cobrado siempre coinciden.

### RNF-07 · Rendimiento

Las conexiones a la base de datos se administran mediante un pool configurado entre 1 y 10 conexiones. Un segundo pool independiente atiende las consultas del panel administrativo utilizando un rol con menores privilegios.

### RNF-08 · Respaldo

El proyecto incluye los scripts `backup.bat` y `restaurar.bat`, que utilizan `pg_dump` y `pg_restore` ejecutados con un rol dedicado de solo lectura. La estrategia completa está documentada en `database/backup/estrategia_respaldo.md`.

### RNF-09 · Reproducibilidad

Los once scripts SQL numerados permiten reconstruir la base completa desde cero. El archivo `setup.bat` los ejecuta en orden. Todos son reejecutables gracias al uso de `DROP ... IF EXISTS` antes de crear vistas y triggers.

### RNF-10 · Mantenibilidad

El backend está organizado en cuatro capas, cada una con una responsabilidad definida:

```
routes → services → repositories → PostgreSQL
```

El CSS se dividió en cuatro archivos según su función. Los nombres de variables, funciones y tablas se mantienen en español de forma consistente en todo el proyecto.

---

## 3. Reglas de negocio

| ID | Regla |
|----|-------|
| RN-01 | El IVA aplicado es del 15%, vigente en Ecuador |
| RN-02 | El envío es gratuito para todos los pedidos |
| RN-03 | Un hoodie con gramaje igual o superior a 400 gsm tiene un recargo del 10% |
| RN-04 | Un pantalón de corte Carpenter o Workwear tiene un recargo del 5% |
| RN-05 | Un accesorio con precio igual o superior a $70 recibe un descuento del 5% |
| RN-06 | El precio de oferta debe ser menor que el precio de lista |
| RN-07 | El stock no puede quedar en valores negativos |
| RN-08 | Un producto cuyo stock sea igual o menor al mínimo se marca en nivel crítico |
| RN-09 | Solo un administrador de nivel 2 o superior puede cambiar el estado de un pedido o reponer stock |
| RN-10 | El precio unitario del detalle se congela al momento de realizar la compra |
| RN-11 | Un pedido cancelado devuelve automáticamente el stock al inventario |
| RN-12 | Un cliente únicamente puede consultar sus propios pedidos |
| RN-13 | Hoodies y pantalones se venden en tallas S, M, L y XL; los accesorios en talla única |
| RN-14 | El stock se controla por combinación de producto y talla, no por producto |
| RN-15 | El precio mostrado y el cobrado se calculan con el mismo método del modelo |
| RN-16 | Una cuenta administrativa no puede realizar compras |
| RN-17 | Una reposición no puede superar las 1000 unidades por operación |

---

## 4. Actores del sistema

| Actor | Permisos |
|-------|----------|
| **Visitante** | Ver el catálogo, consultar la ficha de producto, armar el carrito, enviar mensajes de contacto y registrarse |
| **Cliente** | Todo lo anterior, además de iniciar sesión, administrar sus direcciones, realizar pedidos y consultar su historial |
| **Administrador nivel 1** | Consultar el catálogo, los reportes, el inventario y los mensajes |
| **Administrador nivel 2** | Lo anterior, además de gestionar productos, reponer stock, cambiar estados de pedido y responder mensajes |
| **Administrador nivel 3** | Lo anterior, además de gestionar usuarios y consultar la auditoría |