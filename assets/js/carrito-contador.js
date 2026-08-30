const RGE_CLAVE_CARRITO  = "rge_carrito";
const RGE_CLAVE_PEDIDO   = "rge_ultimo_pedido";
const RGE_CLAVE_NUMERO   = "rge_numero_pedido";
const RGE_CLAVE_SESION   = "rge_sesion";
const RGE_CLAVE_USUARIOS = "rge_usuarios";
const RGE_IVA = 0.15;

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

function rgeLeerUsuarios() {
    try {
        const datos = localStorage.getItem(RGE_CLAVE_USUARIOS);
        const lista = datos ? JSON.parse(datos) : [];
        return Array.isArray(lista) ? lista : [];
    } catch (error) {
        console.error("No se pudo leer la lista de usuarios:", error);
        return [];
    }
}

function rgeRegistrarUsuario(usuario) {
    const lista = rgeLeerUsuarios();

    const existe = lista.some(function (u) {
        return u.email.toLowerCase() === usuario.email.toLowerCase();
    });

    if (existe) {
        return false;
    }

    lista.push(usuario);
    localStorage.setItem(RGE_CLAVE_USUARIOS, JSON.stringify(lista));
    return true;
}

function rgeBuscarUsuario(email) {
    return rgeLeerUsuarios().find(function (u) {
        return u.email.toLowerCase() === email.toLowerCase();
    }) || null;
}

function rgeLeerSesion() {
    try {
        const datos = localStorage.getItem(RGE_CLAVE_SESION);
        return datos ? JSON.parse(datos) : null;
    } catch (error) {
        console.error("No se pudo leer la sesion:", error);
        return null;
    }
}

function rgeAbrirSesion(usuario) {
    localStorage.setItem(RGE_CLAVE_SESION, JSON.stringify(usuario));
    rgeAplicarEstadoSesion();
}

function rgeCerrarSesion() {
    localStorage.removeItem(RGE_CLAVE_SESION);
    rgeAplicarEstadoSesion();
}

function rgeHaySesion() {
    return rgeLeerSesion() !== null;
}

function rgeAplicarEstadoSesion() {
    const sesion = rgeLeerSesion();
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
        saludo.textContent = sesion ? sesion.nombres + " " + sesion.apellidos : "";
    }

    const boton = document.getElementById("btn-usuario");
    if (boton) {
        boton.title = sesion ? "Sesion de " + sesion.nombres : "Iniciar sesion";
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
        salir.addEventListener("click", function () {
            rgeCerrarSesion();
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
    rgeAplicarEstadoSesion();
    rgeIniciarMenuUsuario();
});