# Guion de Sustentación

**Red Goat Eyes — Proyecto Integrador de Segundo Nivel**  
PUCE TEC · Agosto 2026

**Equipo:** Felipe Nicolás Campos Cisneros · Elian Emanuel Valenzuela Álvarez · Rafael Chiriboga

---

## Estructura de la defensa

| Parte | Duración aproximada | Puntos |
|-------|---------------------|--------|
| Presentación de la idea | 2–3 min | 5 |
| Demostración | 5–7 min | 5 |
| Preguntas teóricas | 5 min | 10 |
| **Total** | **~15 min** | **20** |

## PARTE 1 · Presentación de la idea

### Problema

Muchas marcas pequeñas de ropa urbana manejan sus ventas por Instagram y mensajes directos. Cuando existen pocos pedidos puede funcionar, pero al aumentar las ventas aparecen problemas: el stock se vuelve difícil de controlar, especialmente cuando una prenda existe en varias tallas; no existe un historial organizado; el cliente no siempre recibe un comprobante; y resulta complicado obtener información sobre qué productos o categorías venden más.

### Solución

Para responder a esos problemas desarrollamos Red Goat Eyes, una tienda en línea con 24 productos divididos entre hoodies, pantalones y accesorios, gestionados en 72 combinaciones de producto y talla. El cliente puede revisar el catálogo desde su teléfono, abrir la ficha de una prenda, elegir su talla conociendo las unidades disponibles, preparar su carrito y registrar un pedido. Cuando se confirma la compra, el pedido queda almacenado en PostgreSQL, se descuenta el inventario de esa talla concreta y se prepara un recibo PDF para enviarlo por correo.

### Qué destaca del proyecto

Una parte importante del proyecto es que las validaciones no dependen únicamente de JavaScript. También existen comprobaciones en Python y PostgreSQL. La base cuenta con 56 restricciones CHECK, 7 triggers y 4 procedimientos almacenados, por lo que varias reglas importantes continúan aplicándose aunque una petición no pase por la interfaz.

El administrador cuenta además con un panel donde revisa indicadores, controla el inventario talla por talla, repone stock de forma auditada y lee los mensajes recibidos.

### Cierre

El resultado es un sistema funcional que integra Desarrollo Web, Programación Orientada a Objetos y Base de Datos dentro de un mismo proceso de compra.

## PARTE 2 · Demostración

### Antes de empezar

Comprobar:

- PostgreSQL activo;
- `python run.py` ejecutándose;
- pgAdmin abierto en `red_goat_eyes`;
- sitio abierto en `http://127.0.0.1:5000/`;
- correo abierto;
- endpoint `/api/productos` preparado en otra pestaña;
- **una cuenta de cliente registrada** y al menos dos compras realizadas, para que los reportes tengan datos.

### 1. Catálogo y responsive

Mostrar la página principal y una categoría. Reducir el ancho de la ventana.

Explicación:

Diseñamos la interfaz para que también funcione correctamente en teléfonos. Tenemos cuatro puntos de quiebre: 992, 768, 600 y 480 píxeles. Por ejemplo, al reducir la pantalla el menú cambia a hamburguesa y la rejilla se adapta.

Cada tarjeta muestra una etiqueta con las unidades disponibles y las tallas existentes, de modo que el usuario decide si abrir la ficha sin necesidad de hacerlo.

### 2. Información obtenida desde la API

Abrir `/api/productos`.

Explicación:

Estos son los datos que recibe el frontend. Los precios, la disponibilidad y las tallas no están escritos directamente en las tarjetas HTML, sino que se obtienen desde el sistema y la base de datos.

### 3. Ficha de producto y selección de talla

Pulsar una tarjeta para abrir la ficha. Mostrar las tallas con su stock y pulsar `+` hasta alcanzar el límite.

Explicación:

Al manejar varias tallas por producto, un botón directo de agregar al carrito dejaría de tener sentido, porque el sistema no puede saber qué talla quiere el usuario. La ficha resuelve esa elección sin salir del catálogo. El selector de cantidad se detiene en el stock de la talla seleccionada y explica por qué.

### 4. Carrito con tallas separadas

Agregar el mismo producto en dos tallas distintas y abrir el carrito.

Explicación:

