# Estrategia de respaldo · Red Goat Eyes

Proyecto Integrador 
Motor: PostgreSQL 18 · Base: `red_goat_eyes`

---

## 1. Por qué respaldar

La base guarda pedidos, clientes y el historial de ventas. Un fallo de
disco, un `DELETE` mal escrito o una actualización fallida pueden
destruir información que no se puede reconstruir desde el código fuente.

El código vive en GitHub y siempre se puede recuperar. **Los datos no.**

---

## 2. Qué se respalda

| Elemento | ¿Se respalda? | Motivo |
|---|---|---|
| Estructura (tablas, triggers, procedimientos) | Sí | Garantiza que estructura y datos correspondan al mismo momento |
| Datos de todas las tablas | Sí | Es lo irrecuperable |
| Roles y permisos | Sí, en archivo aparte | `pg_dump` no los incluye: son objetos del clúster, no de la base |
| Imágenes de `assets/img/` | No | Están versionadas en Git |

---

## 3. Tipos de respaldo

### 3.1 Respaldo lógico — `pg_dump`

Genera un archivo con las instrucciones necesarias para reconstruir la
base. Es el que usamos.

**Ventajas:** portable entre versiones de PostgreSQL, permite restaurar
tablas sueltas.
**Limitación:** lento en bases muy grandes. Irrelevante en este proyecto.

Formato elegido: **custom** (`-F c`), porque va comprimido y permite
restauración selectiva con `pg_restore`.

### 3.2 Respaldo de roles — `pg_dumpall --roles-only`

Los roles `rge_flask`, `rge_panel` y `rge_respaldo` pertenecen al
clúster, no a la base. Sin este segundo archivo, al restaurar en otro
servidor los `GRANT` fallarían porque los roles no existirían.

---

## 4. Frecuencia y retención

| Cuándo | Qué | Se conserva |
|---|---|---|
| Diario, 23:00 | Base completa | 7 días |
| Semanal, domingo | Base completa + roles | 4 semanas |
| Antes de cada entrega | Manual, etiquetado | Permanente |

`backup.bat` elimina automáticamente los archivos con más de 7 días.

**Regla 3-2-1** aplicada al alcance del proyecto:

- **3** copias: la base viva, el respaldo local, una copia en la nube
- **2** medios distintos: disco del equipo y almacenamiento en la nube
- **1** fuera del equipo: Google Drive u OneDrive del equipo

---

## 5. Cómo respaldar

cd database\backup
backup.bat


Genera dos archivos con fecha y hora:

red_goat_eyes_2026-08-30_2300.dump
roles_2026-08-30_2300.sql


---

## 6. Cómo restaurar

cd database\backup
restaurar.bat red_goat_eyes_2026-08-30_2300.dump


Pide confirmación escrita antes de sobrescribir, porque la restauración
**destruye** la base actual.

---

## 7. Verificación mensual

Un respaldo que nunca se ha restaurado no es un respaldo: es un archivo
del que se supone que funciona.

Una vez al mes:

1. Restaurar el último respaldo sobre una base de prueba `red_goat_eyes_test`
2. Comprobar los conteos:

```sql
SELECT COUNT(*) FROM producto;   
SELECT COUNT(*) FROM pedido;

Ejecutar los cuatro reportes y comprobar que devuelven datos
Eliminar la base de prueba

8. Seguridad del respaldo
Los respaldos contienen los hashes de contraseña de los usuarios.
Trátalos como información sensible.
Nunca subas un .dump al repositorio. El .gitignore ya excluye
database/backup.dump

Los respaldos se generan con el rol rge_respaldo, que solo tiene
permiso de lectura. Nunca con el superusuario postgres.

9. Qué hacer ante una pérdida de datos
* Detener la aplicación Flask para que no siga escribiendo
* Identificar el respaldo más reciente anterior al incidente
* Restaurar sobre una base de prueba y verificar el contenido
* Solo entonces restaurar sobre la base de producción
* Consultar la tabla auditoria para reconstruir los cambios posteriores al respaldo
