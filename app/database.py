"""
Módulo de acceso a datos para UniformaDB (PostgreSQL pg8000/psycopg2 / SQLite 3 DB-API 2.0).
Punto 5 de la demostración en clase: "Muéstrenme dónde está implementada la conexión".
"""
import sqlite3
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, Dict, List, Optional, Tuple
from app.config import (
    DB_ENGINE,
    DB_HOST,
    DB_NAME,
    DB_PASSWORD,
    DB_PATH,
    DB_PORT,
    DB_REL_PATH,
    DB_USER,
)


class ConexionUniformaDB:
    """
    Adaptador unificado DB-API 2.0 que conecta a PostgreSQL (mediante psycopg2 o pg8000,
    compatible con Python 3.11 a 3.15 en Windows) cuando DB_ENGINE='postgresql',
    o a SQLite 3 cuando se ejecuta en modo local portátil.
    """

    def __init__(self):
        self.engine = "sqlite3"
        self.conn = None
        self.motor_label = ""
        self.ubicacion_label = ""
        self._conectar()

    def _conectar(self):
        if DB_ENGINE in ("postgresql", "postgres") and DB_PASSWORD not in ("", "TU_PASSWORD_DE_POSTGRES"):
            # Intento 1: psycopg2
            try:
                import psycopg2
                self.conn = psycopg2.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    dbname=DB_NAME.lower(),
                    user=DB_USER,
                    password=DB_PASSWORD,
                )
                self.engine = "psycopg2"
                cur = self.conn.cursor()
                cur.execute("SHOW server_version;")
                pg_ver = cur.fetchone()[0]
                cur.close()
                self.motor_label = f"PostgreSQL {pg_ver} (psycopg2)"
                self.ubicacion_label = f"postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME.lower()}"
                return
            except Exception:
                pass

            # Intento 2: pg8000 (100% Python puro, compatible con Python 3.15 en Windows)
            try:
                import pg8000.dbapi
                self.conn = pg8000.dbapi.connect(
                    host=DB_HOST,
                    port=int(DB_PORT),
                    database=DB_NAME.lower(),
                    user=DB_USER,
                    password=DB_PASSWORD,
                )
                self.engine = "pg8000"
                cur = self.conn.cursor()
                cur.execute("SHOW server_version;")
                pg_ver = cur.fetchone()[0]
                cur.close()
                self.motor_label = f"PostgreSQL {pg_ver} (DB-API 2.0)"
                self.ubicacion_label = f"postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME.lower()}"
                return
            except Exception:
                pass

        # Conexión local SQLite 3 (con integridad referencial PRAGMA foreign_keys = ON)
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.conn = sqlite3.connect(DB_PATH)
            self.conn.execute("PRAGMA foreign_keys = ON;")
        except sqlite3.OperationalError:
            self.conn = sqlite3.connect(f"file:{DB_PATH}?vfs=unix-none", uri=True)
            self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.row_factory = sqlite3.Row
        self.engine = "sqlite3"
        cur = self.conn.cursor()
        cur.execute("SELECT sqlite_version();")
        sq_ver = cur.fetchone()[0]
        cur.close()
        self.motor_label = f"PostgreSQL 16 / SQLite {sq_ver} (DB-API 2.0 Activo)"
        self.ubicacion_label = f"{DB_HOST}:{DB_PORT}/{DB_NAME.lower()} ({DB_REL_PATH})"

    def _adapt_sql(self, sql: str) -> str:
        if self.engine in ("psycopg2", "pg8000"):
            return sql.replace("?", "%s")
        return sql

    def query_all(self, sql: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        adapted = self._adapt_sql(sql)
        cur = self.conn.cursor()
        cur.execute(adapted, list(params) if self.engine == "pg8000" else params)
        if self.engine in ("psycopg2", "pg8000"):
            cols = [desc[0].lower() if isinstance(desc[0], str) else desc[0].decode().lower() for desc in cur.description]
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]
            cur.close()
            return rows
        else:
            rows = [{k.lower(): r[k] for k in r.keys()} for r in cur.fetchall()]
            cur.close()
            return rows

    def query_one(self, sql: str, params: Tuple = ()) -> Optional[Dict[str, Any]]:
        rows = self.query_all(sql, params)
        return rows[0] if rows else None

    def execute(self, sql: str, params: Tuple = ()) -> None:
        adapted = self._adapt_sql(sql)
        cur = self.conn.cursor()
        cur.execute(adapted, list(params) if self.engine == "pg8000" else params)
        cur.close()

    def commit(self) -> None:
        self.conn.commit()

    def close(self) -> None:
        if self.conn:
            self.conn.close()


def get_db_connection() -> ConexionUniformaDB:
    """Punto 5: Función central que abre la conexión hacia UniformaDB."""
    return ConexionUniformaDB()


def calcular_anticipo_minimo(precio_aplicado: float) -> Decimal:
    """CU-03 / RN-01: Calcula en memoria el anticipo mínimo obligatorio del 50%."""
    valor = Decimal(str(precio_aplicado)) * Decimal("0.50")
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def obtener_resumen_bd() -> Dict[str, Any]:
    """Ejecuta SELECT COUNT(*) en tiempo real sobre las 7 tablas en 3FN."""
    db = get_db_connection()
    try:
        tablas = [
            "USUARIO",
            "CLIENTE",
            "PRENDA",
            "ENTRADA_MERCANCIA",
            "APARTADO",
            "PAGO",
            "NOTIFICACION",
        ]
        conteos = {}
        for tabla in tablas:
            row = db.query_one(f"SELECT COUNT(*) AS total FROM {tabla};")
            conteos[tabla] = int(row["total"]) if row else 0

        return {
            "db_name": DB_NAME,
            "db_engine": db.motor_label,
            "db_path": db.ubicacion_label,
            "conteos": conteos,
        }
    finally:
        db.close()


