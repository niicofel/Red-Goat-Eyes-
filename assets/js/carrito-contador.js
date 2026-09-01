// ============================================================
// CARRITO-CONTADOR.JS
// Se carga en las 13 paginas. Aqui vive todo lo compartido:
// hablar con la API, la sesion, el carrito y las notificaciones.
// Los demas archivos usan las funciones que estan aqui.
// ============================================================
// ---------------- Constantes del sistema ----------------
// RGE_API es la direccion base de la API. Todo cuelga de /api
const RGE_CLAVE_CARRITO = "rge_carrito";
const RGE_CLAVE_PEDIDO  = "rge_ultimo_pedido";
const RGE_API = "/api";
const RGE_IVA = 0.15;

let rgeSesionActual = null;
let rgeCatalogoCache = null;


// ---------------- Hablar con la API ----------------
// Envuelve fetch: arma el JSON, y si algo falla lanza un error con codigo y mensaje
async function rgeApi(ruta, opciones) {
    const config = Object.assign({
        credentials: "same-origin",
        headers: { "Accept": "application/json" }
    }, opciones || {});

    if (config.cuerpo !== undefined) {
        config.method = config.method || "POST";
        config.headers["Content-Type"] = "application/json";
        config.body = JSON.stringify(config.cuerpo);
        delete config.cuerpo;
    }

    let respuesta;

    try {
        respuesta = await fetch(RGE_API + ruta, config);
    } catch (error) {
        throw {
            codigo: "SIN_CONEXION",
            estado: 0,
            mensaje: "No se pudo conectar con el servidor. Verifica que Flask este corriendo."
        };
    }

    let datos = null;

    try {
        datos = await respuesta.json();
    } catch (error) {
        datos = null;
    }

    if (!respuesta.ok) {
        throw {
            codigo: (datos && datos.error) || "ERROR",
            estado: respuesta.status,
            mensaje: (datos && datos.mensaje) || "Ocurrio un error inesperado",
            campo: datos && datos.campo
        };
    }

    return datos;
}


// ---------------- Leer y guardar el carrito ----------------
// El carrito vive en localStorage, o sea en el navegador del usuario
function rgeLeerCarrito() {
    try {
        const datos = localStorage.getItem(RGE_CLAVE_CARRITO);
        const carrito = datos ? JSON.parse(datos) : [];
        return Array.isArray(carrito) ? carrito : [];
    } catch (error) {
        console.error("No se pudo leer el carrito:", error);
        return [];
    }
}

function rgeGuardarCarrito(carrito) {
    try {
        localStorage.setItem(RGE_CLAVE_CARRITO, JSON.stringify(carrito));
        rgeActualizarContador();
    } catch (error) {
        console.error("No se pudo guardar el carrito:", error);
    }
}

function rgeVaciarCarrito() {
    localStorage.removeItem(RGE_CLAVE_CARRITO);
    rgeActualizarContador();
}


// ---------------- Contador del icono del carrito ----------------
function rgeContarUnidades() {
    return rgeLeerCarrito().reduce(function (suma, item) {
        return suma + item.cantidad;
    }, 0);
}

function rgeActualizarContador() {
    const contador = document.getElementById("carrito-contador");

    if (!contador) {
        return;
    }

    const total = rgeContarUnidades();
    contador.textContent = total;
    contador.style.display = total > 0 ? "flex" : "none";
}


// ---------------- Catalogo en memoria ----------------
// Se pide una sola vez por pagina y se guarda para no repetir la peticion
async function rgeCatalogo() {
    if (rgeCatalogoCache) {
        return rgeCatalogoCache;
    }

    const datos = await rgeApi("/productos");
    rgeCatalogoCache = datos.productos;
    return rgeCatalogoCache;
}

async function rgeBuscarPorCodigo(codigo) {
    const catalogo = await rgeCatalogo();

    return catalogo.find(function (producto) {
        return producto.codigo === codigo;
    }) || null;
}