Cada combinación de producto y talla se maneja como una línea independiente, porque su inventario también es independiente. Los totales los calcula el servidor, no el navegador.

### 5. Inicio de sesión

Intentar continuar al pago sin una sesión.

Explicación:

Permitimos preparar el carrito sin una cuenta. La autenticación se solicita cuando el usuario quiere continuar al pago. Después de iniciar sesión puede regresar al mismo punto sin perder el carrito.

### 6. Validaciones

Ingresar una contraseña incorrecta.

Explicación:

Los mensajes se muestran debajo del campo correspondiente para que el usuario pueda identificar rápidamente qué debe corregir.

### 7. Pedido y recibo

Completar la información, confirmar el pedido y mostrar el código `RGE-2026-XXXX` junto con las tallas compradas. Después, revisar el correo y abrir el PDF recibido.

### 8. Base de datos

En pgAdmin:

```sql
SELECT codigo_pedido, total, id_estado
FROM pedido
ORDER BY id_pedido DESC
LIMIT 1;

SELECT p.codigo, t.codigo AS talla, pt.stock
FROM producto_talla pt
JOIN producto p ON p.id_producto = pt.id_producto
JOIN talla t ON t.id_talla = pt.id_talla
WHERE p.codigo = 'RGE-HOO-001'
ORDER BY t.orden;

SELECT destinatario, estado
FROM envio_correo
ORDER BY id_envio DESC
LIMIT 1;
```

Explicación:

Aquí comprobamos que el pedido quedó almacenado, que el descuento de stock afectó únicamente a la talla comprada y que existe el registro asociado al envío del correo.

### 9. Panel administrativo

Entrar con una cuenta administrativa. Señalar el enlace del menú de usuario, los indicadores y los reportes.

Explicación:

El acceso al panel aparece únicamente cuando la sesión es administrativa. Los indicadores resumen el estado del negocio, y los reportes ayudan a analizar las ventas. Por ejemplo, el ranking de clientes utiliza un CTE junto con `DENSE_RANK()`.

### 10. Inventario y reposición

Abrir la pestaña **Inventario**, pulsar **Reponer** en una fila y confirmar.

Explicación:

Aquí vemos las 72 combinaciones de producto y talla. Al reponer, el procedimiento `sp_reponer_stock` vuelve a verificar dentro de PostgreSQL que el administrador tenga nivel suficiente y registra la operación en la auditoría. No basta con que Flask lo autorice.

### 11. Mensajes de contacto

Abrir la pestaña **Mensajes** y pulsar una fila.

Explicación:

El mensaje se guarda en la base y además llega al correo de la tienda con la cabecera `Reply-To` del cliente, de modo que al responder ese correo la respuesta le llega directamente a él.

### 12. Control de acceso

Entrar como cliente e intentar abrir `/api/reportes/ventas`. Intentar también comprar con la cuenta administrativa.

Explicación:

El cliente recibe un 403 porque no tiene autorización. Además del control realizado por Flask, PostgreSQL también utiliza roles con permisos separados. Y una cuenta administrativa no puede comprar, porque los pedidos se asocian a clientes.

## PARTE 3 · POSIBLES PREGUNTAS

### Base de Datos

**¿Por qué guardaron subtotal, IVA y total si podrían calcularlos después?**

Porque necesitamos conservar los valores que correspondían al pedido cuando se realizó la compra. El precio de un producto puede cambiar posteriormente, pero un pedido ya registrado debe seguir mostrando los valores originales. Por eso también se conserva el `precio_unitario` de cada detalle.

**¿Qué normalización utilizaron?**

Trabajamos con tercera forma normal: las tablas tienen sus claves y los atributos dependen de la entidad que representan. Los valores monetarios guardados en `pedido` son una decisión específica para mantener el historial de la compra.

**¿Cómo modelaron las tallas?**

Mediante la tabla `producto_talla`, que relaciona un producto con una talla y guarda el stock de esa combinación concreta. Es una tabla puente con una restricción `UNIQUE (id_producto, id_talla)`.

Gracias a ese diseño, ampliar el catálogo de talla única a cuatro tallas no requirió modificar ninguna tabla: bastó con agregar filas.

**¿Por qué la vista del catálogo agrupa por producto?**

