# Seguridad y Protección de la Información

**Proyecto:** Red Goat Eyes  
**Asignatura:** Base de Datos I  
**Versión:** 2.0 · Agosto 2026

---

## 1. Principio principal

La aplicación no se conecta a PostgreSQL utilizando un superusuario. Cada parte del sistema trabaja únicamente con los permisos que necesita.

Esta decisión sigue el principio de mínimo privilegio: si una cuenta llegara a verse comprometida, su capacidad de acceder o modificar información estaría limitada por los permisos asignados.

## 2. Control de acceso

### 2.1 Roles utilizados

Se definieron 7 roles divididos en dos grupos.

**Roles que agrupan permisos**

| Rol | Función |
|-----|---------|
| `rge_app_read` | Lectura del catálogo público |
| `rge_app_write` | Escritura relacionada con pedidos, clientes y mensajes |
| `rge_admin` | Acceso a información administrativa y reportes |
| `rge_backup` | Lectura necesaria para respaldos |

**Roles utilizados para conectarse**

| Rol | Permisos heredados | Uso |
|-----|--------------------|-----|
| `rge_flask` | `rge_app_read` + `rge_app_write` | Aplicación web |
| `rge_panel` | `rge_admin` | Panel y reportes |
| `rge_respaldo` | `rge_backup` | Respaldos |

Separar los permisos de las cuentas de conexión permite administrar el acceso de una manera más ordenada. Agregar una cuarta cuenta de conexión no exige reescribir ningún `GRANT`: basta con concederle el rol de grupo correspondiente.

### 2.2 Acceso limitado a columnas

La aplicación no recibe permiso para consultar libremente toda la tabla `usuario`. Solo puede acceder a los campos que necesita para realizar determinadas operaciones.

Los datos de usuario destinados a consultas generales se obtienen mediante `v_usuario_seguro`, vista que no expone el hash de contraseña.

### 2.3 Comprobación de los permisos

Durante el desarrollo se verificaron los permisos utilizando los diferentes roles, con resultados que condicionaron el diseño del sistema.

| Operación | `rge_flask` | `rge_panel` |
|-----------|-------------|-------------|
| `SELECT * FROM usuario` | Denegado | Denegado |
| `SELECT * FROM v_usuario_seguro` | Permitido | Permitido |
| `INSERT INTO mensaje_contacto` | Permitido | — |
| `SELECT * FROM mensaje_contacto` | Denegado | Permitido |
| `SELECT * FROM rpt_top_clientes` | Denegado | Permitido |

La aplicación puede escribir mensajes de contacto pero no leerlos. Esta separación obligó a que el panel administrativo utilizara un segundo grupo de conexiones con el rol `rge_panel`, lo cual resultó ser la arquitectura correcta: fueron los permisos de la base de datos los que impusieron esa decisión.

Se detectó también un caso relacionado: la operación `INSERT ... RETURNING` requiere permiso de lectura sobre las columnas devueltas. Como `rge_flask` solo tiene permiso de escritura sobre `mensaje_contacto`, se eliminó la cláusula `RETURNING` del registro de mensajes, algo que además evita exponer identificadores internos hacia el exterior.

### 2.4 Autorización en diferentes niveles

Una solicitud a los reportes pasa por tres controles:

1. Flask comprueba mediante `@requiere_admin` que la sesión corresponda a un administrador.
2. La consulta utiliza la conexión asociada a `rge_panel`.
3. PostgreSQL verifica los permisos concedidos mediante `GRANT`.

Así, la autorización no depende únicamente de una comprobación en el frontend o en Flask.

La reposición de stock añade un cuarto control: el procedimiento `sp_reponer_stock` vuelve a consultar el `nivel_acceso` del administrador dentro de PostgreSQL y rechaza la operación si es inferior a 2, aunque Flask ya la hubiese autorizado.

## 3. Protección de credenciales

### 3.1 Contraseñas de usuarios

Las contraseñas se almacenan mediante bcrypt con 12 rondas. El valor original no se guarda en texto plano, no se escribe en los registros del servidor y tampoco se devuelve al navegador.

Bcrypt es una función de un solo sentido, por lo que una contraseña olvidada no puede recuperarse: únicamente puede restablecerse generando un hash nuevo. Aunque alguien obtuviera una copia completa de la base, no obtendría ninguna contraseña.

### 3.2 Credenciales de PostgreSQL

Durante el desarrollo se detectó que una versión inicial de `06_roles_permisos.sql` contenía contraseñas. Esto se corrigió separando las credenciales del archivo que se versiona.

Actualmente:

- `06_roles_permisos.sql` crea los roles sin incluir las contraseñas;
- `database/07_credenciales.sql` contiene las credenciales y está incluido en `.gitignore`;
- `07_credenciales.sql.example` funciona como plantilla sin información real.

Ambas plantillas fueron eliminadas por error en un commit posterior y se restauraron, ya que sin ellas no es posible configurar el proyecto en un equipo nuevo.

