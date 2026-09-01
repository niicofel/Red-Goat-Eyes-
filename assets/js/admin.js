// ============================================================
// ADMIN.JS
// Solo en admin.html. Llena las cinco pestanas del panel.
// Todas las peticiones son de administrador; si entra un cliente
// se bloquean las tablas.
// ============================================================
document.addEventListener("DOMContentLoaded", async function () {


// ---------------- Cambio de pestanas ----------------
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


// ---------------- Comprobar que sea administrador ----------------
// Si no lo es, bloquea las tablas y avisa
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
        btnReporte.addEventListener("click", cargarVentas);
    }

    const formReponer = document.getElementById("form-reponer");
    if (formReponer) {
        formReponer.addEventListener("submit", reponerStock);
    }

    const filtroInventario = document.getElementById("filtro-inventario");
    if (filtroInventario) {
        filtroInventario.addEventListener("change", cargarInventario);
    }


// ---------------- Cargar todo en paralelo ----------------
// Siete peticiones a la vez tardan lo que la mas lenta, no la suma
    await Promise.all([
        cargarResumen(),
        cargarVentas(),
        cargarClientes(),
        cargarProductos(),
        cargarInventario(),
        cargarPedidos(),
        cargarMensajes()
    ]);


// ---------------- Tarjetas de indicadores ----------------
// Productos, clientes, pedidos, mensajes y alertas de stock
    async function cargarResumen() {
        const caja = document.getElementById("resumen-admin");

        if (!caja) {
            return;
        }

        let datos;

        try {
            datos = await rgeApi("/reportes/resumen");
        } catch (error) {
            caja.textContent = error.mensaje;
            return;
        }

        const tarjetas = [
            ["Productos activos", datos.productos],
            ["Clientes", datos.clientes],
            ["Pedidos", datos.pedidos],
            ["Mensajes sin leer", datos.mensajes_pendientes],
            ["Alertas de stock", datos.alertas_stock]
        ];

        caja.textContent = "";

        tarjetas.forEach(function (par) {
            const tarjeta = document.createElement("div");
            tarjeta.className = "kpi-card";

            const valor = document.createElement("span");
            valor.className = "kpi-valor";
            valor.textContent = par[1];

            const etiqueta = document.createElement("span");
            etiqueta.className = "kpi-etiqueta";
            etiqueta.textContent = par[0];

            if (par[0] === "Alertas de stock" && par[1] > 0) {
                tarjeta.classList.add("kpi-alerta");
            }

            tarjeta.appendChild(valor);
            tarjeta.appendChild(etiqueta);
            caja.appendChild(tarjeta);
        });
    }


// ---------------- Reporte de ventas por categoria ----------------
// Se puede filtrar por fechas
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


// ---------------- Reporte de ranking de clientes ----------------
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


// ---------------- Tabla de productos ----------------
    async function cargarProductos() {
        await llenar("tabla-productos", "/productos", "productos", function (fila) {
            return [
                fila.codigo,
                fila.nombre,
                fila.categoria,
                rgeFormatearPrecio(fila.precio_final),
                fila.stock,
                fila.disponible ? "Disponible" : "Agotado"
            ];
        });
    }


// ---------------- Inventario por talla ----------------
// Las 72 combinaciones. Resalta en amarillo las criticas y en rojo las agotadas
    async function cargarInventario() {
        const tabla = document.getElementById("tabla-inventario");

        if (!tabla) {
            return;
        }

        const cuerpo = tabla.querySelector("tbody");
        const columnas = tabla.querySelectorAll("thead th").length;
        const filtro = valorCampo("filtro-inventario");

        mensajeEnTabla(cuerpo, columnas, "Cargando...");

        let datos;

        try {
            datos = await rgeApi("/productos/inventario");
        } catch (error) {
            mensajeEnTabla(cuerpo, columnas, error.mensaje);
            return;
        }

        let filas = datos.inventario;

        if (filtro === "criticos") {
            filas = filas.filter(function (f) { return f.critico; });
        } else if (filtro === "agotados") {
            filas = filas.filter(function (f) { return f.agotado; });
        }

            llenarSelectTallas(datos.inventario);

        const contador = document.getElementById("inventario-contador");
        if (contador) {
            contador.textContent = datos.total + " combinaciones  ·  " +
                                   datos.criticos + " en nivel critico  ·  " +
                                   datos.agotados + " agotadas";
        }

        if (filas.length === 0) {
            mensajeEnTabla(cuerpo, columnas, "No hay registros con ese filtro.");
            return;
        }

        cuerpo.textContent = "";

        filas.forEach(function (registro) {
            const fila = document.createElement("tr");

            if (registro.agotado) {
                fila.className = "fila-agotada";
            } else if (registro.critico) {
                fila.className = "fila-critica";
            }

            const valores = [
                registro.codigo,
                registro.nombre,
                registro.categoria,
                registro.talla,
                registro.stock,
                registro.stock_minimo,
                registro.agotado ? "Agotado" : (registro.critico ? "Critico" : "Normal")
            ];

            valores.forEach(function (valor) {
                const celda = document.createElement("td");
                celda.textContent = valor;
                fila.appendChild(celda);
            });

            const acciones = document.createElement("td");
            const boton = document.createElement("button");
            boton.type = "button";
            boton.className = "btn-mini";
            boton.textContent = "Reponer";
            boton.addEventListener("click", function () {
                prepararReposicion(registro);
            });
            acciones.appendChild(boton);
            fila.appendChild(acciones);

            cuerpo.appendChild(fila);
        });
    }


// ---------------- Llenar el menu de tallas del formulario ----------------
    function llenarSelectTallas(inventario) {
        const select = document.getElementById("reponer-talla");

        if (!select || select.options.length > 1) {
            return;
        }

        const vistas = [];

        inventario.forEach(function (registro) {
            if (vistas.indexOf(registro.talla) === -1) {
                vistas.push(registro.talla);
            }
        });

        vistas.forEach(function (talla) {
            const opcion = document.createElement("option");
            opcion.value = talla;
            opcion.textContent = talla;
            select.appendChild(opcion);
        });
    }


// ---------------- Rellenar el formulario al pulsar Reponer ----------------
    function prepararReposicion(registro) {
        escribirCampo("reponer-codigo", registro.codigo);
        escribirCampo("reponer-talla", registro.talla);
        escribirCampo("reponer-cantidad", "10");

        const aviso = document.getElementById("reponer-aviso");
        if (aviso) {
            aviso.textContent = registro.nombre + " talla " + registro.talla +
                                " tiene " + registro.stock + " unidades";
            aviso.className = "reponer-aviso";
        }

        const form = document.getElementById("form-reponer");
        if (form) {
            form.scrollIntoView({ behavior: "smooth", block: "center" });
        }
    }


// ---------------- Reponer stock ----------------
// Llama a la API, que a su vez llama al procedimiento sp_reponer_stock
    async function reponerStock(evento) {
        evento.preventDefault();

        const aviso = document.getElementById("reponer-aviso");
        const boton = evento.target.querySelector('button[type="submit"]');

        boton.disabled = true;
        boton.textContent = "Reponiendo...";

        try {
            const respuesta = await rgeApi("/productos/reponer", {
                cuerpo: {
                    codigo_producto: valorCampo("reponer-codigo").toUpperCase(),
                    codigo_talla: valorCampo("reponer-talla"),
                    cantidad: parseInt(valorCampo("reponer-cantidad"), 10)
                }
            });

            const p = respuesta.producto;

            aviso.textContent = p.nombre + " talla " + p.talla +
                                " quedo en " + p.stock + " unidades";
            aviso.className = "reponer-aviso exito";

            rgeNotificar("Stock repuesto correctamente", "exito");

            await Promise.all([cargarInventario(), cargarProductos(), cargarResumen()]);

        } catch (error) {
            aviso.textContent = error.mensaje;
            aviso.className = "reponer-aviso error";
            rgeNotificar(error.mensaje, "aviso");

        } finally {
            boton.disabled = false;
            boton.textContent = "Reponer stock";
        }
    }


// ---------------- Tabla de todos los pedidos ----------------
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


// ---------------- Tabla de mensajes de contacto ----------------
// Cada fila se puede pulsar para leer el mensaje completo
    async function cargarMensajes() {
        const tabla = document.getElementById("tabla-mensajes");

        if (!tabla) {
            return;
        }

        const cuerpo = tabla.querySelector("tbody");
        const columnas = tabla.querySelectorAll("thead th").length;

        mensajeEnTabla(cuerpo, columnas, "Cargando...");

        let datos;

        try {
            datos = await rgeApi("/contacto/mensajes");
        } catch (error) {
            mensajeEnTabla(cuerpo, columnas, error.mensaje);
            return;
        }

        if (datos.mensajes.length === 0) {
            mensajeEnTabla(cuerpo, columnas, "No hay mensajes recibidos.");
            return;
        }

        cuerpo.textContent = "";

        datos.mensajes.forEach(function (mensaje) {
            const fila = document.createElement("tr");
            fila.className = "fila-clicable";
            fila.title = "Ver el mensaje completo";

            [
                formatearFecha(mensaje.fecha_envio),
                mensaje.nombre,
                mensaje.email,
                mensaje.ciudad,
                mensaje.asunto,
                mensaje.estado
            ].forEach(function (valor) {
                const celda = document.createElement("td");
                celda.textContent = valor;
                fila.appendChild(celda);
            });

            fila.addEventListener("click", function () {
                abrirMensaje(mensaje);
            });

            cuerpo.appendChild(fila);
        });
    }


// ---------------- Ventana con el mensaje completo ----------------
// Incluye un boton para responder por correo con el asunto ya escrito
    function abrirMensaje(mensaje) {
        let modal = document.getElementById("modal-mensaje");

        if (!modal) {
            modal = document.createElement("div");
            modal.id = "modal-mensaje";
            modal.className = "modal-overlay";
            document.body.appendChild(modal);

            modal.addEventListener("click", function (evento) {
                if (evento.target === modal) {
                    modal.classList.remove("activo");
                }
            });
        }

        modal.textContent = "";

        const tarjeta = document.createElement("div");
        tarjeta.className = "modal-card modal-mensaje-card";

        const cerrar = document.createElement("button");
        cerrar.type = "button";
        cerrar.className = "btn-cerrar-modal";
        cerrar.textContent = "×";
        cerrar.setAttribute("aria-label", "Cerrar");
        cerrar.addEventListener("click", function () {
            modal.classList.remove("activo");
        });
        tarjeta.appendChild(cerrar);

        const titulo = document.createElement("h2");
        titulo.className = "modal-titulo";
        titulo.textContent = mensaje.asunto;
        tarjeta.appendChild(titulo);

        const datos = [
            ["De", mensaje.nombre],
            ["Correo", mensaje.email],
            ["Ciudad", mensaje.ciudad],
            ["Fecha", formatearFecha(mensaje.fecha_envio)],
            ["Estado", mensaje.estado]
        ];

        const lista = document.createElement("dl");
        lista.className = "mensaje-datos";

        datos.forEach(function (par) {
            const clave = document.createElement("dt");
            clave.textContent = par[0];
            const valor = document.createElement("dd");
            valor.textContent = par[1];
            lista.appendChild(clave);
            lista.appendChild(valor);
        });

        tarjeta.appendChild(lista);

        const encabezado = document.createElement("h4");
        encabezado.textContent = "MENSAJE";
        tarjeta.appendChild(encabezado);

        const cuerpoTexto = document.createElement("p");
        cuerpoTexto.className = "mensaje-cuerpo";
        cuerpoTexto.textContent = mensaje.descripcion;
        tarjeta.appendChild(cuerpoTexto);

        const responder = document.createElement("a");
        responder.className = "btn-agregar-modal";
        responder.href = "mailto:" + mensaje.email +
                         "?subject=" + encodeURIComponent("Re: " + mensaje.asunto + " - Red Goat Eyes");
        responder.textContent = "RESPONDER POR CORREO";
        tarjeta.appendChild(responder);

        modal.appendChild(tarjeta);
        modal.classList.add("activo");
    }


// ---------------- Funcion generica para llenar tablas ----------------
// Recibe la tabla, la ruta de la API y como convertir cada registro en fila
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


// ---------------- Mensaje dentro de una tabla vacia ----------------
    function mensajeEnTabla(cuerpo, columnas, texto) {
        if (!cuerpo) {
            return;
        }

        cuerpo.textContent = "";

        const fila = document.createElement("tr");
        const celda = document.createElement("td");

        celda.className = "tabla-vacia";
        celda.colSpan = columnas;
        celda.textContent = texto;

        fila.appendChild(celda);
        cuerpo.appendChild(fila);
    }


// ---------------- Bloquear el panel a quien no es admin ----------------
    function bloquearPanel(mensaje) {
        ["tabla-rpt1", "tabla-rpt2", "tabla-productos",
         "tabla-inventario", "tabla-pedidos", "tabla-mensajes"].forEach(function (id) {
            const tabla = document.getElementById(id);

            if (tabla) {
                mensajeEnTabla(tabla.querySelector("tbody"),
                               tabla.querySelectorAll("thead th").length, mensaje);
            }
        });
    }


// ---------------- Ayudantes de formulario y fechas ----------------
    function valorCampo(id) {
        const elemento = document.getElementById(id);
        return elemento ? elemento.value.trim() : "";
    }

    function escribirCampo(id, valor) {
        const elemento = document.getElementById(id);
        if (elemento) {
            elemento.value = valor;
        }
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