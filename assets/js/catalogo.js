document.addEventListener("DOMContentLoaded", async function () {

    const tarjetas = document.querySelectorAll(".card[data-id]");

    if (tarjetas.length === 0) {
        return;
    }

    let catalogo = [];

    try {
        catalogo = await rgeCatalogo();
    } catch (error) {
        rgeNotificar(error.mensaje, "aviso");
    }

    tarjetas.forEach(function (tarjeta) {
        sincronizarTarjeta(tarjeta, catalogo);
    });

    document.querySelectorAll(".btn-agregar").forEach(function (boton) {
        boton.addEventListener("click", function () {
            const tarjeta = boton.closest(".card");

            if (tarjeta) {
                agregarAlCarrito(tarjeta);
            }
        });
    });

    function sincronizarTarjeta(tarjeta, lista) {
        const real = lista.find(function (producto) {
            return producto.codigo === tarjeta.dataset.id;
        });

        const boton = tarjeta.querySelector(".btn-agregar");

        if (!real) {
            tarjeta.dataset.disponible = "false";

            if (boton) {
                boton.disabled = true;
                boton.textContent = "No disponible";
            }
            return;
        }

        tarjeta.dataset.ptid = real.id_producto_talla;
        tarjeta.dataset.precio = real.precio_final;
        tarjeta.dataset.stock = real.stock;
        tarjeta.dataset.disponible = real.stock > 0 ? "true" : "false";

        const etiquetaPrecio = tarjeta.querySelector(".price");

        if (etiquetaPrecio) {
            etiquetaPrecio.textContent = rgeFormatearPrecio(real.precio_final);
        }

        if (boton && real.stock <= 0) {
            boton.disabled = true;
            boton.textContent = "Agotado";
        }
    }

    async function agregarAlCarrito(tarjeta) {
        const codigo = tarjeta.dataset.id;

        if (tarjeta.dataset.disponible === "false") {
            rgeNotificar("Este producto no esta disponible", "aviso");
            return;
        }

        let producto;

        try {
            producto = await rgeBuscarPorCodigo(codigo);
        } catch (error) {
            rgeNotificar(error.mensaje, "aviso");
            return;
        }

        if (!producto) {
            rgeNotificar("No se pudo agregar este producto", "aviso");
            return;
        }

        const carrito = rgeLeerCarrito();

        const existente = carrito.find(function (item) {
            return item.codigo === codigo;
        });

        const cantidadFinal = existente ? existente.cantidad + 1 : 1;

        let disponibilidad;

        try {
            disponibilidad = await rgeApi("/productos/disponibilidad/" +
                producto.id_producto_talla + "?cantidad=" + cantidadFinal);
        } catch (error) {
            rgeNotificar(error.mensaje, "aviso");
            return;
        }

        if (!disponibilidad.disponible) {
            rgeNotificar("Solo quedan " + producto.stock + " unidades de " + producto.nombre, "aviso");
            return;
        }

        if (existente) {
            existente.cantidad = cantidadFinal;
            existente.precio = producto.precio_final;
        } else {
            carrito.push({
                codigo: producto.codigo,
                id_producto_talla: producto.id_producto_talla,
                nombre: producto.nombre,
                precio: producto.precio_final,
                imagen: tarjeta.dataset.imagen,
                categoria: producto.categoria,
                stock: producto.stock,
                cantidad: 1
            });
        }

        rgeGuardarCarrito(carrito);
        rgeNotificar(producto.nombre + " agregado al carrito", "exito");
    }

});