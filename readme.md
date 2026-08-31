# Red Goat Eyes

Tienda en línea de ropa urbana. Proyecto Integrador de Segundo Nivel — PUCE TEC.

Integra tres asignaturas: **Base de Datos I**, **Programación Orientada a Objetos**
y **Desarrollo Web Frontend UX/UI**.

---

## Qué hace

Una tienda funcional de punta a punta: el cliente navega el catálogo, arma su
carrito, se registra, paga y recibe un recibo en PDF por correo. El
administrador consulta reportes de ventas, inventario y mensajes.

| | |
|---|---|
| Productos | 24 en 3 categorías |
| Páginas | 13 |
| Endpoints de la API | 24 |
| Tablas | 21 |
| Clases del dominio | 15 |

---

## Tecnologías

| Capa | Herramientas |
|------|-------------|
| Presentación | HTML5, CSS3, JavaScript (sin frameworks) |
| Lógica | Python 3, Flask, psycopg 3, bcrypt, fpdf2 |
| Datos | PostgreSQL 18 |

---

## Estructura

```
Red-Goat-Eyes-/
├── index.html              Portada
├── pages/                  12 páginas
├── assets/
│   ├── css/                base · layout · components · responsive
│   ├── js/                 9 archivos
│   └── img/                Banners, categorías y productos
├── backend/
│   ├── app/
│   │   ├── models/         15 clases del dominio
│   │   ├── repositories/   Acceso a datos (patrón Repository)
│   │   ├── services/       Reglas de negocio
│   │   ├── routes/         6 blueprints de Flask
│   │   ├── database/       Pool de conexiones
│   │   └── utils/          Validadores y excepciones
│   ├── run.py              Arranca el servidor
│   └── enviar_correos.py   Procesa la cola de recibos
├── database/               10 scripts SQL numerados
│   ├── backup/             Scripts y estrategia de respaldo
│   └── diagramas/          Modelo E-R y relacional
└── docs/                   Documentación del proyecto
```

---

## Instalación

**1. Clonar y preparar el entorno**

```
git clone https://github.com/niicofel/Red-Goat-Eyes-.git
cd Red-Goat-Eyes-
python -m venv venv
venv\Scripts\activate
python -m pip install -r backend/requirements.txt
```

**2. Crear la base de datos**

En pgAdmin, como `postgres`, ejecutar en orden los archivos de `database/`:

```
00_create_database.sql   →   01_schema.sql   →   02_seed.sql
03_functions_triggers.sql →  04_procedures.sql →  05_views_reportes.sql
06_roles_permisos.sql    →   07_credenciales.sql →  08_security_definer.sql
```

> `07_credenciales.sql` no está en el repositorio. Copiar
> `07_credenciales.sql.example`, renombrarlo y poner las contraseñas.

**3. Configurar el entorno**

Copiar `backend/.env.example` como `backend/.env` y completar las variables.

**4. Ejecutar**

```
cd backend
python run.py
```

Abrir **http://127.0.0.1:5000/**

---

## Arquitectura

El backend está en cuatro capas, cada una con una responsabilidad:

```
routes        →  Reciben la petición HTTP y controlan el acceso
services      →  Aplican las reglas de negocio
repositories  →  Traducen entre objetos y SQL
PostgreSQL    →  Persiste y garantiza la integridad
```

### Decisiones destacadas

**Las reglas viven en las tres capas.** Una validación del formulario está
replicada en Python y como restricción `CHECK` en PostgreSQL. Si alguien evita
el navegador, la base rechaza el dato igual.

**La base encola, la aplicación envía.** PostgreSQL no tiene cliente SMTP. El
trigger `trg_encolar_correo` registra el envío en la tabla `envio_correo`, y
Flask consume esa cola. La base es la fuente de la verdad; la aplicación sale
a la red.

**La venta nunca depende del correo.** El envío corre en segundo plano. Si Gmail
falla, el pedido se registra igual y el recibo queda pendiente de reintento.

**El dinero nunca es punto flotante.** `Decimal` en Python, `NUMERIC` en
PostgreSQL. JavaScript, Flask y la base producen el mismo total.

---

## Seguridad

- La aplicación **nunca** se conecta como superusuario
- 7 roles con permisos a nivel de columna
- Contraseñas con bcrypt de 12 rondas
- Credenciales fuera del repositorio (`.gitignore`)
- Consultas parametrizadas, sin concatenación de SQL
- Autorización verificada en tres capas independientes

Detalle completo en [`docs/05_seguridad_datos.md`](docs/05_seguridad_datos.md).

---

## Documentación

| Documento | Contenido |
|-----------|-----------|
| [01 Planteamiento del problema](docs/01_planteamiento_problema.md) | Problema, necesidad y justificación |
| [02 Requerimientos](docs/02_requerimientos.md) | Funcionales, no funcionales y reglas de negocio |
| [03 Diagrama de clases](docs/03_diagrama_clases.png) | Modelo UML del dominio |
| [04 Decisiones UX/UI](docs/04_decisiones_ux_ui.md) | Justificación de cada decisión de diseño |
| [05 Seguridad de datos](docs/05_seguridad_datos.md) | Control de acceso, integridad y respaldos |
| [06 Manual de usuario](docs/06_manual_usuario.md) | Guía para cliente y administrador |
| [07 Guion de sustentación](docs/07_guion_sustentacion.md) | Preparación de la defensa |

---

## Equipo

| Integrante | Instagram |
|------------|-----------|
| Felipe Nicolás Campos Cisneros | [@niicofel](https://www.instagram.com/niicofel/) |
| Elian Emanuel Valenzuela Álvarez | [@elian.valenzuela.16](https://www.instagram.com/elian.valenzuela.16/) |
| Rafael Chiriboga | [@rafachiriboga](https://www.instagram.com/rafachiriboga/) |

PUCE TEC · Unidad Académica de Formación Técnica y Tecnológica
Quito, Ecuador · Agosto 2026