Porque `producto_talla` guarda una fila por cada combinación. Con cuatro tallas, un `JOIN` directo devolvería 72 filas y el catálogo mostraría el mismo hoodie cuatro veces. La vista agrupa por producto, suma el stock con `SUM()` y arma la lista de tallas con `STRING_AGG`, de modo que el frontend recibe 24 productos con su stock total y sus tallas disponibles.

**¿Por qué utilizar triggers?**

Porque ciertas reglas deben cumplirse aunque el cambio no venga directamente desde Flask. Si una operación se realiza desde otra herramienta, el trigger sigue ejecutándose dentro de PostgreSQL.

**¿Cómo evitan un stock negativo?**

Lo comprobamos en varios niveles. PostgreSQL tiene `CHECK stock >= 0`, existe `trg_validar_stock` y Python también revisa la disponibilidad. Así no dependemos de una única validación.

**Explique un reporte.**

`rpt_top_clientes` primero agrupa las compras de cada cliente mediante un CTE. Después utiliza `DENSE_RANK()` para asignar una posición y `CASE` para clasificar al cliente según su número de pedidos.

**¿Sus scripts se pueden volver a ejecutar?**

Sí. Los once scripts son reejecutables. Para lograrlo tuvimos en cuenta dos limitaciones de PostgreSQL: `CREATE TRIGGER` no admite `OR REPLACE`, y `CREATE OR REPLACE VIEW` no permite cambiar nombres ni orden de columnas. En ambos casos anteponemos `DROP ... IF EXISTS`, y en las vistas volvemos a conceder los permisos, porque al eliminarlas se pierden.

### Programación Orientada a Objetos

**¿Dónde existe polimorfismo?**

Un ejemplo está en `calcular_precio_final()`. `Producto` define el comportamiento general y cada tipo de producto lo implementa según su regla. Un `Hoodie` con gramaje de 400 o más añade 10 %, un `Pantalon` Carpenter añade 5 % y un `Accesorio` de más de 70 dólares aplica 5 % de descuento.

**Encontraron un error relacionado con eso. ¿Cuál era?**

La tarjeta del catálogo tomaba el precio de la vista SQL, que solo aplica el precio de oferta, mientras que el cobro usaba `calcular_precio_final()`, que además aplica los recargos. Siete de veinticuatro productos mostraban un precio y cobraban otro: un hoodie premium se anunciaba en 35 dólares y se cobraba 38,50.

Lo corregimos haciendo que el catálogo también use el método del modelo. La regla de negocio queda en un solo lugar, que es justamente donde está el polimorfismo, y no puede desincronizarse.

**¿Cómo utilizaron encapsulamiento?**

Los atributos se controlan mediante propiedades y setters. Por ejemplo, el precio se convierte a `Decimal` y no se acepta un valor menor o igual a cero. También se comprueba que un precio de oferta sea menor que el precio normal.

**¿Cuándo utilizaron herencia y cuándo composición?**

Utilizamos herencia cuando una clase realmente representa un tipo de otra: un `Hoodie` es un `Producto` y un `Cliente` es una `Persona`.

Usamos composición cuando un objeto contiene otros que forman parte de él. Un `Pedido`, por ejemplo, contiene `DetallePedido`.

**¿Por qué Decimal y no float?**

Porque `float` puede introducir pequeñas diferencias al representar números decimales. Para dinero necesitamos valores más precisos, por eso usamos `Decimal` en Python y `NUMERIC` en PostgreSQL.

**¿Para qué sirve Repository?**

Sirve para separar las consultas y el acceso a la base de datos de la lógica principal. Los servicios utilizan los repositorios en lugar de colocar SQL directamente en las rutas.

### Desarrollo Web / UX

**¿Por qué se puede preparar el carrito sin registrarse?**

Porque quisimos evitar pedir información al usuario antes de que realmente quiera comprar. La cuenta se solicita al continuar al pago y después el sistema puede devolverlo al mismo punto.

**¿Por qué una ficha emergente en lugar de una página de producto?**

Porque el usuario no pierde el contexto del catálogo. Con varias tallas necesitábamos un espacio donde elegir talla y cantidad, pero abrir una página independiente obligaría a volver atrás para seguir mirando.

**¿Cómo adaptaron el sitio a móviles?**

