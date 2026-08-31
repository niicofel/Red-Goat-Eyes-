# Decisiones de Diseño UX/UI

**Proyecto:** Red Goat Eyes  
**Asignatura:** Desarrollo Web Frontend UX/UI  
**Versión:** 1.0 · Agosto 2026

---

## 1. Usuario objetivo

La interfaz está pensada principalmente para personas de entre 16 y 30 años que conocen la marca mediante Instagram y normalmente ingresan desde un teléfono.

El objetivo es que puedan identificar rápidamente el producto, conocer su precio y avanzar hacia la compra sin encontrarse con pasos innecesarios. Debido a que este tipo de usuario puede abandonar el sitio si la navegación resulta confusa, el diseño prioriza pantallas pequeñas y un proceso de compra corto.

## 2. Identidad visual

### 2.1 Colores

La identidad utiliza principalmente negro, rojo, blanco y tonos neutros.

| Variable | Color | Uso |
|----------|-------|-----|
| `--rojo` | `#c00000` | Acciones principales, precios y elementos destacados |
| `--rojo-oscuro` | `#900000` | Estado hover |
| `--negro` | `#0a0a0a` | Cabecera, pie y fondos |
| `--blanco` | `#ffffff` | Contenido |
| `--gris-fondo` | `#f4f4f4` | Separación visual |
| `--error` | `#ff4d4d` | Mensajes de error |
| `--exito` | `#2e7d32` | Confirmaciones |

El negro y el rojo se relacionan con la estética de ropa urbana utilizada por la marca. El rojo se emplea principalmente en acciones importantes, mientras los fondos se mantienen más neutros para dar protagonismo a las fotografías.

Los colores están declarados como variables CSS dentro de `:root`, lo que permite modificar la identidad visual desde un único lugar.

### 2.2 Tipografía

Se utilizan `Arial, Helvetica, sans-serif`.

Se eligieron fuentes del sistema para evitar descargas adicionales y conseguir que el texto aparezca rápidamente incluso cuando la conexión móvil no es muy rápida.

## 3. Organización de las páginas

La navegación principal está formada por:

- `index.html`
- `categorias.html`
  - `hoodies.html`
  - `pantalones.html`
  - `accesorios.html`
- `productos.html`
- `contacto.html`
- `carrito.html`
  - `pago.html`
  - `gracias.html`
- `login.html`
- `registro.html`
- `admin.html`

Desde la portada es posible llegar a una categoría en pocos pasos. De la misma manera, desde un producto el usuario puede agregarlo, abrir el carrito y continuar al pago sin recorrer una navegación extensa.

## 4. Principales decisiones de UX/UI

### 4.1 Menú hamburguesa en pantallas pequeñas

Cuando el ancho es menor a 768 px, la navegación se transforma en un menú hamburguesa. Mantener los siete enlaces de forma horizontal obligaría a reducir demasiado el tamaño del texto o a utilizar desplazamiento lateral.

### 4.2 Contador del carrito visible

El icono del carrito muestra un número que cambia cuando se agregan productos. También se presenta una notificación temporal confirmando la acción. Con esto, el usuario recibe una respuesta inmediata y sabe que el producto sí fue añadido.

### 4.3 Botón principal claramente identificado

El botón `Agregar al carrito` ocupa un lugar visible dentro de cada tarjeta y utiliza el color rojo definido para las acciones principales. El texto explica directamente lo que sucederá al presionarlo.

### 4.4 Uso de “Continuar al pago”

En una versión inicial se utilizaba el texto “Finalizar compra”, aunque todavía faltaba completar información. Se cambió a `Continuar al pago` para que el botón describa correctamente el siguiente paso.

### 4.5 Inicio de sesión al momento de pagar

El usuario puede revisar productos y preparar el carrito sin crear previamente una cuenta. La autenticación se solicita cuando intenta continuar al pago.

Si es necesario iniciar sesión, la dirección de destino se conserva mediante `login.html?destino=pago`. Después de autenticarse, el usuario puede regresar al proceso sin perder el carrito.

### 4.6 Errores junto al campo

Los errores se muestran debajo del campo correspondiente mediante un elemento `<small class="error">`. También se cambia visualmente el borde para facilitar su identificación.

Este enfoque evita que la persona tenga que cerrar una alerta y luego buscar qué campo produjo el problema.

### 4.7 Respuestas del servidor ubicadas correctamente

Las validaciones del navegador y del servidor no siempre comprueban lo mismo. Por ejemplo, el navegador puede revisar la longitud de la cédula mientras Python valida su dígito verificador. Cuando la API rechaza un valor, también informa a qué campo corresponde para que JavaScript coloque el mensaje en el lugar adecuado.

### 4.8 Estado de procesamiento

Cuando se envía un formulario, el botón se deshabilita temporalmente y muestra textos como `Ingresando...`, `Creando cuenta...` o `Procesando pago...`.

Esto informa al usuario de que la operación sigue en curso y disminuye la posibilidad de enviar el mismo formulario varias veces.

### 4.9 Productos sin stock

Un producto agotado continúa visible, pero su botón de compra se deshabilita y muestra el texto `Agotado`. Así se comunica que el producto pertenece al catálogo aunque temporalmente no existan unidades.

### 4.10 Confirmación basada en información de la base

La pantalla final consulta el pedido mediante su código. De esta manera, el comprobante mostrado corresponde a los datos realmente almacenados y no a valores que podrían haberse modificado en el navegador.

## 5. Diseño adaptable

Se utilizan cuatro puntos de quiebre:

| Ancho | Cambio principal |
|-------|------------------|
| ≤ 992 px | La rejilla pasa de tres a dos columnas |
| ≤ 768 px | Se activa el menú hamburguesa |
| ≤ 600 px | Los formularios pasan a una columna |
| ≤ 480 px | La interfaz utiliza una sola columna y ajusta la tipografía |

La interfaz fue revisada a 375 px, comprobando que no exista desplazamiento horizontal, que el menú móvil funcione y que los controles puedan utilizarse correctamente.

### Organización del CSS

| Archivo | Responsabilidad |
|---------|-----------------|
| `base.css` | Variables, reinicio y tipografía |
| `layout.css` | Cabecera, pie, rejillas y contenedores |
| `components.css` | Botones, tarjetas, formularios, tablas y notificaciones |
| `responsive.css` | Adaptaciones para los diferentes anchos |

Separar el CSS por responsabilidad facilita el mantenimiento y reduce los conflictos cuando varias personas trabajan en el proyecto.

## 6. Accesibilidad

Se implementaron diferentes medidas:

- 64 imágenes cuentan con texto alternativo;
- existen 42 atributos `aria-label` en controles sin texto visible;
- 21 campos poseen su `label` asociado;
- se utiliza HTML semántico como `header`, `nav`, `main`, `section`, `article`, `aside` y `footer`;
- el menú de usuario puede cerrarse con Escape;
- se mantiene contraste entre texto y fondo.

Estas medidas ayudan a que la interfaz pueda ser comprendida y utilizada por más personas.

## 7. Rendimiento

El favicon original fue reducido de 1813 KB a 12,6 KB mediante una versión PNG de 192 × 192 píxeles, lo que representa una disminución aproximada del 99,3 %.

Font Awesome se carga desde un CDN utilizando `integrity` (SRI), por lo que el navegador puede verificar el recurso externo.

El proyecto utiliza JavaScript nativo distribuido en 9 archivos, sin jQuery, React ni un proceso adicional de compilación. Esto mantiene el proyecto más ligero y sencillo de ejecutar.