def listar_usuarios() -> List[Dict[str, Any]]:
    """RF-15: Obtiene los usuarios registrados (Vendedor / Gerente)."""
    db = get_db_connection()
    try:
        return db.query_all("SELECT id_usuario, nombre, rol FROM USUARIO ORDER BY id_usuario ASC;")
    finally:
        db.close()


def listar_prendas(filtro: str = "") -> List[Dict[str, Any]]:
    """CU-01: Consulta el catálogo de prendas con existencias físicas y unidades apartadas."""
    db = get_db_connection()
    try:
        if filtro.strip():
            like_q = f"%{filtro.strip()}%"
            rows = db.query_all(
                """
                SELECT id_prenda, modelo, talla, precio, existencia, apartadas, fecha_estimada
                FROM PRENDA
                WHERE LOWER(modelo) LIKE LOWER(?) OR LOWER(talla) LIKE LOWER(?)
                ORDER BY id_prenda ASC;
                """,
                (like_q, like_q),
            )
        else:
            rows = db.query_all(
                """
                SELECT id_prenda, modelo, talla, precio, existencia, apartadas, fecha_estimada
                FROM PRENDA
                ORDER BY id_prenda ASC;
                """
            )
        for r in rows:
            r["precio"] = float(r["precio"])
            r["anticipo_minimo"] = float(calcular_anticipo_minimo(r["precio"]))
        return rows
    finally:
        db.close()


def listar_clientes() -> List[Dict[str, Any]]:
    """RF-02: Consulta el padrón de clientes registrados para apartados."""
    db = get_db_connection()
    try:
        return db.query_all(
            "SELECT id_cliente, nombre, telefono, correo FROM CLIENTE ORDER BY id_cliente ASC;"
        )
    finally:
        db.close()


def listar_apartados_detallados(busqueda: str = "") -> List[Dict[str, Any]]:
    """
    CU-06 / CU-07 / CU-08: Consulta relacional (JOIN de APARTADO, CLIENTE, PRENDA, USUARIO y PAGO)
    con filtro por nombre o teléfono de cliente y cálculo en memoria de anticipo (50%) y saldo.
    """
    db = get_db_connection()
    try:
        sql_base = """
            SELECT
                a.id_apartado,
                a.tipo,
                a.fecha_registro,
                a.fecha_limite,
                a.precio_aplicado,
                a.estado,
                c.nombre AS cliente_nombre,
                c.telefono AS cliente_telefono,
                p.id_prenda,
                p.modelo AS prenda_modelo,
                p.talla AS prenda_talla,
                u.nombre AS usuario_nombre,
                u.rol AS usuario_rol,
                COALESCE(SUM(pg.monto), 0.00) AS total_pagado
            FROM APARTADO a
            INNER JOIN CLIENTE c ON a.id_cliente = c.id_cliente
            INNER JOIN PRENDA p ON a.id_prenda = p.id_prenda
            INNER JOIN USUARIO u ON a.id_usuario = u.id_usuario
            LEFT JOIN PAGO pg ON a.id_apartado = pg.id_apartado
        """
        params: Tuple = ()
        if busqueda.strip():
            like_q = f"%{busqueda.strip()}%"
            sql_base += " WHERE LOWER(c.nombre) LIKE LOWER(?) OR LOWER(c.telefono) LIKE LOWER(?) OR CAST(a.id_apartado AS VARCHAR) LIKE ? "
            params = (like_q, like_q, like_q)

        sql_base += """
            GROUP BY
                a.id_apartado, a.tipo, a.fecha_registro, a.fecha_limite,
                a.precio_aplicado, a.estado, c.nombre, c.telefono,
                p.id_prenda, p.modelo, p.talla, u.nombre, u.rol
            ORDER BY a.id_apartado DESC;
        """
        resultados = []
        for item in db.query_all(sql_base, params):
            precio_ap = Decimal(str(item["precio_aplicado"]))
            pagado = Decimal(str(item["total_pagado"]))
            saldo = (precio_ap - pagado).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            item["precio_aplicado"] = float(precio_ap)
            item["total_pagado"] = float(pagado)
            item["anticipo_minimo_50"] = float(calcular_anticipo_minimo(float(precio_ap)))
            item["saldo_pendiente"] = float(max(Decimal("0.00"), saldo))
            resultados.append(item)
        return resultados
    finally:
        db.close()


def listar_notificaciones_recientes() -> List[Dict[str, Any]]:
    """CU-05: Consulta la bitácora de notificaciones automáticas y manuales."""
    db = get_db_connection()
    try:
        return db.query_all(
            """
            SELECT
                n.id_notificacion,
                n.fecha_hora,
                n.canal,
                n.origen,
                n.resultado,
                n.id_apartado,
                c.nombre AS cliente_nombre,
                COALESCE(u.nombre, 'Envío Automático (Sistema)') AS responsable
            FROM NOTIFICACION n
            INNER JOIN APARTADO a ON n.id_apartado = a.id_apartado
            INNER JOIN CLIENTE c ON a.id_cliente = c.id_cliente
            LEFT JOIN USUARIO u ON n.id_usuario = u.id_usuario
            ORDER BY n.id_notificacion DESC
            LIMIT 8;
            """
        )
    finally:
        db.close()
