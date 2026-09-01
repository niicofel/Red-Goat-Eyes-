-- ============================================================
-- 06 · ROLES Y PERMISOS
-- Crea 7 roles: 4 que agrupan permisos y 3 que se conectan.
-- La aplicacion nunca entra como superusuario.
-- Los roles se crean SIN contrasena: eso va en el 07, que no
-- se sube a Git.
-- ============================================================
DO $$
DECLARE
    v_faltantes TEXT := '';
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables
                   WHERE table_schema = 'public' AND table_name = 'producto') THEN
        v_faltantes := v_faltantes || E'\n  - 01_schema.sql (no existe la tabla producto)';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM producto) THEN
        v_faltantes := v_faltantes || E'\n  - 02_seed.sql (la tabla producto esta vacia)';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_proc p
                   JOIN pg_namespace n ON n.oid = p.pronamespace
                   WHERE n.nspname = 'public' AND p.proname = 'fn_verificar_stock') THEN
        v_faltantes := v_faltantes || E'\n  - 03_functions_triggers.sql (no existe fn_verificar_stock)';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_proc p
                   JOIN pg_namespace n ON n.oid = p.pronamespace
                   WHERE n.nspname = 'public' AND p.proname = 'sp_registrar_pedido') THEN
        v_faltantes := v_faltantes || E'\n  - 04_procedures.sql (no existe sp_registrar_pedido)';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM information_schema.views
                   WHERE table_schema = 'public' AND table_name = 'v_usuario_seguro') THEN
        v_faltantes := v_faltantes || E'\n  - 05_views_reportes.sql (no existe v_usuario_seguro)';
    END IF;

    IF v_faltantes <> '' THEN
        RAISE EXCEPTION E'Faltan por ejecutar estos scripts antes del 06:%', v_faltantes;
    END IF;

    RAISE NOTICE 'Comprobacion superada: los scripts 01 a 05 estan aplicados';
END $$;


REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL TABLES    IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL ROUTINES  IN SCHEMA public FROM PUBLIC;

REVOKE CONNECT ON DATABASE red_goat_eyes FROM PUBLIC;



DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rge_app_read') THEN
        CREATE ROLE rge_app_read NOLOGIN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rge_app_write') THEN
        CREATE ROLE rge_app_write NOLOGIN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rge_admin') THEN
        CREATE ROLE rge_admin NOLOGIN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rge_backup') THEN
        CREATE ROLE rge_backup NOLOGIN;
    END IF;
END $$;

COMMENT ON ROLE rge_app_read  IS 'Solo lectura del catalogo publico. Sin acceso a datos personales';
COMMENT ON ROLE rge_app_write IS 'Rol de la aplicacion Flask. Escribe pedidos y clientes, nunca borra';
COMMENT ON ROLE rge_admin     IS 'Panel administrativo. Gestion de catalogo, pedidos y reportes';
COMMENT ON ROLE rge_backup    IS 'Lectura global exclusiva para pg_dump. No modifica nada';



DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rge_flask') THEN
        CREATE ROLE rge_flask LOGIN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rge_panel') THEN
        CREATE ROLE rge_panel LOGIN;
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rge_respaldo') THEN
        CREATE ROLE rge_respaldo LOGIN;
    END IF;
END $$;

GRANT rge_app_write TO rge_flask;
GRANT rge_app_read  TO rge_flask;
GRANT rge_admin     TO rge_panel;
GRANT rge_backup    TO rge_respaldo;

GRANT CONNECT ON DATABASE red_goat_eyes TO rge_flask, rge_panel, rge_respaldo;

GRANT USAGE ON SCHEMA public TO rge_app_read, rge_app_write, rge_admin, rge_backup;



GRANT SELECT ON
    categoria,
    producto,
    producto_talla,
    talla,
    imagen_producto,
    provincia,
    ciudad,
    v_catalogo_publico
TO rge_app_read;


GRANT SELECT ON
    categoria, producto, talla, imagen_producto,
    provincia, ciudad, estado_pedido, metodo_pago, asunto_contacto,
    v_catalogo_publico
TO rge_app_write;

GRANT SELECT, UPDATE ON producto_talla TO rge_app_write;



GRANT SELECT (id_usuario, email, password_hash, rol, activo, ultimo_acceso)
    ON usuario TO rge_app_write;

GRANT INSERT (email, password_hash, rol, activo)
    ON usuario TO rge_app_write;

GRANT UPDATE (ultimo_acceso, password_hash)
    ON usuario TO rge_app_write;

GRANT SELECT, INSERT, UPDATE ON cliente          TO rge_app_write;
GRANT SELECT, INSERT, UPDATE ON direccion_envio  TO rge_app_write;
GRANT SELECT                 ON v_usuario_seguro TO rge_app_write;

GRANT SELECT, INSERT, UPDATE, DELETE ON carrito      TO rge_app_write;
GRANT SELECT, INSERT, UPDATE, DELETE ON carrito_item TO rge_app_write;

