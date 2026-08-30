document.addEventListener("DOMContentLoaded", function () {

    const contenedor  = document.getElementById("carrito-items");
    const vacio       = document.getElementById("carrito-vacio");
    const botonPagar  = document.getElementById("btn-continuar");
    const avisoLogin  = document.getElementById("aviso-login");

    if (!contenedor) {
        return;
    }

    pintarCarrito();

    if (botonPagar) {
        botonPagar.addEventListener("click", continuarAlPago);
    }

    function pintarCarrito() {
        const carrito = rgeLeerCarrito();
        contenedor.textContent = "";

        if (carrito.length === 0) {
            if (vacio) {
                vacio.style.display = "block";
            }
            if (botonPagar) {
                botonPagar.disabled = true;
            }
            if (avisoLogin) {
                avisoLogin.classList.add("oculto");
            }
            actualizarResumen({ subtotal: 0, iva: 0, total: 0 });
            return;
        }

        if (vacio) {
            vacio.style.display = "none";
        }
        if (botonPagar) {
            botonPagar.disabled = false;
        }
        if (avisoLogin && rgeHaySesion()) {
            avisoLogin.classList.add("oculto");
        }

        carrito.forEach(function (item) {
            contenedor.appendChild(crearFila(item));
        });

        actualizarResumen(rgeCalcularTotales(carrito));
    }

    function crearFila(item) {

        const fila = document.createElement("article");
        fila.className = "carrito-item";

        const imagen = document.createElement("img");
        imagen.className = "carrito-item-imagen";
        imagen.src = item.imagen;
        imagen.alt = item.nombre;

        const datos = document.createElement("div");
        datos.className = "carrito-item-datos";

        const titulo = document.createElement("h3");
        titulo.textContent = item.nombre;

        const categoria = document.createElement("p");
        categoria.className = "carrito-item-categoria";
        categoria.textContent = item.categoria;

        const precio = document.createElement("p");
        precio.className = "carrito-item-precio";
        precio.textContent = rgeFormatearPrecio(item.precio * item.cantidad);

        datos.appendChild(titulo);
        datos.appendChild(categoria);
        datos.appendChild(precio);

        const acciones = document.createElement("div");
        acciones.className = "carrito-item-acciones";

        const control = document.createElement("div");
        control.className = "cantidad-control";

        const menos = document.createElement("button");
        menos.type = "button";
        menos.textContent = "-";
        menos.setAttribute("aria-label", "Quitar una unidad");
        menos.addEventListener("click", function () {
            cambiarCantidad(item.id, -1);
        });

        const cantidad = document.createElement("span");
        cantidad.textContent = item.cantidad;

        const mas = document.createElement("button");
        mas.type = "button";
        mas.textContent = "+";
        mas.setAttribute("aria-label", "Agregar una unidad");
        mas.addEventListener("click", function () {
            cambiarCantidad(item.id, 1);
        });

        control.appendChild(menos);
        control.appendChild(cantidad);
        control.appendChild(mas);

        const eliminar = document.createElement("button");
        eliminar.type = "button";
        eliminar.className = "btn-eliminar";
        eliminar.textContent = "Eliminar";
        eliminar.addEventListener("click", function () {
            eliminarItem(item.id);
        });

        acciones.appendChild(control);
        acciones.appendChild(eliminar);

        fila.appendChild(imagen);
        fila.appendChild(datos);
        fila.appendChild(acciones);

        return fila;
    }

    function cambiarCantidad(id, cambio) {
        const carrito = rgeLeerCarrito();

        const item = carrito.find(function (producto) {
            return producto.id === id;
        });

        if (!item) {
            return;
        }

        item.cantidad = item.cantidad + cambio;

        if (item.cantidad <= 0) {
            const filtrado = carrito.filter(function (producto) {
                return producto.id !== id;
            });
            rgeGuardarCarrito(filtrado);
        } else {
            rgeGuardarCarrito(carrito);
        }

        pintarCarrito();
    }

    function eliminarItem(id) {
        const carrito = rgeLeerCarrito().filter(function (producto) {
            return producto.id !== id;
        });

        rgeGuardarCarrito(carrito);
        rgeNotificar("Producto eliminado del carrito", "aviso");
        pintarCarrito();
    }

    function actualizarResumen(totales) {
        const subtotal = document.getElementById("resumen-subtotal");
        const iva      = document.getElementById("resumen-iva");
        const total    = document.getElementById("resumen-total");

        if (subtotal) {
            subtotal.textContent = rgeFormatearPrecio(totales.subtotal);
        }
        if (iva) {
            iva.textContent = rgeFormatearPrecio(totales.iva);
        }
        if (total) {
            total.textContent = rgeFormatearPrecio(totales.total);
        }
    }

    function continuarAlPago() {
        const carrito = rgeLeerCarrito();

        if (carrito.length === 0) {
            rgeNotificar("Tu carrito esta vacio", "aviso");
            return;
        }

        if (!rgeHaySesion()) {
            if (avisoLogin) {
                avisoLogin.classList.remove("oculto");
            }
            rgeNotificar("Inicia sesion para continuar con tu compra", "aviso");

            setTimeout(function () {
                window.location.href = "login.html?destino=pago";
            }, 1200);
            return;
        }

        window.location.href = "pago.html";
    }

});