document.addEventListener("DOMContentLoaded", function () {

    const botones = document.querySelectorAll(".btn-agregar");

    if (botones.length === 0) {
        return;
    }

    botones.forEach(function (boton) {
        boton.addEventListener("click", function () {

            const tarjeta = boton.closest(".card");
            if (!tarjeta) {
                return;
            }

            const producto = {
                id:        tarjeta.dataset.id,
                nombre:    tarjeta.dataset.nombre,
                precio:    parseFloat(tarjeta.dataset.precio),
                imagen:    tarjeta.dataset.imagen,
                categoria: tarjeta.dataset.categoria,
                cantidad:  1
            };

            if (!producto.id || isNaN(producto.precio)) {
                console.error("Tarjeta sin datos validos:", tarjeta);
                rgeNotificar("No se pudo agregar este producto", "aviso");
                return;
            }

            agregarAlCarrito(producto);
        });
    });

    function agregarAlCarrito(producto) {
        const carrito = rgeLeerCarrito();

        const existente = carrito.find(function (item) {
            return item.id === producto.id;
        });

        if (existente) {
            existente.cantidad = existente.cantidad + 1;
        } else {
            carrito.push(producto);
        }

        rgeGuardarCarrito(carrito);
        rgeNotificar(producto.nombre + " agregado al carrito", "exito");
    }

});