// ============================================================
// PAGO.JS
// Solo en pago.html. Comprueba la sesion, arma el resumen,
// valida el formulario y registra el pedido en la base.
// ============================================================
document.addEventListener("DOMContentLoaded", async function () {

    const formulario = document.getElementById("pagoForm");

    if (!formulario) {
        return;
    }


// ---------------- Comprobar que haya sesion ----------------
// Sin sesion no se puede pagar: manda al login
    const sesion = await rgeCargarSesion();

    if (!sesion) {
        rgeNotificar("Debes iniciar sesion para pagar", "aviso");
        setTimeout(function () {
            window.location.href = "login.html?destino=pago";
        }, 1200);
        return;
    }


// ---------------- Comprobar que el carrito no este vacio ----------------
    const carrito = await rgeSincronizarCarrito();

    if (carrito.length === 0) {
        rgeNotificar("Tu carrito esta vacio", "aviso");
        setTimeout(function () {
            window.location.href = "productos.html";
        }, 1200);
        return;
    }

    const campoNombre = document.getElementById("pago-nombre");
    const campoEmail  = document.getElementById("pago-email");

    campoNombre.value = sesion.nombre;
    campoEmail.value  = sesion.email;


// ---------------- Traer los metodos de pago de la base ----------------
    let metodosPago = [];

    try {
        const datos = await rgeApi("/pedidos/metodos-pago");
        metodosPago = datos.metodos;
    } catch (error) {
        rgeNotificar(error.mensaje, "aviso");
    }

    await pintarResumen(carrito);

    formulario.addEventListener("submit", async function (evento) {
        evento.preventDefault();

        if (!validarPago()) {
            return;
        }

        await procesarPago();
    });


// ---------------- Resumen del pedido ----------------
// Los totales los calcula el servidor
    async function pintarResumen(items) {
        const contenedor = document.getElementById("pago-items");
        contenedor.textContent = "";

        items.forEach(function (item) {
            const fila = document.createElement("div");
            fila.className = "pago-item";

            const nombre = document.createElement("span");
            nombre.className = "pago-item-nombre";
            nombre.textContent = item.nombre + "  x" + item.cantidad;

            const precio = document.createElement("span");
            precio.className = "pago-item-precio";
            precio.textContent = rgeFormatearPrecio(item.precio * item.cantidad);

            fila.appendChild(nombre);
            fila.appendChild(precio);
            contenedor.appendChild(fila);
        });

        let totales;

        try {
            totales = await rgeCalcularTotalesServidor(items);
        } catch (error) {
            rgeNotificar(error.mensaje, "aviso");
            totales = rgeCalcularTotales(items);
        }

        document.getElementById("pago-subtotal").textContent = rgeFormatearPrecio(totales.subtotal);
        document.getElementById("pago-iva").textContent      = rgeFormatearPrecio(totales.iva);
        document.getElementById("pago-total").textContent    = rgeFormatearPrecio(totales.total);
    }


// ---------------- Quitar tildes para comparar ----------------
// El HTML dice 'Tarjeta de credito' con tilde y la base sin tilde
    function sinTildes(texto) {
        return String(texto)
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .trim()
            .toLowerCase();
    }


// ---------------- Saber que metodo eligio el usuario ----------------
    function idMetodoSeleccionado() {
        const marcado = document.querySelector('input[name="metodo"]:checked');

        if (!marcado) {
            return null;
        }

        const encontrado = metodosPago.find(function (metodo) {
            return sinTildes(metodo.nombre) === sinTildes(marcado.value);
        });

        return encontrado ? encontrado.id_metodo : null;
    }


// ---------------- Validar el formulario ----------------
    function validarPago() {
        let valido = true;

        if (!rgeEmailValido(campoEmail.value)) {
            mostrarError(campoEmail, "Ingrese un correo válido para recibir su recibo.");
            valido = false;
        } else {
            limpiarError(campoEmail);
        }

        const direccion = document.getElementById("pago-direccion");
        if (direccion.value.trim().length < 5) {
            mostrarError(direccion, "Ingrese una dirección de entrega válida.");
            valido = false;
        } else {
            limpiarError(direccion);
        }

        const errorMetodo = document.getElementById("error-metodo");
        if (idMetodoSeleccionado() === null) {
            errorMetodo.textContent = "Seleccione un método de pago.";
            valido = false;
        } else {
            errorMetodo.textContent = "";
        }

        const confirmo = document.getElementById("pago-confirmo");
        if (!confirmo.checked) {
            mostrarErrorGrupo(confirmo, "Debe confirmar el pago para continuar.");
            valido = false;
        } else {
            limpiarErrorGrupo(confirmo);
        }

        return valido;
    }


// ---------------- Registrar el pedido ----------------
// Manda los items con su id_producto_talla y guarda el codigo del pedido
    async function procesarPago() {
        const boton = formulario.querySelector('button[type="submit"]');
        const textoOriginal = boton ? boton.textContent : "";

        if (boton) {
            boton.disabled = true;
            boton.textContent = "Procesando pago...";
        }

        const items = rgeLeerCarrito().map(function (item) {
            return {
                id_producto_talla: item.id_producto_talla,
                cantidad: item.cantidad
            };
        });

        try {
            const respuesta = await rgeApi("/pedidos", {
                cuerpo: {
                    items: items,
                    email: campoEmail.value.trim(),
                    id_metodo_pago: idMetodoSeleccionado(),
                    direccion: document.getElementById("pago-direccion").value.trim(),
                    referencia: document.getElementById("pago-referencia").value.trim()
                }
            });

            localStorage.setItem(RGE_CLAVE_PEDIDO, respuesta.pedido.codigo_pedido);
            rgeVaciarCarrito();

            rgeNotificar("Pago confirmado. Generando tu recibo...", "exito");

            setTimeout(function () {
                window.location.href = "gracias.html";
            }, 1000);

        } catch (error) {
            if (boton) {
                boton.disabled = false;
                boton.textContent = textoOriginal;
            }

            if (error.codigo === "STOCK_INSUFICIENTE") {
                rgeNotificar(error.mensaje, "aviso");
                await rgeSincronizarCarrito();
                await pintarResumen(rgeLeerCarrito());
                return;
            }

            if (error.codigo === "SIN_SESION") {
                rgeNotificar("Tu sesion expiro. Inicia sesion de nuevo.", "aviso");
                setTimeout(function () {
                    window.location.href = "login.html?destino=pago";
                }, 1200);
                return;
            }

            if (error.campo === "direccion" || error.campo === "id_ciudad") {
                mostrarError(document.getElementById("pago-direccion"), error.mensaje);
                return;
            }

            rgeNotificar(error.mensaje, "aviso");
        }
    }


// ---------------- Mostrar y limpiar errores ----------------
    function mostrarError(elemento, mensaje) {
        const grupo = elemento.parentElement;
        const errorDisplay = grupo.querySelector(".error");

        if (errorDisplay) {
            errorDisplay.textContent = mensaje;
        }
        elemento.classList.add("error-input");
    }

    function limpiarError(elemento) {
        const grupo = elemento.parentElement;
        const errorDisplay = grupo.querySelector(".error");

        if (errorDisplay) {
            errorDisplay.textContent = "";
        }
        elemento.classList.remove("error-input");
    }

    function mostrarErrorGrupo(elemento, mensaje) {
        const grupo = elemento.closest(".form-group");
        const errorDisplay = grupo ? grupo.querySelector(".error") : null;

        if (errorDisplay) {
            errorDisplay.textContent = mensaje;
        }
    }

    function limpiarErrorGrupo(elemento) {
        const grupo = elemento.closest(".form-group");
        const errorDisplay = grupo ? grupo.querySelector(".error") : null;

        if (errorDisplay) {
            errorDisplay.textContent = "";
        }
    }

});