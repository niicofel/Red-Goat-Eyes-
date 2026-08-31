INSERT INTO provincia (nombre) VALUES
    ('Azuay'),
    ('Bolivar'),
    ('Canar'),
    ('Carchi'),
    ('Chimborazo'),
    ('Cotopaxi'),
    ('El Oro'),
    ('Esmeraldas'),
    ('Galapagos'),
    ('Guayas'),
    ('Imbabura'),
    ('Loja'),
    ('Los Rios'),
    ('Manabi'),
    ('Morona Santiago'),
    ('Napo'),
    ('Orellana'),
    ('Pastaza'),
    ('Pichincha'),
    ('Santa Elena'),
    ('Santo Domingo de los Tsachilas'),
    ('Sucumbios'),
    ('Tungurahua'),
    ('Zamora Chinchipe')
ON CONFLICT (nombre) DO NOTHING;



INSERT INTO ciudad (id_provincia, nombre, costo_envio_base)
SELECT p.id_provincia, datos.ciudad, 0.00
FROM (VALUES
    ('Pichincha',                      'Quito'),
    ('Pichincha',                      'Sangolqui'),
    ('Guayas',                         'Guayaquil'),
    ('Guayas',                         'Duran'),
    ('Guayas',                         'Samborondon'),
    ('Azuay',                          'Cuenca'),
    ('Tungurahua',                     'Ambato'),
    ('Manabi',                         'Portoviejo'),
    ('Manabi',                         'Manta'),
    ('Manabi',                         'Chone'),
    ('Loja',                           'Loja'),
    ('Imbabura',                       'Ibarra'),
    ('Chimborazo',                     'Riobamba'),
    ('El Oro',                         'Machala'),
    ('El Oro',                         'Pasaje'),
    ('Esmeraldas',                     'Esmeraldas'),
    ('Santo Domingo de los Tsachilas', 'Santo Domingo'),
    ('Santa Elena',                    'Santa Elena'),
    ('Los Rios',                       'Babahoyo'),
    ('Cotopaxi',                       'Latacunga'),
    ('Bolivar',                        'Guaranda'),
    ('Canar',                          'Azogues'),
    ('Carchi',                         'Tulcan'),
    ('Morona Santiago',                'Macas'),
    ('Napo',                           'Tena'),
    ('Orellana',                       'Puerto Francisco de Orellana'),
    ('Pastaza',                        'Puyo'),
    ('Sucumbios',                      'Nueva Loja'),
    ('Zamora Chinchipe',               'Zamora'),
    ('Galapagos',                      'Puerto Baquerizo Moreno')
) AS datos(provincia, ciudad)
JOIN provincia p ON p.nombre = datos.provincia
ON CONFLICT (id_provincia, nombre) DO NOTHING;



INSERT INTO categoria (nombre, slug, descripcion, imagen_portada, activa) VALUES
    ('Hoodies',    'hoodies',
     'Hoodies oversize de gramaje pesado y siluetas boxy.',
     'assets/img/categorias/Hoodie1Portada.png', TRUE),

    ('Pantalones', 'pantalones',
     'Pantalones baggy, loose fit y workwear en denim y algodon.',
     'assets/img/categorias/Pantalon1Portada.png', TRUE),

    ('Accesorios', 'accesorios',
     'Gorras, gorros, collares y cadenas para completar el outfit.',
     'assets/img/categorias/Accesorios1Portada.png', TRUE)
ON CONFLICT (nombre) DO NOTHING;



INSERT INTO talla (codigo, descripcion, orden) VALUES
    ('XS',  'Extra Small',  1),
    ('S',   'Small',        2),
    ('M',   'Medium',       3),
    ('L',   'Large',        4),
    ('XL',  'Extra Large',  5),
    ('XXL', 'Double XL',    6),
    ('U',   'Talla unica',  7)
ON CONFLICT (codigo) DO NOTHING;



INSERT INTO estado_pedido (nombre, descripcion, orden) VALUES
    ('Pendiente',      'El pedido fue creado pero aun no se confirma el pago', 1),
    ('Pagado',         'El pago fue confirmado y se genera el recibo',         2),
    ('En preparacion', 'El pedido se esta empacando en bodega',                3),
    ('Enviado',        'El pedido salio hacia la direccion de entrega',        4),
    ('Entregado',      'El cliente recibio el pedido conforme',                5),
    ('Cancelado',      'El pedido fue anulado y el stock devuelto',            6)
