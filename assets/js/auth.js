document.addEventListener("DOMContentLoaded", async function () {

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

    const selectCiudad = document.getElementById("reg-ciudad");
    if (selectCiudad) {
        await cargarCiudades(selectCiudad);
    }

    if (formLogin) {
        formLogin.addEventListener("submit", async function (evento) {
            evento.preventDefault();

            const email    = document.getElementById("login-email");
            const password = document.getElementById("login-password");

            let valido = true;

            if (!rgeEmailValido(email.value)) {
                mostrarError(email, "Ingrese un correo válido.");
                valido = false;
            } else {
                limpiarError(email);
            }

            if (password.value.trim() === "") {
                mostrarError(password, "Ingrese su contraseña.");
                valido = false;
            } else {
                limpiarError(password);
            }

            if (!valido) {
                return;
            }

            const boton = formLogin.querySelector('button[type="submit"]');
            bloquear(boton, "Ingresando...");

            try {
                const datos = await rgeApi("/auth/login", {
                    cuerpo: {
                        email: email.value.trim(),
                        password: password.value
                    }
                });

                rgeNotificar("Bienvenido de nuevo, " + datos.usuario.nombres, "exito");

                setTimeout(function () {
                    window.location.href = datos.usuario.rol === "administrador"
                        ? "admin.html"
                        : destino;
                }, 900);

            } catch (error) {
                desbloquear(boton, "Iniciar sesión");

                if (error.codigo === "CREDENCIALES_INVALIDAS") {
                    mostrarError(password, "El correo o la contraseña no son correctos.");
                } else {
                    mostrarError(email, error.mensaje);
                }
            }
        });
    }

    if (formRegistro) {
        formRegistro.addEventListener("submit", async function (evento) {
            evento.preventDefault();

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

            const boton = formRegistro.querySelector('button[type="submit"]');
            bloquear(boton, "Creando cuenta...");

            try {
                const datos = await rgeApi("/auth/registro", {
                    cuerpo: {
                        nombres:   nombres.value.trim(),
                        apellidos: apellidos.value.trim(),
                        cedula:    cedula.value.trim(),
                        email:     email.value.trim(),
                        telefono:  document.getElementById("reg-telefono").value.trim(),
                        id_ciudad: parseInt(ciudad.value, 10),
                        password:  password.value
                    }
                });

                rgeNotificar("Cuenta creada. Bienvenido, " + datos.usuario.nombres, "exito");

                setTimeout(function () {
                    window.location.href = destino;
                }, 900);

            } catch (error) {
                desbloquear(boton, "Crear cuenta");
                mostrarErrorPorCampo(error);
            }
        });
    }

    async function cargarCiudades(select) {
        try {
            const datos = await rgeApi("/ciudades");

            select.textContent = "";

            const inicial = document.createElement("option");
            inicial.value = "";
            inicial.textContent = "Seleccione una ciudad";
            select.appendChild(inicial);

            datos.ciudades.forEach(function (ciudad) {
                const opcion = document.createElement("option");
                opcion.value = ciudad.id_ciudad;
                opcion.textContent = ciudad.nombre + " (" + ciudad.provincia + ")";
                select.appendChild(opcion);
            });

        } catch (error) {
            rgeNotificar(error.mensaje, "aviso");
        }
    }

    function mostrarErrorPorCampo(error) {
        const mapa = {
            email: "reg-email",
            password: "reg-password",
            cedula: "reg-cedula",
            nombres: "reg-nombres",
            apellidos: "reg-apellidos",
            telefono: "reg-telefono",
            id_ciudad: "reg-ciudad"
        };

        if (error.codigo === "USUARIO_DUPLICADO") {
            mostrarError(document.getElementById("reg-email"),
                "Ya existe una cuenta con este correo.");
            return;
        }

        const destinoCampo = mapa[error.campo];

        if (destinoCampo) {
            mostrarError(document.getElementById(destinoCampo), error.mensaje);
        } else {
            rgeNotificar(error.mensaje, "aviso");
        }
    }

    function bloquear(boton, texto) {
        if (boton) {
            boton.disabled = true;
            boton.dataset.textoOriginal = boton.textContent;
            boton.textContent = texto;
        }
    }

    function desbloquear(boton, texto) {
        if (boton) {
            boton.disabled = false;
            boton.textContent = boton.dataset.textoOriginal || texto;
        }
    }

    function mostrarError(elemento, mensaje) {
        if (!elemento) {
            rgeNotificar(mensaje, "aviso");
            return;
        }

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