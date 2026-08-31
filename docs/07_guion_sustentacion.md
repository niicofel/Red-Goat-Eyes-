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

Muchas marcas pequeñas de ropa urbana manejan sus ventas por Instagram y mensajes directos. Cuando existen pocos pedidos puede funcionar, pero al aumentar las ventas aparecen problemas: el stock se vuelve difícil de controlar, no existe un historial organizado, el cliente no siempre recibe un comprobante y resulta complicado obtener información sobre qué productos o categorías venden más.

### Solución

Para responder a esos problemas desarrollamos Red Goat Eyes, una tienda en línea con 24 productos divididos entre hoodies, pantalones y accesorios. El cliente puede revisar el catálogo desde su teléfono, consultar disponibilidad, preparar su carrito y registrar un pedido. Cuando se confirma la compra, el pedido queda almacenado en PostgreSQL, se actualiza el inventario y se prepara un recibo PDF para enviarlo por correo.

### Qué destaca del proyecto

Una parte importante del proyecto es que las validaciones no dependen únicamente de JavaScript. También existen comprobaciones en Python y PostgreSQL. La base cuenta con 56 restricciones CHECK, 7 triggers y 4 procedimientos almacenados, por lo que varias reglas importantes continúan aplicándose aunque una petición no pase por la interfaz.

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
- endpoint `/api/productos` preparado en otra pestaña.

### 1. Catálogo y responsive

Mostrar la página principal y una categoría. Reducir el ancho de la ventana.

Explicación:

Diseñamos la interfaz para que también funcione correctamente en teléfonos. Tenemos cuatro puntos de quiebre: 992, 768, 600 y 480 píxeles. Por ejemplo, al reducir la pantalla el menú cambia a hamburguesa y la rejilla se adapta.

### 2. Información obtenida desde la API

Abrir `/api/productos`.

Explicación:

Estos son los datos que recibe el frontend. Los precios y la disponibilidad no están escritos directamente en las tarjetas HTML, sino que se obtienen desde el sistema y la base de datos.

### 3. Carrito y stock

Agregar productos e intentar superar la cantidad disponible.

Explicación:

El sistema vuelve a comprobar el stock antes de permitir determinadas cantidades. Esto evita registrar una compra con unidades que realmente no existen.

### 4. Inicio de sesión

Intentar continuar al pago sin una sesión.

Explicación:

Permitimos preparar el carrito sin una cuenta. La autenticación se solicita cuando el usuario quiere continuar al pago. Después de iniciar sesión puede regresar al mismo punto sin perder el carrito.

### 5. Validaciones

Ingresar una contraseña incorrecta.

Explicación:

Los mensajes se muestran debajo del campo correspondiente para que el usuario pueda identificar rápidamente qué debe corregir.

### 6. Pedido y recibo

Completar la información, confirmar el pedido y mostrar el código `RGE-2026-XXXX`. Después, revisar el correo y abrir el PDF recibido.

### 7. Base de datos

En pgAdmin:

```sql
SELECT codigo_pedido, total, id_estado
FROM pedido
ORDER BY id_pedido DESC
LIMIT 1;

SELECT destinatario, estado
FROM envio_correo
ORDER BY id_envio DESC
LIMIT 1;
```

Explicación:

Aquí podemos comprobar que el pedido quedó almacenado y también revisar el registro asociado al envío del correo.

### 8. Panel administrativo

Entrar con una cuenta administrativa y mostrar los reportes.

Explicación:

El panel permite consultar información que ayuda a analizar las ventas. Por ejemplo, uno de los reportes utiliza un CTE junto con `DENSE_RANK()` para generar un ranking.

### 9. Control de acceso

Entrar como cliente e intentar abrir `/api/reportes/ventas`.

Explicación:

El cliente recibe un 403 porque no tiene autorización. Además del control realizado por Flask, PostgreSQL también utiliza roles con permisos separados.

