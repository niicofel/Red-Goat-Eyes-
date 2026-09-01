# Decisiones de Diseño UX/UI

**Proyecto:** Red Goat Eyes  
**Asignatura:** Desarrollo Web Frontend UX/UI  
**Versión:** 2.0 · Agosto 2026

---

## 1. Usuario objetivo

La interfaz está pensada principalmente para personas de entre 16 y 30 años que conocen la marca mediante Instagram y normalmente ingresan desde un teléfono.

El objetivo es que puedan identificar rápidamente el producto, conocer su precio y avanzar hacia la compra sin encontrarse con pasos innecesarios. Debido a que este tipo de usuario puede abandonar el sitio si la navegación resulta confusa, el diseño prioriza pantallas pequeñas y un proceso de compra corto.

Existe además un segundo perfil: el administrador de la marca, que necesita revisar ventas, controlar el inventario y atender los mensajes recibidos. Sus necesidades son distintas y por eso cuenta con una pantalla propia.

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
| `--exito` | `#2e7d32` | Confirmaciones y etiqueta de stock |

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

Desde la portada es posible llegar a una categoría en pocos pasos. De la misma manera, desde un producto el usuario puede abrir su ficha, elegir talla, agregarlo y continuar al pago sin recorrer una navegación extensa.

La página `admin.html` no aparece en la navegación general porque no corresponde al recorrido de compra. Se accede desde el menú de usuario, que la muestra únicamente a las cuentas administrativas.

## 4. Principales decisiones de UX/UI

### 4.1 Menú hamburguesa en pantallas pequeñas

Cuando el ancho es menor a 768 px, la navegación se transforma en un menú hamburguesa. Mantener los siete enlaces de forma horizontal obligaría a reducir demasiado el tamaño del texto o a utilizar desplazamiento lateral.

### 4.2 Contador del carrito visible

El icono del carrito muestra un número que cambia cuando se agregan productos. También se presenta una notificación temporal confirmando la acción. Con esto, el usuario recibe una respuesta inmediata y sabe que el producto sí fue añadido.

### 4.3 Etiqueta de stock en la tarjeta

Cada tarjeta muestra una etiqueta verde con las unidades disponibles y, debajo del precio, las tallas existentes.

El usuario decide si vale la pena abrir la ficha sin necesidad de hacerlo. Si el producto está agotado, la etiqueta cambia y lo comunica de inmediato.

### 4.4 Ficha de producto en ventana emergente

Al pulsar una tarjeta se abre una ficha con la imagen, la descripción, las tallas con su stock individual y un selector de cantidad.

Esta decisión surgió de una necesidad concreta: al incorporar varias tallas por producto, el botón directo de "agregar al carrito" dejó de tener sentido, porque el sistema no puede adivinar qué talla desea el usuario. La ficha resuelve la elección sin abandonar el catálogo, que es lo que ocurriría con una página de producto independiente.

El selector de cantidad se detiene en el stock de la talla elegida y explica el motivo. Antes de agregar, el sistema vuelve a comprobar la disponibilidad contra el servidor.

### 4.5 Uso de “Continuar al pago”

En una versión inicial se utilizaba el texto “Finalizar compra”, aunque todavía faltaba completar información. Se cambió a `Continuar al pago` para que el botón describa correctamente el siguiente paso.

### 4.6 Inicio de sesión al momento de pagar

El usuario puede revisar productos y preparar el carrito sin crear previamente una cuenta. La autenticación se solicita cuando intenta continuar al pago.

Si es necesario iniciar sesión, la dirección de destino se conserva mediante `login.html?destino=pago`. Después de autenticarse, el usuario puede regresar al proceso sin perder el carrito.

### 4.7 Errores junto al campo

Los errores se muestran debajo del campo correspondiente mediante un elemento `<small class="error">`. También se cambia visualmente el borde para facilitar su identificación.

Este enfoque evita que la persona tenga que cerrar una alerta y luego buscar qué campo produjo el problema.

### 4.8 Respuestas del servidor ubicadas correctamente

Las validaciones del navegador y del servidor no siempre comprueban lo mismo. Por ejemplo, el navegador puede revisar la longitud de la cédula mientras Python valida su dígito verificador. Cuando la API rechaza un valor, también informa a qué campo corresponde para que JavaScript coloque el mensaje en el lugar adecuado.

### 4.9 Estado de procesamiento

Cuando se envía un formulario, el botón se deshabilita temporalmente y muestra textos como `Ingresando...`, `Creando cuenta...`, `Procesando pago...` o `Reponiendo...`.

Esto informa al usuario de que la operación sigue en curso y disminuye la posibilidad de enviar el mismo formulario varias veces.

### 4.10 Productos y tallas sin stock

Un producto agotado continúa visible, pero su botón se deshabilita y muestra el texto `Agotado`. Dentro de la ficha ocurre lo mismo con cada talla: las que no tienen unidades aparecen deshabilitadas, en lugar de ocultarse.

Mostrarlas comunica que la talla existe en el catálogo y puede reponerse, mientras que ocultarla haría pensar que la marca no la fabrica.

