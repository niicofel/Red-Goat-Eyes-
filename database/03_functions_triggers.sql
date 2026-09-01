-- ============================================================
-- 03 · FUNCIONES Y TRIGGERS
-- Un trigger es codigo que PostgreSQL ejecuta solo cuando pasa
-- algo en una tabla. Nadie los llama: saltan automaticamente.
-- Aqui estan las reglas que deben cumplirse siempre, aunque el
-- cambio no venga desde la aplicacion.
-- ============================================================
-- ---------------- Funciones de ayuda ----------------
-- El IVA se define en un solo lugar: 15%
CREATE OR REPLACE FUNCTION fn_tasa_iva()
RETURNS NUMERIC(4,4)
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT 0.1500::NUMERIC(4,4);
$$;

COMMENT ON FUNCTION fn_tasa_iva() IS 'Tasa de IVA vigente en Ecuador (15%). Unica fuente de verdad';


CREATE OR REPLACE FUNCTION fn_verificar_stock(
    p_id_producto_talla INT,
    p_cantidad          INT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_stock INT;
BEGIN
    SELECT stock INTO v_stock
    FROM producto_talla
    WHERE id_producto_talla = p_id_producto_talla;

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    RETURN v_stock >= p_cantidad;
END;
$$;

COMMENT ON FUNCTION fn_verificar_stock(INT, INT) IS 'TRUE si hay unidades suficientes del producto y talla indicados';


CREATE OR REPLACE FUNCTION fn_calcular_total_pedido(p_id_pedido INT)
RETURNS NUMERIC(10,2)
LANGUAGE sql
STABLE
AS $$
    SELECT COALESCE(SUM(subtotal_linea), 0)::NUMERIC(10,2)
    FROM detalle_pedido
    WHERE id_pedido = p_id_pedido;
$$;

COMMENT ON FUNCTION fn_calcular_total_pedido(INT) IS 'Suma de las lineas de un pedido';




-- ---------------- Trigger: validar stock ----------------
-- Rechaza la linea del pedido si no hay unidades suficientes
CREATE OR REPLACE FUNCTION fn_trg_validar_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_necesario INT;
    v_stock     INT;
    v_producto  VARCHAR(120);
BEGIN
    IF TG_OP = 'INSERT' THEN
        v_necesario := NEW.cantidad;
    ELSE
        v_necesario := NEW.cantidad - OLD.cantidad;
    END IF;

    IF v_necesario <= 0 THEN
        RETURN NEW;
    END IF;

    SELECT pt.stock, p.nombre
    INTO   v_stock, v_producto
    FROM   producto_talla pt
    JOIN   producto p ON p.id_producto = pt.id_producto
    WHERE  pt.id_producto_talla = NEW.id_producto_talla;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'El producto solicitado no existe en el inventario (id_producto_talla = %)',
            NEW.id_producto_talla
            USING ERRCODE = 'foreign_key_violation';
    END IF;

    IF v_stock < v_necesario THEN
        RAISE EXCEPTION 'Stock insuficiente para "%": se solicitan % unidades y solo hay % disponibles',
            v_producto, v_necesario, v_stock
            USING ERRCODE = 'check_violation';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_validar_stock ON detalle_pedido;

CREATE TRIGGER trg_validar_stock
    BEFORE INSERT OR UPDATE OF cantidad ON detalle_pedido
    FOR EACH ROW
    EXECUTE FUNCTION fn_trg_validar_stock();



-- ---------------- Trigger: ajustar stock ----------------
-- Descuenta al comprar y devuelve al borrar. Por eso el stock se recupera solo
CREATE OR REPLACE FUNCTION fn_trg_ajustar_stock()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE producto_talla
        SET    stock = stock - NEW.cantidad
        WHERE  id_producto_talla = NEW.id_producto_talla;

    ELSIF TG_OP = 'UPDATE' THEN
        IF NEW.id_producto_talla <> OLD.id_producto_talla THEN
            UPDATE producto_talla
            SET    stock = stock + OLD.cantidad
            WHERE  id_producto_talla = OLD.id_producto_talla;

            UPDATE producto_talla
            SET    stock = stock - NEW.cantidad
            WHERE  id_producto_talla = NEW.id_producto_talla;
        ELSE
            UPDATE producto_talla
            SET    stock = stock - (NEW.cantidad - OLD.cantidad)
            WHERE  id_producto_talla = NEW.id_producto_talla;
        END IF;

    ELSIF TG_OP = 'DELETE' THEN
        UPDATE producto_talla
        SET    stock = stock + OLD.cantidad
        WHERE  id_producto_talla = OLD.id_producto_talla;

        RETURN OLD;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_ajustar_stock ON detalle_pedido;

CREATE TRIGGER trg_ajustar_stock
    AFTER INSERT OR UPDATE OR DELETE ON detalle_pedido
    FOR EACH ROW
    EXECUTE FUNCTION fn_trg_ajustar_stock();



-- ---------------- Trigger: recalcular totales ----------------
CREATE OR REPLACE FUNCTION fn_trg_recalcular_pedido()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_pedido INT;
    v_subtotal  NUMERIC(10,2);
    v_iva       NUMERIC(10,2);
BEGIN
    IF TG_OP = 'DELETE' THEN
        v_id_pedido := OLD.id_pedido;
    ELSE
        v_id_pedido := NEW.id_pedido;
    END IF;

    v_subtotal := fn_calcular_total_pedido(v_id_pedido);
    v_iva      := ROUND(v_subtotal * fn_tasa_iva(), 2);

    UPDATE pedido
    SET    subtotal = v_subtotal,
           iva      = v_iva,
           total    = v_subtotal + v_iva + costo_envio
    WHERE  id_pedido = v_id_pedido;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_recalcular_pedido ON detalle_pedido;

CREATE TRIGGER trg_recalcular_pedido
    AFTER INSERT OR UPDATE OR DELETE ON detalle_pedido
    FOR EACH ROW
    EXECUTE FUNCTION fn_trg_recalcular_pedido();




-- ---------------- Trigger: devolver stock al cancelar ----------------
CREATE OR REPLACE FUNCTION fn_trg_devolver_stock_cancelacion()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_cancelado INT;
BEGIN
    SELECT id_estado INTO v_id_cancelado
    FROM estado_pedido
    WHERE nombre = 'Cancelado';

    IF NEW.id_estado = v_id_cancelado AND OLD.id_estado <> v_id_cancelado THEN

        UPDATE producto_talla pt
        SET    stock = pt.stock + d.cantidad
        FROM   detalle_pedido d
        WHERE  d.id_pedido = NEW.id_pedido
          AND  pt.id_producto_talla = d.id_producto_talla;

        RAISE NOTICE 'Pedido % cancelado: stock devuelto al inventario', NEW.codigo_pedido;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_devolver_stock_cancelacion ON pedido;

CREATE TRIGGER trg_devolver_stock_cancelacion
    AFTER UPDATE OF id_estado ON pedido
    FOR EACH ROW
    WHEN (OLD.id_estado IS DISTINCT FROM NEW.id_estado)
    EXECUTE FUNCTION fn_trg_devolver_stock_cancelacion();



-- ---------------- Trigger: auditar cambios ----------------
CREATE OR REPLACE FUNCTION fn_trg_auditar_producto()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        IF to_jsonb(OLD) IS DISTINCT FROM to_jsonb(NEW) THEN
            INSERT INTO auditoria (tabla_afectada, operacion, id_registro,
                                   datos_anteriores, datos_nuevos)
            VALUES ('producto', 'UPDATE', OLD.id_producto,
                    to_jsonb(OLD), to_jsonb(NEW));
        END IF;
        RETURN NEW;

    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO auditoria (tabla_afectada, operacion, id_registro,
                               datos_anteriores, datos_nuevos)
        VALUES ('producto', 'DELETE', OLD.id_producto,
                to_jsonb(OLD), NULL);
        RETURN OLD;
    END IF;

    RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS trg_auditar_producto ON producto;

CREATE TRIGGER trg_auditar_producto
    AFTER UPDATE OR DELETE ON producto
    FOR EACH ROW
    EXECUTE FUNCTION fn_trg_auditar_producto();




-- ---------------- Trigger: encolar el recibo ----------------
-- PostgreSQL no puede mandar correos, asi que solo deja el aviso en la cola
CREATE OR REPLACE FUNCTION fn_trg_encolar_correo()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_pagado INT;
    v_email     VARCHAR(120);
BEGIN
    SELECT id_estado INTO v_id_pagado
    FROM estado_pedido
    WHERE nombre = 'Pagado';

    IF NEW.id_estado = v_id_pagado AND OLD.id_estado <> v_id_pagado THEN

        SELECT u.email INTO v_email
        FROM cliente c
        JOIN usuario u ON u.id_usuario = c.id_cliente
        WHERE c.id_cliente = NEW.id_cliente;

        IF v_email IS NULL THEN
            RAISE WARNING 'El pedido % no tiene correo de cliente: no se pudo encolar el recibo',
                NEW.codigo_pedido;
            RETURN NEW;
        END IF;

        INSERT INTO envio_correo (id_pedido, destinatario, asunto, estado)
        VALUES (NEW.id_pedido,
                v_email,
                'Recibo de tu pedido ' || NEW.codigo_pedido || ' | Red Goat Eyes',
                'pendiente');

        RAISE NOTICE 'Recibo del pedido % encolado para %', NEW.codigo_pedido, v_email;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_encolar_correo ON pedido;

CREATE TRIGGER trg_encolar_correo
    AFTER UPDATE OF id_estado ON pedido
    FOR EACH ROW
    WHEN (OLD.id_estado IS DISTINCT FROM NEW.id_estado)
    EXECUTE FUNCTION fn_trg_encolar_correo();




-- ---------------- Trigger: fecha del carrito ----------------
CREATE OR REPLACE FUNCTION fn_trg_actualizar_carrito()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_id_carrito INT;
BEGIN
    IF TG_OP = 'DELETE' THEN
        v_id_carrito := OLD.id_carrito;
    ELSE
        v_id_carrito := NEW.id_carrito;
    END IF;

    UPDATE carrito
    SET    fecha_actualizacion = CURRENT_TIMESTAMP
    WHERE  id_carrito = v_id_carrito;

    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_actualizar_carrito ON carrito_item;

CREATE TRIGGER trg_actualizar_carrito
    AFTER INSERT OR UPDATE OR DELETE ON carrito_item
    FOR EACH ROW
    EXECUTE FUNCTION fn_trg_actualizar_carrito();



DO $$
DECLARE
    v_triggers  INT;
    v_funciones INT;
BEGIN
    SELECT COUNT(DISTINCT trigger_name) INTO v_triggers
    FROM   information_schema.triggers
    WHERE  trigger_schema = 'public';

    SELECT COUNT(*) INTO v_funciones
    FROM   pg_proc p
    JOIN   pg_namespace n ON n.oid = p.pronamespace
    WHERE  n.nspname = 'public'
      AND  p.proname IN ('fn_tasa_iva', 'fn_verificar_stock', 'fn_calcular_total_pedido',
                         'fn_trg_validar_stock', 'fn_trg_ajustar_stock',
                         'fn_trg_recalcular_pedido', 'fn_trg_devolver_stock_cancelacion',
                         'fn_trg_auditar_producto', 'fn_trg_encolar_correo',
                         'fn_trg_actualizar_carrito');

    IF v_triggers < 7 THEN
        RAISE EXCEPTION 'Solo se crearon % triggers de los 7 esperados', v_triggers;
    END IF;

    IF v_funciones < 10 THEN
        RAISE EXCEPTION 'Solo se crearon % funciones de las 10 esperadas', v_funciones;
    END IF;

    RAISE NOTICE 'OK: % triggers y % funciones creados correctamente', v_triggers, v_funciones;
END $$;


SELECT trigger_name       AS trigger,
       event_object_table AS tabla,
       string_agg(event_manipulation, ', ' ORDER BY event_manipulation) AS eventos,
       action_timing      AS momento
FROM   information_schema.triggers
WHERE  trigger_schema = 'public'
GROUP  BY trigger_name, event_object_table, action_timing
ORDER  BY event_object_table, trigger_name;
