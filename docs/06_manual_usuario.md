# Manual de Usuario

**Red Goat Eyes — Tienda de ropa urbana**  
Versión 2.0 · Agosto 2026

---

## 1. Requisitos previos

Para ejecutar el proyecto se necesita:

| Componente | Versión mínima |
|------------|----------------|
| Python | 3.11 |
| PostgreSQL | 16 (el proyecto fue probado en 18) |
| Navegador | Chrome, Edge o Firefox actualizado |

### Instalación inicial

#### 1. Clonar el repositorio

```text
git clone https://github.com/niicofel/Red-Goat-Eyes-.git
cd Red-Goat-Eyes-
```

#### 2. Preparar Python

```text
python -m venv venv
venv\Scripts\activate
python -m pip install -r backend/requirements.txt
```

#### 3. Crear la base

La forma más rápida es ejecutar `database/setup.bat`, que corre los once scripts en el orden correcto y solicita la contraseña de `postgres`.

Si se prefiere hacerlo manualmente desde pgAdmin, utilizando una conexión como `postgres`, el orden es:

```text
00_create_database.sql
01_schema.sql
02_seed.sql
03_functions_triggers.sql
04_procedures.sql
05_views_reportes.sql
06_roles_permisos.sql
07_credenciales.sql
08_security_definer.sql
09_datos_demo.sql
```

`07_credenciales.sql` no se incluye con credenciales reales en el repositorio. Se debe copiar `07_credenciales.sql.example`, cambiar su nombre y configurar las contraseñas correspondientes.

El script `09_datos_demo.sql` deja el catálogo con las tallas S, M, L y XL para hoodies y pantalones, talla única para accesorios y 20 unidades por talla. También crea la cuenta administrativa inicial.

Al terminar se puede comprobar la instalación con:

```text
SELECT COUNT(*) FROM v_catalogo_publico;   -- deben ser 24
SELECT COUNT(*) FROM producto_talla;       -- deben ser 72
```

#### 4. Configurar las variables de entorno

Copiar `backend/.env.example` como `backend/.env` y completar las variables necesarias:

```text
DB_CLAVE=<contraseña del rol rge_flask>
DB_ADMIN_CLAVE=<contraseña del rol rge_panel>
SECRET_KEY=<cadena aleatoria larga>
SMTP_USUARIO=<correo de la tienda>
SMTP_CLAVE=<clave de aplicación de Gmail>
```

El archivo `.env` contiene información sensible y no debe subirse a Git.

## 2. Iniciar el sistema

Desde una terminal:

```text
cd backend
python run.py
```

Después se puede ingresar al sitio desde `http://127.0.0.1:5000/`.

Para comprobar la conexión de la API y la base se puede visitar `http://127.0.0.1:5000/api/salud`.

Para detener el servidor se utiliza `Ctrl + C`.

## 3. Uso como cliente

### 3.1 Consultar productos

Desde la página principal se puede ingresar por **Categorías** para elegir Hoodies, Pantalones o Accesorios, o abrir **Productos** para revisar los 24 artículos.

Cada tarjeta muestra la imagen, el nombre, el precio, una etiqueta con las unidades disponibles y las tallas existentes. Todos esos valores se obtienen desde la base de datos.

La etiqueta de stock indica el total del producto sumando sus tallas. Si un producto no tiene existencias, permanece visible pero aparece como **Agotado**.

### 3.2 Ver la ficha del producto

Al pulsar sobre una tarjeta o el botón **Ver detalles** se abre una ficha con:

- la imagen ampliada;
- la descripción completa;
- las tallas disponibles, cada una con su stock;
- un selector de cantidad.

Las tallas sin unidades aparecen deshabilitadas. Al elegir una talla, el sistema indica cuántas unidades quedan de esa talla en concreto.

Para cerrar la ficha se puede pulsar la equis, hacer clic fuera de ella o presionar la tecla Escape.

### 3.3 Agregar al carrito

Dentro de la ficha:

1. elegir la talla;
2. ajustar la cantidad con `−` y `+`;
3. pulsar **Añadir al carrito**.

El selector no permite superar el stock de la talla elegida e informa el motivo. Antes de agregar, el sistema vuelve a comprobar la disponibilidad contra el servidor.

El contador junto al icono del carrito se actualiza y aparece una confirmación.

