/* ============================================================
   ADMIN.JS  ·  Red Goat Eyes
   Pestanas del panel de administracion.

   PROVISIONAL: las pestanas ya funcionan.
   En la Fase C las tablas se llenaran desde la API de Flask
   (/api/reportes, /api/productos, /api/pedidos, /api/contacto),
   que ejecuta las vistas definidas en 05_views_reportes.sql
   ============================================================ */

document.addEventListener("DOMContentLoaded", function () {

    const botones = document.querySelectorAll(".tab-btn");
    const paneles = document.querySelectorAll(".admin-panel");

    if (botones.length === 0) {
        return;
    }

    /* ---------- Cambio de pestana ---------- */
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

    /* ---------- Mensaje mientras no hay base de datos ---------- */
    const tablas = [
        "tabla-rpt1",
        "tabla-rpt2",
        "tabla-productos",
        "tabla-pedidos",
        "tabla-mensajes"
    ];

    tablas.forEach(function (id) {
        mostrarSinDatos(id);
    });

    function mostrarSinDatos(idTabla) {
        const tabla = document.getElementById(idTabla);
        if (!tabla) {
            return;
        }

        const cuerpo = tabla.querySelector("tbody");
        const columnas = tabla.querySelectorAll("thead th").length;

        if (!cuerpo || cuerpo.children.length > 0) {
            return;
        }

        const fila  = document.createElement("tr");
        const celda = document.createElement("td");

        celda.className = "tabla-vacia";
        celda.colSpan = columnas;
        celda.textContent = "Sin datos. Pendiente de conectar la base de datos.";

        fila.appendChild(celda);
        cuerpo.appendChild(fila);
    }

    /* ---------- Boton del reporte 1 ---------- */
    const btnReporte = document.getElementById("btn-rpt1");
    if (btnReporte) {
        btnReporte.addEventListener("click", function () {
            rgeNotificar("El reporte se generara al conectar la base de datos.", "aviso");
        });
    }

});