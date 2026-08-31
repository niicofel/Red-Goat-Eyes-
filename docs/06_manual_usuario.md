# Manual de Usuario

**Red Goat Eyes — Tienda de ropa urbana**  
Versión 1.0 · Agosto 2026

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

Desde pgAdmin y utilizando una conexión como `postgres`, ejecutar los archivos de `database/` en el siguiente orden:

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
```

`07_credenciales.sql` no se incluye con credenciales reales en el repositorio. Se debe copiar `07_credenciales.sql.example`, cambiar su nombre y configurar las contraseñas correspondientes.

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

Cada tarjeta muestra la imagen, el nombre y el precio. Los valores se obtienen desde la base de datos.

Si un producto no tiene existencias, permanece visible pero aparece como **Agotado**.

### 3.2 Agregar al carrito

Para añadir un artículo se presiona **Agregar al carrito**. El sistema muestra una confirmación y actualiza el contador situado junto al icono del carrito.

Antes de aceptar la cantidad se comprueba el stock disponible.

### 3.3 Administrar el carrito

Dentro del carrito se puede:

- aumentar la cantidad con `+`;
- disminuirla con `−`;
- eliminar el producto.

También se presentan el subtotal, el IVA del 15 % y el total. Estos valores se calculan en el servidor.

### 3.4 Crear una cuenta

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

### 3.5 Iniciar sesión

Se ingresa el correo y la contraseña.

Si el inicio de sesión se solicitó al intentar pagar, después de autenticarse el usuario vuelve al proceso de pago sin perder el contenido del carrito.

### 3.6 Realizar el pedido

En la pantalla de pago:

1. se muestran el nombre y correo de la cuenta;
2. se ingresa una dirección de entrega de al menos 5 caracteres;
3. se puede escribir una referencia opcional;
4. se selecciona un método: transferencia bancaria, efectivo contra entrega, Deuna o tarjeta de crédito;
5. se marca la confirmación;
6. se presiona **Confirmar pago**.

El envío se registra con valor $0.00.

### 3.7 Comprobante

Después de confirmar se muestra una página con el código del pedido, sus productos, subtotal, IVA, total, dirección y método de pago.

El código utiliza un formato como `RGE-2026-0001`.

También se intenta enviar al correo registrado un recibo en PDF. Si el envío del correo falla, la compra permanece registrada y el envío puede reintentarse.

### 3.8 Historial de pedidos

Con una sesión activa, el cliente puede consultar sus propios pedidos y revisar su estado.

La secuencia principal es:

`Pendiente → Pagado → En preparación → Enviado → Entregado`

Cada cliente puede consultar únicamente sus propias compras.

### 3.9 Contacto

El formulario de contacto solicita nombre, correo, ciudad, asunto y un mensaje de mínimo 10 caracteres.

Cuando existe una sesión activa, el nombre y correo pueden completarse automáticamente.

### 3.10 Cerrar sesión

Abrir el menú de usuario y seleccionar **Cerrar sesión**.

## 4. Uso como administrador

### 4.1 Acceso

Una cuenta con rol de administrador es dirigida al panel correspondiente. Las cuentas de cliente no tienen acceso a la información administrativa.

### 4.2 Reportes

El panel permite consultar ventas por categoría y un ranking de clientes. Los reportes pueden mostrar información como unidades vendidas, total de ventas, ciudad, cantidad de pedidos y ticket promedio.

### 4.3 Productos

Se muestran los 24 productos con su código, categoría, precio, stock y estado.

### 4.4 Pedidos

El administrador puede revisar los pedidos registrados, incluyendo código, cliente, fecha, total y estado.

### 4.5 Mensajes

Los mensajes recibidos mediante el formulario de contacto pueden aparecer como **Pendiente**, **Leído** o **Respondido**.

### 4.6 Niveles administrativos

| Nivel | Permisos principales |
|-------|----------------------|
| 1 — Consulta | Catálogo, reportes y mensajes |
| 2 — Gestión | Incluye lo anterior y permite gestionar productos, stock, pedidos y respuestas |
| 3 — Total | Incluye lo anterior y añade gestión de usuarios y auditoría |

### 4.7 Reintento de correos

Si existen correos pendientes, se puede ejecutar:

```text
cd backend
python enviar_correos.py
```

El proceso informa la cantidad de mensajes pendientes, enviados y fallidos.

## 5. Problemas frecuentes

### El sitio no abre

Comprobar que el servidor esté ejecutándose con `python run.py`.

### El navegador indica que no puede conectarse al servidor

Abrir el proyecto mediante `http://127.0.0.1:5000/` y no directamente como un archivo `file://`.

### Aparece un error de permisos

Comprobar que `database/08_security_definer.sql` haya sido ejecutado desde pgAdmin con los permisos necesarios.

### No llega el comprobante

Revisar:

1. que el correo esté escrito correctamente;
2. la carpeta de spam;
3. el estado mediante `python enviar_correos.py`.

### La cédula no es aceptada

El sistema comprueba el dígito verificador ecuatoriano. Se debe utilizar una cédula válida y correctamente escrita.

### El sistema solicita iniciar sesión al pagar

La sesión puede haber expirado. Se debe iniciar sesión nuevamente; el carrito se conserva.