ON CONFLICT (nombre) DO NOTHING;


INSERT INTO metodo_pago (nombre, activo) VALUES
    ('Transferencia bancaria',  TRUE),
    ('Efectivo contra entrega', TRUE),
    ('Deuna',                   TRUE),
    ('Tarjeta de credito',      TRUE)
ON CONFLICT (nombre) DO NOTHING;



INSERT INTO asunto_contacto (nombre, activo) VALUES
    ('Consulta',   TRUE),
    ('Reclamo',    TRUE),
    ('Sugerencia', TRUE)
ON CONFLICT (nombre) DO NOTHING;



INSERT INTO usuario (email, password_hash, rol, activo) VALUES
    ('admin@redgoateyes.com',
     '$2b$12$ypkEynRB15vj/aad1jPkV.aSf5Dvi5iXA22xI3PTEXb03PnLBXjqC',
     'administrador', TRUE)
ON CONFLICT (email) DO NOTHING;

INSERT INTO administrador (id_administrador, nombres, apellidos, cargo, nivel_acceso)
SELECT u.id_usuario, 'Felipe Nicolas', 'Campos Cisneros', 'Administrador general', 3
FROM usuario u
WHERE u.email = 'admin@redgoateyes.com'
ON CONFLICT (id_administrador) DO NOTHING;



INSERT INTO usuario (email, password_hash, rol, activo) VALUES
    ('maria.torres@example.com',
     '$2b$12$nzZDn5cbo9/imZ6og0KyguPIsl4f/79gnDbiGIT02uDNQKHp3myQC', 'cliente', TRUE),
    ('juan.ramirez@example.com',
     '$2b$12$nzZDn5cbo9/imZ6og0KyguPIsl4f/79gnDbiGIT02uDNQKHp3myQC', 'cliente', TRUE),
    ('ana.suarez@example.com',
     '$2b$12$nzZDn5cbo9/imZ6og0KyguPIsl4f/79gnDbiGIT02uDNQKHp3myQC', 'cliente', TRUE)
ON CONFLICT (email) DO NOTHING;


INSERT INTO cliente (id_cliente, nombres, apellidos, cedula, telefono, fecha_nacimiento, id_ciudad)
SELECT u.id_usuario, datos.nombres, datos.apellidos, datos.cedula,
       datos.telefono, datos.nacimiento::DATE, c.id_ciudad
FROM (VALUES
    ('maria.torres@example.com',  'Maria Fernanda', 'Torres Vega',    '1712345675', '0991234567', '2001-04-18', 'Quito'),
    ('juan.ramirez@example.com',  'Juan Carlos',    'Ramirez Solis',  '0923456784', '0987654321', '1999-11-03', 'Guayaquil'),
    ('ana.suarez@example.com',    'Ana Belen',      'Suarez Mora',    '0104567896', '0976543210', '2003-07-25', 'Cuenca')
) AS datos(email, nombres, apellidos, cedula, telefono, nacimiento, ciudad)
JOIN usuario u ON u.email = datos.email
JOIN ciudad  c ON c.nombre = datos.ciudad
ON CONFLICT (id_cliente) DO NOTHING;



INSERT INTO direccion_envio (id_cliente, id_ciudad, calle_principal, calle_secundaria,
                             numeracion, referencia, codigo_postal, es_principal)
SELECT cl.id_cliente, ci.id_ciudad, datos.principal, datos.secundaria,
       datos.numero, datos.referencia, datos.postal, TRUE
FROM (VALUES
    ('maria.torres@example.com', 'Quito',      'Av. 12 de Octubre', 'Vicente Ramon Roca', 'N24-593', 'Frente al parque El Arbolito', '170525'),
    ('juan.ramirez@example.com', 'Guayaquil',  'Av. Francisco de Orellana', 'Justino Cornejo', 'MZ 12 V 8', 'Ciudadela Kennedy Norte',  '090150'),
    ('ana.suarez@example.com',   'Cuenca',     'Av. Solano', 'Federico Malo', '3-24', 'Junto al estadio Alejandro Serrano', '010203')
) AS datos(email, ciudad, principal, secundaria, numero, referencia, postal)
JOIN usuario u  ON u.email = datos.email
JOIN cliente cl ON cl.id_cliente = u.id_usuario
JOIN ciudad ci  ON ci.nombre = datos.ciudad;



