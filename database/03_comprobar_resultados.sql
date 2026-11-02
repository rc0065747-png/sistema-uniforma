-- ============================================================================
-- CONSULTAS PARA DEMOSTRAR EL PUNTO 4 EN CLASE (EN PGADMIN 4 QUERY TOOL)
-- "4. Comprueben el resultado en la BD"
-- Ejecute este script (F5) en pgAdmin 4 después de registrar o liquidar en la web.
-- ============================================================================

-- 1. Ver todos los apartados y su saldo pendiente calculado en tiempo real (3FN):
SELECT
    a.id_apartado AS folio,
    a.tipo,
    c.nombre AS cliente,
    p.modelo AS prenda,
    p.talla,
    a.precio_aplicado,
    COALESCE(SUM(pg.monto), 0.00) AS total_abonado,
    (a.precio_aplicado - COALESCE(SUM(pg.monto), 0.00)) AS saldo_pendiente,
    a.estado,
    a.fecha_limite
FROM APARTADO a
INNER JOIN CLIENTE c ON a.id_cliente = c.id_cliente
INNER JOIN PRENDA p ON a.id_prenda = p.id_prenda
LEFT JOIN PAGO pg ON a.id_apartado = pg.id_apartado
GROUP BY a.id_apartado, a.tipo, c.nombre, p.modelo, p.talla, a.precio_aplicado, a.estado, a.fecha_limite
ORDER BY a.id_apartado DESC;

-- 2. Ver los pagos registrados (Anticipos y Liquidaciones):
SELECT id_pago, tipo, monto, fecha, id_apartado FROM PAGO ORDER BY id_pago DESC;

-- 3. Ver el inventario actualizado en PRENDA (existencia disponible vs apartadas):
SELECT id_prenda, modelo, talla, precio, existencia, apartadas, fecha_estimada FROM PRENDA ORDER BY id_prenda ASC;
