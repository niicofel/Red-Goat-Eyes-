const RGE_CLAVE_CARRITO = "rge_carrito";
const RGE_CLAVE_PEDIDO  = "rge_ultimo_pedido";
const RGE_API = "/api";
const RGE_IVA = 0.15;

let rgeSesionActual = null;
let rgeCatalogoCache = null;

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

        item.id_producto_talla = real.id_producto_talla;
        item.nombre = real.nombre;
        item.precio = real.precio_final;
        item.stock  = real.stock;

        if (item.cantidad > real.stock) {
            item.cantidad = real.stock;
        }

        if (item.cantidad > 0) {
            vigentes.push(item);
        }
    });

    rgeGuardarCarrito(vigentes);
    return vigentes;
}

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
}

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

const RGE_REGEX_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

function rgeEmailValido(email) {
    return RGE_REGEX_EMAIL.test(String(email).trim());
}

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

document.addEventListener("DOMContentLoaded", function () {
    rgeActualizarContador();
    rgeIniciarMenuUsuario();
    rgeCargarSesion();
});