Utilizamos cuatro puntos de quiebre. Debajo de 768 px aparece el menú hamburguesa y debajo de 480 px la rejilla pasa a una sola columna. También se revisó la interfaz a 375 px.

**¿Qué hicieron por accesibilidad?**

Utilizamos HTML semántico, texto alternativo en las imágenes, `aria-label` en controles que lo necesitan y `label` asociados a los campos de formularios. La ficha y el menú se cierran con Escape.

**¿Por qué construyen el HTML desde JavaScript con `createElement`?**

Porque el nombre de un producto o el texto de un mensaje de contacto son datos, no marcado. Si los insertáramos con `innerHTML`, un texto que contuviera etiquetas se ejecutaría en el navegador. Con `textContent` se muestran como texto, que es lo correcto.

### Arquitectura y seguridad

**¿Por qué Flask envía el correo y no PostgreSQL?**

PostgreSQL se encarga de registrar que el correo debe enviarse mediante `trg_encolar_correo`. Flask toma ese registro y realiza el envío hacia Gmail. De esta forma, la base controla el estado del proceso y la aplicación se encarga de la comunicación externa.

**¿Qué ocurre si falla el correo?**

El pedido permanece registrado. El correo queda pendiente y puede reintentarse con `python enviar_correos.py`. Después de cinco intentos puede quedar marcado como fallido.

**¿Por qué existen dos conexiones principales a la base?**

Porque la aplicación pública utiliza `rge_flask`, que tiene permisos limitados. Para operaciones administrativas y reportes se utiliza `rge_panel`. Esto evita entregar permisos administrativos a toda la aplicación.

Fue una decisión que impusieron los propios permisos: descubrimos que `rge_flask` podía escribir mensajes de contacto pero no leerlos, lo cual es correcto, y eso obligó a que el panel usara otra conexión.

**¿Por qué un administrador no puede comprar?**

Porque la tabla `pedido` tiene una clave foránea hacia `cliente`, y un administrador no es un cliente. Antes esto producía un error interno; ahora el servicio comprueba el rol antes de procesar y responde 403 con un mensaje que indica iniciar sesión con una cuenta de cliente.

**¿Cómo se almacenan las contraseñas?**

Se utiliza bcrypt con 12 rondas. No se guarda la contraseña original en texto plano. Además, las credenciales de conexión están en `backend/.env`, archivo excluido mediante `.gitignore`.

**¿Cómo recuperan una contraseña olvidada?**

No se recupera, se restablece. Bcrypt es irreversible por diseño, así que generamos un hash nuevo y lo reemplazamos. Aunque alguien robara la base completa, no obtendría ninguna contraseña.

**¿Cómo utilizaron Git?**

El desarrollo se organizó mediante ramas de funcionalidad y Pull Requests hacia `main`. Cada fase se trabajó en su propia rama con commits separados por tema, y se integró mediante un merge sin *fast-forward* para que la rama quede visible en el historial.

## Reglas para responder durante la defensa

- Si conoces la respuesta, contesta primero la idea principal y después explica el ejemplo.
- Si no recuerdas un dato exacto, no inventes. Indica que no tienes presente la cifra o el archivo exacto.
- Si el evaluador realiza una corrección válida, acéptala y continúa.
- Si preguntan por una función que quedó fuera del alcance, explica que no fue incluida en el alcance definido.

## Datos importantes

| Concepto | Cantidad |
|----------|----------|
| Tablas | 21 |
| Restricciones CHECK | 56 |
| Claves foráneas | 24 |
| Restricciones UNIQUE | 19 |
| Índices | 21 |
| Triggers | 7 |
| Procedimientos almacenados | 4 |
| Reportes | 4 |
| Roles de base de datos | 7 |
| Scripts SQL | 11 |
| Clases del dominio | 15 |
| Endpoints de la API | 31 |
| Productos | 24 |
| Combinaciones producto-talla | 72 |
| Páginas HTML | 13 |
| Archivos JavaScript | 9 |
| Puntos responsive | 4 |
| IVA | 15 % |

## Reparto sugerido

| Parte | Responsable |
|-------|-------------|
| Presentación inicial | Rafael |
| Demostración frontend y UX | Elian |
| Demostración backend y base de datos | Felipe |
| Preguntas de Base de Datos | Felipe |
| Preguntas de POO | Felipe |
| Preguntas de UX/UI | Elian |