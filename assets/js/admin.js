document.addEventListener("DOMContentLoaded", async function () {

    const botones = document.querySelectorAll(".tab-btn");
    const paneles = document.querySelectorAll(".admin-panel");

    if (botones.length === 0) {
        return;
    }

    botones.forEach(function (boton) {
        boton.addEventListener("click", function () {

            botones.forEach(function (otro) {
                otro.classList.remove("activa");
            });
            boton.classList.add("activa");

            paneles.forEach(function (panel) {
                panel.classList.add("oculto");
            });

            const destino = document.getElementById("tab-" + boton.dataset.tab);

            if (destino) {
                destino.classList.remove("oculto");
            }
        });
    });

    const sesion = await rgeCargarSesion();

    if (!sesion) {
        bloquearPanel("Debes iniciar sesion como administrador para ver este panel.");
        setTimeout(function () {
            window.location.href = "login.html";
        }, 1800);
        return;
    }

    if (sesion.rol !== "administrador") {
        bloquearPanel("Tu cuenta no tiene permisos de administrador.");
        rgeNotificar("Acceso restringido a administradores", "aviso");
        return;
    }

    const btnReporte = document.getElementById("btn-rpt1");

    if (btnReporte) {
        btnReporte.addEventListener("click", function () {
            cargarVentas();
        });
    }

    await Promise.all([
        cargarVentas(),
        cargarClientes(),
        cargarProductos(),
        cargarPedidos(),
        cargarMensajes()
    ]);

    async function cargarVentas() {
        const desde = valorCampo("rpt1-desde");
        const hasta = valorCampo("rpt1-hasta");

        const parametros = [];
        if (desde) {
            parametros.push("desde=" + desde);
        }
        if (hasta) {
            parametros.push("hasta=" + hasta);
        }

        const consulta = parametros.length ? "?" + parametros.join("&") : "";

        await llenar("tabla-rpt1", "/reportes/ventas" + consulta, "filas", function (fila) {
            return [
                fila.categoria,
                fila.productos_vendidos,
                fila.unidades,
                rgeFormatearPrecio(fila.total_vendido),
                "#" + fila.ranking
            ];
        });
    }

    async function cargarClientes() {
        await llenar("tabla-rpt2", "/reportes/clientes", "filas", function (fila) {
            return [
                fila.cliente,
                fila.ciudad,
                fila.pedidos,
                rgeFormatearPrecio(fila.total_comprado),
                rgeFormatearPrecio(fila.ticket_promedio),
                formatearFecha(fila.ultima_compra)
            ];
        });
    }

    async function cargarProductos() {
        await llenar("tabla-productos", "/productos", "productos", function (fila) {
            return [
                fila.codigo,
                fila.nombre,
                fila.categoria,
                rgeFormatearPrecio(fila.precio_final),
                fila.stock,
                fila.stock > 0 ? "Disponible" : "Agotado"
            ];
        });
    }

    async function cargarPedidos() {
        await llenar("tabla-pedidos", "/pedidos/todos", "pedidos", function (fila) {
            return [
                fila.codigo_pedido,
                fila.cliente,
                formatearFecha(fila.fecha_pedido),
                rgeFormatearPrecio(fila.total),
                fila.estado
            ];
        });
    }

    async function cargarMensajes() {
        await llenar("tabla-mensajes", "/contacto/mensajes", "mensajes", function (fila) {
            return [
                formatearFecha(fila.fecha_envio),
                fila.nombre,
                fila.ciudad,
                fila.asunto,
                fila.estado
            ];
        });
    }

    async function llenar(idTabla, ruta, campo, transformar) {
        const tabla = document.getElementById(idTabla);

        if (!tabla) {
            return;
        }

        const cuerpo = tabla.querySelector("tbody");
        const columnas = tabla.querySelectorAll("thead th").length;

        mensajeEnTabla(cuerpo, columnas, "Cargando...");

        let datos;

        try {
            datos = await rgeApi(ruta);
        } catch (error) {
            mensajeEnTabla(cuerpo, columnas, error.mensaje);
            return;
        }

        const filas = datos[campo] || [];

        if (filas.length === 0) {
            mensajeEnTabla(cuerpo, columnas, "No hay registros para mostrar.");
            return;
        }

        cuerpo.textContent = "";

        filas.forEach(function (registro) {
            const fila = document.createElement("tr");

            transformar(registro).forEach(function (valor) {
                const celda = document.createElement("td");
                celda.textContent = valor === null || valor === undefined ? "-" : valor;
                fila.appendChild(celda);
            });

            cuerpo.appendChild(fila);
        });
    }

    function mensajeEnTabla(cuerpo, columnas, texto) {
        if (!cuerpo) {
            return;
        }

        cuerpo.textContent = "";

        const fila  = document.createElement("tr");
        const celda = document.createElement("td");

        celda.className = "tabla-vacia";
        celda.colSpan = columnas;
        celda.textContent = texto;

        fila.appendChild(celda);
        cuerpo.appendChild(fila);
    }

    function bloquearPanel(mensaje) {
        const tablas = ["tabla-rpt1", "tabla-rpt2", "tabla-productos",
                        "tabla-pedidos", "tabla-mensajes"];

        tablas.forEach(function (id) {
            const tabla = document.getElementById(id);

            if (tabla) {
                mensajeEnTabla(tabla.querySelector("tbody"),
                               tabla.querySelectorAll("thead th").length, mensaje);
            }
        });
    }

    function valorCampo(id) {
        const elemento = document.getElementById(id);
        return elemento ? elemento.value.trim() : "";
    }

    function formatearFecha(valor) {
        if (!valor) {
            return "-";
        }

        const fecha = new Date(valor);

        if (isNaN(fecha.getTime())) {
            return valor;
        }

        return fecha.toLocaleDateString("es-EC", {
            year: "numeric", month: "2-digit", day: "2-digit"
        });
    }

});