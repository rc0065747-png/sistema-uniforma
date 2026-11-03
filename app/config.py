"""
Carga centralizada de configuración desde variables de entorno (.env).
Soporta conexión nativa a PostgreSQL (pgAdmin 4) y respaldo en SQLite 3.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

APP_NAME = os.getenv("APP_NAME", "Sistema Uniforma")
APP_ENV = os.getenv("APP_ENV", "development")
APP_HOST = os.getenv("APP_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("APP_PORT", "8000"))
APP_VERSION = os.getenv("APP_VERSION", "1.2.0-E1")

# Parámetros de conexión a PostgreSQL (SGBD principal del proyecto)
DB_ENGINE = os.getenv("DB_ENGINE", "postgresql").lower()
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "uniformadb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Ruta local en caso de usar SQLite como respaldo
DB_REL_PATH = os.getenv("DB_PATH", "database/uniforma.db")
DB_PATH = BASE_DIR / DB_REL_PATH
DEFAULT_USER_ID = int(os.getenv("DEFAULT_USER_ID", "101"))
