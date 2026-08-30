document.addEventListener("DOMContentLoaded", function () {

    const formLogin    = document.getElementById("loginForm");
    const formRegistro = document.getElementById("registroForm");

    if (!formLogin && !formRegistro) {
        return;
    }

    const cedulaRegex = /^[0-9]{10}$/;

    const parametros = new URLSearchParams(window.location.search);
    const vieneDelCarrito = parametros.get("destino") === "pago";
    const destino = vieneDelCarrito ? "pago.html" : "productos.html";
    const sufijo  = vieneDelCarrito ? "?destino=pago" : "";

    const enlaceCruzado = document.getElementById("enlace-cruzado");
    if (enlaceCruzado) {
        enlaceCruzado.href = enlaceCruzado.getAttribute("data-destino") + sufijo;
    }

    const avisoCheckout = document.getElementById("aviso-checkout");
    if (vieneDelCarrito && avisoCheckout) {
        avisoCheckout.classList.remove("oculto");
    }

    if (formLogin) {
        formLogin.addEventListener("submit", function (event) {
            event.preventDefault();

            let valido = true;

            const email = document.getElementById("login-email");
            if (!rgeEmailValido(email.value)) {
                mostrarError(email, "Ingrese un correo válido.");
                valido = false;
            } else {
                limpiarError(email);
            }

            const password = document.getElementById("login-password");
            if (password.value.trim() === "") {
                mostrarError(password, "Ingrese su contraseña.");
                valido = false;
            } else {
                limpiarError(password);
            }

            if (!valido) {
                return;
            }

            const usuario = rgeBuscarUsuario(email.value.trim());

            if (!usuario) {
                mostrarError(email, "No existe una cuenta con este correo. Cree una cuenta.");
                return;
            }

            rgeAbrirSesion(usuario);
            rgeNotificar("Bienvenido de nuevo, " + usuario.nombres, "exito");

            setTimeout(function () {
                window.location.href = destino;
            }, 900);
        });
    }

    if (formRegistro) {
        formRegistro.addEventListener("submit", function (event) {
            event.preventDefault();

            let valido = true;

            const nombres = document.getElementById("reg-nombres");
            if (nombres.value.trim().length < 3) {
                mostrarError(nombres, "Los nombres deben tener al menos 3 caracteres.");
                valido = false;
            } else {
                limpiarError(nombres);
            }

            const apellidos = document.getElementById("reg-apellidos");
            if (apellidos.value.trim().length < 3) {
                mostrarError(apellidos, "Los apellidos deben tener al menos 3 caracteres.");
                valido = false;
            } else {
                limpiarError(apellidos);
            }

            const cedula = document.getElementById("reg-cedula");
            if (!cedulaRegex.test(cedula.value.trim())) {
                mostrarError(cedula, "La cédula debe tener exactamente 10 dígitos.");
                valido = false;
            } else {
                limpiarError(cedula);
            }

            const email = document.getElementById("reg-email");
            if (!rgeEmailValido(email.value)) {
                mostrarError(email, "Ingrese un correo válido. Aquí recibirá su recibo.");
                valido = false;
            } else if (rgeBuscarUsuario(email.value.trim())) {
                mostrarError(email, "Ya existe una cuenta con este correo.");
                valido = false;
            } else {
                limpiarError(email);
            }

            const ciudad = document.getElementById("reg-ciudad");
            if (ciudad.value === "") {
                mostrarError(ciudad, "Seleccione una ciudad.");
                valido = false;
            } else {
                limpiarError(ciudad);
            }

            const password = document.getElementById("reg-password");
            if (password.value.length < 8) {
                mostrarError(password, "La contraseña debe tener al menos 8 caracteres.");
                valido = false;
            } else {
                limpiarError(password);
            }

            if (!valido) {
                return;
            }

            const nuevoUsuario = {
                nombres:   nombres.value.trim(),
                apellidos: apellidos.value.trim(),
                cedula:    cedula.value.trim(),
                email:     email.value.trim(),
                telefono:  document.getElementById("reg-telefono").value.trim(),
                id_ciudad: ciudad.value,
                ciudad:    ciudad.options[ciudad.selectedIndex].text.trim()
            };

            if (!rgeRegistrarUsuario(nuevoUsuario)) {
                mostrarError(email, "Ya existe una cuenta con este correo.");
                return;
            }

            rgeAbrirSesion(nuevoUsuario);
            rgeNotificar("Cuenta creada. Bienvenido, " + nuevoUsuario.nombres, "exito");

            setTimeout(function () {
                window.location.href = destino;
            }, 900);
        });
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

});