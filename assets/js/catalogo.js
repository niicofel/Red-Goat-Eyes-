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

        tarjeta.addEventListener("click", function () {
            abrirModalDetalle(tarjeta.dataset.id);
        });
    });

    function sincronizarTarjeta(tarjeta, lista) {
        const real = lista.find(function (producto) {
            return producto.codigo === tarjeta.dataset.id;
        });

        const boton = tarjeta.querySelector(".btn-agregar, .btn-ver-mas");

        if (boton) {
            boton.className = "btn-ver-mas";
            boton.type = "button";
            boton.textContent = "VER DETALLES";
        }

        if (!real) {
            tarjeta.dataset.disponible = "false";
            if (boton) {
                boton.disabled = true;
                boton.textContent = "NO DISPONIBLE";
            }
            return;
        }

        tarjeta.dataset.ptid = real.id_producto_talla;
        tarjeta.dataset.precio = real.precio_final;
        tarjeta.dataset.stock = real.stock;
        tarjeta.dataset.disponible = real.disponible ? "true" : "false";

        const etiquetaPrecio = tarjeta.querySelector(".price");
        if (etiquetaPrecio) {
            etiquetaPrecio.textContent = rgeFormatearPrecio(real.precio_final);
        }

        pintarBadgeStock(tarjeta, real);
        pintarTallasTarjeta(tarjeta, real);

        if (boton && !real.disponible) {
            boton.disabled = true;
            boton.textContent = "AGOTADO";
        }
    }

    function pintarBadgeStock(tarjeta, real) {
        const contenedor = tarjeta.querySelector(".card-image") || tarjeta;
        let badge = tarjeta.querySelector(".badge-stock");

        if (!badge) {
            badge = document.createElement("span");
            badge.className = "badge-stock";
            contenedor.appendChild(badge);
        }

        if (real.stock > 0) {
            badge.textContent = real.stock + " DISPONIBLES";
            badge.classList.remove("agotado");
        } else {
            badge.textContent = "AGOTADO";
            badge.classList.add("agotado");
        }
    }

    function pintarTallasTarjeta(tarjeta, real) {
        let contenedor = tarjeta.querySelector(".card-tallas-preview");

        if (!contenedor) {
            contenedor = document.createElement("div");
            contenedor.className = "card-tallas-preview";

            const precio = tarjeta.querySelector(".price");

            if (precio && precio.parentNode) {
                precio.parentNode.insertBefore(contenedor, precio.nextSibling);
            } else {
                (tarjeta.querySelector(".card-info") || tarjeta).appendChild(contenedor);
            }
        }

        contenedor.textContent = "";

        (real.tallas || []).forEach(function (codigoTalla) {
            const etiqueta = document.createElement("span");
            etiqueta.className = "badge-talla-card";
            etiqueta.textContent = codigoTalla;
            contenedor.appendChild(etiqueta);
        });
    }

    async function abrirModalDetalle(codigo) {
        let producto;

        try {
            producto = await rgeApi("/productos/" + encodeURIComponent(codigo));
        } catch (error) {
            rgeNotificar(error.mensaje, "aviso");
            return;
        }

        const modal = obtenerModal();
        modal.textContent = "";
        modal.appendChild(construirTarjetaModal(producto, modal));
        modal.classList.add("activo");
        document.body.classList.add("modal-abierto");
    }

    function obtenerModal() {
        let modal = document.getElementById("modal-producto");

        if (!modal) {
            modal = document.createElement("div");
            modal.id = "modal-producto";
            modal.className = "modal-overlay";
            document.body.appendChild(modal);

            modal.addEventListener("click", function (evento) {
                if (evento.target === modal) {
                    cerrarModal(modal);
                }
            });

            document.addEventListener("keydown", function (evento) {
                if (evento.key === "Escape") {
                    cerrarModal(modal);
                }
            });
        }

        return modal;
    }

    function cerrarModal(modal) {
        modal.classList.remove("activo");
        document.body.classList.remove("modal-abierto");
    }

    function construirTarjetaModal(producto, modal) {
        const tarjeta = crear("div", "modal-card");

        const cerrar = crear("button", "btn-cerrar-modal", "×");
        cerrar.type = "button";
        cerrar.setAttribute("aria-label", "Cerrar");
        cerrar.addEventListener("click", function () {
            cerrarModal(modal);
        });
        tarjeta.appendChild(cerrar);

        const grid = crear("div", "modal-grid");

        const marco = crear("div", "modal-img-wrapper");
        const imagen = document.createElement("img");
        imagen.src = imagenDeTarjeta(producto.codigo) || producto.imagen_principal || "";
        imagen.alt = producto.nombre;
        marco.appendChild(imagen);
        grid.appendChild(marco);

        const detalles = crear("div", "modal-details");
        detalles.appendChild(crear("span", "modal-categoria", producto.categoria || ""));
        detalles.appendChild(crear("h2", "modal-titulo", producto.nombre));
        detalles.appendChild(crear("p", "modal-precio", rgeFormatearPrecio(producto.precio_final)));

        const bloqueDesc = crear("div", "modal-seccion");
        bloqueDesc.appendChild(crear("h4", null, "DESCRIPCION"));
        bloqueDesc.appendChild(crear("p", null, producto.descripcion || ""));
        detalles.appendChild(bloqueDesc);

        const estado = { ptid: null, stock: 0 };

        const bloqueTallas = crear("div", "modal-seccion");
        bloqueTallas.appendChild(crear("h4", null, "SELECCIONAR TALLA"));

        const rejilla = crear("div", "modal-tallas-grid");
        const botonesTalla = [];

        (producto.tallas || []).forEach(function (talla) {
            const boton = crear("button", "btn-talla-opcion", talla.nombre_talla);
            boton.type = "button";
            boton.dataset.ptid = talla.id_producto_talla;
            boton.dataset.stock = talla.stock;
            boton.title = talla.descripcion + " - " + talla.stock + " disponibles";

            if (!talla.disponible) {
                boton.disabled = true;
                boton.classList.add("sin-stock");
            } else if (estado.ptid === null) {
                estado.ptid = talla.id_producto_talla;
                estado.stock = talla.stock;
                boton.classList.add("selected");
            }

            boton.addEventListener("click", function () {
                botonesTalla.forEach(function (otro) {
                    otro.classList.remove("selected");
                });
                boton.classList.add("selected");
                estado.ptid = parseInt(boton.dataset.ptid, 10);
                estado.stock = parseInt(boton.dataset.stock, 10);
                entrada.value = 1;
                actualizarAviso();
            });

            botonesTalla.push(boton);
            rejilla.appendChild(boton);
        });

        bloqueTallas.appendChild(rejilla);

        const aviso = crear("small", "modal-aviso-stock");
        bloqueTallas.appendChild(aviso);
        detalles.appendChild(bloqueTallas);

        const acciones = crear("div", "modal-seccion modal-acciones-row");

        const selector = crear("div", "selector-cantidad");
        const menos = crear("button", "btn-cant", "-");
        menos.type = "button";
        const entrada = document.createElement("input");
        entrada.type = "number";
        entrada.id = "cant-input";
        entrada.value = "1";
        entrada.min = "1";
        entrada.readOnly = true;
        const mas = crear("button", "btn-cant", "+");
        mas.type = "button";

        menos.addEventListener("click", function () {
            const valor = parseInt(entrada.value, 10);
            if (valor > 1) {
                entrada.value = valor - 1;
                actualizarAviso();
            }
        });

        mas.addEventListener("click", function () {
            const valor = parseInt(entrada.value, 10);
            if (valor < estado.stock) {
                entrada.value = valor + 1;
                actualizarAviso();
            } else {
                rgeNotificar("Solo quedan " + estado.stock + " unidades de esa talla", "aviso");
            }
        });

        selector.appendChild(menos);
        selector.appendChild(entrada);
        selector.appendChild(mas);
        acciones.appendChild(selector);

        const comprar = crear("button", "btn-agregar-modal", "AÑADIR AL CARRITO");
        comprar.type = "button";

        comprar.addEventListener("click", async function () {
            await agregarAlCarrito(producto, estado, parseInt(entrada.value, 10), modal, comprar);
        });

        acciones.appendChild(comprar);
        detalles.appendChild(acciones);

        if (estado.ptid === null) {
            comprar.disabled = true;
            comprar.textContent = "SIN STOCK";
        }

        function actualizarAviso() {
            aviso.textContent = estado.ptid === null
                ? "Este producto no tiene tallas disponibles"
                : "Quedan " + estado.stock + " unidades de esta talla";
        }

        actualizarAviso();

        grid.appendChild(detalles);
        tarjeta.appendChild(grid);
        return tarjeta;
    }

    function crear(etiqueta, clases, texto) {
        const elemento = document.createElement(etiqueta);

        if (clases) {
            elemento.className = clases;
        }
        if (texto !== undefined && texto !== null) {
            elemento.textContent = texto;
        }

        return elemento;
    }

    function imagenDeTarjeta(codigo) {
        const tarjeta = document.querySelector('.card[data-id="' + codigo + '"]');
        return tarjeta ? tarjeta.dataset.imagen : "";
    }

    async function agregarAlCarrito(producto, estado, cantidad, modal, boton) {
        if (estado.ptid === null) {
            rgeNotificar("Selecciona una talla disponible", "aviso");
            return;
        }

        const carrito = rgeLeerCarrito();

        const existente = carrito.find(function (item) {
            return item.id_producto_talla === estado.ptid;
        });

        const total = existente ? existente.cantidad + cantidad : cantidad;

        boton.disabled = true;

        try {
            const respuesta = await rgeApi("/productos/disponibilidad/" + estado.ptid +
                                          "?cantidad=" + total);

            if (!respuesta.disponible) {
                rgeNotificar("Solo quedan " + estado.stock + " unidades de esa talla", "aviso");
                return;
            }
        } catch (error) {
            rgeNotificar(error.mensaje, "aviso");
            return;
        } finally {
            boton.disabled = false;
        }

        const talla = (producto.tallas || []).find(function (t) {
            return t.id_producto_talla === estado.ptid;
        });

        if (existente) {
            existente.cantidad = total;
            existente.precio = producto.precio_final;
        } else {
            carrito.push({
                codigo: producto.codigo,
                id_producto_talla: estado.ptid,
                nombre: producto.nombre,
                talla: talla ? talla.nombre_talla : "",
                precio: producto.precio_final,
                imagen: imagenDeTarjeta(producto.codigo) || producto.imagen_principal,
                categoria: producto.categoria,
                stock: estado.stock,
                cantidad: cantidad
            });
        }

        rgeGuardarCarrito(carrito);
        rgeNotificar(producto.nombre + " talla " + (talla ? talla.nombre_talla : "") +
                     " agregado al carrito", "exito");
        cerrarModal(modal);
    }

});