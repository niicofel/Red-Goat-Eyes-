-- ============================================================
-- 04 · PROCEDIMIENTOS ALMACENADOS
-- Operaciones que tocan varias tablas y deben hacerse completas
-- o no hacerse. Si algo falla a la mitad, se deshace todo.
-- ============================================================
CREATE SEQUENCE IF NOT EXISTS seq_codigo_pedido
    START WITH 1
    INCREMENT BY 1
    MINVALUE 1
    MAXVALUE 9999
    NO CYCLE;

COMMENT ON SEQUENCE seq_codigo_pedido IS 'Numerador de codigos de pedido. Evita colisiones por concurrencia';

SELECT setval(
    'seq_codigo_pedido',
    COALESCE((SELECT MAX(SUBSTRING(codigo_pedido FROM 10 FOR 4)::INT) FROM pedido), 0),
    TRUE
);




-- ---------------- Registrar un pedido ----------------
-- Crea el pedido y todas sus lineas de una sola vez
CREATE OR REPLACE PROCEDURE sp_registrar_pedido(
    IN    p_id_cliente      INT,
    IN    p_id_direccion    INT,
    IN    p_id_metodo_pago  INT,
    IN    p_items           JSONB,
    IN    p_observaciones   TEXT DEFAULT NULL,
    INOUT p_codigo_pedido   VARCHAR(20) DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_pedido         INT;
    v_id_estado         INT;
    v_item              JSONB;
    v_id_producto_talla INT;
    v_cantidad          INT;
    v_precio            NUMERIC(10,2);
    v_nombre_producto   VARCHAR(120);
    v_lineas            INT := 0;
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM   cliente c
        JOIN   usuario u ON u.id_usuario = c.id_cliente
        WHERE  c.id_cliente = p_id_cliente AND u.activo = TRUE
    ) THEN
        RAISE EXCEPTION 'El cliente % no existe o su cuenta esta desactivada', p_id_cliente
            USING ERRCODE = 'foreign_key_violation';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM direccion_envio
        WHERE  id_direccion = p_id_direccion AND id_cliente = p_id_cliente
    ) THEN
        RAISE EXCEPTION 'La direccion % no pertenece al cliente %', p_id_direccion, p_id_cliente
            USING ERRCODE = 'check_violation';
    END IF;

    IF p_items IS NULL OR jsonb_typeof(p_items) <> 'array' OR jsonb_array_length(p_items) = 0 THEN
        RAISE EXCEPTION 'El pedido no contiene productos'
            USING ERRCODE = 'check_violation';
    END IF;

    IF p_id_metodo_pago IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM metodo_pago
        WHERE  id_metodo = p_id_metodo_pago AND activo = TRUE
    ) THEN
        RAISE EXCEPTION 'El metodo de pago % no esta disponible', p_id_metodo_pago
            USING ERRCODE = 'check_violation';
    END IF;

    p_codigo_pedido := 'RGE-'
                    || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT
                    || '-'
                    || LPAD(nextval('seq_codigo_pedido')::TEXT, 4, '0');

    SELECT id_estado INTO v_id_estado
    FROM   estado_pedido WHERE nombre = 'Pendiente';

    INSERT INTO pedido (codigo_pedido, id_cliente, id_direccion, id_estado,
                        id_metodo_pago, observaciones)
    VALUES (p_codigo_pedido, p_id_cliente, p_id_direccion, v_id_estado,
            p_id_metodo_pago, p_observaciones)
    RETURNING id_pedido INTO v_id_pedido;

    FOR v_item IN SELECT * FROM jsonb_array_elements(p_items)
    LOOP
        v_id_producto_talla := (v_item ->> 'id_producto_talla')::INT;
        v_cantidad          := (v_item ->> 'cantidad')::INT;

        IF v_id_producto_talla IS NULL OR v_cantidad IS NULL THEN
            RAISE EXCEPTION 'Cada item debe traer id_producto_talla y cantidad. Recibido: %', v_item
                USING ERRCODE = 'check_violation';
        END IF;

        IF v_cantidad <= 0 THEN
            RAISE EXCEPTION 'La cantidad debe ser mayor que cero. Recibido: %', v_cantidad
                USING ERRCODE = 'check_violation';
        END IF;

        SELECT COALESCE(p.precio_oferta, p.precio), p.nombre
        INTO   v_precio, v_nombre_producto
        FROM   producto_talla pt
        JOIN   producto p ON p.id_producto = pt.id_producto
        WHERE  pt.id_producto_talla = v_id_producto_talla
          AND  p.activo = TRUE;

        IF NOT FOUND THEN
            RAISE EXCEPTION 'El producto % no existe o no esta disponible', v_id_producto_talla
                USING ERRCODE = 'foreign_key_violation';
        END IF;

        INSERT INTO detalle_pedido (id_pedido, id_producto_talla, cantidad, precio_unitario)
        VALUES (v_id_pedido, v_id_producto_talla, v_cantidad, v_precio);

        v_lineas := v_lineas + 1;
    END LOOP;

    RAISE NOTICE 'Pedido % registrado con % lineas', p_codigo_pedido, v_lineas;
