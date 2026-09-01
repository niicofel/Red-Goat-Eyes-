-- ============================================================
-- 09 · DATOS DE LA DEMOSTRACION
-- Deja la tienda limpia y con el catalogo por tallas:
-- hoodies y pantalones en S, M, L y XL, accesorios en talla
-- unica, 20 unidades cada una, y un solo administrador.
-- ============================================================
BEGIN;


-- ---------------- Limpieza ----------------
-- Los pedidos van primero porque pedido -> cliente es RESTRICT
DELETE FROM pedido;
DELETE FROM mensaje_contacto;
DELETE FROM usuario;



-- ---------------- Administrador unico ----------------
INSERT INTO usuario (email, password_hash, rol, activo)
VALUES ('fc762798@gmail.com',
        '$2b$12$6Z099j1VCS4HWeuDoOesV.2/GoMwTl4hy0F8kSYobgPR6hMVvXQjy',
        'administrador',
        TRUE);

INSERT INTO administrador (id_administrador, nombres, apellidos, cargo, nivel_acceso)
SELECT id_usuario, 'Felipe Nicolas', 'Campos Cisneros', 'Administrador general', 3
FROM   usuario
WHERE  email = 'fc762798@gmail.com';



-- ---------------- Tallas del catalogo ----------------
-- Borra la talla unica de hoodies y pantalones y pone S, M, L y XL
DELETE FROM producto_talla pt
USING  producto p, categoria c
WHERE  pt.id_producto  = p.id_producto
  AND  c.id_categoria  = p.id_categoria
  AND  c.nombre IN ('Hoodies', 'Pantalones');

INSERT INTO producto_talla (id_producto, id_talla, stock, stock_minimo)
SELECT p.id_producto, t.id_talla, 20, 3
FROM   producto p
JOIN   categoria c ON c.id_categoria = p.id_categoria
CROSS  JOIN talla t
WHERE  c.nombre IN ('Hoodies', 'Pantalones')
  AND  t.codigo IN ('S', 'M', 'L', 'XL')
ON CONFLICT (id_producto, id_talla)
DO UPDATE SET stock = 20, stock_minimo = 3;

UPDATE producto_talla pt
SET    stock = 20, stock_minimo = 3
FROM   producto p, categoria c
WHERE  pt.id_producto = p.id_producto
  AND  c.id_categoria = p.id_categoria
  AND  c.nombre = 'Accesorios';




-- ---------------- Comprobacion final ----------------
SELECT 'usuarios'          AS elemento, COUNT(*)::TEXT AS valor FROM usuario
UNION ALL
SELECT 'pedidos',          COUNT(*)::TEXT FROM pedido
UNION ALL
SELECT 'mensajes',         COUNT(*)::TEXT FROM mensaje_contacto
UNION ALL
SELECT 'filas de talla',   COUNT(*)::TEXT FROM producto_talla
UNION ALL
SELECT 'productos activos', COUNT(*)::TEXT FROM v_catalogo_publico;


COMMIT;