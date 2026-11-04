# Alcance, Casos de Uso Aprobados y Plan de Integración (U3-E1)

**Proyecto:** Sistema Uniforma (Control de inventario y seguimiento de apartados)  
**Equipo:** Equipo 16  
**Integrante responsable:** Ricardo Uriel Mejía Cortez  

## 1. Trazabilidad de Casos de Uso Aprobados (U1 / U2) hacia la Base de Datos (`UniformaDB`)

| ID | Caso de Uso Aprobado | Actor(es) | Requisitos Asociados | Tablas de `UniformaDB` Involucradas | Prioridad | Etapa de Construcción |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Transversal** | Control de acceso y sesión por rol | Vendedor, Gerente | `RF-15` | `USUARIO` | Alta | Base en E1 / Completo en E2 (Corte 1) |
| **CU-01** | Consultar disponibilidad por modelo y talla | Vendedor, Gerente | `RF-01`, `RF-07` | `PRENDA` | Alta | Demostrado en E1 / Filtros en E2 (Corte 1) |
| **CU-02** | Registrar apartado | Vendedor, Gerente | `RF-01`, `RF-02`, `RF-03`, `RF-05`, `RF-08`, `RF-12`, `RF-14`, `RF-15` | `CLIENTE`, `PRENDA`, `APARTADO`, `PAGO`, `USUARIO` | Alta | Operación base en E1 / Flujo completo en E2 (Corte 1) |
| **CU-03** | Validar anticipo mínimo de 50 % (`<<include>>`) | Sistema | `RF-05`, `RN-01` | `APARTADO` (`precio_aplicado`), `PAGO` (`monto`) | Alta | Validación activa en E1 / E2 (Corte 1) |
| **CU-04** | Registrar pedido especial sin existencia (`<<extend>>`) | Vendedor, Gerente | `RF-07`, `RF-09`, `RF-14` | `PRENDA`, `APARTADO`, `PAGO` | Alta | E2 (Corte 1 - 12 de noviembre) |
| **CU-05** | Notificar automáticamente a clientes | Sistema, Gerente | `RF-04`, `RF-16` | `NOTIFICACION`, `APARTADO`, `CLIENTE`, `USUARIO` | Media | E2 (Corte 2 - 19 de noviembre) |
| **CU-06** | Consultar estado de apartado por nombre o teléfono | Vendedor, Gerente | `RF-10`, `RF-14` | `APARTADO`, `CLIENTE`, `PRENDA`, `PAGO` | Alta | Consulta base en E1 / Buscador en E2 (Corte 1) |
| **CU-07** | Liquidar y entregar pedido (incluye `CU-06`) | Vendedor, Gerente | `RF-08`, `RF-10`, `RF-11`, `RF-12`, `RF-14`, `RF-15` | `APARTADO`, `PAGO`, `PRENDA`, `USUARIO` | Alta | E2 (Corte 2 - 19 de noviembre) |
| **CU-08** | Gestionar vencimientos de apartados (> 30 días) | Gerente | `RF-12`, `RF-14`, `RF-15` | `APARTADO`, `CLIENTE`, `NOTIFICACION` | Media | E2 (Corte 2 - 19 de noviembre) |
| **CU-09** | Cancelar apartado vencido y reingresar prenda (`<<extend>>`) | Gerente | `RF-06`, `RF-08`, `RF-14`, `RF-15` | `APARTADO`, `PRENDA`, `USUARIO` | Media | E2 (Cierre - 23 de noviembre) |
| **CU-10** | Registrar entrada de mercancía y fecha estimada | Gerente | `RF-07`, `RF-08`, `RF-13`, `RF-14`, `RF-15` | `ENTRADA_MERCANCIA`, `PRENDA`, `APARTADO`, `NOTIFICACION` | Media | E2 (Cierre - 23 de noviembre) |