GRANT SELECT, INSERT, UPDATE ON pedido         TO rge_app_write;
GRANT SELECT, INSERT         ON detalle_pedido TO rge_app_write;

GRANT INSERT ON mensaje_contacto TO rge_app_write;

GRANT SELECT, UPDATE ON envio_correo TO rge_app_write;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO rge_app_write;


GRANT SELECT, INSERT, UPDATE ON categoria       TO rge_admin;
GRANT SELECT, INSERT, UPDATE ON producto        TO rge_admin;
GRANT SELECT, INSERT, UPDATE ON producto_talla  TO rge_admin;
GRANT SELECT, INSERT, UPDATE ON imagen_producto TO rge_admin;
GRANT SELECT                 ON talla           TO rge_admin;

GRANT SELECT, UPDATE ON pedido         TO rge_admin;
GRANT SELECT         ON detalle_pedido TO rge_admin;
GRANT SELECT         ON estado_pedido, metodo_pago TO rge_admin;

GRANT SELECT, UPDATE ON mensaje_contacto TO rge_admin;
GRANT SELECT         ON asunto_contacto  TO rge_admin;

GRANT SELECT ON v_usuario_seguro TO rge_admin;
GRANT SELECT ON cliente, direccion_envio, provincia, ciudad TO rge_admin;

GRANT SELECT ON
    rpt_ventas_por_categoria,
    rpt_top_clientes,
    rpt_stock_critico,
    rpt_mensajes_contacto,
    v_catalogo_publico
TO rge_admin;

GRANT SELECT ON auditoria    TO rge_admin;
GRANT SELECT ON envio_correo TO rge_admin;

GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO rge_admin;




GRANT EXECUTE ON ALL ROUTINES IN SCHEMA public TO rge_app_write;
GRANT EXECUTE ON ALL ROUTINES IN SCHEMA public TO rge_admin;

GRANT EXECUTE ON FUNCTION fn_verificar_stock(integer, integer) TO rge_app_read;
GRANT EXECUTE ON FUNCTION fn_tasa_iva()                        TO rge_app_read;



GRANT SELECT ON ALL TABLES    IN SCHEMA public TO rge_backup;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO rge_backup;



ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO rge_backup;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON SEQUENCES TO rge_backup;


ALTER ROLE rge_flask    CONNECTION LIMIT 20;
ALTER ROLE rge_panel    CONNECTION LIMIT 5;
ALTER ROLE rge_respaldo CONNECTION LIMIT 2;

ALTER ROLE rge_flask SET statement_timeout = '30s';
ALTER ROLE rge_panel SET statement_timeout = '60s';



DO $$
DECLARE
    v_sin_clave TEXT;
BEGIN
    SELECT string_agg(rolname, ', ' ORDER BY rolname) INTO v_sin_clave
    FROM   pg_authid
    WHERE  rolname IN ('rge_flask', 'rge_panel', 'rge_respaldo')
      AND  rolpassword IS NULL;

    IF v_sin_clave IS NOT NULL THEN
        RAISE WARNING E'\n\n'
            '  ROLES SIN CONTRASENA: %\n\n'
            '  Existen y tienen sus permisos definidos, pero todavia NO\n'
            '  pueden conectarse.\n\n'
            '  Siguiente paso: ejecutar 07_credenciales.sql\n', v_sin_clave;
    ELSE
        RAISE NOTICE 'Los tres roles de conexion ya tienen contrasena asignada';
    END IF;
EXCEPTION
    WHEN insufficient_privilege THEN
        RAISE NOTICE 'No se pudo comprobar las contrasenas (requiere superusuario)';
END $$;


SELECT rolname      AS rol,
       rolcanlogin  AS puede_conectarse,
       rolsuper     AS es_superusuario,
       rolconnlimit AS limite_conexiones
FROM   pg_roles
WHERE  rolname LIKE 'rge_%'
ORDER  BY rolcanlogin, rolname;


SELECT r.rolname AS usuario, g.rolname AS hereda_de
FROM   pg_auth_members m
JOIN   pg_roles r ON r.oid = m.member
JOIN   pg_roles g ON g.oid = m.roleid
WHERE  r.rolname LIKE 'rge_%'
ORDER  BY usuario;


SELECT grantee    AS rol,
       table_name AS tabla,
       string_agg(DISTINCT privilege_type, ', ' ORDER BY privilege_type) AS permisos
FROM   information_schema.role_table_grants
WHERE  table_schema = 'public'
  AND  grantee LIKE 'rge_%'
GROUP  BY grantee, table_name
ORDER  BY grantee, table_name;


SELECT grantee        AS rol,
       table_name     AS tabla,
       column_name    AS columna,
       privilege_type AS permiso
FROM   information_schema.column_privileges
WHERE  table_schema = 'public'
  AND  grantee LIKE 'rge_%'
ORDER  BY grantee, table_name, column_name;