> Cada talla se maneja como una línea independiente. Si se agrega el mismo hoodie en talla M y en talla L, el carrito mostrará dos líneas separadas.

### 3.4 Administrar el carrito

Dentro del carrito cada línea muestra el producto y su talla. Se puede:

- aumentar la cantidad con `+`;
- disminuirla con `−`;
- eliminar la línea.

También se presentan el subtotal, el IVA del 15 % y el total. Estos valores se calculan en el servidor.

### 3.5 Crear una cuenta

No es obligatorio registrarse para preparar el carrito, pero sí para continuar al pago.

Los datos solicitados son:

| Campo | Requisito |
|-------|-----------|
| Nombres | Mínimo 3 caracteres |
| Apellidos | Mínimo 3 caracteres |
| Cédula | 10 dígitos y validación ecuatoriana |
| Correo | Dirección válida donde se recibirá el comprobante |
| Teléfono | Entre 7 y 15 dígitos |
| Ciudad | Selección dentro de las 30 disponibles |
| Contraseña | Mínimo 8 caracteres |

Los mensajes de validación aparecen debajo del campo que contiene el problema.

> Conviene revisar el correo antes de enviar. Un error como escribir `.con` en lugar de `.com` impide que llegue el comprobante, y ningún sistema puede detectarlo porque ambas formas son válidas.

### 3.6 Iniciar sesión

Se ingresa el correo y la contraseña.

Si el inicio de sesión se solicitó al intentar pagar, después de autenticarse el usuario vuelve al proceso de pago sin perder el contenido del carrito.

### 3.7 Realizar el pedido

En la pantalla de pago:

1. se muestran el nombre y correo de la cuenta;
2. se ingresa una dirección de entrega de al menos 5 caracteres;
3. se puede escribir una referencia opcional;
4. se selecciona un método: transferencia bancaria, efectivo contra entrega, Deuna o tarjeta de crédito;
5. se marca la confirmación;
6. se presiona **Confirmar pago**.

El envío se registra con valor $0.00.

> Una cuenta administrativa no puede realizar compras. Si se intenta, el sistema indica que debe iniciarse sesión con una cuenta de cliente.

### 3.8 Comprobante

Después de confirmar se muestra una página con el código del pedido, sus productos con la talla comprada, subtotal, IVA, total, dirección y método de pago.

El código utiliza un formato como `RGE-2026-0001`.

También se intenta enviar al correo registrado un recibo en PDF. Si el envío del correo falla, la compra permanece registrada y el envío puede reintentarse.

### 3.9 Historial de pedidos

Con una sesión activa, el cliente puede consultar sus propios pedidos y revisar su estado.

La secuencia principal es:

`Pendiente → Pagado → En preparación → Enviado → Entregado`

Cada cliente puede consultar únicamente sus propias compras.

### 3.10 Contacto

El formulario de contacto solicita nombre, correo, ciudad, asunto y un mensaje de mínimo 10 caracteres.

Cuando existe una sesión activa, el nombre y correo se completan automáticamente.

El mensaje queda registrado en el sistema y además se envía un aviso al buzón de la tienda, de modo que el administrador pueda responderlo.

### 3.11 Cerrar sesión

Abrir el menú de usuario y seleccionar **Cerrar sesión**.

## 4. Uso como administrador

### 4.1 Acceso

Al iniciar sesión, una cuenta con rol de administrador es dirigida automáticamente al panel.

El menú de usuario muestra el rol de la sesión activa y una opción **Panel de administración**, disponible desde cualquier página del sitio. Esa opción solo aparece para cuentas administrativas.

Si una cuenta de cliente intenta abrir la dirección del panel directamente, las tablas se bloquean con un aviso y la API rechaza las consultas.

### 4.2 Indicadores generales

La pestaña **Reportes** comienza con cinco tarjetas que resumen productos activos, clientes registrados, pedidos, mensajes sin leer y alertas de stock.

La tarjeta de alertas cambia de color cuando existe al menos un producto en nivel crítico.

### 4.3 Reportes

El panel permite consultar ventas por categoría y un ranking de clientes. Los reportes muestran información como unidades vendidas, total de ventas, ciudad, cantidad de pedidos y ticket promedio.

El reporte de ventas puede filtrarse por período mediante los campos **Desde** y **Hasta**, pulsando después **Generar**.

### 4.4 Productos

Se muestran los 24 productos con su código, categoría, precio, stock total y estado.

