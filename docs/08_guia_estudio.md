# Guía de Estudio Definitiva

**Red Goat Eyes — Proyecto Integrador de Segundo Nivel**
PUCE TEC · Septiembre 2026

Este documento explica **todo** el proyecto: qué hace cada archivo, cómo funciona
cada pieza y por qué se tomó cada decisión. Está pensado para memorizar el sistema
completo antes de la defensa.

---

## ÍNDICE

1. [Visión general](#1-visión-general)
2. [Arquitectura](#2-arquitectura)
3. [Base de datos](#3-base-de-datos)
4. [Programación Orientada a Objetos](#4-programación-orientada-a-objetos)
5. [Backend](#5-backend)
6. [Frontend](#6-frontend)
7. [Flujos completos](#7-flujos-completos)
8. [Errores encontrados y cómo se resolvieron](#8-errores-encontrados)
9. [Preguntas y respuestas](#9-preguntas-y-respuestas)

---

# 1. VISIÓN GENERAL

## Qué es

Una tienda en línea de ropa urbana con 24 productos en 3 categorías (Hoodies,
Pantalones, Accesorios). Los hoodies y pantalones se venden en 4 tallas (S, M, L,
XL) y los accesorios en talla única, lo que da **72 combinaciones de producto y
talla**, cada una con su propio stock.

## Qué resuelve

Las marcas pequeñas venden por Instagram y mensajes directos. Eso funciona con
pocos pedidos, pero se rompe cuando crecen:

| Problema | Cómo lo resuelve el sistema |
|----------|----------------------------|
| No se sabe cuánto stock queda de cada talla | Tabla `producto_talla` con stock por combinación |
| No queda historial de ventas | Tablas `pedido` y `detalle_pedido` |
| El cliente no recibe comprobante | Recibo PDF enviado por correo |
| El IVA se calcula a mano | 15 % aplicado en las tres capas |
| No se sabe en qué va el pedido | Máquina de estados de 6 pasos |
| Las consultas se pierden | Formulario de contacto guardado y avisado por correo |

## Cifras que hay que saber de memoria

| Concepto | Cantidad |
|----------|----------|
| Tablas | 21 |
| Restricciones CHECK | 56 (13 replican validaciones del formulario) |
| Claves foráneas | 24 |
| Restricciones UNIQUE | 19 |
| Índices | 21 |
| Triggers | 7 |
| Procedimientos almacenados | 4 |
| Reportes | 4 |
| Vistas | 6 |
| Roles de base de datos | 7 |
| Scripts SQL | 11 |
| Clases del dominio | 15 |
| Endpoints de la API | 31 |
| Productos | 24 |
| Combinaciones producto-talla | 72 |
| Páginas HTML | 13 |
| Archivos CSS | 4 |
| Archivos JavaScript | 9 |
| Archivos Python | 51 |
| Puntos de quiebre responsive | 4 (992, 768, 600, 480) |
| IVA | 15 % |

---

# 2. ARQUITECTURA

## Las tres capas

```
NAVEGADOR              SERVIDOR                    BASE DE DATOS
HTML + CSS + JS   →    Python + Flask         →    PostgreSQL 18
(presentación)         (lógica de negocio)         (datos e integridad)
```

## Las cuatro capas del backend

Esta es la parte que más preguntan. El backend no es un archivo con todo dentro,
sino cuatro capas donde cada una hace **una sola cosa**:

```
routes/         Reciben la petición HTTP y comprueban permisos
    ↓
services/       Aplican las reglas del negocio
    ↓
repositories/   Traducen entre objetos de Python y SQL
    ↓
PostgreSQL      Guarda y garantiza la integridad
```

**Regla de oro:** una capa solo habla con la de abajo. Una ruta nunca escribe SQL;
un repositorio nunca decide reglas de negocio.

### Ejemplo concreto: agregar un producto al carrito

```
1. catalogo.js llama a  GET /api/productos/disponibilidad/96?cantidad=3
2. productos_bp.py      recibe la petición
3. producto_service.py  llama a verificar_disponibilidad()
4. producto_repository  ejecuta  SELECT fn_verificar_stock(96, 3)
5. PostgreSQL           responde TRUE o FALSE
```

## Por qué esta separación

- Si mañana cambiamos de PostgreSQL a otro motor, **solo se tocan los repositorios**.
- Si cambia una regla de negocio (por ejemplo el IVA), **solo se toca el servicio**.
- Las rutas quedan cortas y fáciles de leer.

---

# 3. BASE DE DATOS

## 3.1 Los 11 scripts y para qué sirve cada uno

| Script | Qué hace |
|--------|----------|
| `00_create_database.sql` | Crea la base `red_goat_eyes` con codificación UTF-8 |
| `01_schema.sql` | Crea las 21 tablas con sus restricciones e índices |
| `02_seed.sql` | Carga provincias, ciudades, categorías, tallas y los 24 productos |
| `03_functions_triggers.sql` | Crea 3 funciones de utilidad y los 7 triggers |
| `04_procedures.sql` | Crea los 4 procedimientos almacenados |
| `05_views_reportes.sql` | Crea las 6 vistas y las funciones de reporte |
| `06_roles_permisos.sql` | Crea los 7 roles y concede los permisos |
| `07_credenciales.sql` | Asigna las contraseñas (**no se sube a Git**) |
| `08_security_definer.sql` | Eleva privilegios de 4 objetos concretos |
| `09_datos_demo.sql` | Deja el catálogo por tallas y crea el administrador |
| `99_drop_all.sql` | Borra todo, para reinstalar desde cero |

`setup.bat` los ejecuta en orden.

### Por qué el orden importa

`09_datos_demo.sql` empieza borrando los pedidos. Esto no es capricho: la clave
foránea `detalle_pedido → producto_talla` es `RESTRICT`, así que no se pueden
eliminar las filas de talla única si existen pedidos que las referencian.

## 3.2 Las 21 tablas

### Catálogo geográfico

| Tabla | Para qué |
|-------|----------|
| `provincia` | Las 24 provincias del Ecuador |
| `ciudad` | 30 ciudades, cada una pertenece a una provincia |

### Catálogo de productos

| Tabla | Para qué |
|-------|----------|
| `categoria` | Hoodies, Pantalones, Accesorios. Tiene `slug` para las URLs |
| `talla` | XS, S, M, L, XL, XXL y U (única). El campo `orden` sirve para ordenarlas |
| `producto` | Los 24 productos: código, nombre, descripción, precio, material, género |
| `producto_talla` | **Tabla puente.** Une producto con talla y guarda el `stock` |
| `imagen_producto` | Imágenes adicionales con su texto alternativo |

> **`producto_talla` es la tabla más importante del catálogo.** El stock no vive
> en `producto`, vive aquí. Un hoodie con 4 tallas tiene 4 filas, cada una con su
> stock independiente. La restricción `UNIQUE (id_producto, id_talla)` impide
> duplicados.

### Usuarios

| Tabla | Para qué |
|-------|----------|
| `usuario` | Credenciales: email, `password_hash`, rol, activo |
| `cliente` | Datos del cliente. Su PK **es también** FK hacia `usuario` |
| `administrador` | Cargo y `nivel_acceso` (1 a 3). Misma relación 1:1 |
| `direccion_envio` | Direcciones de cada cliente |

> Esto se llama **especialización**. `usuario` guarda lo común (credenciales) y
> `cliente`/`administrador` lo específico. Es la forma relacional de representar
> la herencia que en Python es `Persona → Cliente / Administrador`.

### Pedidos

| Tabla | Para qué |
|-------|----------|
| `estado_pedido` | Los 6 estados con su `orden` |
| `metodo_pago` | Transferencia, efectivo, Deuna, tarjeta |
| `pedido` | Cabecera: código, cliente, dirección, estado, subtotal, IVA, total |
| `detalle_pedido` | Una fila por línea: producto_talla, cantidad, precio congelado |
| `carrito` | Carrito guardado del cliente |
| `carrito_item` | Líneas del carrito |

### Contacto y control

| Tabla | Para qué |
|-------|----------|
| `asunto_contacto` | Consulta, Reclamo, Sugerencia |
| `mensaje_contacto` | Los mensajes del formulario |
| `auditoria` | Registro de cambios en productos, en formato JSONB |
| `envio_correo` | Cola de correos pendientes de enviar |

## 3.3 Normalización

El modelo está en **tercera forma normal (3FN)**:

- **1FN:** no hay campos multivaluados. Por eso las tallas están en su propia
  tabla y no como un texto `"S,M,L,XL"` dentro de `producto`.
- **2FN:** todos los atributos dependen de la clave completa. En `producto_talla`,
  el stock depende de producto **y** talla juntos, no de uno solo.
- **3FN:** no hay dependencias transitivas. La provincia no se repite en `ciudad`
  como texto, se referencia por su ID.

### La desnormalización deliberada

`pedido` guarda `subtotal`, `iva` y `total`, que **podrían calcularse** sumando
sus detalles. Esto rompe 3FN a propósito.

**Por qué:** el precio de un producto puede cambiar mañana. Si recalculáramos el
total de un pedido antiguo, cambiaría un documento ya emitido. Guardamos los
montos y además congelamos `precio_unitario` en cada detalle, de modo que el
pedido conserva las condiciones del día de la compra.

Es la respuesta correcta cuando pregunten "¿por qué guardan datos calculados?".

## 3.4 Las reglas de borrado

Cada clave foránea tiene una regla elegida según el **significado** del dato:

| Relación | Regla | Por qué |
|----------|-------|---------|
| `pedido` → `cliente` | `RESTRICT` | Un cliente con ventas no se borra: protege el historial |
| `detalle_pedido` → `pedido` | `CASCADE` | Una línea no existe sin su pedido |
| `detalle_pedido` → `producto_talla` | `RESTRICT` | No se borra una talla que ya fue vendida |
| `direccion_envio` → `cliente` | `CASCADE` | Una dirección no existe sin su titular |
| `cliente` → `usuario` | `CASCADE` | Borrar la cuenta borra el perfil |
| `mensaje_contacto` → `cliente` | `SET NULL` | El mensaje sobrevive, anonimizado |
| `envio_correo` → `pedido` | `CASCADE` | La cola no tiene sentido sin el pedido |

## 3.5 Las 3 funciones de utilidad

| Función | Qué hace |
|---------|----------|
| `fn_tasa_iva()` | Devuelve 0.15. Centraliza el IVA en un solo lugar |
| `fn_verificar_stock(id_producto_talla, cantidad)` | Devuelve TRUE si hay unidades suficientes |
| `fn_calcular_total_pedido(id_pedido)` | Suma los detalles de un pedido |

## 3.6 Los 7 triggers

Un trigger es código que PostgreSQL ejecuta **automáticamente** cuando ocurre algo
en una tabla. Nadie los llama: se disparan solos.

| Trigger | Cuándo salta | Qué hace |
|---------|--------------|----------|
| `trg_validar_stock` | Antes de insertar en `detalle_pedido` | Rechaza la línea si no hay stock |
| `trg_ajustar_stock` | Después de INSERT/UPDATE/DELETE en `detalle_pedido` | Descuenta o devuelve unidades |
| `trg_recalcular_pedido` | Después de cambiar `detalle_pedido` | Recalcula subtotal, IVA y total |
| `trg_devolver_stock_cancelacion` | Al cambiar el estado de un pedido | Repone el stock si se canceló |
| `trg_auditar_producto` | Al cambiar precio o stock | Escribe en `auditoria` |
| `trg_encolar_correo` | Cuando el pedido pasa a Pagado | Inserta en `envio_correo` |
| `trg_actualizar_carrito` | Al cambiar `carrito_item` | Actualiza la fecha del carrito |

### Por qué triggers y no código Python

Porque la base puede recibir cambios desde fuera de la aplicación: pgAdmin, un
script de migración, otra herramienta. Si el descuento de stock viviera solo en
Python, cualquiera de esas vías dejaría el inventario mal. El trigger garantiza la
regla **sin importar quién escriba**.

### Dato importante sobre `trg_ajustar_stock`

Se dispara también en `DELETE`. Por eso, cuando se borra un pedido, el stock
**vuelve solo**. No hay que ajustarlo a mano.

## 3.7 Los 4 procedimientos almacenados

| Procedimiento | Parámetros | Qué hace |
|---------------|-----------|----------|
| `sp_registrar_cliente` | datos del cliente | Crea `usuario` + `cliente` en una transacción |
| `sp_registrar_pedido` | cliente, dirección, método, items (JSONB) | Crea el pedido y sus detalles; devuelve el código |
| `sp_cambiar_estado_pedido` | código, nuevo estado, administrador | Valida la transición y cambia el estado |
| `sp_reponer_stock` | código producto, talla, cantidad, administrador | Suma unidades y audita |

### Por qué procedimientos

Un pedido toca tres tablas: `pedido`, `detalle_pedido` y (por trigger)
`producto_talla`. Si eso se hiciera con tres llamadas separadas desde Python y
fallara la segunda, quedaría un pedido a medias. El procedimiento lo ejecuta
**como una sola transacción**: o se hace todo, o no se hace nada.

### `sp_reponer_stock` valida dos veces

Aunque Flask ya comprobó que el usuario es administrador, el procedimiento vuelve
a consultar su `nivel_acceso` dentro de PostgreSQL y rechaza la operación si es
menor que 2. Si alguien saltara el control de Flask, la base lo para igual.

## 3.8 Las 6 vistas

| Vista | Para qué |
|-------|----------|
| `v_catalogo_publico` | El catálogo que consume el frontend |
| `v_usuario_seguro` | Datos de usuario **sin** el hash de contraseña |
| `rpt_ventas_por_categoria` | Reporte 1 |
| `rpt_top_clientes` | Reporte 2 |
| `rpt_stock_critico` | Reporte 3 |
| `rpt_mensajes_contacto` | Reporte 4 |

### `v_catalogo_publico` — la más importante de entender

**El problema:** `producto_talla` tiene una fila por cada combinación. Un `JOIN`
directo devolvería 72 filas, y el catálogo mostraría el mismo hoodie cuatro veces.

**La solución:** agrupar por producto.

```sql
SUM(pt.stock)::INT                         AS stock,
COUNT(*) FILTER (WHERE pt.stock > 0)::INT  AS tallas_disponibles,
STRING_AGG(t.codigo, ',' ORDER BY t.orden)
    FILTER (WHERE pt.stock > 0)            AS tallas,
...
GROUP BY p.id_producto, p.codigo, ...
```

Resultado: **24 filas**, cada una con el stock sumado y la lista de tallas
disponibles como texto (`"S,M,L,XL"`).

Si preguntan por esta vista, la respuesta es: *"agrupa el inventario por producto
para que el catálogo muestre 24 artículos y no 72 entradas repetidas".*

### `v_usuario_seguro` — la de seguridad

La aplicación **no puede** leer la tabla `usuario` completa. Todo lo que necesita
saber sobre usuarios lo obtiene de esta vista, que excluye `password_hash`.

## 3.9 Los 4 reportes y su técnica SQL

Este punto vale 2 puntos de la rúbrica. Hay que saber **qué técnica usa cada uno**.

| Reporte | Técnica | Qué muestra |
|---------|---------|-------------|
| Ventas por categoría | `RANK() OVER` en una función con parámetros de fecha | Productos vendidos, unidades, total y ranking por categoría |
| Top clientes | **CTE** + `DENSE_RANK()` + `CASE` | Ranking de clientes con segmentación Nuevo/Recurrente/Frecuente |
| Stock crítico | **Subconsulta correlacionada** sobre la demanda de 30 días | Productos por agotarse y días de cobertura |
| Mensajes de contacto | Agregación con `FILTER` | Mensajes por asunto y ciudad, con porcentaje de respuesta |

### Cómo explicar `rpt_top_clientes`

```
1. Un CTE llamado compras_cliente agrupa las compras uniendo 4 tablas:
   cliente, usuario, pedido y detalle_pedido
2. Sobre ese resultado, DENSE_RANK() asigna la posición por monto comprado
3. Un CASE clasifica: 5+ pedidos = Frecuente, 2+ = Recurrente, resto = Nuevo
4. AGE() calcula los días sin comprar
```

Un **CTE** (Common Table Expression) es un `WITH nombre AS (...)`. Sirve para
nombrar un resultado intermedio y luego usarlo, en lugar de anidar subconsultas.

## 3.10 Los 7 roles y el control de acceso

Este punto vale 2 puntos. Es de lo más sólido del proyecto.

### Dos niveles de roles

**Roles de privilegio** (no se conectan, solo agrupan permisos):

| Rol | Alcance |
|-----|---------|
| `rge_app_read` | Lectura del catálogo público |
| `rge_app_write` | Escritura de pedidos, clientes y mensajes |
| `rge_admin` | Lectura de reportes y datos administrativos |
| `rge_backup` | Lectura completa, solo para respaldos |

**Roles de conexión** (con contraseña, los usa el sistema):

| Rol | Hereda | Lo usa |
|-----|--------|--------|
| `rge_flask` | `rge_app_read` + `rge_app_write` | La aplicación web |
| `rge_panel` | `rge_admin` | Los reportes del panel |
| `rge_respaldo` | `rge_backup` | Los scripts de respaldo |

**Por qué dos niveles:** los permisos se conceden a roles de grupo, no a usuarios.
Agregar un cuarto usuario de conexión no exige reescribir ningún `GRANT`.

### Permisos por columna

```sql
GRANT SELECT (id_usuario, email, password_hash, rol, activo, ultimo_acceso)
      ON usuario TO rge_app_read;
```

La aplicación solo puede leer **esas seis columnas**, las que necesita para
autenticar. Todo lo demás pasa por `v_usuario_seguro`.

### La separación, comprobada

| Operación | `rge_flask` | `rge_panel` |
|-----------|-------------|-------------|
| `SELECT * FROM usuario` | Denegado | Denegado |
| `SELECT * FROM v_usuario_seguro` | Permitido | Permitido |
| `INSERT INTO mensaje_contacto` | Permitido | — |
| `SELECT * FROM mensaje_contacto` | **Denegado** | Permitido |
| `SELECT * FROM rpt_top_clientes` | **Denegado** | Permitido |

**La aplicación puede escribir mensajes pero no leerlos.** Esto obligó a que el
panel administrativo use un segundo grupo de conexiones con `rge_panel`. Fue la
base de datos la que impuso la arquitectura correcta.

### Las tres capas de autorización

Una petición a los reportes atraviesa tres controles independientes:

```
1. Flask       → el decorador @requiere_admin comprueba el rol de la sesión
2. Conexión    → la consulta viaja por el pool del rol rge_panel
3. PostgreSQL  → el GRANT del motor autoriza o rechaza
```

Si alguien evita el primero, el segundo y el tercero siguen ahí.

## 3.11 SECURITY DEFINER

**El problema:** el trigger `fn_trg_encolar_correo` necesita insertar en
`envio_correo`, pero se ejecuta con los permisos de `rge_flask`, que no puede
escribir en esa tabla.

**Lo que NO se hizo:** dar permiso de escritura a `rge_flask` sobre `envio_correo`.
Eso ampliaría los privilegios de toda la aplicación para resolver un caso puntual.

**Lo que sí se hizo:**

```sql
ALTER FUNCTION fn_trg_encolar_correo()
    SECURITY DEFINER SET search_path = public, pg_temp;
```

La función se ejecuta con los permisos de **su propietario**, y solo durante esa
operación. El `search_path` fijo evita que alguien redirija la función hacia
objetos falsos.

Se aplica a 4 objetos: `fn_trg_encolar_correo`, `fn_trg_auditar_producto`,
`sp_cambiar_estado_pedido` y `sp_reponer_stock`.

## 3.12 Los scripts son reejecutables

Todos los scripts se pueden volver a ejecutar sin error. Esto exigió conocer dos
limitaciones de PostgreSQL:

| Objeto | ¿Admite `OR REPLACE`? |
|--------|----------------------|
| `FUNCTION` / `PROCEDURE` | Sí, sin límites |
| `VIEW` | Solo si **no cambian** nombres, orden ni tipos de columnas |
| `TRIGGER` | No |

Por eso se antepone `DROP ... IF EXISTS`. Y en el caso de las vistas hay que
**volver a conceder los permisos**, porque al eliminar una vista se pierden.

## 3.13 Respaldos

| Aspecto | Decisión |
|---------|----------|
| Herramienta | `pg_dump` en formato personalizado (`-F c`) |
| Alcance | Estructura y datos en el mismo volcado |
| Roles | Archivo aparte con `pg_dumpall --roles-only` |
| Rol ejecutor | `rge_respaldo`, **solo lectura** |
| Restauración | `pg_restore` mediante `restaurar.bat` |
| Imágenes | No se respaldan: están en Git |

**Por qué los roles van aparte:** `pg_dump` respalda una base, pero los roles son
objetos **del servidor**, no de la base. Por eso hace falta `pg_dumpall`.

**El principio:** el código vive en GitHub y siempre se puede recuperar. Los datos
no.

---

# 4. PROGRAMACIÓN ORIENTADA A OBJETOS

## 4.1 Las 15 clases

Están en `backend/app/models/`, un archivo por clase (salvo `talla.py`, que tiene dos).

| Clase | Archivo | Qué representa |
|-------|---------|----------------|
| `Persona` | `persona.py` | Clase **abstracta** base de las personas |
| `Cliente` | `cliente.py` | Quien compra |
| `Administrador` | `administrador.py` | Quien gestiona |
| `Producto` | `producto.py` | Clase **abstracta** base de las prendas |
| `Hoodie` | `hoodie.py` | Buzo con capucha |
| `Pantalon` | `pantalon.py` | Pantalón |
| `Accesorio` | `accesorio.py` | Gorra, gorro, collar o cadena |
| `Categoria` | `categoria.py` | Agrupa productos |
| `Talla` | `talla.py` | XS a XXL y U |
| `ProductoTalla` | `talla.py` | Une producto y talla, guarda el stock |
| `Direccion` | `direccion.py` | Dirección de entrega |
| `Pedido` | `pedido.py` | La compra completa |
| `DetallePedido` | `detalle_pedido.py` | Una línea del pedido |
| `Carrito` | `carrito.py` | Carrito antes de comprar |
| `Mensaje` | `mensaje.py` | Mensaje de contacto |

## 4.2 Los cuatro pilares, con ejemplos del proyecto

### ABSTRACCIÓN

`Persona` y `Producto` son clases **abstractas**: heredan de `ABC` y tienen métodos marcados con `@abstractmethod`. No se pueden instanciar directamente.

```python
class Producto(ABC):
    @abstractmethod
    def calcular_precio_final(self):
        pass
```

Si intentas `Producto(...)` Python lanza un error. Solo puedes crear un `Hoodie`, un `Pantalon` o un `Accesorio`.

**Para qué sirve:** obliga a que toda subclase implemente ese método. Es un contrato.

### ENCAPSULAMIENTO

Los atributos son privados y el acceso pasa por `@property`:

```python
@property
def precio(self):
    return self.__precio

@precio.setter
def precio(self, valor):
    monto = Decimal(str(valor))
    if monto <= 0:
        raise ErrorValidacion("precio", "El precio debe ser mayor que cero")
    self.__precio = monto.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

**Qué logra:** es imposible dejar un objeto en estado inválido. No puedes poner un precio negativo ni un precio de oferta mayor al de lista, porque el setter lo rechaza.

En Python, `__precio` (dos guiones bajos) es privado de verdad; `_activo` (uno) es una convención de "protegido".

### HERENCIA

Dos jerarquías:

```
    Persona (abstracta)              Producto (abstracta)
      /        \                    /      |      \
 Cliente   Administrador      Hoodie   Pantalon   Accesorio
```

Se usa herencia cuando hay una relación **"es un"**: un Hoodie **es un** Producto, un Cliente **es una** Persona.

Las subclases llaman al padre con `super().__init__(...)` y amplían lo que necesitan.

### POLIMORFISMO

**Este es el punto estrella del proyecto.** Los tres productos calculan su precio de forma distinta:

| Clase | Regla | Ejemplo |
|-------|-------|---------|
| `Hoodie` | +10 % si gramaje >= 400 gsm | $35.00 -> $38.50 |
| `Pantalon` | +5 % si el corte es Carpenter o Workwear | $29.99 -> $31.49 |
| `Accesorio` | -5 % si el precio >= $70 | $79.00 -> $75.05 |

```python
# Hoodie
def calcular_precio_final(self):
    base = self.precio_venta
    if self.es_premium:
        base = base * (Decimal("1") + self.RECARGO_PREMIUM)
    return base.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

El servicio de pedidos llama a `producto.calcular_precio_final()` **sin saber qué tipo tiene delante**. Python elige la implementación correcta en tiempo de ejecución. Eso es polimorfismo.

## 4.3 Composición y agregación

| Relación | Tipo | Por qué |
|----------|------|---------|
| `Pedido` contiene `DetallePedido` | **Composición** | Una línea no existe sin su pedido |
| `Cliente` tiene `Direccion` | **Composición** | Una dirección no existe sin su titular |
| `Categoria` agrupa `Producto` | **Agregación** | El producto existe aunque se borre la categoría |
| `Carrito` reserva `ProductoTalla` | **Agregación** | Vaciar el carrito no borra el inventario |

**Cómo distinguirlas:** en composición, la parte **muere con el todo**. En la base de datos eso se refleja como `ON DELETE CASCADE`. En agregación, la parte sobrevive.

## 4.4 Métodos especiales

Las clases implementan métodos que Python usa internamente:

| Método | Dónde | Qué permite |
|--------|-------|-------------|
| `__len__` | `Pedido`, `Carrito` | `len(pedido)` devuelve el número de líneas |
| `__iter__` | `Pedido`, `Carrito` | `for linea in pedido:` |
| `__eq__` | `Persona`, `Producto`, `Talla` | Comparar por ID o código, no por objeto |
| `__lt__` | `Producto`, `Talla` | Ordenar productos por precio |
| `__str__` | Casi todas | Texto legible del objeto |
| `__bool__` | `Carrito` | `if carrito:` es falso si está vacío |
| `__hash__` | Las que definen `__eq__` | Poder usarlas en conjuntos y diccionarios |

## 4.5 Clases importantes en detalle

### `Cliente` — la validación de cédula

Implementa el algoritmo del **dígito verificador ecuatoriano**:

```
1. Los dos primeros dígitos deben ser una provincia válida (1-24 o 30)
2. El tercer dígito debe ser menor que 6
3. Se multiplican los 9 primeros dígitos por (2,1,2,1,2,1,2,1,2)
4. Si un producto pasa de 9, se le resta 9
5. Se suman todos
6. El verificador es (10 - suma % 10) % 10
7. Debe coincidir con el décimo dígito
```

Por eso una cédula inventada es rechazada aunque tenga 10 dígitos.

Otros métodos: `edad` (calculada desde la fecha de nacimiento), `es_mayor_de_edad`, `direccion_principal`, `puede_comprar()`.

### `Administrador` — los niveles

| Nivel | Nombre | Puede |
|-------|--------|-------|
| 1 | Consulta | Ver catálogo, reportes y mensajes |
| 2 | Gestión | Lo anterior + gestionar productos, reponer stock, cambiar estados |
| 3 | Total | Lo anterior + gestionar usuarios y ver auditoría |

El método `exigir(accion)` centraliza la comprobación y lanza `PermisoDenegado` si el nivel no alcanza.

### `Pedido` — la máquina de estados

```python
TRANSICIONES = {
    "Pendiente":      ("Pagado", "Cancelado"),
    "Pagado":         ("En preparacion", "Cancelado"),
    "En preparacion": ("Enviado", "Cancelado"),
    "Enviado":        ("Entregado",),
    "Entregado":      (),
    "Cancelado":      (),
}
```

Un diccionario define qué transiciones son válidas. `puede_pasar_a()` consulta el diccionario y `cambiar_estado()` rechaza lo que no esté permitido. No se puede pasar de "Entregado" a "Pendiente".

### `DetallePedido` — el precio congelado

Al crear un detalle, el precio se **copia** en ese momento mediante `_congelar_precio()`. Si el producto sube de precio mañana, el pedido sigue mostrando lo que costó el día de la compra.

### `ProductoTalla` — el inventario

Propiedades: `disponible`, `en_nivel_critico`, `agotado`.
Métodos: `hay_stock(cantidad)`, `descontar(cantidad)`, `reponer(cantidad)`.

Es el objeto que representa una fila de la tabla `producto_talla`.

---

# 5. BACKEND

## 5.1 Estructura de carpetas

```
backend/
├── app/
│   ├── __init__.py         create_app(): la fábrica de la aplicación
│   ├── config.py           Lee el .env y expone la configuración
│   ├── database/
│   │   └── conexion.py     Los dos pools de conexiones
│   ├── models/             Las 15 clases del dominio
│   ├── repositories/       Acceso a datos
│   ├── services/           Reglas de negocio
│   ├── routes/             Los 6 blueprints
│   └── utils/
│       ├── validadores.py  Validaciones reutilizables
│       └── excepciones.py  Excepciones propias
├── run.py                  Arranca el servidor
├── enviar_correos.py       Procesa la cola de correos
└── requirements.txt
```

## 5.2 `config.py`

Lee `backend/.env` con `python-dotenv` y expone todo como atributos de clase.

Lo importante: **hay dos cadenas de conexión**.

```python
cadena_conexion()        # usa DB_USUARIO       -> rge_flask
cadena_conexion_admin()  # usa DB_ADMIN_USUARIO -> rge_panel
```

## 5.3 `database/conexion.py` — los dos pools

Un **pool** es un conjunto de conexiones abiertas y reutilizables. Abrir una conexión a PostgreSQL es lento; el pool las mantiene listas.

| Pool | Rol | Tamaño | Para qué |
|------|-----|--------|----------|
| `_pool` | `rge_flask` | 1 a 10 | Toda la aplicación pública |
| `_pool_admin` | `rge_panel` | 1 a 3 | Reportes y mensajes del panel |

Funciones que expone:

| Función | Qué hace |
|---------|----------|
| `consultar_todos(sql, params)` | Devuelve una lista de filas |
| `consultar_uno(sql, params)` | Devuelve una fila o None |
| `consultar_valor(sql, params)` | Devuelve un único valor |
| `ejecutar(sql, params)` | INSERT/UPDATE/DELETE, devuelve filas afectadas |
| `llamar_procedimiento(nombre, params)` | Ejecuta un `CALL` |
| `consultar_todos_admin(...)` | Igual, pero por el pool administrativo |

### La traducción de errores

La función `_traducir()` convierte los errores técnicos de PostgreSQL en mensajes comprensibles:

| Error de PostgreSQL | Mensaje al usuario |
|---------------------|--------------------|
| `UniqueViolation` | "Ya existe un registro con esos datos" |
| `ForeignKeyViolation` | "El registro referenciado no existe" |
| `InsufficientPrivilege` | "La aplicacion no tiene permisos para esta operacion" |
| `OperationalError` | "No se pudo conectar con la base de datos" |

**Por qué:** un mensaje como *"permiso denegado a la tabla usuario"* revela la estructura interna. El detalle técnico queda en la bitácora del servidor.

## 5.4 `utils/excepciones.py`

Una jerarquía de excepciones propias, todas heredan de `ErrorRedGoatEyes`:

| Excepción | Código HTTP |
|-----------|-------------|
| `ErrorValidacion` | 400 |
| `CarritoVacio` | 400 |
| `CredencialesInvalidas` | 401 |
| `PermisoDenegado` | 403 |
| `ProductoNoEncontrado` | 404 |
| `StockInsuficiente` | 409 |
| `TransicionInvalida` | 409 |
| `UsuarioDuplicado` | 409 |
| `ErrorBaseDatos` | 500 |

En `app/__init__.py` hay un manejador que traduce cada excepción a su código HTTP. Por eso el frontend recibe siempre un JSON con `error`, `mensaje` y a veces `campo`.

`ErrorValidacion` incluye el **nombre del campo**, y por eso el JavaScript puede colocar el mensaje debajo del campo correcto.

## 5.5 `repositories/` — el patrón Repository

### Qué es

Una capa que traduce entre **objetos de Python** y **SQL**. Los servicios piden objetos; el repositorio se encarga de las consultas.

### `base_repository.py`

Clase abstracta con lo común:

```python
class BaseRepository(ABC):
    @property
    @abstractmethod
    def tabla(self): pass

    @property
    @abstractmethod
    def clave_primaria(self): pass

    @abstractmethod
    def a_objeto(self, fila): pass
```

Y métodos ya implementados que sirven a todos: `contar()`, `existe()`, `obtener_por_id()`, `obtener_todos()`, `eliminar()`.

**Esto es reutilización:** los 5 repositorios heredan ese comportamiento sin repetirlo.

### Los 5 repositorios

| Repositorio | De qué se encarga |
|-------------|-------------------|
| `ProductoRepository` | Catálogo, inventario, tallas, reposición |
| `UsuarioRepository` | Credenciales, registro, direcciones, ciudades |
| `PedidoRepository` | Pedidos, detalles, métodos de pago, cola de correos |
| `MensajeRepository` | Mensajes de contacto |
| `ReporteRepository` | Los 4 reportes (usa el pool administrativo) |

### La fábrica polimórfica

`ProductoRepository.a_objeto()` decide qué clase crear según la categoría:

```python
if categoria == "Hoodies":
    return Hoodie(**comunes, gramaje=self._gramaje(fila.get("material")))
if categoria == "Pantalones":
    return Pantalon(**comunes, tipo_corte=self._corte(fila["nombre"]))
if categoria == "Accesorios":
    return Accesorio(**comunes, tipo_accesorio=self._tipo_accesorio(fila["nombre"]))
```

Una fila de SQL entra, y sale el objeto correcto. Es el puente entre el modelo relacional y el modelo de objetos.

### `ReporteRepository` sobrescribe la conexión

```python
def _consultar_todos(self, sql, parametros=None):
    return consultar_todos_admin(sql, parametros)
```

Los reportes viajan por el pool de `rge_panel` porque `rge_flask` no tiene permiso sobre esas vistas.

## 5.6 `services/` — las reglas de negocio

| Servicio | De qué se encarga |
|----------|-------------------|
| `AuthService` | Hashear, verificar, iniciar sesión, registrar |
| `ProductoService` | Catálogo, detalle, inventario, reposición |
| `PedidoService` | Calcular totales, registrar pedidos, historial |
| `ReporteService` | Formatear los reportes |
| `PdfService` | Generar el recibo en PDF |
| `CorreoService` | Enviar correos por SMTP |

### `AuthService` — bcrypt

```python
def hashear(self, password):
    semilla = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
    return bcrypt.hashpw(password.encode("utf-8"), semilla).decode("utf-8")
```

**12 rondas.** Bcrypt añade una sal aleatoria por contraseña y es deliberadamente lento, lo que encarece los ataques por fuerza bruta.

Es una función **de un solo sentido**: se puede comprobar si una contraseña coincide, pero no recuperarla. Por eso una contraseña olvidada se restablece, no se recupera.

### `ProductoService._formatear()` — donde se arregló el bug de precios

```python
def _formatear(self, fila):
    tallas = fila.get("tallas") or ""
    producto = self._repo.a_objeto(fila)
    return {
        ...
        "precio_final": float(producto.calcular_precio_final()),
        "tallas": tallas.split(",") if tallas else [],
        ...
    }
```

La línea clave es `producto.calcular_precio_final()`. Antes tomaba el precio de la vista SQL, y por eso 7 de 24 productos mostraban un precio y cobraban otro.

### `PedidoService.calcular_totales()`

```python
subtotal = subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
iva = (subtotal * self.IVA).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
```

Todo con `Decimal`, nunca `float`. `ROUND_HALF_UP` es el redondeo comercial: 0.5 sube.

### `PedidoService.registrar()` — la validación de rol

```python
comprador = self._usuarios.obtener_por_id(id_cliente)

if comprador is None or comprador.obtener_rol() != "cliente":
    raise PermisoDenegado(
        "realizar compras con una cuenta administrativa. "
        "Inicie sesion con una cuenta de cliente")
```

Un administrador no puede comprar porque `pedido` referencia a `cliente`.

### `CorreoService` — la arquitectura del correo

**PostgreSQL no tiene cliente SMTP.** No puede abrir una conexión de red a Gmail. La solución reparte la responsabilidad:

```
1. El trigger trg_encolar_correo escribe en la tabla envio_correo
2. Flask lee esa cola con correos_pendientes()
3. Genera el PDF con PdfService
4. Envía por SMTP
5. Marca el registro como enviado o fallido
```

**La frase para la defensa:** *"La base encola y audita; la aplicación envía."*

El envío corre en un **hilo aparte** (`threading.Thread` con `daemon=True`), de modo que si Gmail está caído la venta se registra igual.

Reintentos: hasta 5 intentos; después el registro pasa a `fallido`.

El mismo servicio avisa al administrador cuando llega un mensaje de contacto, con la cabecera `Reply-To` del cliente para que la respuesta le llegue directamente.

## 5.7 `routes/` — los 6 blueprints

Un **blueprint** de Flask agrupa rutas relacionadas. Cada uno tiene su prefijo.

| Blueprint | Prefijo | Endpoints |
|-----------|---------|-----------|
| `productos_bp` | `/api/productos` | 6 |
| `categorias_bp` | `/api` | 2 |
| `auth_bp` | `/api/auth` | 6 |
| `pedidos_bp` | `/api/pedidos` | 8 |
| `contacto_bp` | `/api/contacto` | 3 |
| `reportes_bp` | `/api/reportes` | 5 |

### `sesion.py` — los decoradores

```python
@requiere_sesion                  # 401 si no hay sesión
@requiere_admin()                 # 403 si no es administrador
@requiere_admin(nivel_minimo=2)   # 403 si el nivel es menor que 2
```

Un **decorador** envuelve una función y ejecuta código antes. Estos comprueban la sesión antes de dejar entrar a la ruta.

### Orden de las rutas: un detalle importante

En `productos_bp.py`, la ruta `/<codigo>` va **al final**:

```python
@productos_bp.get("/inventario")            # primero las estáticas
@productos_bp.post("/reponer")
@productos_bp.get("/disponibilidad/<int:id>")
@productos_bp.get("/<codigo>")              # la dinámica al final
```

Si `/<codigo>` fuera primero, capturaría `/inventario` como si fuera un código de producto.

## 5.8 `app/__init__.py` — la fábrica

`create_app()` hace cinco cosas:

```
1. Crea la aplicación Flask apuntando a assets/ y pages/
2. Configura sesiones (HttpOnly, SameSite=Lax, duración)
3. Abre el pool de conexiones
4. Registra los 6 blueprints
5. Registra los manejadores de error
```

También sirve el sitio: `/` devuelve `index.html` y `/pages/<archivo>` las demás. Por eso todo corre en un solo servidor y las llamadas a `/api/...` funcionan sin problemas de CORS.

## 5.9 Los 31 endpoints

### Públicos

| Método | Ruta | Devuelve |
|--------|------|----------|
| GET | `/api/salud` | Estado de la conexión |
| GET | `/api/productos` | 24 productos (acepta `?categoria=` y `?q=`) |
| GET | `/api/productos/destacados` | Los destacados |
| GET | `/api/productos/<codigo>` | Detalle con tallas y stock |
| GET | `/api/productos/disponibilidad/<id>` | Si hay stock suficiente |
| GET | `/api/categorias` | Las 3 categorías |
| GET | `/api/ciudades` | Las 30 ciudades |
| GET | `/api/contacto/asuntos` | Los 3 asuntos |
| POST | `/api/contacto` | Registra un mensaje |
| POST | `/api/pedidos/calcular` | Subtotal, IVA y total |
| GET | `/api/pedidos/metodos-pago` | Los 4 métodos |
| POST | `/api/auth/login` `/registro` `/logout` | Sesión |
| GET | `/api/auth/sesion` | Usuario actual |

### Requieren sesión

| Método | Ruta |
|--------|------|
| GET/POST | `/api/auth/direcciones` |
| POST | `/api/pedidos` |
| GET | `/api/pedidos/mios` y `/api/pedidos/<codigo>` |

### Requieren administrador

| Método | Ruta | Nivel |
|--------|------|-------|
| GET | `/api/reportes/resumen` `/ventas` `/clientes` `/stock` `/mensajes` | 1 |
| GET | `/api/pedidos/todos` | 1 |
| GET | `/api/contacto/mensajes` | 1 |
| GET | `/api/productos/inventario` | 1 |
| GET/POST | `/api/pedidos/correos/estado` y `/procesar` | 1 |
| POST | `/api/productos/reponer` | **2** |
| PATCH | `/api/pedidos/<codigo>/estado` | **2** |

---

# 6. FRONTEND

## 6.1 Los 4 archivos CSS

| Archivo | Líneas | De qué se encarga |
|---------|--------|-------------------|
| `base.css` | 68 | Variables de color, reinicio, tipografía |
| `layout.css` | 238 | Cabecera, pie, rejillas, contenedores |
| `components.css` | ~1500 | Tarjetas, botones, formularios, tablas, modales, panel |
| `responsive.css` | 307 | Los 4 puntos de quiebre |

Se cargan **en ese orden**. Eso importa: lo que viene después puede sobrescribir
lo anterior.

### Las variables de color

```css
:root {
    --rojo: #c00000;
    --negro: #0a0a0a;
    --blanco: #ffffff;
    --error: #ff4d4d;
    --exito: #2e7d32;
}
```

Cambiar la identidad visual de la marca es editar siete líneas.

### Los 4 puntos de quiebre

| Ancho | Qué cambia |
|-------|-----------|
| ≤ 992 px | Rejilla de 3 a 2 columnas |
| ≤ 768 px | Menú hamburguesa |
| ≤ 600 px | Formularios a una columna |
| ≤ 480 px | Una columna, tipografía reducida |

## 6.2 Los 9 archivos JavaScript

| Archivo | Se carga en | Qué hace |
|---------|-------------|----------|
| `carrito-contador.js` | **las 13 páginas** | Capa de API, sesión, carrito, notificaciones |
| `menu.js` | las 13 páginas | Menú hamburguesa |
| `catalogo.js` | hoodies, pantalones, accesorios, productos | Tarjetas y ficha de producto |
| `carrito.js` | carrito.html | Líneas del carrito y totales |
| `auth.js` | login.html, registro.html | Iniciar sesión y registrarse |
| `pago.js` | pago.html | Formulario de pago |
| `gracias.js` | gracias.html | Comprobante |
| `admin.js` | admin.html | Panel completo |
| `validaciones.js` | contacto.html | Formulario de contacto |

### `carrito-contador.js` — el núcleo

Es el archivo más importante del frontend porque **se carga en todas las páginas**
y contiene la capa de acceso a la API.

**Por qué está ahí:** al ponerlo en un archivo que ya se cargaba en las 13
páginas, no hubo que tocar ni un HTML para añadir la capa de API.

Funciones que expone:

| Función | Qué hace |
|---------|----------|
| `rgeApi(ruta, opciones)` | Envuelve `fetch`. Añade cabeceras, convierte a JSON y normaliza errores |
| `rgeLeerCarrito()` / `rgeGuardarCarrito()` | Leen y escriben en `localStorage` |
| `rgeActualizarContador()` | Actualiza el número junto al icono |
| `rgeCatalogo()` | Pide el catálogo una vez y lo guarda en memoria |
| `rgeCargarSesion()` | Consulta `/api/auth/sesion` y aplica las clases al `body` |
| `rgeEsAdministrador()` | Devuelve si la sesión es administrativa |
| `rgeCalcularTotalesServidor()` | Pide los totales al servidor |
| `rgeFormatearPrecio()` | Convierte 35 en `"$35.00"` |
| `rgeNotificar(mensaje, tipo)` | Muestra el aviso flotante |
| `rgeMostrarRol()` / `rgeEnlaceAdministracion()` | Inyectan el rol y el enlace al panel |

#### Cómo funciona `rgeApi`

```javascript
async function rgeApi(ruta, opciones) {
    ...
    if (!respuesta.ok) {
        throw {
            codigo: datos.error,      // "STOCK_INSUFICIENTE"
            estado: respuesta.status, // 409
            mensaje: datos.mensaje,   // texto para el usuario
            campo: datos.campo        // "cedula", si aplica
        };
    }
    return datos;
}
```

Todos los demás archivos usan esta función. Si el servidor está caído, lanza un
error con código `SIN_CONEXION` y un mensaje comprensible.

#### El enlace al panel

```javascript
function rgeRutaPaginas() {
    return window.location.pathname.indexOf("/pages/") !== -1 ? "" : "pages/";
}
```

Detecta dónde está la página para armar la ruta correcta: desde la raíz usa
`pages/admin.html`, desde dentro usa `admin.html`. Por eso el enlace funciona en
las 13 páginas sin duplicar código en el HTML.

### `catalogo.js` — tarjetas y ficha

Dos partes:

**1. Sincronizar las tarjetas.** El HTML tiene las tarjetas escritas a mano con
`data-id="RGE-HOO-001"`. Al cargar la página, el JavaScript pide el catálogo y
actualiza cada tarjeta con el precio, el stock y las tallas reales.

**Por qué así:** las tarjetas siguen siendo HTML de verdad (bueno para el
criterio de estructura), pero los datos vienen de la base.

**2. La ficha de producto.** Al pulsar una tarjeta, pide `/api/productos/<codigo>`
y construye una ventana emergente con las tallas, cada una con su stock.

Puntos importantes:

- Todo se construye con `document.createElement()` y `textContent`, **nunca con
  `innerHTML`**, para evitar XSS
- El selector de cantidad se detiene en el stock de la talla elegida
- Antes de agregar, vuelve a preguntar al servidor si hay stock
- Cada talla se guarda como una **línea independiente** del carrito

### `carrito.js`

Pinta las líneas del carrito. Lo importante: identifica cada línea por
`id_producto_talla`, **no por código de producto**. Por eso el mismo hoodie en
talla M y talla L aparece como dos líneas separadas.

Los totales los pide al servidor con `rgeCalcularTotalesServidor()`; si falla,
usa un cálculo local como respaldo.

### `auth.js`

Login y registro. Dos detalles:

- El `<select>` de ciudades **se llena desde `/api/ciudades`**. Antes tenía 8
  ciudades escritas a mano con IDs que no coincidían con la base
- Tras iniciar sesión, si el rol es administrador redirige al panel; si no, al
  destino que traía (`?destino=pago`)

### `pago.js`

El detalle más curioso: los radios del HTML dicen "Tarjeta de crédito" (con
tilde) y la base guarda "Tarjeta de credito" (sin tilde). La función `sinTildes()`
normaliza ambos antes de compararlos:

```javascript
String(texto).normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase()
```

`normalize("NFD")` separa la letra de su tilde, y el `replace` borra las tildes.

### `admin.js`

El más largo. Carga siete cosas en paralelo con `Promise.all()`:

```javascript
await Promise.all([
    cargarResumen(), cargarVentas(), cargarClientes(),
    cargarProductos(), cargarInventario(), cargarPedidos(), cargarMensajes()
]);
```

**Por qué en paralelo:** siete peticiones seguidas tardarían la suma de todas. En
paralelo tardan lo que la más lenta.

La función `llenar()` es genérica: recibe el id de la tabla, la ruta de la API y
una función que convierte cada registro en una fila. Así las cinco tablas
comparten el mismo código.

### `validaciones.js`

El formulario de contacto. Detalle interesante: el campo "Ciudad" era un
`<input type="text">` en el HTML, y el JavaScript **lo reemplaza por un
`<select>`** poblado desde la API, conservando su `id` y su `name`.

Los asuntos también se cargan desde la base, porque el HTML tenía `"consulta"` en
minúscula y la base espera `"Consulta"`.

## 6.3 Dónde se guarda cada cosa

| Dato | Dónde vive | Por qué |
|------|-----------|---------|
| Carrito | `localStorage` del navegador | Sobrevive al cerrar la pestaña, es privado de cada usuario |
| Sesión | Cookie firmada por Flask | El servidor debe poder verificarla |
| Catálogo | Memoria de la página | Se pide una vez y se reutiliza |
| Código del último pedido | `localStorage` | Para que `gracias.html` sepa qué pedido mostrar |

---

# 7. FLUJOS COMPLETOS

## 7.1 Una compra, paso a paso

```
1.  El cliente abre hoodies.html
2.  catalogo.js pide GET /api/productos
3.  productos_bp -> producto_service.catalogo() -> repositorio -> v_catalogo_publico
4.  Vuelven 24 productos con stock y tallas
5.  Cada tarjeta se actualiza: precio, etiqueta verde de stock, tallas

6.  El cliente pulsa una tarjeta
7.  catalogo.js pide GET /api/productos/RGE-HOO-001
8.  El servicio arma el objeto Hoodie y le pide obtener_tallas_por_producto()
9.  Vuelve el detalle con 4 tallas y su stock
10. Se construye la ficha con createElement

11. El cliente elige talla L y cantidad 3
12. Antes de agregar: GET /api/productos/disponibilidad/128?cantidad=3
13. PostgreSQL responde con fn_verificar_stock(128, 3) -> TRUE
14. Se guarda en localStorage con su id_producto_talla

15. El cliente abre carrito.html
16. carrito.js pide POST /api/pedidos/calcular
17. pedido_service calcula con Decimal: 105.00 + 15.75 = 120.75
18. Se pintan los totales

19. Pulsa "Continuar al pago" sin sesión
20. Redirige a login.html?destino=pago
21. Inicia sesión: POST /api/auth/login
22. auth_service verifica el hash bcrypt
23. Se abre la sesión y vuelve a pago.html

24. Completa dirección y método, confirma
25. POST /api/pedidos
26. pedido_service comprueba que el rol sea cliente
27. Resuelve o crea la dirección
28. Llama a CALL sp_registrar_pedido(...)
29.   -> el procedimiento crea el pedido
30.   -> inserta los detalles
31.   -> trg_validar_stock comprueba existencias
32.   -> trg_ajustar_stock descuenta el stock de cada talla
33.   -> trg_recalcular_pedido recalcula los totales
34. Se llama a sp_cambiar_estado_pedido(codigo, 'Pagado')
35.   -> trg_encolar_correo inserta en envio_correo
36. Flask lanza un hilo que procesa la cola
37.   -> genera el PDF con fpdf2
38.   -> lo envía por SMTP a Gmail
39.   -> marca el registro como enviado
40. El navegador guarda el código y va a gracias.html
41. gracias.js pide GET /api/pedidos/<codigo>
42. Se muestra el comprobante leído de la base
```

**El dato para la defensa:** en el paso 17 el navegador muestra $120.75, en el 28
PostgreSQL calcula $120.75, y el PDF del paso 37 dice $120.75. Tres capas
independientes, el mismo número.

## 7.2 Un mensaje de contacto

```
1. El visitante llena el formulario en contacto.html
2. validaciones.js valida en el navegador
3. POST /api/contacto
4. contacto_bp valida otra vez en Python
5. mensaje_repository hace el INSERT
6. Se lanza un hilo con notificar_mensaje_contacto()
7. Llega un correo al buzón de la tienda con Reply-To del cliente
8. El administrador lo ve en el panel y puede responder
```

## 7.3 Una reposición de stock

```
1. El administrador abre la pestaña Inventario
2. GET /api/productos/inventario devuelve las 72 combinaciones
3. Pulsa "Reponer" en una fila -> el formulario se rellena solo
4. POST /api/productos/reponer
5. @requiere_admin(nivel_minimo=2) comprueba el nivel en Flask
6. producto_service valida que la cantidad esté entre 1 y 1000
7. CALL sp_reponer_stock(codigo, talla, cantidad, id_admin)
8.   -> el procedimiento VUELVE A comprobar el nivel del administrador
9.   -> suma las unidades
10.  -> trg_auditar_producto registra el cambio
11. Se devuelve el stock resultante y la tabla se recarga
```

## 7.4 Qué pasa si algo falla

| Falla | Qué ocurre |
|-------|-----------|
| Gmail está caído | El pedido se guarda igual; el correo queda pendiente |
| No hay stock | 409 con el mensaje exacto y las unidades disponibles |
| La sesión expiró | 401 y redirección al login conservando el carrito |
| Un cliente pide un pedido ajeno | 403 |
| Un administrador intenta comprar | 403 con mensaje explicativo |
| PostgreSQL está apagado | "No se pudo conectar con la base de datos" |
| Se abre el HTML con doble clic | "No se pudo conectar con el servidor" |

---

# 8. ERRORES ENCONTRADOS

Esta sección es oro para la pregunta *"¿qué problemas tuvieron?"*. Son errores
reales, encontrados y corregidos.

## 8.1 El precio mostrado no era el cobrado

**Qué pasaba:** la tarjeta tomaba el precio de la vista SQL, que solo aplica el
precio de oferta. El cobro usaba `calcular_precio_final()` del modelo, que además
aplica los recargos. **7 de 24 productos** mostraban un precio y cobraban otro.

Un hoodie premium se anunciaba en $35.00 y se cobraba $38.50.

**Cómo se resolvió:** el catálogo también usa el método del modelo. La regla de
negocio vive en un solo lugar, que es donde está el polimorfismo.

## 8.2 El catálogo mostraba 72 productos

**Qué pasaba:** al agregar las tallas, `v_catalogo_publico` devolvía una fila por
combinación, así que cada hoodie aparecía cuatro veces.

**Cómo se resolvió:** la vista agrupa por producto con `SUM(stock)` y
`STRING_AGG` de tallas.

## 8.3 Un administrador no podía comprar, pero fallaba mal

**Qué pasaba:** al intentar comprar con la cuenta de administrador, el sistema
lanzaba `AttributeError: 'Administrador' object has no attribute 'ciudad'` y
devolvía una página de error de 500.

**Por qué:** `pedido` referencia a `cliente`, y un administrador no lo es.

**Cómo se resolvió:** el servicio comprueba el rol antes de procesar y responde
403 con un mensaje claro.

## 8.4 Las contraseñas estaban en un archivo versionado

**Qué pasaba:** la primera versión de `06_roles_permisos.sql` traía las
contraseñas en texto plano, y ese archivo sí se sube a Git.

**Cómo se resolvió:** los roles se crean sin contraseña, y las credenciales van en
`07_credenciales.sql`, que está en `.gitignore`. Se versiona una plantilla
`.example`.

## 8.5 El trigger del correo no tenía permisos

**Qué pasaba:** `fn_trg_encolar_correo` debe escribir en `envio_correo`, pero se
ejecutaba con los permisos de `rge_flask`, que no puede.

**Cómo se resolvió:** `SECURITY DEFINER` con `search_path` fijo, en lugar de
ampliar los permisos de toda la aplicación.

## 8.6 `INSERT ... RETURNING` fallaba

**Qué pasaba:** al registrar un mensaje de contacto, el `RETURNING id_mensaje`
daba error de permisos.

**Por qué:** `RETURNING` exige permiso de **lectura** sobre las columnas
devueltas, y `rge_flask` solo tiene escritura sobre esa tabla.

**Cómo se resolvió:** se quitó el `RETURNING`. De paso, es mejor no exponer
identificadores internos.

## 8.7 Los scripts no se podían reejecutar

**Qué pasaba:** `CREATE TRIGGER` no admite `OR REPLACE`, y
`CREATE OR REPLACE VIEW` falla si cambian los nombres de columnas
(error `42P16`).

**Cómo se resolvió:** `DROP ... IF EXISTS` antes de crear, y volver a conceder los
permisos de las vistas, porque al borrarlas se pierden.

## 8.8 Las etiquetas del panel eran invisibles

**Qué pasaba:** la regla `.form-group label { color: var(--blanco) }` estaba
pensada para formularios sobre fondo oscuro. Al reutilizar la clase en el panel,
que tiene fondo claro, las etiquetas desaparecían.

**Cómo se resolvió:** una regla más específica limitada al panel.

---

# 9. PREGUNTAS Y RESPUESTAS

## Base de Datos

**¿Por qué guardan subtotal, IVA y total si se pueden calcular?**
Para conservar las condiciones del día de la compra. El precio de un producto
puede cambiar mañana; un pedido emitido no debe cambiar. Por eso también
congelamos `precio_unitario` en el detalle.

**¿Qué normalización usaron?**
Tercera forma normal. La única excepción es la desnormalización de montos en
`pedido`, que acabamos de justificar.

**¿Cómo modelaron las tallas?**
Con la tabla puente `producto_talla`, que une producto y talla y guarda el stock
de esa combinación. Tiene `UNIQUE (id_producto, id_talla)`.

**¿Por qué la vista agrupa?**
Porque el inventario está por talla. Sin agrupar, el catálogo mostraría 72
entradas en vez de 24 productos.

**¿Por qué triggers y no código Python?**
Porque la base puede recibir cambios desde pgAdmin u otra herramienta. El trigger
garantiza la regla sin importar quién escriba.

**¿Cómo evitan stock negativo?**
Tres barreras: `CHECK stock >= 0`, el trigger `trg_validar_stock` y la validación
en Python.

**Expliquen un reporte.**
`rpt_top_clientes` usa un CTE que agrupa las compras uniendo cuatro tablas, y
sobre ese resultado aplica `DENSE_RANK()` y un `CASE` que segmenta en Nuevo,
Recurrente o Frecuente.

**¿Sus scripts se pueden volver a ejecutar?**
Sí. Usamos `DROP ... IF EXISTS` porque `CREATE TRIGGER` no admite `OR REPLACE` y
`CREATE OR REPLACE VIEW` no permite cambiar columnas.

## POO

**¿Dónde hay polimorfismo?**
En `calcular_precio_final()`. `Producto` lo declara abstracto y las tres subclases
lo implementan distinto: hoodie premium +10 %, pantalón Carpenter +5 %, accesorio
sobre $70 −5 %.

**¿Cómo aplicaron encapsulamiento?**
Atributos privados con `@property`. El setter de `precio` rechaza valores menores
o iguales a cero; el de `precio_oferta` exige que sea menor al de lista.

**¿Herencia o composición?**
Herencia donde hay "es un": un Hoodie **es un** Producto. Composición donde hay
"tiene un" con dependencia de vida: un Pedido **tiene** DetallePedido que no
existen sin él. En la base eso es `ON DELETE CASCADE`.

**¿Por qué `Decimal` y no `float`?**
Porque `float` es binario y no representa exactamente los decimales:
`0.1 + 0.2` da `0.30000000000000004`. En dinero eso descuadra centavos.

**¿Qué es el patrón Repository?**
Aísla el acceso a datos. `BaseRepository` es abstracta con lo común; cada
repositorio concreto añade sus consultas. Los servicios no escriben SQL: piden
objetos.

## Frontend / UX

**¿Por qué se arma el carrito sin cuenta?**
Porque exigir registro antes de ver precios es la principal causa de abandono.
Pedimos la cuenta al pagar, cuando el usuario ya está comprometido.

**¿Por qué una ficha emergente y no una página de producto?**
Porque el usuario no pierde el contexto del catálogo. Con varias tallas
necesitábamos un espacio para elegir, pero una página aparte obligaría a volver
atrás.

**¿Por qué construyen el HTML con `createElement`?**
Porque el nombre de un producto o el texto de un mensaje son datos, no marcado.
Con `innerHTML`, un texto con etiquetas se ejecutaría. Con `textContent` se
muestra como texto.

**¿Qué hicieron por accesibilidad?**
HTML semántico, las 64 imágenes con `alt`, 42 `aria-label`, 21 `label` asociados,
cierre con Escape.

## Arquitectura y seguridad

**¿Por qué Flask envía el correo y no PostgreSQL?**
Porque PostgreSQL no tiene cliente SMTP. El trigger **encola y audita** en
`envio_correo`; Flask **consume esa cola y envía**. La base es la fuente de la
verdad; la aplicación es el brazo que sale a la red.

**¿Qué pasa si falla el correo?**
La venta se registra igual. El envío corre en un hilo aparte y el registro queda
pendiente con el error guardado. Se reintenta con `python enviar_correos.py`.

**¿Por qué dos conexiones a la base?**
Porque `rge_flask` no tiene permiso sobre los reportes ni los mensajes, y está
bien que no lo tenga. El panel usa `rge_panel`. Fue un hallazgo del desarrollo:
los permisos nos forzaron a la arquitectura correcta.

**¿Cómo protegen las contraseñas?**
bcrypt con 12 rondas. Nunca se guardan ni se devuelven en texto plano. Las
credenciales de base viven en `backend/.env`, que está en `.gitignore`.

**¿Cómo recuperan una contraseña olvidada?**
No se recupera, se restablece. Bcrypt es irreversible por diseño.

**¿Cómo usaron Git?**
Ramas de funcionalidad con Pull Request hacia `main`, commits separados por tema
y merge sin *fast-forward* para que la rama quede visible en el historial.

---

## Cómo responder cuando no sabes

- Di la idea principal primero, el ejemplo después.
- Si no recuerdas una cifra exacta, dilo. No inventes.
- Si te corrigen y tienen razón, acéptalo y sigue.
- Si preguntan por algo fuera del alcance, señala que se documentó como excluido.
