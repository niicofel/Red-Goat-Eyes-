# Especificación de Requerimientos

**Proyecto:** Red Goat Eyes — Tienda de ropa urbana  
**Versión:** 1.0 · Agosto 2026

---

## 1. Requerimientos funcionales

### RF-01 · Catálogo de productos

El sistema debe presentar únicamente los productos que se encuentren activos. Para cada producto se muestra su nombre, precio, imagen, disponibilidad y stock.

El usuario puede consultar todo el catálogo o aplicar una categoría y un texto de búsqueda. Esta funcionalidad se encuentra implementada mediante `GET /api/productos` y la vista `v_catalogo_publico`.

### RF-02 · Búsqueda y filtrado

El catálogo permite buscar productos por nombre, descripción o código. También se puede filtrar por las categorías `hoodies`, `pantalones` y `accesorios`.

La API utiliza los parámetros `?categoria=` y `?q=` para recibir estos filtros.

### RF-03 · Carrito de compras

El usuario puede agregar productos, cambiar las cantidades y eliminar artículos del carrito.

Para mantener los datos correctos se aplican las siguientes reglas:

- no se permite solicitar una cantidad mayor al stock disponible;
- los precios utilizados se consultan desde la base de datos y no se confía en un precio enviado por el navegador;
- el carrito se conserva entre visitas dentro del navegador.

Esta funcionalidad utiliza `assets/js/carrito.js` y el endpoint `GET /api/productos/disponibilidad/<id>`.

### RF-04 · Registro de usuarios

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

### RF-05 · Autenticación

El sistema compara las credenciales ingresadas con el hash bcrypt almacenado. Si los datos son correctos, crea una sesión con duración limitada y actualiza la fecha del último acceso.

Endpoint utilizado: `POST /api/auth/login`.

### RF-06 · Cálculo de totales

El servidor calcula los valores del pedido para evitar que puedan ser modificados desde el navegador.

| Concepto | Cálculo |
|----------|---------|
| Subtotal | Suma del precio final por la cantidad de cada producto |
| IVA | Subtotal × 0.15 |
| Envío | 0.00 |
| Total | Subtotal + IVA |

Esta operación se encuentra en `POST /api/pedidos/calcular`.

### RF-07 · Registro del pedido

Para registrar un pedido, el usuario debe estar autenticado y su carrito debe contener productos.

El sistema recibe los artículos, correo, dirección y método de pago. Antes de confirmar verifica nuevamente el stock, conserva el precio unitario utilizado en ese momento y descuenta las existencias correspondientes.

Como resultado se genera un código con el formato `RGE-AAAA-NNNN`.

Implementación: `POST /api/pedidos` y procedimiento `sp_registrar_pedido`.

### RF-08 · Envío del recibo

Después de confirmar el pedido, se genera un comprobante PDF que se envía al correo del cliente.

El proceso de correo se ejecuta de forma separada del registro de la venta. Por ello, si existe un problema al enviar el mensaje, el pedido no se pierde: queda registrado y el correo puede volver a intentarse.

Participan `correo_service.py`, `pdf_service.py` y el trigger `trg_encolar_correo`.

### RF-09 · Estados del pedido

El sistema maneja diferentes estados para representar el avance de una compra y permitir que tanto el cliente como el administrador puedan conocer su situación actual.


```
Pendiente → Pagado → En preparación → Enviado → Entregado
     ↓         ↓            ↓
             Cancelado
```

El sistema rechaza cualquier transición que no siga este orden. Cuando un pedido se cancela, el stock de sus productos se devuelve automáticamente al inventario.

Participan el procedimiento `sp_cambiar_estado_pedido` y el trigger `trg_devolver_stock_cancelacion`.

### RF-10 · Consulta de pedidos propios

El cliente puede revisar el historial de sus compras junto con el estado actual de cada una.

Por seguridad, un cliente no puede consultar el pedido de otra persona: el sistema responde con un error de permiso denegado.