INSERT INTO producto (id_categoria, codigo, nombre, descripcion, precio,
                      imagen_principal, material, genero, activo, destacado)
SELECT c.id_categoria, datos.codigo, datos.nombre, datos.descripcion,
       datos.precio::NUMERIC(10,2), datos.imagen, datos.material,
       'Unisex', TRUE, datos.destacado
FROM (VALUES
    ('Hoodies', 'RGE-HOO-001', 'SUPERNOVA',
     'Hoodie oversize con estampado frontal de gran formato. Corte boxy y capucha forrada.',
     '35.00', 'assets/img/productos/Hoodie1.png', 'Algodon 80% poliester 20%, 380 gsm', TRUE),

    ('Hoodies', 'RGE-HOO-002', 'FADED ART',
     'Hoodie con lavado desgastado y grafica artistica en la espalda. Hombros caidos.',
     '35.00', 'assets/img/productos/Hoodie2.png', 'Algodon 80% poliester 20%, 380 gsm', FALSE),

    ('Hoodies', 'RGE-HOO-003', 'SCARLET CROS',
     'Hoodie de silueta amplia con bordado en pecho y punos acanalados reforzados.',
     '35.00', 'assets/img/productos/Hoodie3.png', 'Algodon 80% poliester 20%, 380 gsm', FALSE),

    ('Hoodies', 'RGE-HOO-004', 'COLD SPIRIT',
     'Hoodie de gramaje pesado pensado para clima frio. Interior perchado.',
     '35.00', 'assets/img/productos/Hoodie4.png', 'Algodon 80% poliester 20%, 400 gsm', FALSE),

    ('Hoodies', 'RGE-HOO-005', 'EMERALD SAINT',
     'Hoodie con paleta verde profunda y grafica serigrafiada a dos tintas.',
     '35.00', 'assets/img/productos/Hoodie5.png', 'Algodon 80% poliester 20%, 380 gsm', FALSE),

    ('Hoodies', 'RGE-HOO-006', 'NOIR BOTANICA',
     'Hoodie negro con motivo botanico en tono sobre tono. Acabado mate.',
     '35.00', 'assets/img/productos/Hoodie6.png', 'Algodon 80% poliester 20%, 380 gsm', TRUE),

    ('Hoodies', 'RGE-HOO-007', 'HAVEN',
     'Hoodie minimalista de linea limpia, sin estampado frontal. Bolsillo canguro.',
     '35.00', 'assets/img/productos/Hoodie7.png', 'Algodon 80% poliester 20%, 380 gsm', FALSE),

    ('Hoodies', 'RGE-HOO-008', 'COBALT BLOOM',
     'Hoodie con grafica floral en azul cobalto sobre base oscura. Edicion limitada.',
     '35.00', 'assets/img/productos/Hoodie8.png', 'Algodon 80% poliester 20%, 380 gsm', FALSE),

    ('Pantalones', 'RGE-PAN-001', 'GRAVITY Baggy Denim',
     'Pantalon baggy en denim rigido con caida amplia desde la cadera.',
     '29.99', 'assets/img/productos/Pantalones1.png', 'Denim 100% algodon, 14 oz', TRUE),

    ('Pantalones', 'RGE-PAN-002', 'ONYX Core Loose',
     'Pantalon loose fit en negro solido. Bolsillos laterales profundos.',
     '29.99', 'assets/img/productos/Pantalones2.png', 'Algodon 98% elastano 2%', FALSE),

    ('Pantalones', 'RGE-PAN-003', 'UTILITY Carpenter Blue',
     'Pantalon carpintero con presilla para herramientas y doble costura.',
     '29.99', 'assets/img/productos/Pantalones3.png', 'Denim 100% algodon, 12 oz', FALSE),

    ('Pantalones', 'RGE-PAN-004', 'INDIGO MIST Denim',
     'Denim en tono indigo claro con lavado suave y corte recto amplio.',
     '29.99', 'assets/img/productos/Pantalones4.png', 'Denim 100% algodon, 13 oz', FALSE),

    ('Pantalones', 'RGE-PAN-005', 'ASH Straight Baggy',
     'Pantalon recto baggy en gris ceniza. Pretina reforzada con cinco pasadores.',
     '29.99', 'assets/img/productos/Pantalones5.png', 'Algodon 100%, 12 oz', FALSE),

    ('Pantalones', 'RGE-PAN-006', 'STARDUST Acid Wash',
     'Denim con lavado acido irregular. Cada pieza tiene un patron unico.',
     '29.99', 'assets/img/productos/Pantalones6.png', 'Denim 100% algodon, 13 oz', TRUE),

    ('Pantalones', 'RGE-PAN-007', 'IVORY Workwear Pant',
     'Pantalon workwear en marfil con refuerzos en rodilla y bolsillo de regla.',
     '29.99', 'assets/img/productos/Pantalones7.png', 'Lona de algodon 100%, 10 oz', FALSE),

    ('Pantalones', 'RGE-PAN-008', 'SKYLINE Loose Fit',
     'Pantalon loose de caida vertical y tobillo abierto. Silueta arquitectonica.',
     '29.99', 'assets/img/productos/Pantalones8.png', 'Algodon 98% elastano 2%', FALSE),

    ('Accesorios', 'RGE-ACC-001', 'Gorro Alas de Espolon Oseo',
     'Gorro tejido de punto grueso con aplicacion lateral. Diseno de autor.',
     '25.00', 'assets/img/productos/Accesorios1.png', 'Acrilico 100%', FALSE),

    ('Accesorios', 'RGE-ACC-002', 'Collar cubano estilo Miami',
     'Collar de eslabon cubano con cierre de seguridad. Acabado brillante.',
     '15.00', 'assets/img/productos/Accesorios2.png', 'Acero inoxidable 316L', FALSE),

    ('Accesorios', 'RGE-ACC-003', 'Cadena de acero inoxidable banada en plata',
     'Cadena de eslabon fino banada en plata. Resistente al agua y al oxido.',
     '16.00', 'assets/img/productos/Accesorios3.png', 'Acero inoxidable banado en plata', FALSE),

    ('Accesorios', 'RGE-ACC-004', 'Gorra Los Angeles Dodgers MLB Floral',
     'Gorra snapback con bordado del equipo y forro interior floral.',
     '79.00', 'assets/img/productos/Accesorios4.png', 'Poliester 100%', TRUE),

    ('Accesorios', 'RGE-ACC-005', 'Gorra Los Angeles Dodgers MLB Cloud',
     'Gorra con degradado tipo nube y visera plana. Ajuste trasero regulable.',
     '75.00', 'assets/img/productos/Accesorios5.png', 'Poliester 100%', FALSE),

    ('Accesorios', 'RGE-ACC-006', 'Gorra Los Angeles Dodgers MLB Food Icon',
     'Gorra de edicion especial con iconos bordados en la visera.',
     '69.99', 'assets/img/productos/Accesorios6.png', 'Poliester 100%', FALSE),

    ('Accesorios', 'RGE-ACC-007', 'Gorra Chicago Cubs MLB Mascots',
     'Gorra con la mascota del equipo bordada en frente y lateral.',
     '73.00', 'assets/img/productos/Accesorios7.png', 'Poliester 100%', FALSE),

    ('Accesorios', 'RGE-ACC-008', 'Gorra New York Yankees MLB Many Patch',
     'Gorra con multiples parches cosidos. Pieza de coleccion.',
     '75.00', 'assets/img/productos/Accesorios8.png', 'Poliester 100%', TRUE)

) AS datos(categoria, codigo, nombre, descripcion, precio, imagen, material, destacado)
JOIN categoria c ON c.nombre = datos.categoria
ON CONFLICT (codigo) DO NOTHING;


