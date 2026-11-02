-- ============================================================================
-- PROYECTO: Sistema Uniforma (Control de inventario y seguimiento de apartados)
-- EQUIPO 16: Ricardo Uriel Mejía Cortez
-- UNIDAD 3 - EVIDENCIA 1 (U3-E1): Script DDL Oficial para PostgreSQL (3FN)
-- Basado estrictamente en el Modelo de Base de Datos aprobado en U2-E2.
-- Instrucción en pgAdmin 4: Crear la BD "uniformadb", abrir Query Tool y ejecutar (F5).
-- ============================================================================

DROP TABLE IF EXISTS NOTIFICACION CASCADE;
DROP TABLE IF EXISTS PAGO CASCADE;
DROP TABLE IF EXISTS APARTADO CASCADE;
DROP TABLE IF EXISTS ENTRADA_MERCANCIA CASCADE;
DROP TABLE IF EXISTS PRENDA CASCADE;
DROP TABLE IF EXISTS CLIENTE CASCADE;
DROP TABLE IF EXISTS USUARIO CASCADE;

-- 1. Tabla USUARIO (Personal operativo: Vendedor / Gerente - RF-15)
CREATE TABLE USUARIO (
    id_usuario INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    rol VARCHAR(20) NOT NULL CHECK (rol IN ('Vendedor', 'Gerente'))
);

-- 2. Tabla CLIENTE (Datos de contacto para apartados y notificaciones - RF-02, RF-10)
CREATE TABLE CLIENTE (
    id_cliente INT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20) NOT NULL,
    correo VARCHAR(100) NULL
);

-- 3. Tabla PRENDA (Catálogo e inventario físico y apartado por modelo y talla - RF-01, RF-07, RF-08)
CREATE TABLE PRENDA (
    id_prenda INT PRIMARY KEY,
    modelo VARCHAR(50) NOT NULL,
    talla VARCHAR(10) NOT NULL,
    precio DECIMAL(10,2) NOT NULL CHECK (precio > 0),
    existencia INT NOT NULL DEFAULT 0 CHECK (existencia >= 0),
    apartadas INT NOT NULL DEFAULT 0 CHECK (apartadas >= 0),
    fecha_estimada DATE NULL,
    CONSTRAINT uq_prenda_modelo_talla UNIQUE (modelo, talla)
);

-- 4. Tabla ENTRADA_MERCANCIA (Bitácora de abastecimiento por el Gerente - CU-10, RF-13)
CREATE TABLE ENTRADA_MERCANCIA (
    id_entrada INT PRIMARY KEY,
    fecha DATE NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    id_prenda INT NOT NULL,
    id_usuario INT NOT NULL,
    CONSTRAINT fk_entrada_prenda FOREIGN KEY (id_prenda) REFERENCES PRENDA(id_prenda)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_entrada_usuario FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 5. Tabla APARTADO (Operación central de apartados y pedidos especiales - CU-02, CU-04, CU-08, CU-09)
-- Incluye precio_aplicado para preservar en 3FN el precio pactado al momento del registro.
CREATE TABLE APARTADO (
    id_apartado INT PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('Apartado', 'Pedido especial')),
    fecha_registro DATE NOT NULL,
    fecha_limite DATE NULL,
    precio_aplicado DECIMAL(10,2) NOT NULL CHECK (precio_aplicado > 0),
    estado VARCHAR(20) NOT NULL CHECK (estado IN ('En espera', 'Disponible', 'Vencido', 'Entregado', 'Cancelado')),
    id_cliente INT NOT NULL,
    id_prenda INT NOT NULL,
    id_usuario INT NOT NULL,
    CONSTRAINT fk_apartado_cliente FOREIGN KEY (id_cliente) REFERENCES CLIENTE(id_cliente)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_apartado_prenda FOREIGN KEY (id_prenda) REFERENCES PRENDA(id_prenda)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_apartado_usuario FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 6. Tabla PAGO (Historial de anticipos >= 50% y liquidaciones - CU-03, CU-07, RF-05, RF-11)
CREATE TABLE PAGO (
    id_pago INT PRIMARY KEY,
    monto DECIMAL(10,2) NOT NULL CHECK (monto > 0),
    fecha DATE NOT NULL,
    tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('Anticipo', 'Liquidacion')),
    id_apartado INT NOT NULL,
    CONSTRAINT fk_pago_apartado FOREIGN KEY (id_apartado) REFERENCES APARTADO(id_apartado)
        ON UPDATE CASCADE ON DELETE RESTRICT
);

-- 7. Tabla NOTIFICACION (Trazabilidad de avisos automáticos y manuales - CU-05, RF-04, RF-16)
CREATE TABLE NOTIFICACION (
    id_notificacion INT PRIMARY KEY,
    fecha_hora TIMESTAMP NOT NULL,
    canal VARCHAR(20) NOT NULL CHECK (canal IN ('SMS', 'Correo', 'Llamada')),
    origen VARCHAR(20) NOT NULL CHECK (origen IN ('Sistema', 'Usuario')),
    resultado VARCHAR(20) NOT NULL CHECK (resultado IN ('Entregado', 'Fallido', 'Pendiente')),
    id_apartado INT NOT NULL,
    id_usuario INT NULL,
    CONSTRAINT fk_notificacion_apartado FOREIGN KEY (id_apartado) REFERENCES APARTADO(id_apartado)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_notificacion_usuario FOREIGN KEY (id_usuario) REFERENCES USUARIO(id_usuario)
        ON UPDATE CASCADE ON DELETE SET NULL
);