### 3.3 Variables sensibles

`backend/.env` almacena valores como la contraseña de la base, la clave de sesión y las credenciales utilizadas para el correo. Este archivo tampoco se sube al repositorio. En su lugar se mantiene `.env.example` como referencia de configuración.

Antes de cada commit se comprueba con `git check-ignore` que `backend/.env`, `database/07_credenciales.sql` y `venv/` continúen excluidos.

### 3.4 Sesiones

Las sesiones utilizan medidas como:

| Configuración | Propósito |
|---------------|-----------|
| `HttpOnly=True` | Evitar que JavaScript pueda leer directamente la cookie |
| `SameSite=Lax` | Reducir determinadas peticiones entre sitios |
| Duración limitada | Disminuir el tiempo útil de una sesión comprometida |

## 4. Calidad e integridad de los datos

### 4.1 Validación en varias capas

La información importante se revisa en más de un lugar.

| Dato | JavaScript | Python | PostgreSQL |
|------|-----------|--------|------------|
| Correo | Expresión regular | `validar_email()` | `CHECK` con expresión regular |
| Cédula | Longitud de 10 dígitos | Dígito verificador | `CHECK` de longitud |
| Contraseña | Mínimo 8 caracteres | `validar_password()` | Validación sobre el hash |
| Precio | — | `Decimal > 0` | `CHECK precio > 0` |
| Stock por talla | Tope del selector | `hay_stock()` | `CHECK stock >= 0` y trigger |
| Cantidad | — | `validar_cantidad()` | `CHECK cantidad > 0` |
| Reposición | — | Entre 1 y 1000 | `CHECK` dentro del procedimiento |

En total existen 56 restricciones `CHECK`, de las cuales 13 corresponden también a validaciones realizadas desde los formularios. Esto permite rechazar valores incorrectos incluso si una petición evita la interfaz web.

### 4.2 Integridad referencial

La base cuenta con:

- 24 claves foráneas;
- 19 restricciones `UNIQUE`;
- 56 restricciones `CHECK`;
- 21 índices.

Las reglas de eliminación dependen de cada relación:

| Relación | Regla | Motivo |
|----------|-------|--------|
| `pedido` → `cliente` | `RESTRICT` | Un cliente con ventas no debe borrarse: protege el historial |
| `detalle_pedido` → `pedido` | `CASCADE` | Una línea no existe sin su pedido |
| `direccion_envio` → `cliente` | `CASCADE` | Una dirección no existe sin su titular |
| `mensaje_contacto` → `cliente` | `SET NULL` | El mensaje se conserva, sin quedar vinculado |
| `detalle_pedido` → `producto_talla` | `RESTRICT` | Impide eliminar una talla que ya fue vendida |

La restricción `UNIQUE (id_producto, id_talla)` garantiza que no puedan existir dos registros de inventario para la misma combinación.

### 4.3 Triggers y procedimientos

Se utilizan 7 triggers para automatizar reglas importantes:

| Trigger | Función |
|---------|---------|
| `trg_validar_stock` | Comprueba existencias |
| `trg_ajustar_stock` | Ajusta el stock |
| `trg_recalcular_pedido` | Recalcula subtotal, IVA y total |
| `trg_devolver_stock_cancelacion` | Repone existencias al cancelar |
| `trg_auditar_producto` | Registra cambios de precio y stock |
| `trg_encolar_correo` | Agrega el recibo a la cola de envío |
| `trg_actualizar_carrito` | Actualiza la fecha de modificación |

También existen 4 procedimientos almacenados: `sp_registrar_cliente`, `sp_registrar_pedido`, `sp_cambiar_estado_pedido` y `sp_reponer_stock`.

Estas operaciones permiten concentrar procesos críticos en la base. Por ejemplo, el registro de un pedido se ejecuta como una operación transaccional para evitar que queden datos incompletos.

El uso de triggers responde a que la base puede recibir cambios desde fuera de la aplicación, ya sea mediante pgAdmin o un script de mantenimiento. Si el descuento de stock viviera únicamente en Python, cualquiera de esas vías dejaría el inventario incorrecto.

### 4.4 Valores monetarios

Para los valores económicos se utiliza `Decimal` en Python y `NUMERIC` en PostgreSQL en lugar de punto flotante.

Como prueba, con un subtotal de $105.00 las capas calculan $15.75 de IVA y un total de $120.75.

### 4.5 Coherencia entre el precio mostrado y el cobrado

Durante las pruebas se detectó que la vista SQL calculaba el precio aplicando únicamente el precio de oferta, mientras el cobro utilizaba `calcular_precio_final()` del modelo, que además aplica los recargos y descuentos propios de cada tipo de prenda. Siete de los veinticuatro productos mostraban un importe distinto al que se cobraba.