### 4.11 Confirmación basada en información de la base

La pantalla final consulta el pedido mediante su código. De esta manera, el comprobante mostrado corresponde a los datos realmente almacenados y no a valores que podrían haberse modificado en el navegador.

### 4.12 Construcción del DOM sin `innerHTML`

Tanto la ficha de producto como las tablas del panel se construyen con `document.createElement()` y `textContent`.

El nombre de un producto o el texto de un mensaje de contacto son datos, no marcado. Si se insertaran como HTML, un texto que contuviera etiquetas se ejecutaría en el navegador. Con `textContent` se muestran como texto, que es el comportamiento correcto y coherente con lo declarado en el documento de seguridad.

### 4.13 Acceso al panel solo para administradores

El enlace al panel se agrega al menú de usuario desde JavaScript cuando la sesión es administrativa, y en ese caso se oculta el acceso al carrito.

Antes de este cambio, salir del panel obligaba a escribir la dirección a mano para volver. Resolverlo desde JavaScript evita duplicar el enlace en las trece páginas y garantiza que aparezca únicamente a quien corresponde. El menú indica además el rol de la sesión activa.

### 4.14 Indicadores en el panel administrativo

La pestaña de reportes comienza con cinco tarjetas que resumen productos, clientes, pedidos, mensajes sin leer y alertas de stock.

El administrador conoce el estado general del negocio sin leer ninguna tabla. La tarjeta de alertas cambia de color cuando existe al menos un producto en nivel crítico.

### 4.15 Reposición desde la propia tabla

En el inventario, cada fila incluye un botón que rellena automáticamente el formulario de reposición con ese producto y esa talla.

Evita que el administrador tenga que copiar códigos a mano, que es donde se producen la mayoría de los errores. Las filas en nivel crítico se resaltan en amarillo y las agotadas en rojo.

### 4.16 Lectura completa de los mensajes

En la tabla de mensajes cada fila es pulsable y abre una ventana con el remitente, su correo, la ciudad, la fecha y el texto íntegro, además de un botón para responder por correo.

Una tabla no puede mostrar un mensaje largo sin volverse ilegible, pero el administrador necesita leerlo completo para poder responder.

## 5. Diseño adaptable

Se utilizan cuatro puntos de quiebre:

| Ancho | Cambio principal |
|-------|------------------|
| ≤ 992 px | La rejilla pasa de tres a dos columnas |
| ≤ 768 px | Se activa el menú hamburguesa |
| ≤ 600 px | Los formularios pasan a una columna |
| ≤ 480 px | La interfaz utiliza una sola columna y ajusta la tipografía |

La interfaz fue revisada a 375 px, comprobando que no exista desplazamiento horizontal, que el menú móvil funcione y que los controles puedan utilizarse correctamente.

Las tablas del panel se colocan dentro de un contenedor con desplazamiento propio, de modo que el contenido ancho no obligue a desplazar toda la página.

### Organización del CSS

| Archivo | Responsabilidad |
|---------|-----------------|
| `base.css` | Variables, reinicio y tipografía |
| `layout.css` | Cabecera, pie, rejillas y contenedores |
| `components.css` | Botones, tarjetas, formularios, tablas, ventanas emergentes y panel |
| `responsive.css` | Adaptaciones para los diferentes anchos |

Separar el CSS por responsabilidad facilita el mantenimiento y reduce los conflictos cuando varias personas trabajan en el proyecto.

Durante el desarrollo apareció un problema derivado de esta organización: la regla general `.form-group label` usaba color blanco, pensada para los formularios sobre fondo oscuro. Al reutilizar esa clase en el panel, que tiene fondo claro, las etiquetas resultaban invisibles. Se resolvió con una regla más específica limitada al panel, sin modificar el comportamiento del resto del sitio.

## 6. Accesibilidad

Se implementaron diferentes medidas:

- 64 imágenes cuentan con texto alternativo;
- existen 42 atributos `aria-label` en controles sin texto visible;
- 21 campos poseen su `label` asociado;
- se utiliza HTML semántico como `header`, `nav`, `main`, `section`, `article`, `aside` y `footer`;
- el menú de usuario y la ficha de producto pueden cerrarse con Escape;
- los botones de talla incluyen un `title` con la descripción y las unidades disponibles;
- se mantiene contraste entre texto y fondo.

Estas medidas ayudan a que la interfaz pueda ser comprendida y utilizada por más personas.

## 7. Rendimiento

El favicon original fue reducido de 1813 KB a 12,6 KB mediante una versión PNG de 192 × 192 píxeles, lo que representa una disminución aproximada del 99,3 %.

Font Awesome se carga desde un CDN utilizando `integrity` (SRI), por lo que el navegador puede verificar el recurso externo.

El catálogo se solicita una sola vez por página y queda en memoria; la ficha de producto consulta el detalle únicamente cuando el usuario la abre. De esta manera se evitan peticiones innecesarias al mostrar la lista.

El proyecto utiliza JavaScript nativo distribuido en 9 archivos, sin jQuery, React ni un proceso adicional de compilación. Esto mantiene el proyecto más ligero y sencillo de ejecutar.