## PARTE 3 · POSIBLES PREGUNTAS

### Base de Datos

**¿Por qué guardaron subtotal, IVA y total si podrían calcularlos después?**

Porque necesitamos conservar los valores que correspondían al pedido cuando se realizó la compra. El precio de un producto puede cambiar posteriormente, pero un pedido ya registrado debe seguir mostrando los valores originales. Por eso también se conserva el `precio_unitario` de cada detalle.

**¿Qué normalización utilizaron?**

Trabajamos con tercera forma normal: las tablas tienen sus claves y los atributos dependen de la entidad que representan. Los valores monetarios guardados en `pedido` son una decisión específica para mantener el historial de la compra.

**¿Por qué utilizar triggers?**

Porque ciertas reglas deben cumplirse aunque el cambio no venga directamente desde Flask. Si una operación se realiza desde otra herramienta, el trigger sigue ejecutándose dentro de PostgreSQL.

**¿Cómo evitan un stock negativo?**

Lo comprobamos en varios niveles. PostgreSQL tiene `CHECK stock >= 0`, existe `trg_validar_stock` y Python también revisa la disponibilidad. Así no dependemos de una única validación.

**Explique un reporte.**

`rpt_top_clientes` primero agrupa las compras de cada cliente mediante un CTE. Después utiliza `DENSE_RANK()` para asignar una posición y `CASE` para clasificar al cliente según su número de pedidos.

### Programación Orientada a Objetos

**¿Dónde existe polimorfismo?**

Un ejemplo está en `calcular_precio_final()`. `Producto` define el comportamiento general y cada tipo de producto lo implementa según su regla. Un `Hoodie` con gramaje de 400 o más añade 10 %, un `Pantalon` Carpenter añade 5 % y un `Accesorio` de más de 70 dólares aplica 5 % de descuento.

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

**¿Cómo adaptaron el sitio a móviles?**

Utilizamos cuatro puntos de quiebre. Debajo de 768 px aparece el menú hamburguesa y debajo de 480 px la rejilla pasa a una sola columna. También se revisó la interfaz a 375 px.

**¿Qué hicieron por accesibilidad?**

Utilizamos HTML semántico, texto alternativo en las imágenes, `aria-label` en controles que lo necesitan y `label` asociados a los campos de formularios.

### Arquitectura y seguridad

**¿Por qué Flask envía el correo y no PostgreSQL?**

PostgreSQL se encarga de registrar que el correo debe enviarse mediante `trg_encolar_correo`. Flask toma ese registro y realiza el envío hacia Gmail. De esta forma, la base controla el estado del proceso y la aplicación se encarga de la comunicación externa.

**¿Qué ocurre si falla el correo?**

El pedido permanece registrado. El correo queda pendiente y puede reintentarse con `python enviar_correos.py`. Después de cinco intentos puede quedar marcado como fallido.

**¿Por qué existen dos conexiones principales a la base?**

Porque la aplicación pública utiliza `rge_flask`, que tiene permisos limitados. Para operaciones administrativas y reportes se utiliza `rge_panel`. Esto evita entregar permisos administrativos a toda la aplicación.

**¿Cómo se almacenan las contraseñas?**

Se utiliza bcrypt con 12 rondas. No se guarda la contraseña original en texto plano. Además, las credenciales de conexión están en `backend/.env`, archivo excluido mediante `.gitignore`.

**¿Cómo utilizaron Git?**

El desarrollo se organizó mediante ramas de funcionalidad y Pull Requests hacia `main`. La fase de backend se trabajó en `feature/backend-flask` con commits separados y posteriormente se integró conservando el historial de la rama.

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
| Triggers | 7 |
| Procedimientos almacenados | 4 |
| Reportes | 4 |
| Roles de base de datos | 7 |
| Clases del dominio | 15 |
| Endpoints de la API | 24 |
| Productos | 24 |
| Páginas HTML | 13 |
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
