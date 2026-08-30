document.addEventListener("DOMContentLoaded", function () {

    const boton = document.getElementById("menu-toggle");
    const menu  = document.getElementById("nav-links");

    if (!boton || !menu) {
        return;
    }

    boton.addEventListener("click", function () {
        const abierto = menu.classList.toggle("abierto");

        boton.setAttribute("aria-expanded", abierto ? "true" : "false");
        boton.innerHTML = abierto
            ? '<i class="fa-solid fa-xmark"></i>'
            : '<i class="fa-solid fa-bars"></i>';
    });

    const desplegable = menu.querySelector(".dropdown");

    if (desplegable) {
        const enlace = desplegable.querySelector("a");

        enlace.addEventListener("click", function (evento) {
            if (window.innerWidth <= 768) {
                evento.preventDefault();
                desplegable.classList.toggle("abierto");
            }
        });
    }

    window.addEventListener("resize", function () {
        if (window.innerWidth > 768) {
            menu.classList.remove("abierto");
            boton.setAttribute("aria-expanded", "false");
            boton.innerHTML = '<i class="fa-solid fa-bars"></i>';

            if (desplegable) {
                desplegable.classList.remove("abierto");
            }
        }
    });

});