INSERT INTO producto_talla (id_producto, id_talla, stock, stock_minimo)
SELECT p.id_producto, t.id_talla, datos.stock, 3
FROM (VALUES
    ('RGE-HOO-001', 18),   -- vendio 2 unidades
    ('RGE-HOO-002', 20),
    ('RGE-HOO-003', 20),
    ('RGE-HOO-004', 15),
    ('RGE-HOO-005', 20),
    ('RGE-HOO-006', 12),
    ('RGE-HOO-007', 19),
    ('RGE-HOO-008',  2),
    ('RGE-PAN-001', 17),
    ('RGE-PAN-002', 20),
    ('RGE-PAN-003', 14),
    ('RGE-PAN-004', 20),
    ('RGE-PAN-005', 18),
    ('RGE-PAN-006', 10),
    ('RGE-PAN-007', 20),
    ('RGE-PAN-008', 20),   
    ('RGE-ACC-001', 20),
    ('RGE-ACC-002', 19),   
    ('RGE-ACC-003', 18),   
    ('RGE-ACC-004', 19),   
    ('RGE-ACC-005', 20),
    ('RGE-ACC-006',  8),
    ('RGE-ACC-007', 20),
    ('RGE-ACC-008', 19)    
) AS datos(codigo, stock)
JOIN producto p ON p.codigo = datos.codigo
JOIN talla    t ON t.codigo = 'U'
ON CONFLICT (id_producto, id_talla) DO NOTHING;


