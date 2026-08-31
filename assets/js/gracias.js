document.addEventListener("DOMContentLoaded", async function () {

    const cuerpo = document.querySelector("#tabla-pedido tbody");
    const codigo = document.getElementById("codigo-pedido");

    if (!cuerpo) {
        return;
    }

    await rgeCargarSesion();

    const codigoPedido = localStorage.getItem(RGE_CLAVE_PEDIDO);

    if (!codigoPedido) {
        mostrarSinPedido("No hay ningun pedido reciente para mostrar.");
        return;
    }

    let pedido;

    try {
        pedido = await rgeApi("/pedidos/" + encodeURIComponent(codigoPedido));
    } catch (error) {
        if (error.codigo === "SIN_SESION") {
            mostrarSinPedido("Inicia sesion para ver el detalle de tu pedido.");
        } else {
            mostrarSinPedido(error.mensaje);
        }
        return;
    }

    if (codigo) {
        codigo.textContent = pedido.codigo_pedido;
    }

    escribirTexto("gracias-email", pedido.email);
    escribirTexto("gracias-cliente", pedido.cliente);
    escribirTexto("gracias-metodo", pedido.metodo_pago || "No especificado");

    const direccion = pedido.referencia
        ? pedido.direccion + " (" + pedido.referencia + ")"
        : pedido.direccion;

    escribirTexto("gracias-direccion", direccion);

    pedido.detalles.forEach(function (linea) {
        const fila = document.createElement("tr");

        fila.appendChild(crearCelda(linea.producto));
        fila.appendChild(crearCelda(linea.cantidad));
        fila.appendChild(crearCelda(rgeFormatearPrecio(linea.precio_unitario)));
        fila.appendChild(crearCelda(rgeFormatearPrecio(linea.subtotal_linea)));

        cuerpo.appendChild(fila);
    });

    escribirTotal("gracias-subtotal", pedido.subtotal);
    escribirTotal("gracias-iva", pedido.iva);
    escribirTotal("gracias-total", pedido.total);

    function crearCelda(texto) {
        const celda = document.createElement("td");
        celda.textContent = texto;
        return celda;
    }

    function escribirTexto(id, texto) {
        const elemento = document.getElementById(id);

        if (elemento) {
            elemento.textContent = texto;
        }
    }

    function escribirTotal(id, valor) {
        const elemento = document.getElementById(id);

        if (elemento) {
            elemento.textContent = rgeFormatearPrecio(valor);
        }
    }

    function mostrarSinPedido(mensaje) {
        const fila  = document.createElement("tr");
        const celda = document.createElement("td");

        celda.className = "tabla-vacia";
        celda.colSpan = 4;
        celda.textContent = mensaje;

        fila.appendChild(celda);
        cuerpo.appendChild(fila);

        if (codigo) {
            codigo.textContent = "Sin pedido";
        }
    }

});