Implementado en `GET /api/pedidos/mios` y `GET /api/pedidos/<codigo>`.

### RF-11 · Formulario de contacto

Cualquier visitante puede escribir a la tienda indicando nombre, correo, ciudad, asunto y el detalle de su mensaje.

Los asuntos disponibles son Consulta, Reclamo y Sugerencia. La descripción debe tener al menos 10 caracteres. Si el visitante tiene sesión abierta, el mensaje queda vinculado a su cuenta de cliente.

Implementado en `POST /api/contacto`.

### RF-12 · Panel administrativo

El panel está reservado para usuarios con rol de administrador y reúne cinco tablas: ventas por categoría, ranking de clientes, inventario de productos, listado de pedidos y buzón de mensajes.

Implementado en `pages/admin.html` y `assets/js/admin.js`.

### RF-13 · Reportes

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
- "Stock insuficiente para 'COBALT BLOOM': se solicitan 500 unidades y solo hay 2"
- "El correo o la contraseña no son correctos."

### RNF-03 · Seguridad

| Medida | Implementación |
|--------|----------------|
| Contraseñas | bcrypt con 12 rondas, nunca almacenadas en texto plano |
| Acceso a datos | 7 roles de PostgreSQL con permisos a nivel de columna |
| Credenciales | Fuera del repositorio, en `backend/.env` ignorado por Git |
| Sesiones | Cookie con `HttpOnly` y `SameSite=Lax` |
| Autorización | Verificada en tres capas: Flask, rol de conexión y permisos del motor |

### RNF-04 · Integridad de datos

| Mecanismo | Cantidad |
|-----------|----------|
| Restricciones `CHECK` | 56 |
| Claves foráneas | 24 |
| Restricciones `UNIQUE` | 19 |
| Índices | 21 |
| Triggers | 7 |
| Procedimientos almacenados | 4 |

De las 56 restricciones `CHECK`, trece replican exactamente una validación que también existe en el formulario. Si alguien envía datos sin pasar por el navegador, la base de datos los rechaza igualmente.

### RNF-05 · Precisión monetaria

Todos los montos se manejan con el tipo `Decimal` en Python y `NUMERIC` en PostgreSQL. No se utiliza punto flotante para representar dinero, ya que introduce errores de redondeo. El redondeo aplicado es `ROUND_HALF_UP` a dos decimales.

### RNF-06 · Rendimiento

Las conexiones a la base de datos se administran mediante un pool configurado entre 1 y 10 conexiones. Un segundo pool independiente atiende las consultas del panel administrativo utilizando un rol con menores privilegios.

### RNF-07 · Respaldo

El proyecto incluye los scripts `backup.bat` y `restaurar.bat`, que utilizan `pg_dump` y `pg_restore` ejecutados con un rol dedicado de solo lectura. La estrategia completa está documentada en `database/backup/estrategia_respaldo.md`.

### RNF-08 · Mantenibilidad

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
| RN-09 | Solo un administrador de nivel 2 o superior puede cambiar el estado de un pedido |
| RN-10 | El precio unitario del detalle se congela al momento de realizar la compra |
| RN-11 | Un pedido cancelado devuelve automáticamente el stock al inventario |
| RN-12 | Un cliente únicamente puede consultar sus propios pedidos |

---

## 4. Actores del sistema

| Actor | Permisos |
|-------|----------|
| **Visitante** | Ver el catálogo, buscar productos, armar el carrito, enviar mensajes de contacto y registrarse |
| **Cliente** | Todo lo anterior, además de iniciar sesión, administrar sus direcciones, realizar pedidos y consultar su historial |
| **Administrador nivel 1** | Consultar el catálogo, los reportes y los mensajes |
| **Administrador nivel 2** | Lo anterior, además de gestionar productos, reponer stock, cambiar estados de pedido y responder mensajes |
| **Administrador nivel 3** | Lo anterior, además de gestionar usuarios y consultar la auditoría |
