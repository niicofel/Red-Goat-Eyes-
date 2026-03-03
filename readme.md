[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/V2gL3_Hy)
# 🛒 TRABAJO FINAL

## Simulación de E-Commerce con HTML5, CSS y JavaScript

------------------------------------------------------------------------

## 🎯 Objetivo

Desarrollar un sitio web que simule una tienda en línea utilizando
únicamente:

-   HTML5 semántico
-   CSS
-   JavaScript (Vanilla JS)

El proyecto debe demostrar comprensión de:

-   Estructura semántica moderna
-   Diseño responsive
-   Manipulación del DOM
-   Eventos
-   Validación de formularios
-   Organización clara del código
-   Despliegue web básico

------------------------------------------------------------------------

## 👥 Modalidad

-   Trabajo en grupos de máximo 2 personas
-   Ambos integrantes deben participar en la exposición
-   Ambos deben comprender completamente el código entregado

------------------------------------------------------------------------

## 🏬 Temáticas Disponibles (Elegir una)

1.  🎸 Instrumentos musicales
2.  🐾 Tienda de mascotas
3.  💿 Tienda de discos de música
4.  📚 Librería online
5.  🎮 Tienda de videojuegos
6.  👕 Tienda de ropa urbana
7.  💻 Tienda de tecnología
8.  ⚽ Tienda de artículos deportivos
9.  ☕ Tienda de café y productos gourmet
10. 🌱 Tienda de plantas y jardinería

------------------------------------------------------------------------

# 🧱 Estructura HTML5 Obligatoria

Todas las páginas deben utilizar correctamente etiquetas semánticas
como:

-   ```{=html}
    <header>
    ```

-   ```{=html}
    <nav>
    ```

-   ```{=html}
    <main>
    ```

-   ```{=html}
    <section>
    ```

-   ```{=html}
    <article>
    ```

-   ```{=html}
    <footer>
    ```

No se aceptarán páginas construidas únicamente con
```{=html}
<div>
```
sin estructura semántica.

El código debe estar correctamente indentado y organizado.

------------------------------------------------------------------------

# 📄 Páginas Obligatorias

El proyecto debe contener mínimo 4 páginas HTML conectadas entre sí
mediante navegación.

------------------------------------------------------------------------

## 1️⃣ Página de Bienvenida (index.html)

Debe incluir:

-   Nombre de la tienda
-   Banner o imagen principal
-   Descripción breve
-   Enlace hacia la página de categorías

------------------------------------------------------------------------

## 2️⃣ Página de Categorías

Debe incluir:

-   Mínimo 3 categorías
-   Imagen representativa por categoría
-   Enlace hacia productos filtrados por categoría

------------------------------------------------------------------------

## 3️⃣ Página de Productos

Debe mostrar:

-   Mínimo 6 productos
-   Cada producto debe tener:
    -   Nombre
    -   Precio
    -   Imagen
    -   Descripción breve

Los productos pueden estar escritos directamente en el HTML con una estructura clara y organizada.

------------------------------------------------------------------------

## 4️⃣ Página de Contacto

Formulario con:

-   Nombre
-   Ciudad
-   Email
-   Asunto
-   Descripción

### Validaciones obligatorias con JavaScript:

-   Campos no vacíos
-   Email con formato válido
-   Nombre mínimo 3 caracteres
-   Descripción mínimo 10 caracteres
-   Mostrar mensajes de error dinámicos
-   Evitar envío si existen errores

------------------------------------------------------------------------

# 📱 Diseño Responsive (OBLIGATORIO)

El sitio debe:

-   Adaptarse correctamente a dispositivos móviles
-   Usar media queries
-   Mantener navegación funcional en pantallas pequeñas
-   Evitar desbordamientos horizontales

Si el sitio no es responsive, habrá penalización significativa.

------------------------------------------------------------------------

# 🌍 Despliegue Obligatorio (Parte Investigativa)

Como parte del componente investigativo del proyecto:

-   El sitio debe ser desplegado utilizando GitHub Pages.
-   Los estudiantes deberán investigar cómo realizar el despliegue.
-   No se proporcionará tutorial paso a paso en clase.

### Deben entregar:

1.  Enlace al repositorio en GitHub
2.  Enlace público del sitio funcionando en GitHub Pages

Si el sitio no está publicado correctamente, se descontará puntaje.

------------------------------------------------------------------------

# 📂 Estructura del Proyecto

```
trabajo-final/
│
├── index.html
├── categorias.html
├── productos.html
├── contacto.html
│
├── assets/
│   ├── css/
│   │   └── styles.css
│   │
│   ├── js/
│   │   └── script.js
│   │
│   └── img/
│       ├── productos/
│       ├── categorias/
│       └── banners/
│
└── README.md
```

### 📝 Descripción de la estructura:

- **Archivos HTML**: En la raíz del proyecto para fácil acceso
- **assets/css/**: Todos los archivos de estilos
- **assets/js/**: Todos los archivos JavaScript
- **assets/img/**: Todas las imágenes organizadas por carpetas
  - `productos/`: Imágenes de productos
  - `categorias/`: Imágenes de categorías
  - `banners/`: Banners e imágenes principales

------------------------------------------------------------------------

# 📘 README Obligatorio

Debe incluir:

-   Nombre del proyecto: Red Goat Eyes
-   Integrantes: Felipe Nicolas Campos Cisneros / Elian Emanuel Valenzuela Alvarez
-   Temática elegida: Ropa Urbana
-   Descripción del proyecto: El proyecto es una pagina web dedicada a una tienda de ropa de invención propia.
-   Enlace al sitio desplegado en GitHub Pages: 

------------------------------------------------------------------------

# 🎤 Exposición (8--10 minutos)

Cada grupo deberá explicar:

-   Cómo estructuraron el HTML5 semántico
-   Cómo implementaron el diseño responsive
-   Cómo realizaron la validación del formulario
-   Cómo realizaron el despliegue en GitHub Pages
-   Qué fue lo más complejo del proyecto

Ambos integrantes deben participar.

------------------------------------------------------------------------

# 📊 Rúbrica de Evaluación

  Criterio                       Puntos
  ------------------------------ ---------
  Estructura semántica HTML5     10
  Diseño CSS                     10
  Responsive design              7.5
  Validación del formulario      7.5
  Despliegue en GitHub Pages     5
  Organización del código        2.5
  Exposición                     7.5
  ------------------------------ ---------
  **TOTAL**                      **50**
