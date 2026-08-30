CREATE OR REPLACE VIEW rpt_ventas_por_categoria AS
SELECT
    c.nombre                                        AS categoria,
    COUNT(DISTINCT p.id_producto)                   AS productos_vendidos,
    COUNT(DISTINCT ped.id_pedido)                   AS pedidos,
    SUM(d.cantidad)                                 AS unidades,
    SUM(d.subtotal_linea)::NUMERIC(12,2)            AS total_vendido,
    ROUND(AVG(d.precio_unitario), 2)                AS precio_promedio,
    ROUND(SUM(d.subtotal_linea)
          / NULLIF(COUNT(DISTINCT ped.id_pedido), 0), 2) AS ticket_promedio,
    RANK() OVER (ORDER BY SUM(d.subtotal_linea) DESC)    AS ranking,
    ROUND(100.0 * SUM(d.subtotal_linea)
          / SUM(SUM(d.subtotal_linea)) OVER (), 2)       AS porcentaje_del_total
FROM        categoria       c
JOIN        producto        p   ON p.id_categoria      = c.id_categoria
JOIN        producto_talla  pt  ON pt.id_producto      = p.id_producto
JOIN        talla           t   ON t.id_talla          = pt.id_talla
JOIN        detalle_pedido  d   ON d.id_producto_talla = pt.id_producto_talla
JOIN        pedido          ped ON ped.id_pedido       = d.id_pedido
JOIN        estado_pedido   e   ON e.id_estado         = ped.id_estado
WHERE       e.nombre <> 'Cancelado'
GROUP BY    c.id_categoria, c.nombre
HAVING      SUM(d.cantidad) > 0
ORDER BY    total_vendido DESC;

COMMENT ON VIEW rpt_ventas_por_categoria IS
    'Reporte 1: ventas agregadas por categoria con ranking. JOIN de 6 tablas + RANK() OVER';



