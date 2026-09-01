// ============================================================
// VALIDACIONES.JS
// Solo en contacto.html. Valida el formulario y lo envia.
// El mensaje se guarda en la base y ademas se avisa por correo
// al administrador.
// ============================================================
document.addEventListener("DOMContentLoaded", async function () {

    const form = document.getElementById("contactForm");

    if (!form) {
        return;
    }


// ---------------- Si hay sesion, rellenar nombre y correo ----------------
    const sesion = await rgeCargarSesion();

    let selectCiudad = null;

    await cargarAsuntos();
    selectCiudad = await construirSelectCiudades();

    if (sesion) {
        const nombre = document.getElementById("nombre");
        const email  = document.getElementById("email");

        if (nombre && !nombre.value) {
            nombre.value = sesion.nombre;
        }
        if (email && !email.value) {
            email.value = sesion.email;
        }
    }


// ---------------- Enviar el mensaje ----------------
// Si la API rechaza un campo, el error se muestra debajo de ese campo
    form.addEventListener("submit", async function (evento) {
        evento.preventDefault();

        if (!validarFormulario()) {
            return;
        }

        const boton = form.querySelector('button[type="submit"]');
        const textoOriginal = boton ? boton.textContent : "";

        if (boton) {
            boton.disabled = true;
            boton.textContent = "Enviando...";
        }

        try {
            await rgeApi("/contacto", {
                cuerpo: {
                    nombre: document.getElementById("nombre").value.trim(),
                    email: document.getElementById("email").value.trim(),
                    asunto: document.getElementById("asunto").value,
                    id_ciudad: parseInt(selectCiudad.value, 10),
                    descripcion: document.getElementById("descripcion").value.trim()
                }
            });

            rgeNotificar("Mensaje enviado con exito. Te responderemos pronto.", "exito");
            form.reset();

            window.scrollTo({ top: 0, behavior: "smooth" });

            document.querySelectorAll(".error-input").forEach(function (elemento) {
                elemento.classList.remove("error-input");
            });
            document.querySelectorAll(".error").forEach(function (elemento) {
                elemento.textContent = "";
            });

        } catch (error) {
            const mapa = {
                nombre: "nombre",
                email: "email",
                asunto: "asunto",
                descripcion: "descripcion",
                id_ciudad: "ciudad"
            };

            const destino = mapa[error.campo];

            if (destino) {
                mostrarError(document.getElementById(destino), error.mensaje);
            } else {
                rgeNotificar(error.mensaje, "aviso");
            }

        } finally {
            if (boton) {
                boton.disabled = false;
                boton.textContent = textoOriginal;
            }
        }
    });


// ---------------- Traer los asuntos de la base ----------------
// La base guarda 'Consulta' con mayuscula, por eso no se escriben a mano
    async function cargarAsuntos() {
        const select = document.getElementById("asunto");

        if (!select) {
            return;
        }

        try {
            const datos = await rgeApi("/contacto/asuntos");

            select.textContent = "";

            const inicial = document.createElement("option");
            inicial.value = "";
            inicial.textContent = "Seleccione un asunto";
            select.appendChild(inicial);

            datos.asuntos.forEach(function (asunto) {
                const opcion = document.createElement("option");
                opcion.value = asunto.nombre;
                opcion.textContent = asunto.nombre;
                select.appendChild(opcion);
            });

        } catch (error) {
            rgeNotificar(error.mensaje, "aviso");
        }
    }


// ---------------- Convertir el campo Ciudad en un menu ----------------
// En el HTML es un input de texto; aqui se reemplaza por un select con las 30 ciudades
    async function construirSelectCiudades() {
        const original = document.getElementById("ciudad");

        if (!original) {
            return null;
        }

        const select = document.createElement("select");
        select.id = original.id;
        select.name = original.name;
        select.required = original.required;

        const inicial = document.createElement("option");
        inicial.value = "";
        inicial.textContent = "Seleccione una ciudad";
        select.appendChild(inicial);

        try {
            const datos = await rgeApi("/ciudades");

            datos.ciudades.forEach(function (ciudad) {
                const opcion = document.createElement("option");
                opcion.value = ciudad.id_ciudad;
                opcion.textContent = ciudad.nombre + " (" + ciudad.provincia + ")";
                select.appendChild(opcion);
            });

        } catch (error) {
            rgeNotificar(error.mensaje, "aviso");
        }

        original.parentElement.replaceChild(select, original);
        return select;
    }


// ---------------- Validar los campos ----------------
    function validarFormulario() {
        let esValido = true;

        const nombre = document.getElementById("nombre");
        if (nombre.value.trim().length < 3) {
            mostrarError(nombre, "El nombre tiene que tener al menos 3 caracteres.");
            esValido = false;
        } else {
            limpiarError(nombre);
        }

        const ciudad = document.getElementById("ciudad");
        if (!ciudad || ciudad.value === "") {
            mostrarError(ciudad, "Seleccione una ciudad.");
            esValido = false;
        } else {
            limpiarError(ciudad);
        }

        const email = document.getElementById("email");
        if (!rgeEmailValido(email.value)) {
            mostrarError(email, "Ingrese un correo válido.");
            esValido = false;
        } else {
            limpiarError(email);
        }

        const asunto = document.getElementById("asunto");
        if (asunto.value === "") {
            mostrarError(asunto, "Seleccione un asunto.");
            esValido = false;
        } else {
            limpiarError(asunto);
        }

        const descripcion = document.getElementById("descripcion");
        if (descripcion.value.trim().length < 10) {
            mostrarError(descripcion, "Mensaje muy corto. Ingrese minimo 10 caracteres.");
            esValido = false;
        } else {
            limpiarError(descripcion);
        }

        const foto = document.getElementById("foto");
        limpiarError(foto);

        if (foto.files.length > 0) {
            const archivo = foto.files[0];
            const tiposPermitidos = ["image/png", "image/jpeg", "image/webp"];
            const pesoMaximo = 2 * 1024 * 1024;

            if (tiposPermitidos.indexOf(archivo.type) === -1) {
                mostrarError(foto, "Solo se permiten imagenes PNG, JPG o WEBP.");
                esValido = false;
            } else if (archivo.size > pesoMaximo) {
                mostrarError(foto, "La imagen no puede pesar mas de 2 MB.");
                esValido = false;
            }
        }

        return esValido;
    }


// ---------------- Mostrar y limpiar errores ----------------
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
        if (!elemento) {
            return;
        }

        const grupo = elemento.parentElement;
        const errorDisplay = grupo.querySelector(".error");

        if (errorDisplay) {
            errorDisplay.textContent = "";
        }
        elemento.classList.remove("error-input");
    }

});