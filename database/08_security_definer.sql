-- ============================================================
-- 08 · PERMISOS ESPECIALES
-- Algunas funciones necesitan escribir en tablas donde el rol
-- de la aplicacion no tiene permiso. En vez de darle mas
-- permisos a toda la aplicacion, solo estas funciones se
-- ejecutan con los permisos de su dueno.
-- IMPORTANTE: se ejecuta como postgres.
-- ============================================================
ALTER FUNCTION fn_trg_encolar_correo()
    SECURITY DEFINER
    SET search_path = public, pg_temp;

ALTER FUNCTION fn_trg_auditar_producto()
    SECURITY DEFINER
    SET search_path = public, pg_temp;

ALTER PROCEDURE sp_cambiar_estado_pedido(character varying, character varying, integer)
    SECURITY DEFINER
    SET search_path = public, pg_temp;

ALTER PROCEDURE sp_reponer_stock(character varying, character varying, integer, integer)
    SECURITY DEFINER
    SET search_path = public, pg_temp;


SELECT p.proname AS rutina,
       CASE WHEN p.prosecdef THEN 'SECURITY DEFINER' ELSE 'SECURITY INVOKER' END AS modo,
       pg_get_userbyid(p.proowner) AS dueno
FROM   pg_proc p
JOIN   pg_namespace n ON n.oid = p.pronamespace
WHERE  n.nspname = 'public'
  AND  p.proname IN ('fn_trg_encolar_correo', 'fn_trg_auditar_producto',
                     'sp_cambiar_estado_pedido', 'sp_reponer_stock')
ORDER  BY p.proname;