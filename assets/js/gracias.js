document.addEventListener("DOMContentLoaded", function () {

    const cuerpo = document.querySelector("#tabla-pedido tbody");
    const codigo = document.getElementById("codigo-pedido");

    if (!cuerpo) {
        return;
    }

    let pedido = null;

    try {
        const datos = localStorage.getItem(RGE_CLAVE_PEDIDO);
        pedido = datos ? JSON.parse(datos) : null;
    } catch (error) {
        console.error("No se pudo leer el pedido:", error);
    }

    if (!pedido || !Array.isArray(pedido.items) || pedido.items.length === 0) {
        mostrarSinPedido();
        return;
    }

    if (codigo) {
        codigo.textContent = pedido.codigo;
    }

    if (pedido.cliente) {
        escribirTexto("gracias-email", pedido.cliente.email);
        escribirTexto("gracias-cliente", pedido.cliente.nombres + " " + pedido.cliente.apellidos);
    }

    escribirTexto("gracias-metodo", pedido.metodo_pago || "No especificado");

    if (pedido.entrega) {
        const direccion = pedido.entrega.referencia
            ? pedido.entrega.direccion + " (" + pedido.entrega.referencia + ")"
            : pedido.entrega.direccion;
        escribirTexto("gracias-direccion", direccion);
    }

    pedido.items.forEach(function (item) {
        const fila = document.createElement("tr");

        fila.appendChild(crearCelda(item.nombre));
        fila.appendChild(crearCelda(item.cantidad));
        fila.appendChild(crearCelda(rgeFormatearPrecio(item.precio)));
        fila.appendChild(crearCelda(rgeFormatearPrecio(item.precio * item.cantidad)));

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

    function mostrarSinPedido() {
        const fila  = document.createElement("tr");
        const celda = document.createElement("td");

        celda.className = "tabla-vacia";
        celda.colSpan = 4;
        celda.textContent = "No hay ningun pedido reciente para mostrar.";

        fila.appendChild(celda);
        cuerpo.appendChild(fila);

        if (codigo) {
            codigo.textContent = "Sin pedido";
        }
    }

});