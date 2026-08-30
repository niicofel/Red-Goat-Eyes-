document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("contactForm");

    if (!form) {
        return;
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        if (validarFormulario()) {
            rgeNotificar("Formulario enviado con exito", "exito");
            form.reset();

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

            document.querySelectorAll(".error-input").forEach(function (el) {
                el.classList.remove("error-input");
            });
            document.querySelectorAll(".error").forEach(function (el) {
                el.textContent = "";
            });
        }
    });

    function validarFormulario() {
        let itsValid = true;

        const nombre = document.getElementById("nombre");
        if (nombre.value.trim().length < 3) {
            mostrarError(nombre, "El nombre tiene que tener al menos 3 caracteres.");
            itsValid = false;
        } else {
            limpiarError(nombre);
        }

        const ciudad = document.getElementById("ciudad");
        if (ciudad.value.trim() === "") {
            mostrarError(ciudad, "El campo es obligatorio.");
            itsValid = false;
        } else {
            limpiarError(ciudad);
        }

        const email = document.getElementById("email");
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.value)) {
            mostrarError(email, "Ingrese un correo válido.");
            itsValid = false;
        } else {
            limpiarError(email);
        }

        const asunto = document.getElementById("asunto");
        if (asunto.value === "") {
            mostrarError(asunto, "Seleccione un asunto.");
            itsValid = false;
        } else {
            limpiarError(asunto);
        }

        const descripcion = document.getElementById("descripcion");
        if (descripcion.value.trim().length < 10) {
            mostrarError(descripcion, "Mensaje muy corto. Ingrese minimo 10 caracteres.");
            itsValid = false;
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
                itsValid = false;
            } else if (archivo.size > pesoMaximo) {
                mostrarError(foto, "La imagen no puede pesar mas de 2 MB.");
                itsValid = false;
            }
        }

        return itsValid;
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