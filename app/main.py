"""
Módulo FastAPI sincronizado con las 4 Pantallas Individuales aprobadas en U2-E3:
- Pantalla 0 (/login): Iniciar sesión y redirigir a Registrar apartado
- Pantalla 1 (/registrar-apartado): Registrar apartado
- Pantalla 2 (/liquidar): Liquidar y entregar pedido
- Pantalla 3 (/vencimientos): Vencimientos de apartados 30 días y cancelación
"""
from pathlib import Path
from urllib.parse import parse_qs

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from app.config import APP_NAME, APP_VERSION, DEFAULT_USER_ID
from app.database import get_db_connection
from run_server import (
    obtener_usuario_sesion,
    render_liquidar,
    render_login,
    render_registrar_apartado,
    render_vencimientos,
)

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
@app.get("/login", response_class=HTMLResponse)
@app.get("/logout", response_class=HTMLResponse)
async def get_login(request: Request):
    qs = parse_qs(str(request.url.query))
    user_id = int(qs.get("user_id", [str(DEFAULT_USER_ID)])[0]) if "user_id" in qs else None
    u = obtener_usuario_sesion(user_id) if user_id else None
    return HTMLResponse(render_login(qs, usuario_activo=u).decode("utf-8"))


@app.post("/login")
async def post_login(
    id_usuario: str = Form(""),
    nombre: str = Form(""),
    rol: str = Form("Vendedor"),
):
    id_in = id_usuario.strip()
    nombre_in = nombre.strip()
    rol_in = rol.strip()

    db = get_db_connection()
    try:
        row = db.query_one(
            "SELECT id_usuario, nombre, rol FROM USUARIO WHERE id_usuario = ?;",
            (int(id_in) if id_in.isdigit() else -1,),
        )
    finally:
        db.close()

    if not row or row["rol"].lower() != rol_in.lower() or not nombre_in or nombre_in.lower() not in row["nombre"].lower():
        err = "Las credenciales ingresadas no son válidas. Verifique sus datos e intente nuevamente."
        return HTMLResponse(
            render_login(
                {},
                msg_exito=False,
                msg_error=err,
                usuario_activo={"id_usuario": id_in, "nombre": nombre_in, "rol": rol_in},
            ).decode("utf-8")
        )

    return RedirectResponse(url=f"/registrar-apartado?user_id={row['id_usuario']}&bienvenida=1", status_code=303)


@app.get("/registrar-apartado", response_class=HTMLResponse)
@app.get("/conexion-bd", response_class=HTMLResponse)
async def get_registrar_apartado(
    request: Request,
    user_id: int = DEFAULT_USER_ID,
    modelo: str = "",
    talla: str = "",
    bienvenida: int = 0,
):
    return HTMLResponse(
        render_registrar_apartado(
            user_id,
            modelo_q=modelo,
            talla_q=talla,
            bienvenida=(bienvenida == 1),
        ).decode("utf-8")
    )


@app.get("/liquidar", response_class=HTMLResponse)
async def get_liquidar(request: Request, user_id: int = DEFAULT_USER_ID, q: str = "Ana Sofía López", folio: int = None):
    return HTMLResponse(render_liquidar(user_id, q=q, folio_sel=folio).decode("utf-8"))


@app.get("/vencimientos", response_class=HTMLResponse)
async def get_vencimientos(request: Request, user_id: int = 201, folio: int = None):
    return HTMLResponse(render_vencimientos(user_id, folio_sel=folio).decode("utf-8"))
