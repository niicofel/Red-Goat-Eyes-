-- ============================================================
-- 99 · BORRAR TODO
-- Elimina toda la estructura para reinstalar desde cero.
-- OJO: esto borra los datos. Solo usar en desarrollo.
-- ============================================================
DO $$
BEGIN
    IF current_setting('rge.confirmo_borrado', TRUE) IS DISTINCT FROM 'SI_BORRAR_TODO' THEN
        RAISE EXCEPTION E'\n\n'
            '  BORRADO CANCELADO POR SEGURIDAD\n\n'
            '  Este script elimina TODOS los datos del proyecto.\n\n'
            '  Si de verdad quieres continuar, ejecuta primero esta linea\n'
            '  sola, y despues el resto del archivo en la MISMA pestana:\n\n'
            '      SET rge.confirmo_borrado = ''SI_BORRAR_TODO'';\n';
    END IF;

    RAISE NOTICE 'Confirmacion recibida. Eliminando objetos del proyecto...';
END $$;



DROP TRIGGER IF EXISTS trg_validar_stock              ON detalle_pedido;
DROP TRIGGER IF EXISTS trg_ajustar_stock              ON detalle_pedido;
DROP TRIGGER IF EXISTS trg_recalcular_pedido          ON detalle_pedido;
DROP TRIGGER IF EXISTS trg_devolver_stock_cancelacion ON pedido;
DROP TRIGGER IF EXISTS trg_encolar_correo             ON pedido;
DROP TRIGGER IF EXISTS trg_auditar_producto           ON producto;
DROP TRIGGER IF EXISTS trg_actualizar_carrito         ON carrito_item;


DROP VIEW IF EXISTS rpt_ventas_por_categoria CASCADE;
DROP VIEW IF EXISTS rpt_top_clientes         CASCADE;
DROP VIEW IF EXISTS rpt_stock_critico        CASCADE;
DROP VIEW IF EXISTS rpt_mensajes_contacto    CASCADE;
DROP VIEW IF EXISTS v_usuario_seguro         CASCADE;
DROP VIEW IF EXISTS v_catalogo_publico       CASCADE;


DO $$
DECLARE
    r        RECORD;
    v_total  INT := 0;
BEGIN
    FOR r IN
        SELECT p.oid::regprocedure AS firma,
               p.prokind
        FROM   pg_proc p
        JOIN   pg_namespace n ON n.oid = p.pronamespace
        WHERE  n.nspname = 'public'
          AND  (p.proname LIKE 'fn\_%' OR p.proname LIKE 'sp\_%')
    LOOP
        EXECUTE format('DROP %s IF EXISTS %s CASCADE',
                       CASE WHEN r.prokind = 'p' THEN 'PROCEDURE' ELSE 'FUNCTION' END,
                       r.firma);
        v_total := v_total + 1;
    END LOOP;

    RAISE NOTICE 'Eliminadas % rutinas (funciones y procedimientos)', v_total;
END $$;


DROP SEQUENCE IF EXISTS seq_codigo_pedido CASCADE;


DROP TABLE IF EXISTS
    envio_correo,
    auditoria,
    mensaje_contacto,
    asunto_contacto,
    carrito_item,
    carrito,
    detalle_pedido,
    pedido,
    metodo_pago,
    estado_pedido,
    direccion_envio,
    administrador,
    cliente,
    usuario,
    imagen_producto,
    producto_talla,
    producto,
    talla,
    categoria,
    ciudad,
    provincia
CASCADE;


DO $$
DECLARE
    v_tablas   INT;
    v_vistas   INT;
    v_rutinas  INT;
BEGIN
    SELECT COUNT(*) INTO v_tablas
    FROM   information_schema.tables
    WHERE  table_schema = 'public' AND table_type = 'BASE TABLE';

    SELECT COUNT(*) INTO v_vistas
    FROM   information_schema.views
    WHERE  table_schema = 'public';

    SELECT COUNT(*) INTO v_rutinas
    FROM   pg_proc p
    JOIN   pg_namespace n ON n.oid = p.pronamespace
    WHERE  n.nspname = 'public'
      AND  (p.proname LIKE 'fn\_%' OR p.proname LIKE 'sp\_%');

    IF v_tablas = 0 AND v_vistas = 0 AND v_rutinas = 0 THEN
        RAISE NOTICE 'LIMPIEZA COMPLETA: el esquema public quedo vacio';
        RAISE NOTICE 'Para reinstalar: ejecutar 01, 02, 03, 04, 05 y 06 en orden';
        RAISE NOTICE 'O ejecutar directamente database\setup.bat';
    ELSE
        RAISE WARNING 'Quedaron objetos sin eliminar: % tablas, % vistas, % rutinas',
            v_tablas, v_vistas, v_rutinas;
    END IF;
END $$;


RESET rge.confirmo_borrado;
