document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("contactForm");

    // El formulario solo existe en contacto.html.
    if (!formulario) {
        return;
    }

    const nombre = document.getElementById("nombre");
    const ciudad = document.getElementById("ciudad");
    const email = document.getElementById("email");
    const asunto = document.getElementById("asunto");
    const descripcion = document.getElementById("descripcion");
    const mensajeExito = document.getElementById("mensajeExito");

    const expresionCorreo = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    formulario.addEventListener("submit", (event) => {
        event.preventDefault();
        limpiarMensajeExito();

        if (!validarFormulario()) {
            return;
        }

        mensajeExito.textContent = "¡Formulario enviado correctamente!";
        formulario.reset();
        limpiarTodosLosErrores();
    });

    function validarFormulario() {
        let esValido = true;

        const nombreValor = nombre.value.trim();
        const ciudadValor = ciudad.value.trim();
        const emailValor = email.value.trim();
        const descripcionValor = descripcion.value.trim();

        if (nombreValor === "") {
            mostrarError(nombre, "El nombre es obligatorio.");
            esValido = false;
        } else if (nombreValor.length < 3) {
            mostrarError(nombre, "El nombre debe contener al menos 3 caracteres.");
            esValido = false;
        } else {
            limpiarError(nombre);
        }

        if (ciudadValor === "") {
            mostrarError(ciudad, "La ciudad es obligatoria.");
            esValido = false;
        } else {
            limpiarError(ciudad);
        }

        if (emailValor === "") {
            mostrarError(email, "El correo electrónico es obligatorio.");
            esValido = false;
        } else if (!expresionCorreo.test(emailValor)) {
            mostrarError(email, "Ingrese un correo electrónico válido.");
            esValido = false;
        } else {
            limpiarError(email);
        }

        if (asunto.value === "") {
            mostrarError(asunto, "Seleccione un asunto.");
            esValido = false;
        } else {
            limpiarError(asunto);
        }

        if (descripcionValor === "") {
            mostrarError(descripcion, "La descripción es obligatoria.");
            esValido = false;
        } else if (descripcionValor.length < 10) {
            mostrarError(
                descripcion,
                "La descripción debe contener al menos 10 caracteres."
            );
            esValido = false;
        } else {
            limpiarError(descripcion);
        }

        return esValido;
    }

    function mostrarError(elemento, mensaje) {
        const grupo = elemento.closest(".form-group");

        if (!grupo) {
            return;
        }

        const mensajeError = grupo.querySelector(".error");

        elemento.classList.add("error-input");
        elemento.setAttribute("aria-invalid", "true");

        if (mensajeError) {
            mensajeError.textContent = mensaje;
        }
    }

    function limpiarError(elemento) {
        const grupo = elemento.closest(".form-group");

        if (!grupo) {
            return;
        }

        const mensajeError = grupo.querySelector(".error");

        elemento.classList.remove("error-input");
        elemento.removeAttribute("aria-invalid");

        if (mensajeError) {
            mensajeError.textContent = "";
        }
    }

    function limpiarTodosLosErrores() {
        [nombre, ciudad, email, asunto, descripcion].forEach((campo) => {
            limpiarError(campo);
        });
    }

    function limpiarMensajeExito() {
        mensajeExito.textContent = "";
    }

    nombre.addEventListener("input", () => limpiarError(nombre));
    ciudad.addEventListener("input", () => limpiarError(ciudad));
    email.addEventListener("input", () => limpiarError(email));
    asunto.addEventListener("change", () => limpiarError(asunto));
    descripcion.addEventListener("input", () => limpiarError(descripcion));
});