INSERT INTO imagen_producto (id_producto, url, alt_text, orden)
SELECT p.id_producto, p.imagen_principal,
       CASE
           WHEN p.codigo LIKE 'RGE-HOO%' THEN 'Hoodie ' || p.nombre
           WHEN p.codigo LIKE 'RGE-PAN%' THEN 'Pantalon ' || p.nombre
           ELSE p.nombre
       END,
       1
FROM producto p
ON CONFLICT (id_producto, orden) DO NOTHING;


INSERT INTO pedido (codigo_pedido, id_cliente, id_direccion, id_estado,
                    id_metodo_pago, fecha_pedido, subtotal, iva, costo_envio, total)
SELECT datos.codigo, cl.id_cliente, d.id_direccion, e.id_estado, m.id_metodo,
       datos.fecha::TIMESTAMP,
       datos.subtotal::NUMERIC(10,2),
       datos.iva::NUMERIC(10,2),
       0.00,
       datos.total::NUMERIC(10,2)
FROM (VALUES
    ('RGE-2026-0001', 'maria.torres@example.com', 'Entregado',      'Transferencia bancaria',  '2026-07-14 10:22:00', '70.00', '10.50', '80.50'),
    ('RGE-2026-0002', 'juan.ramirez@example.com', 'Entregado',      'Deuna',                   '2026-07-28 16:05:00', '94.00', '14.10', '108.10'),
    ('RGE-2026-0003', 'maria.torres@example.com', 'Enviado',        'Transferencia bancaria',  '2026-08-11 09:47:00', '89.97', '13.50', '103.47'),
    ('RGE-2026-0004', 'ana.suarez@example.com',   'En preparacion', 'Efectivo contra entrega', '2026-08-20 14:30:00', '67.00', '10.05', '77.05'),
    ('RGE-2026-0005', 'juan.ramirez@example.com', 'Pagado',         'Tarjeta de credito',      '2026-08-26 18:12:00', '75.00', '11.25', '86.25')
) AS datos(codigo, email, estado, metodo, fecha, subtotal, iva, total)
JOIN usuario u          ON u.email  = datos.email
JOIN cliente cl         ON cl.id_cliente = u.id_usuario
JOIN direccion_envio d  ON d.id_cliente  = cl.id_cliente
JOIN estado_pedido e    ON e.nombre = datos.estado
JOIN metodo_pago m      ON m.nombre = datos.metodo
ON CONFLICT (codigo_pedido) DO NOTHING;


INSERT INTO detalle_pedido (id_pedido, id_producto_talla, cantidad, precio_unitario, descuento)
SELECT ped.id_pedido, pt.id_producto_talla, datos.cantidad, datos.precio::NUMERIC(10,2), 0.00
FROM (VALUES
    ('RGE-2026-0001', 'RGE-HOO-001', 2, '35.00'),
    ('RGE-2026-0002', 'RGE-ACC-004', 1, '79.00'),
    ('RGE-2026-0002', 'RGE-ACC-002', 1, '15.00'),
    ('RGE-2026-0003', 'RGE-PAN-001', 3, '29.99'),
    ('RGE-2026-0004', 'RGE-HOO-007', 1, '35.00'),
    ('RGE-2026-0004', 'RGE-ACC-003', 2, '16.00'),
    ('RGE-2026-0005', 'RGE-ACC-008', 1, '75.00')
) AS datos(pedido, producto, cantidad, precio)
JOIN pedido ped         ON ped.codigo_pedido = datos.pedido
JOIN producto p         ON p.codigo = datos.producto
JOIN talla t            ON t.codigo = 'U'
JOIN producto_talla pt  ON pt.id_producto = p.id_producto AND pt.id_talla = t.id_talla
ON CONFLICT (id_pedido, id_producto_talla) DO NOTHING;


