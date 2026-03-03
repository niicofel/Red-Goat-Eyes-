document.addEventListener("DOMContentLoaded" , function() {
    const form = document.getElementById("contactForm");

    form.addEventListener("submit", function(event) {
        event.preventDefault();
        
        if (validarFormulario()) {
            alert("¡Formulario enviado con éxito!");
            form.reset();
            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });

            document.querySelectorAll(".error-input").forEach(el => el.classList.remove("error-input"));
            document.querySelectorAll(".error").forEach(el => el.textContent = "");
            
        } else {
            console.log("Validación fallida.");
        }
    }); 

    function validarFormulario() {
        let itsValid = true;

        // Validar Nombre
        const nombre = document.getElementById("nombre");
        if (nombre.value.trim().length < 3) {
            mostrarError(nombre, "El nombre tiene que tener al menos 3 caracteres.");
            itsValid = false;
        } else {
            limpiarError(nombre);
        }

        // Validar Ciudad
        const ciudad = document.getElementById("ciudad");
        if (ciudad.value.trim() === "") {
            mostrarError(ciudad, "El campo es obligatorio.");
            itsValid = false;
        } else {
            limpiarError(ciudad);
        }

        // Validad Correo
        const email = document.getElementById("email");
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.value)) {
            mostrarError(email, "Ingrese un correo válido.");
            itsValid = false;
        } else {
            limpiarError(email);
        }

        // Validar Asunto
        const asunto = document.getElementById("asunto");
        if (asunto.value === "") {
            mostrarError(asunto, "Seleccione un asunto.");
            itsValid = false;
        } else {
            limpiarError(asunto);
        }

        // Validar Descripción
        const descripcion = document.getElementById("descripcion");
        if (descripcion.value.trim().length < 10) {
            mostrarError(descripcion, "Mensaje muy corto. Ingrese minimo 10 caracteres.");
            itsValid = false;
        } else {
            limpiarError(descripcion);
        }

        // Validar Foto
        const foto = document.getElementById("foto");
        limpiarError(foto);

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