CREATE OR REPLACE FUNCTION fn_rpt_ventas_por_categoria(
    p_desde DATE DEFAULT NULL,
    p_hasta DATE DEFAULT NULL
)
RETURNS TABLE (
    categoria            VARCHAR(50),
    productos_vendidos   BIGINT,
    pedidos              BIGINT,
    unidades             BIGINT,
    total_vendido        NUMERIC(12,2),
    ticket_promedio      NUMERIC,
    ranking              BIGINT
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        c.nombre,
        COUNT(DISTINCT p.id_producto),
        COUNT(DISTINCT ped.id_pedido),
        SUM(d.cantidad),
        SUM(d.subtotal_linea)::NUMERIC(12,2),
        ROUND(SUM(d.subtotal_linea) / NULLIF(COUNT(DISTINCT ped.id_pedido), 0), 2),
        RANK() OVER (ORDER BY SUM(d.subtotal_linea) DESC)
    FROM        categoria       c
    JOIN        producto        p   ON p.id_categoria      = c.id_categoria
    JOIN        producto_talla  pt  ON pt.id_producto      = p.id_producto
    JOIN        detalle_pedido  d   ON d.id_producto_talla = pt.id_producto_talla
    JOIN        pedido          ped ON ped.id_pedido       = d.id_pedido
    JOIN        estado_pedido   e   ON e.id_estado         = ped.id_estado
    WHERE       e.nombre <> 'Cancelado'

      AND       (p_desde IS NULL OR ped.fecha_pedido >= p_desde)
      AND       (p_hasta IS NULL OR ped.fecha_pedido < (p_hasta + INTERVAL '1 day'))
    GROUP BY    c.id_categoria, c.nombre
    HAVING      SUM(d.cantidad) > 0
    ORDER BY    SUM(d.subtotal_linea) DESC;
$$;

COMMENT ON FUNCTION fn_rpt_ventas_por_categoria(DATE, DATE) IS
    'Reporte 1 filtrado por rango de fechas. Alimenta los campos Desde y Hasta de admin.html';


CREATE OR REPLACE VIEW rpt_top_clientes AS
WITH compras_cliente AS (
    SELECT
        cl.id_cliente,
        cl.nombres || ' ' || cl.apellidos   AS cliente,
        u.email,
        ci.nombre                           AS ciudad,
        pr.nombre                           AS provincia,
        COUNT(DISTINCT ped.id_pedido)       AS pedidos,
        SUM(d.cantidad)                     AS unidades,
        SUM(d.subtotal_linea)::NUMERIC(12,2) AS total_comprado,
        MAX(ped.fecha_pedido)               AS ultima_compra,
        MIN(ped.fecha_pedido)               AS primera_compra
    FROM        cliente        cl
    JOIN        usuario        u   ON u.id_usuario  = cl.id_cliente
    LEFT JOIN   ciudad         ci  ON ci.id_ciudad  = cl.id_ciudad
    LEFT JOIN   provincia      pr  ON pr.id_provincia = ci.id_provincia
    JOIN        pedido         ped ON ped.id_cliente = cl.id_cliente
    JOIN        estado_pedido  e   ON e.id_estado    = ped.id_estado
    JOIN        detalle_pedido d   ON d.id_pedido    = ped.id_pedido
    WHERE       e.nombre <> 'Cancelado'
      AND       u.activo = TRUE
    GROUP BY    cl.id_cliente, cliente, u.email, ci.nombre, pr.nombre
)

SELECT
    cliente,
    email,
    COALESCE(ciudad, 'Sin registrar')     AS ciudad,
    COALESCE(provincia, 'Sin registrar')  AS provincia,
    pedidos,
    unidades,
    total_comprado,
    ROUND(total_comprado / pedidos, 2)    AS ticket_promedio,
    ultima_compra::DATE                   AS ultima_compra,
    EXTRACT(DAY FROM AGE(CURRENT_DATE, ultima_compra))::INT AS dias_sin_comprar,
    DENSE_RANK() OVER (ORDER BY total_comprado DESC)        AS ranking,
    CASE
        WHEN pedidos >= 5 THEN 'Frecuente'
        WHEN pedidos >= 2 THEN 'Recurrente'
        ELSE 'Nuevo'
    END                                   AS segmento
FROM     compras_cliente
ORDER BY total_comprado DESC;

COMMENT ON VIEW rpt_top_clientes IS
    'Reporte 2: ranking de clientes por monto comprado. CTE + DENSE_RANK + segmentacion';



CREATE OR REPLACE VIEW rpt_stock_critico AS
SELECT
    p.codigo,
    p.nombre                        AS producto,
    c.nombre                        AS categoria,
    t.codigo                        AS talla,
    pt.stock                        AS stock_actual,
    pt.stock_minimo,
    (pt.stock_minimo - pt.stock)    AS unidades_faltantes,
    p.precio,

    (SELECT COALESCE(SUM(d.cantidad), 0)
     FROM   detalle_pedido d
     JOIN   pedido        ped ON ped.id_pedido = d.id_pedido
     JOIN   estado_pedido e   ON e.id_estado   = ped.id_estado
     WHERE  d.id_producto_talla = pt.id_producto_talla
       AND  ped.fecha_pedido >= CURRENT_DATE - INTERVAL '30 days'
       AND  e.nombre <> 'Cancelado')  AS demanda_30_dias,

    CASE
        WHEN (SELECT COALESCE(SUM(d.cantidad), 0)
              FROM   detalle_pedido d
              JOIN   pedido ped ON ped.id_pedido = d.id_pedido
              JOIN   estado_pedido e ON e.id_estado = ped.id_estado
              WHERE  d.id_producto_talla = pt.id_producto_talla
                AND  ped.fecha_pedido >= CURRENT_DATE - INTERVAL '30 days'
                AND  e.nombre <> 'Cancelado') = 0
        THEN NULL
        ELSE ROUND(pt.stock / ((SELECT SUM(d.cantidad)::NUMERIC
                                FROM   detalle_pedido d
                                JOIN   pedido ped ON ped.id_pedido = d.id_pedido
                                JOIN   estado_pedido e ON e.id_estado = ped.id_estado
                                WHERE  d.id_producto_talla = pt.id_producto_talla
                                  AND  ped.fecha_pedido >= CURRENT_DATE - INTERVAL '30 days'
                                  AND  e.nombre <> 'Cancelado') / 30.0), 1)
    END                             AS dias_de_cobertura,

    CASE
        WHEN pt.stock = 0                   THEN 'AGOTADO'
        WHEN pt.stock < pt.stock_minimo     THEN 'CRITICO'
        ELSE 'EN EL LIMITE'
    END                             AS nivel_alerta

FROM        producto_talla  pt
JOIN        producto        p ON p.id_producto  = pt.id_producto
JOIN        categoria       c ON c.id_categoria = p.id_categoria
JOIN        talla           t ON t.id_talla     = pt.id_talla
WHERE       p.activo = TRUE
  AND       pt.stock <= pt.stock_minimo
ORDER BY    pt.stock ASC, p.nombre;

COMMENT ON VIEW rpt_stock_critico IS
    'Reporte 3: inventario bajo el minimo cruzado con la demanda de 30 dias. Subconsulta correlacionada';



CREATE OR REPLACE VIEW rpt_mensajes_contacto AS
SELECT
    a.nombre                                          AS asunto,
    COALESCE(ci.nombre, 'Sin registrar')              AS ciudad,
    COALESCE(pr.nombre, 'Sin registrar')              AS provincia,

    COUNT(*)                                          AS total_mensajes,
    COUNT(*) FILTER (WHERE m.leido)                   AS leidos,
    COUNT(*) FILTER (WHERE NOT m.leido)               AS pendientes,
    COUNT(*) FILTER (WHERE m.fecha_respuesta IS NOT NULL) AS respondidos,
    COUNT(*) FILTER (WHERE m.id_cliente IS NOT NULL)  AS de_clientes,
    COUNT(*) FILTER (WHERE m.id_cliente IS NULL)      AS de_visitantes,

    ROUND(100.0 * COUNT(*) FILTER (WHERE m.fecha_respuesta IS NOT NULL)
          / COUNT(*), 1)                              AS porcentaje_respuesta,

    ROUND(AVG(EXTRACT(EPOCH FROM (m.fecha_respuesta - m.fecha_envio)) / 3600.0)
          FILTER (WHERE m.fecha_respuesta IS NOT NULL)::NUMERIC, 1)
                                                      AS horas_promedio_respuesta,

    MIN(m.fecha_envio)::DATE                          AS primer_mensaje,
    MAX(m.fecha_envio)::DATE                          AS ultimo_mensaje

FROM        mensaje_contacto m
JOIN        asunto_contacto  a  ON a.id_asunto    = m.id_asunto
LEFT JOIN   ciudad           ci ON ci.id_ciudad   = m.id_ciudad
LEFT JOIN   provincia        pr ON pr.id_provincia = ci.id_provincia
GROUP BY    a.id_asunto, a.nombre, ci.nombre, pr.nombre
ORDER BY    total_mensajes DESC, asunto;

COMMENT ON VIEW rpt_mensajes_contacto IS
    'Reporte 4: mensajes por asunto y ciudad con tasa y tiempo de respuesta. Agregacion con FILTER';



CREATE OR REPLACE FUNCTION fn_rpt_mensajes_periodo(
    p_desde DATE DEFAULT NULL,
    p_hasta DATE DEFAULT NULL
)
RETURNS TABLE (
    asunto                   VARCHAR(30),
    total_mensajes           BIGINT,
    pendientes               BIGINT,
    respondidos              BIGINT,
    porcentaje_respuesta     NUMERIC,
    horas_promedio_respuesta NUMERIC
)
LANGUAGE sql
STABLE
AS $$
    SELECT
        a.nombre,
        COUNT(*),
        COUNT(*) FILTER (WHERE NOT m.leido),
        COUNT(*) FILTER (WHERE m.fecha_respuesta IS NOT NULL),
        ROUND(100.0 * COUNT(*) FILTER (WHERE m.fecha_respuesta IS NOT NULL) / COUNT(*), 1),
        ROUND(AVG(EXTRACT(EPOCH FROM (m.fecha_respuesta - m.fecha_envio)) / 3600.0)
              FILTER (WHERE m.fecha_respuesta IS NOT NULL)::NUMERIC, 1)
    FROM     mensaje_contacto m
    JOIN     asunto_contacto  a ON a.id_asunto = m.id_asunto
    WHERE    (p_desde IS NULL OR m.fecha_envio >= p_desde)
      AND    (p_hasta IS NULL OR m.fecha_envio < (p_hasta + INTERVAL '1 day'))
    GROUP BY a.id_asunto, a.nombre
    ORDER BY COUNT(*) DESC;
$$;

COMMENT ON FUNCTION fn_rpt_mensajes_periodo(DATE, DATE) IS
    'Reporte 4 filtrado por rango de fechas';



CREATE OR REPLACE VIEW v_usuario_seguro AS
SELECT
    u.id_usuario,
    u.email,
    u.rol,
    u.activo,
    u.fecha_registro,
    u.ultimo_acceso,
    COALESCE(c.nombres,   a.nombres)   AS nombres,
    COALESCE(c.apellidos, a.apellidos) AS apellidos,
    c.cedula,
    c.telefono,
    ci.nombre                          AS ciudad,
    pr.nombre                          AS provincia,
    a.cargo,
    a.nivel_acceso
FROM        usuario       u
LEFT JOIN   cliente       c  ON c.id_cliente       = u.id_usuario
LEFT JOIN   administrador a  ON a.id_administrador = u.id_usuario
LEFT JOIN   ciudad        ci ON ci.id_ciudad       = c.id_ciudad
LEFT JOIN   provincia     pr ON pr.id_provincia    = ci.id_provincia;

COMMENT ON VIEW v_usuario_seguro IS
    'Datos de usuario SIN password_hash. Es la unica via de lectura para la aplicacion';


CREATE OR REPLACE VIEW v_catalogo_publico AS
SELECT
    p.id_producto,
    p.codigo,
    p.nombre,
    p.descripcion,
    c.nombre                                  AS categoria,
    c.slug                                    AS categoria_slug,
    p.precio,
    p.precio_oferta,
    COALESCE(p.precio_oferta, p.precio)       AS precio_final,
    CASE WHEN p.precio_oferta IS NOT NULL
         THEN ROUND(100.0 * (p.precio - p.precio_oferta) / p.precio, 0)
         ELSE 0
    END                                       AS descuento_porcentaje,
    p.imagen_principal,
    p.material,
    p.genero,
    p.destacado,
    t.codigo                                  AS talla,
    pt.id_producto_talla,
    pt.stock,
    (pt.stock > 0)                            AS disponible,
    img.alt_text
FROM        producto        p
JOIN        categoria       c   ON c.id_categoria = p.id_categoria
JOIN        producto_talla  pt  ON pt.id_producto = p.id_producto
JOIN        talla           t   ON t.id_talla     = pt.id_talla
LEFT JOIN   imagen_producto img ON img.id_producto = p.id_producto AND img.orden = 1
WHERE       p.activo = TRUE
  AND       c.activa = TRUE
ORDER BY    c.nombre, p.codigo;

COMMENT ON VIEW v_catalogo_publico IS
    'Catalogo que consume el frontend. Centraliza la regla de que producto es visible';


SELECT table_name AS vista
FROM   information_schema.views
WHERE  table_schema = 'public'
ORDER  BY table_name;
