# Seguridad y Protección de la Información

**Proyecto:** Red Goat Eyes  
**Asignatura:** Base de Datos I  
**Versión:** 1.0 · Agosto 2026

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

Separar los permisos de las cuentas de conexión permite administrar el acceso de una manera más ordenada.

### 2.2 Acceso limitado a columnas

La aplicación no recibe permiso para consultar libremente toda la tabla `usuario`. Solo puede acceder a los campos que necesita para realizar determinadas operaciones.

Los datos de usuario destinados a consultas generales se obtienen mediante `v_usuario_seguro`, vista que no expone el hash de contraseña.

### 2.3 Comprobación de los permisos

Durante el desarrollo se verificaron los permisos utilizando los diferentes roles. Por ejemplo, `rge_flask` puede insertar mensajes de contacto, pero no leer la tabla completa de mensajes ni consultar los reportes administrativos. Para estas operaciones se utiliza `rge_panel`.

Esta separación hizo necesario manejar conexiones diferentes para la aplicación pública y para el panel administrativo.

### 2.4 Autorización en diferentes niveles

Una solicitud a los reportes pasa por tres controles:

1. Flask comprueba mediante `@requiere_admin` que la sesión corresponda a un administrador.
2. La consulta utiliza la conexión asociada a `rge_panel`.
3. PostgreSQL verifica los permisos concedidos mediante `GRANT`.

Así, la autorización no depende únicamente de una comprobación en el frontend o en Flask.

## 3. Protección de credenciales

### 3.1 Contraseñas de usuarios

Las contraseñas se almacenan mediante bcrypt con 12 rondas. El valor original no se guarda en texto plano, no se escribe en los registros del servidor y tampoco se devuelve al navegador.

### 3.2 Credenciales de PostgreSQL

Durante el desarrollo se detectó que una versión inicial de `06_roles_permisos.sql` contenía contraseñas. Esto se corrigió separando las credenciales del archivo que se versiona.

Actualmente:

- `06_roles_permisos.sql` crea los roles sin incluir las contraseñas;
- `database/07_credenciales.sql` contiene las credenciales y está incluido en `.gitignore`;
- `07_credenciales.sql.example` funciona como plantilla sin información real.

### 3.3 Variables sensibles

`backend/.env` almacena valores como la contraseña de la base, la clave de sesión y las credenciales utilizadas para el correo. Este archivo tampoco se sube al repositorio. En su lugar se mantiene `.env.example` como referencia de configuración.

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
| Stock | — | `hay_stock()` | `CHECK stock >= 0` y trigger |
| Cantidad | — | `validar_cantidad()` | `CHECK cantidad > 0` |

En total existen 56 restricciones `CHECK`, de las cuales 13 corresponden también a validaciones realizadas desde los formularios. Esto permite rechazar valores incorrectos incluso si una petición evita la interfaz web.

### 4.2 Integridad referencial

La base cuenta con:

- 24 claves foráneas;
- 19 restricciones `UNIQUE`;
- 56 restricciones `CHECK`;
- 21 índices.

Las reglas de eliminación dependen de cada relación. Por ejemplo, un cliente con pedidos no se elimina mediante cascada porque es necesario conservar el historial; en cambio, un detalle depende completamente de su pedido y puede utilizar `CASCADE`.

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

### 4.4 Valores monetarios

Para los valores económicos se utiliza `Decimal` en Python y `NUMERIC` en PostgreSQL en lugar de punto flotante.

Como prueba, con un subtotal de $105.00 las capas calculan $15.75 de IVA y un total de $120.75.

### 4.5 Auditoría

La tabla `auditoria` registra información sobre cambios en productos, incluyendo la operación, el usuario de base de datos que la ejecutó, los valores anteriores y nuevos en formato `JSONB` y la fecha correspondiente.

## 5. Uso de SECURITY DEFINER

`fn_trg_encolar_correo` necesita registrar datos en `envio_correo`, pero el rol normal de Flask no tiene permiso general de escritura sobre esa tabla.

En lugar de ampliar todos los privilegios de `rge_flask`, determinadas funciones se ejecutan mediante `SECURITY DEFINER`. De esta forma reciben permisos adicionales únicamente durante la operación concreta.

También se establece un `search_path` fijo para reducir el riesgo de que la función utilice objetos diferentes a los esperados.

Esta configuración se aplica a `fn_trg_encolar_correo`, `fn_trg_auditar_producto`, `sp_cambiar_estado_pedido` y `sp_reponer_stock`.

## 6. Seguridad de la aplicación

### 6.1 Inyección SQL

Las consultas utilizan parámetros en lugar de concatenar directamente la entrada del usuario:

```python
consultar_uno("SELECT * FROM producto WHERE codigo = %s", (codigo,))
```

De esta forma, `psycopg` trata los valores como datos y no como parte de la instrucción SQL.

### 6.2 XSS

Para mostrar información proporcionada por usuarios se utilizan métodos como `document.createElement()` y `textContent`. No se inserta contenido de usuario mediante `innerHTML`.

### 6.3 Errores

Los detalles técnicos se registran en el servidor, mientras que el navegador recibe mensajes más generales. Esto evita revelar innecesariamente nombres de tablas u otros detalles internos.

### 6.4 Acceso a recursos

No basta con comprobar el tipo de usuario. También se revisa que un cliente tenga permiso sobre el recurso solicitado. Por ejemplo, intentar consultar el pedido perteneciente a otro cliente produce una respuesta 403.

### 6.5 Recursos externos

Font Awesome utiliza el atributo `integrity` (SRI). El navegador puede verificar que el archivo recibido desde el CDN coincida con el recurso esperado.

## 7. Respaldos

La estrategia utiliza `pg_dump` en formato personalizado y `pg_restore` para la restauración.

El rol `rge_respaldo` posee permisos de solo lectura. De esta manera, el proceso de respaldo puede consultar la información sin modificarla accidentalmente.

Las imágenes no se incluyen en el respaldo de PostgreSQL porque forman parte del repositorio Git.

## 8. Resumen

Las principales medidas implementadas son:

- 7 roles de base de datos;
- permisos limitados y vistas seguras;
- bcrypt con 12 rondas;
- archivos `.env` y credenciales SQL fuera del repositorio;
- cookies configuradas con `HttpOnly` y `SameSite=Lax`;
- 56 `CHECK`, 24 claves foráneas, 19 `UNIQUE` y 21 índices;
- 7 triggers y 4 procedimientos;
- consultas parametrizadas;
- auditoría;
- respaldo con un rol de solo lectura.
