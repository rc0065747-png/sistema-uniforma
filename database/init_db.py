"""
Script reproducible de inicialización de la base de datos UniformaDB (3FN).
Punto 2 de la demostración: "Muéstrenme la BD y cómo la crean con su script".
Soporta PostgreSQL (via psycopg2 o pg8000 en Python 3.11-3.15) y SQLite 3.
"""
import os
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

DB_ENGINE = os.getenv("DB_ENGINE", "postgresql").lower()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "uniformadb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

DB_REL_PATH = os.getenv("DB_PATH", "database/uniforma.db")
DB_FILE = BASE_DIR / DB_REL_PATH
PG_SCHEMA_FILE = BASE_DIR / "database" / "01_schema_postgres.sql"
SQLITE_SCHEMA_FILE = BASE_DIR / "database" / "01_schema_uniforma.sql"
SEED_FILE = BASE_DIR / "database" / "02_seed_demo.sql"

TABLAS_3FN = [
    "USUARIO",
    "CLIENTE",
    "PRENDA",
    "ENTRADA_MERCANCIA",
    "APARTADO",
    "PAGO",
    "NOTIFICACION",
]


def _run_sql_statements(cur, sql_text: str):
    """Ejecuta sentencias SQL separadas por punto y coma ignorando comentarios vacíos."""
    for raw_stmt in sql_text.split(";"):
        lines = [ln for ln in raw_stmt.splitlines() if not ln.strip().startswith("--")]
        stmt = "\n".join(lines).strip()
        if stmt:
            cur.execute(stmt + ";")


def init_postgresql(load_seed: bool = True) -> bool:
    """Conecta a PostgreSQL con pg8000 o psycopg2, crea uniformadb y aplica 01_schema_postgres.sql."""
    if DB_PASSWORD in ("", "TU_PASSWORD_DE_POSTGRES"):
        print("[INFO] DB_PASSWORD tiene el valor de ejemplo. Inicializando base de datos local UniformaDB...")
        return False

    # Intentar con pg8000 (100% Python puro, compatible con Python 3.15 en Windows)
    try:
        import pg8000.dbapi

        admin_conn = pg8000.dbapi.connect(
            host=DB_HOST, port=DB_PORT, database="postgres", user=DB_USER, password=DB_PASSWORD
        )
        admin_conn.autocommit = True
        cur = admin_conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", [DB_NAME.lower()])
        if not cur.fetchone():
            cur.execute(f'CREATE DATABASE "{DB_NAME.lower()}";')
            print(f"[OK] Base de datos PostgreSQL '{DB_NAME.lower()}' creada automáticamente.")
        else:
            print(f"[OK] Base de datos PostgreSQL '{DB_NAME.lower()}' detectada.")
        cur.close()
        admin_conn.close()

        conn = pg8000.dbapi.connect(
            host=DB_HOST, port=DB_PORT, database=DB_NAME.lower(), user=DB_USER, password=DB_PASSWORD
        )
        cur = conn.cursor()
        _run_sql_statements(cur, PG_SCHEMA_FILE.read_text(encoding="utf-8"))
        print(f"[OK] Esquema 3FN aplicado exitosamente en PostgreSQL ({DB_HOST}:{DB_PORT}/{DB_NAME.lower()})")

        if load_seed and SEED_FILE.exists():
            _run_sql_statements(cur, SEED_FILE.read_text(encoding="utf-8"))
            print("[OK] Datos ficticios de demostración (02_seed_demo.sql) cargados en PostgreSQL.")

        conn.commit()
        print("\nResumen de las 7 tablas en PostgreSQL (UniformaDB - 3FN):")
        print("-" * 52)
        for t in TABLAS_3FN:
            cur.execute(f"SELECT COUNT(*) FROM {t};")
            total = cur.fetchone()[0]
            print(f"  - {t:<20} : {total} registros")
        print("-" * 52)
        cur.close()
        conn.close()
        return True
    except Exception as exc:
        print(f"[AVISO PostgreSQL] No se pudo conectar con la clave indicada ({exc}).")
        print("-> Activando motor local UniformaDB para garantizar ejecución inmediata.\n")
        return False


def init_sqlite(load_seed: bool = True) -> None:
    """Inicializa la base de datos local con las mismas 7 tablas en 3FN."""
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(SQLITE_SCHEMA_FILE.read_text(encoding="utf-8"))
    except sqlite3.OperationalError:
        conn = sqlite3.connect(f"file:{DB_FILE}?vfs=unix-none", uri=True)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(SQLITE_SCHEMA_FILE.read_text(encoding="utf-8"))

    print(f"[OK] Esquema 3FN creado exitosamente en: {DB_REL_PATH}")
    if load_seed and SEED_FILE.exists():
        conn.executescript(SEED_FILE.read_text(encoding="utf-8"))
        print("[OK] Datos ficticios de demostración (02_seed_demo.sql) cargados correctamente.")
    conn.commit()

    cur = conn.cursor()
    print("\nResumen de las 7 tablas en UniformaDB (3FN):")
    print("-" * 52)
    for t in TABLAS_3FN:
        cur.execute(f"SELECT COUNT(*) FROM {t};")
        total = cur.fetchone()[0]
        print(f"  - {t:<20} : {total} registros")
    print("-" * 52)
    conn.close()


if __name__ == "__main__":
    seed_flag = "--no-seed" not in sys.argv
    if DB_ENGINE in ("postgresql", "postgres"):
        ok = init_postgresql(load_seed=seed_flag)
        # También inicializa el archivo local de respaldo para que siempre exista
        init_sqlite(load_seed=seed_flag)
    else:
        init_sqlite(load_seed=seed_flag)
