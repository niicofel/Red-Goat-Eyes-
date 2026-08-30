document.addEventListener("DOMContentLoaded", function () {

    const formulario = document.getElementById("pagoForm");
    if (!formulario) {
        return;
    }

    const sesion = rgeLeerSesion();

    if (!sesion) {
        rgeNotificar("Debes iniciar sesion para pagar", "aviso");
        setTimeout(function () {
            window.location.href = "login.html?destino=pago";
        }, 1200);
        return;
    }

    const carrito = rgeLeerCarrito();

    if (carrito.length === 0) {
        rgeNotificar("Tu carrito esta vacio", "aviso");
        setTimeout(function () {
            window.location.href = "productos.html";
        }, 1200);
        return;
    }

    const campoNombre = document.getElementById("pago-nombre");
    const campoEmail  = document.getElementById("pago-email");

    campoNombre.value = sesion.nombres + " " + sesion.apellidos;
    campoEmail.value  = sesion.email;

    pintarResumen(carrito);

    formulario.addEventListener("submit", function (evento) {
        evento.preventDefault();

        if (!validarPago()) {
            return;
        }

        procesarPago(carrito);
    });

    function pintarResumen(items) {
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

        const totales = rgeCalcularTotales(items);

        document.getElementById("pago-subtotal").textContent = rgeFormatearPrecio(totales.subtotal);
        document.getElementById("pago-iva").textContent      = rgeFormatearPrecio(totales.iva);
        document.getElementById("pago-total").textContent    = rgeFormatearPrecio(totales.total);
    }

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

        const metodo = document.querySelector('input[name="metodo"]:checked');
        const errorMetodo = document.getElementById("error-metodo");
        if (!metodo) {
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

    function generarCodigo() {
        const anio = new Date().getFullYear();
        const guardado = localStorage.getItem(RGE_CLAVE_NUMERO) || "0";
        const numero = parseInt(guardado, 10) + 1;

        localStorage.setItem(RGE_CLAVE_NUMERO, numero);

        return "RGE-" + anio + "-" + String(numero).padStart(4, "0");
    }

    function procesarPago(items) {
        const totales = rgeCalcularTotales(items);
        const metodo  = document.querySelector('input[name="metodo"]:checked');

        const pedido = {
            codigo:   generarCodigo(),
            fecha:    new Date().toISOString(),
            estado:   "Pagado",
            items:    items,
            subtotal: Number(totales.subtotal.toFixed(2)),
            iva:      Number(totales.iva.toFixed(2)),
            total:    Number(totales.total.toFixed(2)),
            metodo_pago: metodo.value,
            cliente: {
                nombres:   sesion.nombres,
                apellidos: sesion.apellidos,
                cedula:    sesion.cedula,
                email:     campoEmail.value.trim(),
                ciudad:    sesion.ciudad
            },
            entrega: {
                direccion:  document.getElementById("pago-direccion").value.trim(),
                referencia: document.getElementById("pago-referencia").value.trim()
            }
        };

        try {
            localStorage.setItem(RGE_CLAVE_PEDIDO, JSON.stringify(pedido));
            localStorage.removeItem(RGE_CLAVE_CARRITO);
        } catch (error) {
            console.error("No se pudo registrar el pedido:", error);
            rgeNotificar("No se pudo procesar el pago", "aviso");
            return;
        }


        rgeNotificar("Pago confirmado. Generando tu recibo...", "exito");

        setTimeout(function () {
            window.location.href = "gracias.html";
        }, 1000);
    }


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