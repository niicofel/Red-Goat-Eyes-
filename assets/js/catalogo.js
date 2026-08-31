document.addEventListener("DOMContentLoaded", async function () {

    const tarjetas = document.querySelectorAll(".card[data-id]");

    if (tarjetas.length === 0) {
        return;
    }

    let catalogo = [];

    try {
        if (typeof rgeCatalogo === "function") {
            catalogo = await rgeCatalogo();
        }
    } catch (error) {
        if (typeof rgeNotificar === "function") {
            rgeNotificar(error.mensaje, "aviso");
        }
    }

    tarjetas.forEach(function (tarjeta) {
        sincronizarTarjeta(tarjeta, catalogo);

        // EVENTO: Abrir modal al hacer clic en la tarjeta o en el botón "VER DETALLES"
        tarjeta.addEventListener("click", function () {
            abrirModalDetalle(tarjeta.dataset.id);
        });
    });

    function sincronizarTarjeta(tarjeta, lista) {
        const real = lista.find(function (producto) {
            return producto.codigo === tarjeta.dataset.id;
        });

        // Cambiar el botón principal por "VER DETALLES"
        let botonVer = tarjeta.querySelector(".btn-agregar") || tarjeta.querySelector(".btn-ver-mas");
        if (botonVer) {
            botonVer.className = "btn-ver-mas";
            botonVer.textContent = "VER DETALLES";
            botonVer.type = "button";
        }

        // Tallas a mostrar en la tarjeta principal
        const tallasDisponibles = (real && real.tallas && real.tallas.length > 0) 
            ? real.tallas 
            : [
                { nombre_talla: "S", stock: 2 },
                { nombre_talla: "M", stock: 5 },
                { nombre_talla: "L", stock: 1 },
                { nombre_talla: "XL", stock: 0 }
            ];

        // Insertar visualización de tallas debajo del precio en la tarjeta principal
        let contenedorTallasTarjeta = tarjeta.querySelector(".card-tallas-preview");
        if (!contenedorTallasTarjeta) {
            contenedorTallasTarjeta = document.createElement("div");
            contenedorTallasTarjeta.className = "card-tallas-preview";
            const cardContent = tarjeta.querySelector(".card-content") || tarjeta;
            const precioElem = tarjeta.querySelector(".price");
            if (precioElem && precioElem.parentNode) {
                precioElem.parentNode.insertBefore(contenedorTallasTarjeta, precioElem.nextSibling);
            } else {
                cardContent.appendChild(contenedorTallasTarjeta);
            }
        }

        contenedorTallasTarjeta.innerHTML = tallasDisponibles.map(t => 
            `<span class="badge-talla-card ${t.stock === 0 ? 'agotada' : ''}">${t.nombre_talla || t.talla}</span>`
        ).join("");

        if (!real) {
            tarjeta.dataset.disponible = "false";
            return;
        }

        tarjeta.dataset.ptid = real.id_producto_talla;
        tarjeta.dataset.precio = real.precio_final;
        tarjeta.dataset.stock = real.stock;
        tarjeta.dataset.disponible = real.stock > 0 ? "true" : "false";

        const etiquetaPrecio = tarjeta.querySelector(".price");
        if (etiquetaPrecio && typeof rgeFormatearPrecio === "function") {
            etiquetaPrecio.textContent = rgeFormatearPrecio(real.precio_final);
        }

        // Badge de Stock
        let badgeStock = tarjeta.querySelector(".badge-stock");
        if (!badgeStock) {
            badgeStock = document.createElement("span");
            badgeStock.className = "badge-stock";
            const contenedorImagen = tarjeta.querySelector(".card-image") || tarjeta;
            contenedorImagen.appendChild(badgeStock);
        }

        if (real.stock > 0) {
            badgeStock.textContent = real.stock + " DISPONIBLES";
            badgeStock.classList.remove("agotado");
            badgeStock.classList.add("disponible");
        } else {
            badgeStock.textContent = "AGOTADO";
            badgeStock.classList.remove("disponible");
            badgeStock.classList.add("agotado");
            if (botonVer) {
                botonVer.textContent = "AGOTADO";
                botonVer.disabled = true;
            }
        }
    }

    async function abrirModalDetalle(codigo) {
        try {
            let producto;
            if (typeof rgeBuscarPorCodigo === "function") {
                producto = await rgeBuscarPorCodigo(codigo);
            }

            if (!producto) {
                const tarjetaDom = document.querySelector(`.card[data-id="${codigo}"]`);
                producto = {
                    codigo: codigo,
                    nombre: tarjetaDom ? tarjetaDom.querySelector("h3")?.textContent : "PRENDA",
                    precio_final: tarjetaDom ? tarjetaDom.dataset.precio || "35.00" : "35.00",
                    imagen_principal: tarjetaDom ? tarjetaDom.dataset.imagen : "",
                    categoria: "HOODIE",
                    stock: tarjetaDom ? parseInt(tarjetaDom.dataset.stock) || 0 : 0
                };
            }

            // Mapeo de tallas para el modal
            const listaTallasModal = (producto.tallas && producto.tallas.length > 0)
                ? producto.tallas
                : [
                    { id_producto_talla: 1, nombre_talla: "S", stock: 2 },
                    { id_producto_talla: 2, nombre_talla: "M", stock: 5 },
                    { id_producto_talla: 3, nombre_talla: "L", stock: 1 },
                    { id_producto_talla: 4, nombre_talla: "XL", stock: 0 }
                ];

            let htmlTallas = "";
            let tallaSeleccionadaId = null;

            htmlTallas = listaTallasModal.map(function (t) {
                const sinStock = t.stock <= 0;
                const esPrimeraDisponible = !sinStock && !tallaSeleccionadaId;
                if (esPrimeraDisponible) tallaSeleccionadaId = t.id_producto_talla;

                return `
                    <button type="button" 
                            class="btn-talla-opcion ${sinStock ? 'sin-stock' : ''} ${esPrimeraDisponible ? 'selected' : ''}" 
                            ${sinStock ? 'disabled' : ''} 
                            data-ptid="${t.id_producto_talla}"
                            data-stock="${t.stock}">
                        ${t.nombre_talla || t.talla}
                    </button>
                `;
            }).join("");

            let contenedorModal = document.getElementById("modal-producto");
            if (!contenedorModal) {
                contenedorModal = document.createElement("div");
                contenedorModal.id = "modal-producto";
                contenedorModal.className = "modal-overlay";
                document.body.appendChild(contenedorModal);
            }

            const formatear = typeof rgeFormatearPrecio === "function" ? rgeFormatearPrecio : (p) => "$" + p;

            contenedorModal.innerHTML = `
                <div class="modal-card">
                    <button type="button" class="btn-cerrar-modal">&times;</button>
                    <div class="modal-grid">
                        <div class="modal-img-wrapper">
                            <img src="${producto.imagen_principal || tarjetaImg(codigo)}" alt="${producto.nombre}">
                        </div>
                        <div class="modal-details">
                            <span class="modal-categoria">${producto.categoria || 'URBAN ARCHIVE'}</span>
                            <h2 class="modal-titulo">${producto.nombre}</h2>
                            <p class="modal-precio">${formatear(producto.precio_final)}</p>
                            
                            <div class="modal-seccion">
                                <h4>DESCRIPCIÓN</h4>
                                <p>${producto.descripcion || 'Silueta Boxy Fit / Heavyweight Fleece / Calidad Premium.'}</p>
                            </div>

                            <div class="modal-seccion">
                                <h4>SELECCIONAR TALLA</h4>
                                <div class="modal-tallas-grid">
                                    ${htmlTallas}
                                </div>
                            </div>

                            <div class="modal-seccion modal-acciones-row">
                                <div class="selector-cantidad">
                                    <button type="button" class="btn-cant" id="cant-menos">-</button>
                                    <input type="number" id="cant-input" value="1" min="1" max="10" readonly>
                                    <button type="button" class="btn-cant" id="cant-mas">+</button>
                                </div>
                                <button type="button" class="btn-agregar-modal" id="btn-comprar-modal">
                                    <i class="fa-solid fa-cart-shopping"></i> AÑADIR AL CARRITO
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            contenedorModal.classList.add("activo");

            // Eventos de selección de tallas dentro del modal
            const botonesTalla = contenedorModal.querySelectorAll(".btn-talla-opcion");
            botonesTalla.forEach(btn => {
                btn.addEventListener("click", function () {
                    botonesTalla.forEach(b => b.classList.remove("selected"));
                    btn.classList.add("selected");
                    tallaSeleccionadaId = btn.dataset.ptid;
                });
            });

            // Controles de cantidad (+ / -)
            const inputCant = contenedorModal.querySelector("#cant-input");
            contenedorModal.querySelector("#cant-menos").addEventListener("click", () => {
                let v = parseInt(inputCant.value);
                if (v > 1) inputCant.value = v - 1;
            });
            contenedorModal.querySelector("#cant-mas").addEventListener("click", () => {
                let v = parseInt(inputCant.value);
                if (v < 10) inputCant.value = v + 1;
            });

            // Añadir al carrito desde el modal
            contenedorModal.querySelector("#btn-comprar-modal").addEventListener("click", async () => {
                const cantidad = parseInt(inputCant.value);
                await ejecutarAgregarCarrito(producto, tallaSeleccionadaId, cantidad, contenedorModal);
            });

            // Cerrar modal
            contenedorModal.querySelector(".btn-cerrar-modal").addEventListener("click", () => {
                contenedorModal.classList.remove("activo");
            });
            contenedorModal.addEventListener("click", (e) => {
                if (e.target === contenedorModal) contenedorModal.classList.remove("activo");
            });

        } catch (error) {
            console.error("Error al desplegar modal:", error);
        }
    }

    function tarjetaImg(codigo) {
        const tarjeta = document.querySelector(`.card[data-id="${codigo}"]`);
        return tarjeta ? tarjeta.dataset.imagen : '';
    }

    async function ejecutarAgregarCarrito(producto, ptid, cantidad, modal) {
        if (typeof rgeLeerCarrito !== "function") return;

        const carrito = rgeLeerCarrito();
        const existente = carrito.find(item => item.codigo === producto.codigo && item.id_producto_talla === ptid);
        const cantidadFinal = existente ? existente.cantidad + cantidad : cantidad;

        if (existente) {
            existente.cantidad = cantidadFinal;
        } else {
            carrito.push({
                codigo: producto.codigo,
                id_producto_talla: ptid || producto.id_producto_talla,
                nombre: producto.nombre,
                precio: producto.precio_final,
                imagen: producto.imagen_principal || tarjetaImg(producto.codigo),
                categoria: producto.categoria,
                cantidad: cantidad
            });
        }

        if (typeof rgeGuardarCarrito === "function") rgeGuardarCarrito(carrito);
        if (typeof rgeNotificar === "function") rgeNotificar(producto.nombre + " añadido al carrito", "exito");

        modal.classList.remove("activo");
    }

});