// ---------------- Actualizar precios del carrito ----------------
// Refresca nombre y precio desde la API, por si cambiaron
async function rgeSincronizarCarrito() {
    const carrito = rgeLeerCarrito();

    if (carrito.length === 0) {
        return [];
    }

    let catalogo;

    try {
        catalogo = await rgeCatalogo();
    } catch (error) {
        return carrito;
    }

    const vigentes = [];

    carrito.forEach(function (item) {
        const real = catalogo.find(function (producto) {
            return producto.codigo === item.codigo;
        });

        if (!real) {
            return;
        }


        item.nombre = real.nombre;
        item.precio = real.precio_final;

        if (item.cantidad > 0) {
            vigentes.push(item);
        }

    });

    rgeGuardarCarrito(vigentes);
    return vigentes;
}


// ---------------- Sesion del usuario ----------------
// Pregunta al servidor quien esta conectado y marca el body con con-sesion o sin-sesion
async function rgeCargarSesion() {
    try {
        const datos = await rgeApi("/auth/sesion");
        rgeSesionActual = datos.autenticado ? datos.usuario : null;
    } catch (error) {
        rgeSesionActual = null;
    }

    rgeAplicarEstadoSesion();
    return rgeSesionActual;
}

function rgeLeerSesion() {
    return rgeSesionActual;
}

function rgeHaySesion() {
    return rgeSesionActual !== null;
}

function rgeEsAdministrador() {
    return rgeSesionActual !== null && rgeSesionActual.rol === "administrador";
}

async function rgeCerrarSesion() {
    try {
        await rgeApi("/auth/logout", { method: "POST" });
    } catch (error) {
        console.error("No se pudo cerrar la sesion:", error);
    }

    rgeSesionActual = null;
    rgeAplicarEstadoSesion();
}


// ---------------- Mostrar u ocultar segun quien seas ----------------
// Pone las clases en el body; el CSS se encarga del resto
function rgeAplicarEstadoSesion() {
    const sesion = rgeSesionActual;
    const cuerpo = document.body;

    if (sesion) {
        cuerpo.classList.add("con-sesion");
        cuerpo.classList.remove("sin-sesion");
    } else {
        cuerpo.classList.add("sin-sesion");
        cuerpo.classList.remove("con-sesion");
    }

    const saludo = document.getElementById("usuario-saludo");

    if (saludo) {
        saludo.textContent = sesion ? sesion.nombre : "";
    }

    const boton = document.getElementById("btn-usuario");

    if (boton) {
        boton.title = sesion ? "Sesion de " + sesion.nombre : "Iniciar sesion";
        boton.classList.toggle("sesion-activa", Boolean(sesion));
    }

    cuerpo.classList.toggle("es-admin", rgeEsAdministrador());

    rgeMostrarRol();
    rgeEnlaceAdministracion();
}



// ---------------- Calcular la ruta correcta ----------------
// Desde la raiz hace falta pages/, desde dentro de pages/ no
function rgeRutaPaginas() {
    return window.location.pathname.indexOf("/pages/") !== -1 ? "" : "pages/";
}



// ---------------- Mostrar el rol en el menu ----------------
function rgeMostrarRol() {
    const menu = document.getElementById("usuario-dropdown");

    if (!menu) {
        return;
    }

    let etiqueta = menu.querySelector(".usuario-rol");

    if (!rgeSesionActual) {
        if (etiqueta) {
            etiqueta.remove();
        }
        return;
    }

    if (!etiqueta) {
        etiqueta = document.createElement("li");
        etiqueta.className = "usuario-rol";

        const saludo = document.getElementById("usuario-saludo");

        if (saludo && saludo.parentNode) {
            saludo.parentNode.insertBefore(etiqueta, saludo.nextSibling);
        } else {
            menu.insertBefore(etiqueta, menu.firstChild);
        }
    }

    etiqueta.textContent = rgeEsAdministrador() ? "Administrador" : "Cliente";
    etiqueta.classList.toggle("rol-admin", rgeEsAdministrador());
}