### 4.5 Inventario y reposición

La pestaña **Inventario** muestra las 72 combinaciones de producto y talla, con su stock actual, el mínimo configurado y su estado.

| Estado | Significado |
|--------|-------------|
| Normal | Stock por encima del mínimo |
| Critico | Stock igual o menor al mínimo, fila resaltada en amarillo |
| Agotado | Sin unidades, fila resaltada en rojo |

El desplegable **Mostrar** permite filtrar por nivel crítico o agotados.

Para reponer stock:

1. pulsar **Reponer** en la fila correspondiente, con lo que el formulario se completa automáticamente;
2. o completar el formulario manualmente indicando código, talla y unidades;
3. pulsar **Reponer stock**.

El sistema confirma el stock resultante y actualiza la tabla y los indicadores. La operación requiere nivel 2 o superior y queda registrada en la auditoría con el administrador que la realizó.

### 4.6 Pedidos

El administrador puede revisar todos los pedidos registrados, incluyendo código, cliente, fecha, total y estado.

### 4.7 Mensajes

La tabla muestra la fecha, el remitente, su correo, la ciudad, el asunto y el estado, que puede ser **Pendiente**, **Leido** o **Respondido**.

Al pulsar cualquier fila se abre una ventana con el mensaje completo y un botón **Responder por correo**, que abre el gestor de correo con el destinatario y el asunto ya escritos.

Cada mensaje llega también al buzón de la tienda. Al responder ese correo, la respuesta va directamente al cliente.

### 4.8 Niveles administrativos

| Nivel | Permisos principales |
|-------|----------------------|
| 1 — Consulta | Catálogo, reportes, inventario y mensajes |
| 2 — Gestión | Incluye lo anterior y permite gestionar productos, reponer stock, cambiar estados de pedido y responder mensajes |
| 3 — Total | Incluye lo anterior y añade gestión de usuarios y auditoría |

### 4.9 Reintento de correos

Si existen correos pendientes, se puede ejecutar:

```text
cd backend
python enviar_correos.py
```

El proceso informa la cantidad de mensajes pendientes, enviados y fallidos.

### 4.10 Consultar los usuarios registrados

Desde pgAdmin:

```text
SELECT rol, COUNT(*) FROM v_usuario_seguro GROUP BY rol;

SELECT id_usuario, rol, email, nombres, apellidos, ciudad, activo, ultimo_acceso
FROM v_usuario_seguro
ORDER BY rol, id_usuario;
```

La vista `v_usuario_seguro` es la única forma de consultar usuarios desde la aplicación, ya que no expone el hash de contraseña.

## 5. Problemas frecuentes

### El sitio no abre

Comprobar que el servidor esté ejecutándose con `python run.py`.

### El navegador indica que no puede conectarse al servidor

Abrir el proyecto mediante `http://127.0.0.1:5000/` y no directamente como un archivo `file://`.

### Aparece un error de permisos

Comprobar que `database/08_security_definer.sql` haya sido ejecutado desde pgAdmin con una conexión de `postgres`.

### El catálogo muestra productos repetidos

Indica que la vista `v_catalogo_publico` no fue actualizada. Debe ejecutarse `database/05_views_reportes.sql` completo, que reemplaza la vista por su versión agrupada.

### No llega el comprobante

Revisar:

1. que el correo esté escrito correctamente;
2. la carpeta de spam;
3. el estado mediante `python enviar_correos.py`.

### La cédula no es aceptada

El sistema comprueba el dígito verificador ecuatoriano. Se debe utilizar una cédula válida y correctamente escrita.

### El sistema solicita iniciar sesión al pagar

La sesión puede haber expirado. Se debe iniciar sesión nuevamente; el carrito se conserva.

### No se puede completar una compra con la cuenta administrativa

Es el comportamiento esperado. Los pedidos se asocian a clientes, por lo que debe utilizarse una cuenta de cliente.

### Se olvidó una contraseña

Las contraseñas no pueden recuperarse porque se almacenan con bcrypt, que es irreversible. Debe generarse un hash nuevo y actualizarlo:

```text
cd backend
python -c "from app.services.auth_service import AuthService; print(AuthService().hashear('NuevaClave'))"
```

Después se actualiza en pgAdmin:

```text
UPDATE usuario SET password_hash = '<hash generado>' WHERE email = '<correo>';
```