Se corrigió haciendo que el catálogo utilice también el método del modelo. De esta forma la regla de negocio queda definida en un solo lugar y no puede desincronizarse.

### 4.6 Auditoría

La tabla `auditoria` registra información sobre cambios en productos, incluyendo la operación, el usuario de base de datos que la ejecutó, los valores anteriores y nuevos en formato `JSONB` y la fecha correspondiente.

Cada reposición de stock realizada desde el panel queda registrada, junto con el administrador que la efectuó.

### 4.7 Reproducibilidad de la estructura

Los once scripts SQL numerados permiten reconstruir la base completa desde cero, y `setup.bat` los ejecuta en orden.

Todos son reejecutables. Esto exigió tener en cuenta dos limitaciones de PostgreSQL: `CREATE TRIGGER` no admite `OR REPLACE`, y `CREATE OR REPLACE VIEW` no permite cambiar los nombres, el orden ni los tipos de las columnas. En ambos casos se antepone `DROP ... IF EXISTS`, y en el caso de las vistas se vuelven a conceder los permisos, porque al eliminar una vista se pierden.

## 5. Uso de SECURITY DEFINER

`fn_trg_encolar_correo` necesita registrar datos en `envio_correo`, pero el rol normal de Flask no tiene permiso general de escritura sobre esa tabla.

En lugar de ampliar todos los privilegios de `rge_flask`, determinadas funciones se ejecutan mediante `SECURITY DEFINER`. De esta forma reciben permisos adicionales únicamente durante la operación concreta.

También se establece un `search_path` fijo para reducir el riesgo de que la función utilice objetos diferentes a los esperados.

Esta configuración se aplica a `fn_trg_encolar_correo`, `fn_trg_auditar_producto`, `sp_cambiar_estado_pedido` y `sp_reponer_stock`, y se encuentra en `database/08_security_definer.sql`, incluido en el proceso de instalación.

## 6. Seguridad de la aplicación

### 6.1 Inyección SQL

Las consultas utilizan parámetros en lugar de concatenar directamente la entrada del usuario:

```python
consultar_uno("SELECT * FROM producto WHERE codigo = %s", (codigo,))
```

De esta forma, `psycopg` trata los valores como datos y no como parte de la instrucción SQL.

### 6.2 XSS

Para mostrar información proporcionada por usuarios se utilizan métodos como `document.createElement()` y `textContent`. No se inserta contenido de usuario mediante `innerHTML`.

Esta regla es especialmente relevante en dos lugares donde el contenido proviene de terceros: la ficha de producto, que muestra nombre y descripción, y la ventana de mensajes del panel, que muestra el texto escrito por un visitante.

### 6.3 Errores

Los detalles técnicos se registran en el servidor, mientras que el navegador recibe mensajes más generales. Esto evita revelar innecesariamente nombres de tablas u otros detalles internos.

### 6.4 Acceso a recursos

No basta con comprobar el tipo de usuario. También se revisa que un cliente tenga permiso sobre el recurso solicitado. Por ejemplo, intentar consultar el pedido perteneciente a otro cliente produce una respuesta 403.

Del mismo modo, una cuenta administrativa no puede registrar pedidos, ya que la tabla `pedido` referencia a `cliente`. El servicio verifica el rol antes de procesar y responde 403 con un mensaje comprensible, en lugar de producir un error interno.

### 6.5 Recursos externos

Font Awesome utiliza el atributo `integrity` (SRI). El navegador puede verificar que el archivo recibido desde el CDN coincida con el recurso esperado.

## 7. Respaldos

La estrategia utiliza `pg_dump` en formato personalizado y `pg_restore` para la restauración.

El rol `rge_respaldo` posee permisos de solo lectura. De esta manera, el proceso de respaldo puede consultar la información sin modificarla accidentalmente.

Las imágenes no se incluyen en el respaldo de PostgreSQL porque forman parte del repositorio Git. El principio que guía la estrategia es que el código siempre puede recuperarse desde GitHub, mientras que los datos no.

Los roles y permisos se respaldan en un archivo aparte mediante `pg_dumpall --roles-only`, ya que `pg_dump` no los incluye: pertenecen al servidor y no a la base.

## 8. Resumen

Las principales medidas implementadas son:

- 7 roles de base de datos;
- permisos limitados por columna y vistas seguras;
- bcrypt con 12 rondas, irreversible por diseño;
- archivos `.env` y credenciales SQL fuera del repositorio;
- cookies configuradas con `HttpOnly` y `SameSite=Lax`;
- 56 `CHECK`, 24 claves foráneas, 19 `UNIQUE` y 21 índices;
- 7 triggers y 4 procedimientos, cuatro de ellos con `SECURITY DEFINER`;
- consultas parametrizadas y construcción del DOM sin `innerHTML`;
- precio calculado en un único lugar;
- auditoría de cambios y reposiciones;
- scripts reejecutables que reconstruyen la base completa;
- respaldo con un rol de solo lectura.