INSERT INTO mensaje_contacto (id_asunto, id_ciudad, id_cliente, nombre, email,
                              descripcion, leido, fecha_envio)
SELECT a.id_asunto, ci.id_ciudad, cl.id_cliente, datos.nombre, datos.email,
       datos.descripcion, datos.leido, datos.fecha::TIMESTAMP
FROM (VALUES
    ('Consulta',   'Quito',     'maria.torres@example.com', 'Maria Fernanda Torres', 'maria.torres@example.com',
     'Buenas tardes, quisiera saber si tienen mas unidades del hoodie COBALT BLOOM disponibles.', TRUE,  '2026-08-02 11:15:00'),

    ('Reclamo',    'Guayaquil', 'juan.ramirez@example.com', 'Juan Carlos Ramirez',   'juan.ramirez@example.com',
     'Mi pedido llego con un dia de retraso respecto a la fecha estimada de entrega.',           TRUE,  '2026-08-09 08:40:00'),

    ('Sugerencia', 'Cuenca',    'ana.suarez@example.com',   'Ana Belen Suarez',      'ana.suarez@example.com',
     'Seria excelente que agregaran una guia de tallas con medidas exactas en centimetros.',     FALSE, '2026-08-18 19:05:00'),

    ('Consulta',   'Ambato',    NULL,                       'Diego Andres Paredes',  'diego.paredes@example.com',
     'Hola, hacen envios a Ambato y cual es el tiempo estimado de entrega para esa ciudad.',     FALSE, '2026-08-25 15:50:00')
) AS datos(asunto, ciudad, email_cliente, nombre, email, descripcion, leido, fecha)
JOIN asunto_contacto a ON a.nombre = datos.asunto
JOIN ciudad ci         ON ci.nombre = datos.ciudad
LEFT JOIN usuario u    ON u.email = datos.email_cliente
LEFT JOIN cliente cl   ON cl.id_cliente = u.id_usuario;


SELECT 'provincia'         AS tabla, COUNT(*) AS cargados, 24 AS esperado FROM provincia
UNION ALL SELECT 'ciudad',            COUNT(*), 30 FROM ciudad
UNION ALL SELECT 'categoria',         COUNT(*),  3 FROM categoria
UNION ALL SELECT 'talla',             COUNT(*),  7 FROM talla
UNION ALL SELECT 'estado_pedido',     COUNT(*),  6 FROM estado_pedido
UNION ALL SELECT 'metodo_pago',       COUNT(*),  4 FROM metodo_pago
UNION ALL SELECT 'asunto_contacto',   COUNT(*),  3 FROM asunto_contacto
UNION ALL SELECT 'usuario',           COUNT(*),  4 FROM usuario
UNION ALL SELECT 'administrador',     COUNT(*),  1 FROM administrador
UNION ALL SELECT 'cliente',           COUNT(*),  3 FROM cliente
UNION ALL SELECT 'direccion_envio',   COUNT(*),  3 FROM direccion_envio
UNION ALL SELECT 'producto',          COUNT(*), 24 FROM producto
UNION ALL SELECT 'producto_talla',    COUNT(*), 24 FROM producto_talla
UNION ALL SELECT 'imagen_producto',   COUNT(*), 24 FROM imagen_producto
UNION ALL SELECT 'pedido',            COUNT(*),  5 FROM pedido
UNION ALL SELECT 'detalle_pedido',    COUNT(*),  7 FROM detalle_pedido
UNION ALL SELECT 'mensaje_contacto',  COUNT(*),  4 FROM mensaje_contacto
ORDER BY tabla;


SELECT p.codigo_pedido,
       SUM(d.subtotal_linea) AS suma_lineas,
       p.subtotal            AS subtotal_cabecera,
       CASE WHEN SUM(d.subtotal_linea) = p.subtotal
            THEN 'OK' ELSE 'DESCUADRE' END AS control
FROM pedido p
JOIN detalle_pedido d ON d.id_pedido = p.id_pedido
GROUP BY p.codigo_pedido, p.subtotal
ORDER BY p.codigo_pedido;

