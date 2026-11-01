# Sistema Uniforma: Control de Inventario y Seguimiento de Apartados

**Asignatura:** Ingeniería de Software · Unidad 3 (Desarrollo - Evidencia 1)  
**Equipo:** Equipo 16  
**Integrante:** Ricardo Uriel Mejía Cortez  
**Tipo de aplicación:** Aplicación Web (Cliente-Servidor ejecutada en navegador)  
**SGBD:** PostgreSQL 16 (`uniformadb` en 3FN via `psycopg2-binary`, con soporte portátil SQLite 3)  
**Versión presentada:** `v1.2.0-E1`  

---

## 1. Propósito y Objetivo del Proyecto
El **Sistema Uniforma** resuelve la problemática operativa de la tienda de uniformes *"Uniforma"*, centralizando en una aplicación web conectada a la base de datos relacional **`UniformaDB` (en 3FN)** el control de existencias por modelo y talla (`CU-01`), el registro de apartados (`CU-02`) y pedidos especiales (`CU-04`) con validación en memoria del anticipo mínimo del 50 % (`CU-03` / `RN-01`), la consulta por cliente o teléfono (`CU-06`), la liquidación de saldos y entrega (`CU-07`), el control de vencimientos > 30 días y cancelación con reingreso a stock (`CU-08`, `CU-09`), el registro de entradas de mercancía (`CU-10`) y la bitácora de notificaciones (`CU-05`) bajo permisos por rol (`RF-15`).

## 2. Stack Tecnológico y Versiones
| Componente | Tecnología Seleccionada | Versión |
| :--- | :--- | :--- |
| **Tipo de aplicación** | Aplicación Web (Cliente-Servidor en navegador) | HTML5 / CSS3 / ES6 |
| **Lenguaje principal** | Python | `3.11+` |
| **Framework Web** | FastAPI + Starlette + Plantillas Jinja2 + Uvicorn | `FastAPI 0.92.0` / `Uvicorn 0.17.6` |
| **SGBD Relacional** | PostgreSQL (`uniformadb` en 3FN) + Respaldo portátil SQLite 3 | `PostgreSQL 16` / `psycopg2-binary 2.9.9` |
| **Acceso a datos** | Conector DB-API 2.0 (`psycopg2` / `sqlite3`) + `python-dotenv` | `python-dotenv 1.2.4` |
| **Entorno y versiones** | Visual Studio Code + Git + GitHub Desktop + pgAdmin 4 | `Git 2.39+` |

## 3. Estructura del Repositorio
```text
sistema-uniforma/
├── app/
│   ├── config.py                     # Carga de variables .env (DB_ENGINE, DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
│   ├── database.py                   # Conexión DB-API 2.0 (PostgreSQL psycopg2 / SQLite 3) y reglas 3FN
│   ├── main.py                       # Controladores HTTP (CU-01 a CU-10, liquidación, cancelación y entradas)
│   ├── static/styles.css             # Sistema visual aprobado en U2-E3 (#1E3A8A, #2563EB, #F8FAFC)
│   └── templates/conexion_bd.html    # Panel operativo web conectado en tiempo real a UniformaDB
├── database/
│   ├── 01_schema_postgres.sql        # Script DDL oficial para PostgreSQL / pgAdmin 4 (7 tablas en 3FN)
│   ├── 01_schema_uniforma.sql        # Script DDL compatible con SQLite 3 (7 tablas en 3FN)
│   ├── 02_seed_demo.sql              # Datos ficticios de demostración (clientes, prendas, apartados, pagos)
│   ├── 03_comprobar_resultados.sql   # Consultas SQL listas para comprobar resultados en pgAdmin 4 (Punto 4)
│   └── init_db.py                    # Script automatizado que crea la BD y carga las 7 tablas y datos semilla
├── docs/
│   └── alcance_y_trazabilidad.md     # Matriz de casos de uso aprobados (CU-01 a CU-10) y plan de integración
├── 1_CREAR_BD_Y_DATOS.bat            # Asistente de 1 clic en Windows para instalar dependencias y crear la BD
├── 2_INICIAR_SISTEMA_UNIFORMA.bat    # Asistente de 1 clic en Windows para iniciar el servidor y abrir el navegador
├── 3_VERIFICAR_BD_EN_CONSOLA.bat     # Asistente de 1 clic para comprobar los registros directamente en la BD
├── .env.example                      # Plantilla de variables de entorno (sin contraseñas reales)
├── .gitignore                        # Exclusión de venv/, __pycache__/, .env y archivos .db locales
├── requirements.txt                  # Dependencias del proyecto
└── README.md                         # Documentación paso a paso para ejecutar el proyecto
```

## 4. Cómo otro integrante puede descargar y ejecutar el proyecto paso a paso (Punto 6)

### Opción A: Ejecución rápida en Windows (con los asistentes incluidos)
1. Clonar o descargar el repositorio desde GitHub y abrir la carpeta `sistema-uniforma`.
2. Abrir `.env.example`, guardarlo como `.env` y colocar su contraseña local de PostgreSQL en `DB_PASSWORD` (o dejar `DB_ENGINE="sqlite3"` si desea probar sin servidor externo).
3. Hacer doble clic en **`1_CREAR_BD_Y_DATOS.bat`** (instala `requirements.txt`, crea las 7 tablas en 3FN y carga los datos ficticios).
4. Hacer doble clic en **`2_INICIAR_SISTEMA_UNIFORMA.bat`** (inicia Uvicorn y abre automáticamente `http://127.0.0.1:8000/conexion-bd`).

### Opción B: Ejecución manual desde terminal (Windows / Linux / macOS)
```bash
git clone https://github.com/rc0065747-png/sistema-uniforma.git
cd sistema-uniforma
python -m venv venv
venv\Scripts\activate                 # En Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env                # En Linux/macOS: cp .env.example .env
python database/init_db.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
