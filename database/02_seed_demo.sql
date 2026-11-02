-- ============================================================================
-- DATOS DE DEMOSTRACIÓN FICTICIOS - Sistema Uniforma (U3-E1)
-- Coinciden exactamente con los casos y montos de los prototipos de U2-E3.
-- ============================================================================

-- 1. Usuarios ficticios de demostración (RF-15)
INSERT INTO USUARIO (id_usuario, nombre, rol) VALUES
(101, 'Carlos Méndez', 'Vendedor'),
(201, 'Laura Torres', 'Gerente');

-- 2. Clientes ficticios de demostración (RF-02)
INSERT INTO CLIENTE (id_cliente, nombre, telefono, correo) VALUES
(1, 'Ana Sofía López Hernández', '777 123 4567', 'ana.lopez@correo.mx'),
(2, 'Roberto Gómez', '777 987 6543', 'roberto.gomez@correo.mx'),
(3, 'María Fernanda Ruiz', '777 456 7890', 'mfernanda.ruiz@correo.mx');

-- 3. Catálogo de prendas (RF-01, RF-07, RF-08)
INSERT INTO PRENDA (id_prenda, modelo, talla, precio, existencia, apartadas, fecha_estimada) VALUES
(10, 'Chamarra Secundaria', 'M', 600.00, 8, 1, NULL),
(11, 'Chamarra Secundaria', 'G', 600.00, 5, 0, NULL),
(12, 'Suéter Escolar', 'G', 560.00, 12, 1, NULL),
(13, 'Pants Deportivo', 'M', 500.00, 0, 1, '2026-10-30'),
(14, 'Falda Plisada', 'CH', 480.00, 6, 1, NULL);

-- 4. Bitácora de entradas de mercancía registradas por Gerencia (CU-10, RF-13)
INSERT INTO ENTRADA_MERCANCIA (id_entrada, fecha, cantidad, id_prenda, id_usuario) VALUES
(1, '2026-10-15', 10, 10, 201),
(2, '2026-10-18', 15, 12, 201);

-- 5. Apartados y Pedidos Especiales de demostración (CU-02, CU-04, CU-08)
INSERT INTO APARTADO (id_apartado, tipo, fecha_registro, fecha_limite, precio_aplicado, estado, id_cliente, id_prenda, id_usuario) VALUES
(104, 'Apartado',        '2026-10-22', '2026-11-21', 600.00, 'Disponible', 1, 10, 101),
(109, 'Pedido especial', '2026-10-20', '2026-10-30', 500.00, 'En espera',  1, 13, 101),
(87,  'Apartado',        '2026-09-15', '2026-10-15', 560.00, 'Vencido',    2, 12, 101),
(91,  'Apartado',        '2026-09-18', '2026-10-18', 480.00, 'Vencido',    3, 14, 101);

-- 6. Pagos de anticipo (>= 50% del precio_aplicado conforme a RN-01 / CU-03)
INSERT INTO PAGO (id_pago, monto, fecha, tipo, id_apartado) VALUES
(501, 350.00, '2026-10-22', 'Anticipo', 104),
(502, 250.00, '2026-10-20', 'Anticipo', 109),
(503, 280.00, '2026-09-15', 'Anticipo', 87),
(504, 240.00, '2026-09-18', 'Anticipo', 91);

-- 7. Notificaciones registradas (CU-05, RF-04, RF-16)
INSERT INTO NOTIFICACION (id_notificacion, fecha_hora, canal, origen, resultado, id_apartado, id_usuario) VALUES
(901, '2026-10-22 11:15:00', 'Correo', 'Sistema', 'Entregado', 104, NULL),
(902, '2026-10-16 09:30:00', 'SMS',    'Sistema', 'Entregado', 87,  NULL),
(903, '2026-10-19 10:05:00', 'Llamada','Usuario', 'Entregado', 91,  201);