END;
$$;

COMMENT ON PROCEDURE sp_registrar_pedido IS 'Registra un pedido completo de forma atomica. El precio se lee de la base, nunca del cliente';




-- ---------------- Registrar un cliente ----------------
-- Crea usuario y cliente juntos: si falla uno, no se crea ninguno
CREATE OR REPLACE PROCEDURE sp_registrar_cliente(
    IN    p_email             VARCHAR(120),
    IN    p_password_hash     VARCHAR(255),
    IN    p_nombres           VARCHAR(60),
    IN    p_apellidos         VARCHAR(60),
    IN    p_cedula            VARCHAR(10),
    IN    p_telefono          VARCHAR(15),
    IN    p_id_ciudad         INT,
    IN    p_fecha_nacimiento  DATE DEFAULT NULL,
    INOUT p_id_cliente        INT  DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_usuario INT;
BEGIN
    IF EXISTS (SELECT 1 FROM usuario WHERE LOWER(email) = LOWER(TRIM(p_email))) THEN
        RAISE EXCEPTION 'Ya existe una cuenta registrada con el correo %', p_email
            USING ERRCODE = 'unique_violation';
    END IF;

    IF p_cedula IS NOT NULL AND EXISTS (SELECT 1 FROM cliente WHERE cedula = p_cedula) THEN
        RAISE EXCEPTION 'Ya existe un cliente registrado con la cedula %', p_cedula
            USING ERRCODE = 'unique_violation';
    END IF;

    IF p_id_ciudad IS NOT NULL AND NOT EXISTS (SELECT 1 FROM ciudad WHERE id_ciudad = p_id_ciudad) THEN
        RAISE EXCEPTION 'La ciudad % no existe en el catalogo', p_id_ciudad
            USING ERRCODE = 'foreign_key_violation';
    END IF;

    INSERT INTO usuario (email, password_hash, rol, activo)
    VALUES (LOWER(TRIM(p_email)), p_password_hash, 'cliente', TRUE)
    RETURNING id_usuario INTO v_id_usuario;

    INSERT INTO cliente (id_cliente, nombres, apellidos, cedula,
                         telefono, fecha_nacimiento, id_ciudad)
    VALUES (v_id_usuario, TRIM(p_nombres), TRIM(p_apellidos), p_cedula,
            p_telefono, p_fecha_nacimiento, p_id_ciudad);

    INSERT INTO carrito (id_cliente) VALUES (v_id_usuario);

    p_id_cliente := v_id_usuario;

    RAISE NOTICE 'Cliente % registrado con id %', p_email, v_id_usuario;
END;
$$;

COMMENT ON PROCEDURE sp_registrar_cliente IS 'Crea usuario, cliente y carrito en una sola transaccion. Mantiene la relacion 1:1';




-- ---------------- Cambiar el estado de un pedido ----------------
-- Valida que la transicion sea permitida antes de cambiarlo
CREATE OR REPLACE PROCEDURE sp_cambiar_estado_pedido(
    IN p_codigo_pedido    VARCHAR(20),
    IN p_nuevo_estado     VARCHAR(20),
    IN p_id_administrador INT DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_pedido       INT;
    v_estado_actual   VARCHAR(20);
    v_id_nuevo_estado INT;
    v_permitidos      TEXT[];
BEGIN
    SELECT p.id_pedido, e.nombre
    INTO   v_id_pedido, v_estado_actual
    FROM   pedido p
    JOIN   estado_pedido e ON e.id_estado = p.id_estado
    WHERE  p.codigo_pedido = p_codigo_pedido;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'No existe el pedido %', p_codigo_pedido
            USING ERRCODE = 'no_data_found';
    END IF;

    SELECT id_estado INTO v_id_nuevo_estado
    FROM   estado_pedido WHERE nombre = p_nuevo_estado;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'El estado "%" no existe en el catalogo', p_nuevo_estado
            USING ERRCODE = 'foreign_key_violation';
    END IF;

    IF v_estado_actual = p_nuevo_estado THEN
        RAISE NOTICE 'El pedido % ya se encuentra en estado %', p_codigo_pedido, p_nuevo_estado;
        RETURN;
    END IF;

    IF p_id_administrador IS NOT NULL AND NOT EXISTS (
        SELECT 1 FROM administrador WHERE id_administrador = p_id_administrador
    ) THEN
        RAISE EXCEPTION 'El administrador % no existe', p_id_administrador
            USING ERRCODE = 'foreign_key_violation';
    END IF;

    v_permitidos := CASE v_estado_actual
        WHEN 'Pendiente'      THEN ARRAY['Pagado', 'Cancelado']
        WHEN 'Pagado'         THEN ARRAY['En preparacion', 'Cancelado']
        WHEN 'En preparacion' THEN ARRAY['Enviado', 'Cancelado']
        WHEN 'Enviado'        THEN ARRAY['Entregado']
        ELSE ARRAY[]::TEXT[]
    END;

    IF array_length(v_permitidos, 1) IS NULL THEN
        RAISE EXCEPTION 'El pedido % esta en estado "%", que es final y no admite cambios',
            p_codigo_pedido, v_estado_actual
            USING ERRCODE = 'check_violation';
    END IF;

    IF NOT (p_nuevo_estado = ANY(v_permitidos)) THEN
        RAISE EXCEPTION 'Transicion no permitida: de "%" solo se puede pasar a %',
            v_estado_actual, array_to_string(v_permitidos, ' o ')
            USING ERRCODE = 'check_violation';
    END IF;

    UPDATE pedido
    SET    id_estado = v_id_nuevo_estado
    WHERE  id_pedido = v_id_pedido;

    INSERT INTO auditoria (tabla_afectada, operacion, id_registro,
                           datos_anteriores, datos_nuevos)
    VALUES ('pedido', 'UPDATE', v_id_pedido,
            jsonb_build_object('codigo_pedido', p_codigo_pedido,
                               'estado',        v_estado_actual),
            jsonb_build_object('codigo_pedido',    p_codigo_pedido,
                               'estado',           p_nuevo_estado,
                               'id_administrador', p_id_administrador));

    RAISE NOTICE 'Pedido %: % -> %', p_codigo_pedido, v_estado_actual, p_nuevo_estado;
END;
$$;

COMMENT ON PROCEDURE sp_cambiar_estado_pedido IS 'Cambia el estado de un pedido validando que la transicion sea legal';




-- ---------------- Reponer stock ----------------
-- Vuelve a comprobar el nivel del administrador dentro de PostgreSQL
CREATE OR REPLACE PROCEDURE sp_reponer_stock(
    IN p_codigo_producto  VARCHAR(20),
    IN p_codigo_talla     VARCHAR(5),
    IN p_cantidad         INT,
    IN p_id_administrador INT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_producto_talla INT;
    v_stock_anterior    INT;
    v_stock_nuevo       INT;
    v_nombre_producto   VARCHAR(120);
    v_nivel_acceso      SMALLINT;
BEGIN
    IF p_cantidad IS NULL OR p_cantidad <= 0 THEN
        RAISE EXCEPTION 'La cantidad a reponer debe ser mayor que cero. Recibido: %', p_cantidad
            USING ERRCODE = 'check_violation';
    END IF;

    SELECT nivel_acceso INTO v_nivel_acceso
    FROM   administrador WHERE id_administrador = p_id_administrador;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'El administrador % no existe', p_id_administrador
            USING ERRCODE = 'foreign_key_violation';
    END IF;

    IF v_nivel_acceso < 2 THEN
        RAISE EXCEPTION 'El administrador % no tiene nivel suficiente para reponer stock (nivel actual: %)',
            p_id_administrador, v_nivel_acceso
            USING ERRCODE = 'insufficient_privilege';
    END IF;

    SELECT pt.id_producto_talla, pt.stock, p.nombre
    INTO   v_id_producto_talla, v_stock_anterior, v_nombre_producto
    FROM   producto_talla pt
    JOIN   producto p ON p.id_producto = pt.id_producto
    JOIN   talla    t ON t.id_talla    = pt.id_talla
    WHERE  p.codigo = p_codigo_producto
      AND  t.codigo = p_codigo_talla;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'No existe el producto % en talla %', p_codigo_producto, p_codigo_talla
            USING ERRCODE = 'no_data_found';
    END IF;

    UPDATE producto_talla
    SET    stock = stock + p_cantidad
    WHERE  id_producto_talla = v_id_producto_talla
    RETURNING stock INTO v_stock_nuevo;

    INSERT INTO auditoria (tabla_afectada, operacion, id_registro,
                           datos_anteriores, datos_nuevos)
    VALUES ('producto_talla', 'UPDATE', v_id_producto_talla,
            jsonb_build_object('codigo',   p_codigo_producto,
                               'talla',    p_codigo_talla,
                               'stock',    v_stock_anterior),
            jsonb_build_object('codigo',           p_codigo_producto,
                               'talla',            p_codigo_talla,
                               'stock',            v_stock_nuevo,
                               'repuesto',         p_cantidad,
                               'id_administrador', p_id_administrador));

    RAISE NOTICE 'Stock de "%" (talla %): % -> % (+%)',
        v_nombre_producto, p_codigo_talla, v_stock_anterior, v_stock_nuevo, p_cantidad;
END;
$$;

COMMENT ON PROCEDURE sp_reponer_stock IS 'Repone inventario validando el nivel de acceso del administrador y auditando la operacion';


SELECT p.proname AS procedimiento,
       pg_get_function_identity_arguments(p.oid) AS parametros
FROM   pg_proc p
JOIN   pg_namespace n ON n.oid = p.pronamespace
WHERE  n.nspname = 'public'
  AND  p.prokind = 'p'
ORDER  BY p.proname;


SELECT last_value AS ultimo_numero_usado,
       'RGE-' || EXTRACT(YEAR FROM CURRENT_DATE)::TEXT || '-'
              || LPAD((last_value + 1)::TEXT, 4, '0') AS proximo_codigo
FROM   seq_codigo_pedido;