// ---------------- Enlace al panel solo para admin ----------------
// Se agrega desde JavaScript para no repetirlo en los 13 HTML
function rgeEnlaceAdministracion() {
    const menu = document.getElementById("usuario-dropdown");

    if (!menu) {
        return;
    }

    const enlaceCarrito = menu.querySelector('a[href$="carrito.html"]');

    if (enlaceCarrito && enlaceCarrito.parentNode) {
        enlaceCarrito.parentNode.style.display = rgeEsAdministrador() ? "none" : "";
    }

    let item = menu.querySelector(".solo-admin");

    if (!rgeEsAdministrador()) {
        if (item) {
            item.remove();
        }
        return;
    }

    if (item) {
        return;
    }

    item = document.createElement("li");
    item.className = "solo-admin";

    const enlace = document.createElement("a");
    enlace.href = rgeRutaPaginas() + "admin.html";
    enlace.textContent = "Panel de administracion";
    item.appendChild(enlace);

    const salir = document.getElementById("btn-salir");

    if (salir && salir.parentNode) {
        menu.insertBefore(item, salir.parentNode);
    } else {
        menu.appendChild(item);
    }
}


// ---------------- Menu desplegable del usuario ----------------
// Se cierra al hacer clic fuera o con la tecla Escape
function rgeIniciarMenuUsuario() {
    const boton = document.getElementById("btn-usuario");
    const menu  = document.getElementById("usuario-dropdown");

    if (!boton || !menu) {
        return;
    }

    boton.addEventListener("click", function (evento) {
        evento.stopPropagation();
        const abierto = menu.classList.toggle("abierto");
        boton.setAttribute("aria-expanded", abierto ? "true" : "false");
    });

    document.addEventListener("click", function (evento) {
        if (!menu.contains(evento.target) && evento.target !== boton) {
            menu.classList.remove("abierto");
            boton.setAttribute("aria-expanded", "false");
        }
    });

    document.addEventListener("keydown", function (evento) {
        if (evento.key === "Escape") {
            menu.classList.remove("abierto");
            boton.setAttribute("aria-expanded", "false");
        }
    });

    const salir = document.getElementById("btn-salir");

    if (salir) {
        salir.addEventListener("click", async function () {
            await rgeCerrarSesion();
            menu.classList.remove("abierto");
            rgeNotificar("Sesion cerrada", "aviso");

            setTimeout(function () {
                window.location.reload();
            }, 900);
        });
    }
}


// ---------------- Formato de precios y totales ----------------
// rgeCalcularTotales es un respaldo; lo normal es pedirlos al servidor
function rgeFormatearPrecio(valor) {
    return "$" + Number(valor).toFixed(2);
}

function rgeCalcularTotales(carrito) {
    const subtotal = carrito.reduce(function (suma, item) {
        return suma + (item.precio * item.cantidad);
    }, 0);

    const iva = subtotal * RGE_IVA;

    return {
        subtotal: subtotal,
        iva: iva,
        total: subtotal + iva
    };
}

async function rgeCalcularTotalesServidor(carrito) {
    const items = carrito.map(function (item) {
        return {
            id_producto_talla: item.id_producto_talla,
            cantidad: item.cantidad
        };
    });

    return await rgeApi("/pedidos/calcular", { cuerpo: { items: items } });
}


// ---------------- Validacion de correo ----------------
const RGE_REGEX_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function rgeEmailValido(email) {
    return RGE_REGEX_EMAIL.test(String(email).trim());
}


// ---------------- Notificacion flotante ----------------
// El mensajito que aparece arriba y se va solo a los 2.6 segundos
function rgeNotificar(mensaje, tipo) {
    const anterior = document.querySelector(".notificacion");

    if (anterior) {
        anterior.remove();
    }

    const aviso = document.createElement("div");
    aviso.className = "notificacion " + (tipo || "exito");
    aviso.textContent = mensaje;
    document.body.appendChild(aviso);

    requestAnimationFrame(function () {
        aviso.classList.add("visible");
    });

    setTimeout(function () {
        aviso.classList.remove("visible");
        setTimeout(function () {
            aviso.remove();
        }, 300);
    }, 2600);
}


// ---------------- Arranque ----------------
// Se ejecuta cuando el HTML termino de cargar
document.addEventListener("DOMContentLoaded", function () {
    rgeActualizarContador();
    rgeIniciarMenuUsuario();
    rgeCargarSesion();
});