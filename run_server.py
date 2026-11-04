"""
Servidor Web del Sistema Uniforma con las 4 Pantallas Individuales aprobadas en U2-E3:
- Pantalla 0 (/ o /login): Iniciar sesión y redirigir automáticamente a Registrar apartado.
- Pantalla 1 (/registrar-apartado): Consultar disponibilidad, validar anticipo del 50% y registrar apartado o pedido especial.
- Pantalla 2 (/liquidar): Buscar por nombre o teléfono y liquidar y entregar pedido.
- Pantalla 3 (/vencimientos): Gestionar vencimientos de más de 30 días y cancelar liberando prenda.
"""
import sys
from datetime import date, timedelta
from decimal import Decimal
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from jinja2 import Environment, FileSystemLoader

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from app.config import APP_HOST, APP_NAME, APP_PORT, APP_VERSION, DEFAULT_USER_ID
from app.database import (
    calcular_anticipo_minimo,
    get_db_connection,
    listar_apartados_detallados,
    listar_prendas,
    listar_usuarios,
    obtener_resumen_bd,
)
from database.init_db import DB_FILE, init_sqlite

if not DB_FILE.exists():
    init_sqlite(load_seed=True)

jinja_env = Environment(loader=FileSystemLoader(str(BASE_DIR / "app" / "templates")))


def obtener_usuario_sesion(user_id: int):
    usuarios = listar_usuarios()
    for u in usuarios:
        if int(u["id_usuario"]) == int(user_id):
            return u
    return usuarios[0] if usuarios else {"id_usuario": 101, "nombre": "Carlos Méndez", "rol": "Vendedor"}


def render_login(qs: dict, msg_exito: bool = False, msg_error: str = "", usuario_activo: dict = None) -> bytes:
    resumen = obtener_resumen_bd()
    limpiar = qs.get("limpiar", [""])[0]
    if limpiar:
        form_id, form_nombre, form_rol = "", "", "Vendedor"
    elif usuario_activo:
        form_id = str(usuario_activo["id_usuario"])
        form_nombre = usuario_activo["nombre"]
        form_rol = usuario_activo["rol"]
    else:
        form_id, form_nombre, form_rol = "101", "Carlos Méndez", "Vendedor"

    tmpl = jinja_env.get_template("login.html")
    return tmpl.render(
        resumen=resumen,
        form_id=form_id,
        form_nombre=form_nombre,
        form_rol=form_rol,
        msg_exito=msg_exito,
        msg_error=msg_error,
        usuario_activo=usuario_activo or {"id_usuario": 101, "nombre": "Carlos Méndez", "rol": "Vendedor"},
    ).encode("utf-8")


def render_registrar_apartado(
    user_id: int,
    modelo_q: str = "",
    talla_q: str = "",
    msg_exito: dict = None,
    msg_error: dict = None,
    form_data: dict = None,
    bienvenida: bool = False,
) -> bytes:
    resumen = obtener_resumen_bd()
    usuario_activo = obtener_usuario_sesion(user_id)
    prendas = listar_prendas()

    modelos_unicos = []
    tallas_unicas = []
    for p in prendas:
        if p["modelo"] not in modelos_unicos:
            modelos_unicos.append(p["modelo"])
        if p["talla"] not in tallas_unicas:
            tallas_unicas.append(p["talla"])

    prenda_actual = prendas[0]
    if modelo_q:
        exacta = next((p for p in prendas if p["modelo"] == modelo_q and (not talla_q or p["talla"] == talla_q)), None)
        por_modelo = next((p for p in prendas if p["modelo"] == modelo_q), None)
        prenda_actual = exacta or por_modelo or prendas[0]

    form_data = form_data or {}
    form_cliente_nombre = form_data.get("cliente_nombre", "Ana Sofía López Hernández")
    form_cliente_telefono = form_data.get("cliente_telefono", "777 123 4567")
    form_cliente_correo = form_data.get("cliente_correo", "ana.lopez@correo.mx")
    default_ant = 350.00 if float(prenda_actual["precio"]) == 600.00 else float(prenda_actual["anticipo_minimo"])
    form_anticipo = form_data.get("monto_anticipo", f"{default_ant:.2f}")
    try:
        saldo_preview = max(0.0, float(prenda_actual["precio"]) - float(form_anticipo))
    except ValueError:
        saldo_preview = float(prenda_actual["precio"])

    tmpl = jinja_env.get_template("registrar_apartado.html")
    return tmpl.render(
        resumen=resumen,
        usuario_activo=usuario_activo,
        modelos_unicos=modelos_unicos,
        tallas_unicas=tallas_unicas,
        prenda_actual=prenda_actual,
        form_cliente_nombre=form_cliente_nombre,
        form_cliente_telefono=form_cliente_telefono,
        form_cliente_correo=form_cliente_correo,
        form_anticipo=form_anticipo,
        saldo_preview=saldo_preview,
        msg_exito=msg_exito,
        msg_error=msg_error,
        bienvenida=bienvenida,
    ).encode("utf-8")


def render_liquidar(
    user_id: int,
    q: str = "",
    folio_sel: int = None,
    msg_exito: str = "",
    msg_error: dict = None,
) -> bytes:
    resumen = obtener_resumen_bd()
    usuario_activo = obtener_usuario_sesion(user_id)
    apartados = listar_apartados_detallados(busqueda=q)

    apartado_sel = None
    if folio_sel:
        apartado_sel = next((a for a in apartados if int(a["id_apartado"]) == int(folio_sel)), None)
    if not apartado_sel and apartados:
        apartado_sel = apartados[0]

    tmpl = jinja_env.get_template("liquidar.html")
    return tmpl.render(
        resumen=resumen,
        usuario_activo=usuario_activo,
        q=q,
        apartados=apartados,
        apartado_sel=apartado_sel,
        msg_exito=msg_exito,
        msg_error=msg_error,
    ).encode("utf-8")


def render_vencimientos(
    user_id: int,
    folio_sel: int = None,
    msg_exito: dict = None,
    msg_info: dict = None,
) -> bytes:
    resumen = obtener_resumen_bd()
    usuario_activo = obtener_usuario_sesion(user_id)
    todos = listar_apartados_detallados()
    fecha_ref = date(2026, 10, 22)

    vencidos = []
    for a in todos:
        if a["estado"] == "Vencido":
            try:
                f_lim = date.fromisoformat(str(a["fecha_limite"]))
                dias = max(1, (fecha_ref - f_lim).days)
            except Exception:
                dias = 5
            a["dias_exceso"] = dias
            vencidos.append(a)

    vencido_sel = None
    if folio_sel:
        vencido_sel = next((v for v in vencidos if int(v["id_apartado"]) == int(folio_sel)), None)
    if not vencido_sel and vencidos:
        vencido_sel = vencidos[0]

    tmpl = jinja_env.get_template("vencimientos.html")
    return tmpl.render(
        resumen=resumen,
        usuario_activo=usuario_activo,
        vencidos=vencidos,
        vencido_sel=vencido_sel,
        msg_exito=msg_exito,
        msg_info=msg_info,
    ).encode("utf-8")


class UniformaHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format_str, *args):
        print(f"INFO:     {self.address_string()} - \"{format_str % args}\"")

    def _send_html(self, body: bytes):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _redirect(self, location: str):
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path.startswith("/static/styles.css"):
            css_file = BASE_DIR / "app" / "static" / "styles.css"
            data = css_file.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/css; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        try:
            user_id = int(qs.get("user_id", [str(DEFAULT_USER_ID)])[0])
        except ValueError:
            user_id = DEFAULT_USER_ID

        if path in ("/", "/login", "/logout"):
            u = obtener_usuario_sesion(user_id) if "user_id" in qs else None
            self._send_html(render_login(qs, usuario_activo=u))
            return

        if path in ("/registrar-apartado", "/conexion-bd"):
            modelo_q = unquote(qs.get("modelo", [""])[0])
            talla_q = unquote(qs.get("talla", [""])[0])
            bienvenida = qs.get("bienvenida", [""])[0] == "1"
            self._send_html(
                render_registrar_apartado(
                    user_id,
                    modelo_q=modelo_q,
                    talla_q=talla_q,
                    bienvenida=bienvenida,
                )
            )
            return

        if path == "/liquidar":
            q = unquote(qs.get("q", ["Ana Sofía López"])[0]) if "q" in qs else "Ana Sofía López"
            folio = int(qs["folio"][0]) if "folio" in qs and qs["folio"][0].isdigit() else None
            self._send_html(render_liquidar(user_id, q=q, folio_sel=folio))
            return

        if path == "/vencimientos":
            folio = int(qs["folio"][0]) if "folio" in qs and qs["folio"][0].isdigit() else None
            self._send_html(render_vencimientos(user_id, folio_sel=folio))
            return

        self._send_html(render_login(qs))

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(length).decode("utf-8", errors="ignore")
        form = {k: v[0] for k, v in parse_qs(raw_body, keep_blank_values=True).items()}
        try:
            user_id = int(form.get("user_id", DEFAULT_USER_ID))
        except ValueError:
            user_id = DEFAULT_USER_ID

        # 1. PANTALLA 0: INICIAR SESIÓN
        if path == "/login":
            id_in = form.get("id_usuario", "").strip()
            nombre_in = form.get("nombre", "").strip()
            rol_in = form.get("rol", "Vendedor").strip()

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
                self._send_html(
                    render_login(
                        {},
                        msg_exito=False,
                        msg_error=err,
                        usuario_activo={"id_usuario": id_in, "nombre": nombre_in, "rol": rol_in},
                    )
                )
                return

            # Redirigir por defecto a la primera pantalla operativa: Registrar apartado
            self._redirect(f"/registrar-apartado?user_id={row['id_usuario']}&bienvenida=1")
            return

        # 2. PANTALLA 1: REGISTRAR APARTADO / PEDIDO ESPECIAL
        if path in ("/registrar-apartado", "/conexion-bd/registrar-apartado"):
            id_prenda = int(form.get("id_prenda", 10))
            cliente_nombre = form.get("cliente_nombre", "Ana Sofía López Hernández").strip()
            cliente_telefono = form.get("cliente_telefono", "777 123 4567").strip()
            cliente_correo = form.get("cliente_correo", "").strip() or None
            accion = form.get("accion", "apartado")
            try:
                monto_anticipo = float(form.get("monto_anticipo", "0"))
            except ValueError:
                monto_anticipo = 0.0

            db = get_db_connection()
            try:
                prenda = db.query_one(
                    "SELECT id_prenda, modelo, talla, precio, existencia, fecha_estimada FROM PRENDA WHERE id_prenda = ?;",
                    (id_prenda,),
                )
                if not cliente_nombre or not cliente_telefono:
                    err = {
                        "titulo": "Datos incompletos",
                        "detalle": "Capture el nombre completo y el teléfono del cliente antes de registrar el apartado.",
                    }
                    self._send_html(
                        render_registrar_apartado(
                            user_id,
                            modelo_q=prenda["modelo"],
                            talla_q=prenda["talla"],
                            msg_error=err,
                            form_data=form,
                        )
                    )
                    return

                precio_actual = float(prenda["precio"])
                minimo_50 = float(calcular_anticipo_minimo(precio_actual))
                if Decimal(str(monto_anticipo)) < Decimal(str(minimo_50)):
                    err = {
                        "titulo": "Anticipo insuficiente",
                        "detalle": f"El anticipo debe cubrir al menos el 50% del precio de la prenda (${minimo_50:.2f}). Verifique el monto e intente nuevamente.",
                    }
                    self._send_html(
                        render_registrar_apartado(
                            user_id,
                            modelo_q=prenda["modelo"],
                            talla_q=prenda["talla"],
                            msg_error=err,
                            form_data=form,
                        )
                    )
                    return

                cli = db.query_one(
                    "SELECT id_cliente FROM CLIENTE WHERE LOWER(nombre) = LOWER(?);",
                    (cliente_nombre,),
                )
                if cli:
                    id_cliente = int(cli["id_cliente"])
                else:
                    id_cliente = int(db.query_one("SELECT COALESCE(MAX(id_cliente), 0) + 1 AS next_c FROM CLIENTE;")["next_c"])
                    db.execute(
                        "INSERT INTO CLIENTE (id_cliente, nombre, telefono, correo) VALUES (?, ?, ?, ?);",
                        (id_cliente, cliente_nombre, cliente_telefono, cliente_correo),
                    )

                nuevo_folio = int(db.query_one("SELECT COALESCE(MAX(id_apartado), 100) + 1 AS next_id FROM APARTADO;")["next_id"])
                nuevo_pago_id = int(db.query_one("SELECT COALESCE(MAX(id_pago), 500) + 1 AS next_p FROM PAGO;")["next_p"])

                hoy = date(2026, 10, 22)
                limite = hoy + timedelta(days=30)

                if int(prenda["existencia"]) > 0 and accion != "especial":
                    tipo_op = "Apartado"
                    estado_op = "Disponible"
                    db.execute(
                        "UPDATE PRENDA SET existencia = existencia - 1, apartadas = apartadas + 1 WHERE id_prenda = ?;",
                        (id_prenda,),
                    )
                else:
                    tipo_op = "Pedido especial"
                    estado_op = "En espera"
                    db.execute("UPDATE PRENDA SET apartadas = apartadas + 1 WHERE id_prenda = ?;", (id_prenda,))

                db.execute(
                    """
                    INSERT INTO APARTADO (
                        id_apartado, tipo, fecha_registro, fecha_limite,
                        precio_aplicado, estado, id_cliente, id_prenda, id_usuario
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (
                        nuevo_folio,
                        tipo_op,
                        hoy.isoformat(),
                        limite.isoformat(),
                        precio_actual,
                        estado_op,
                        id_cliente,
                        id_prenda,
                        user_id,
                    ),
                )
                db.execute(
                    "INSERT INTO PAGO (id_pago, monto, fecha, tipo, id_apartado) VALUES (?, ?, ?, 'Anticipo', ?);",
                    (nuevo_pago_id, monto_anticipo, hoy.isoformat(), nuevo_folio),
                )
                db.commit()

                saldo_rest = max(0.0, precio_actual - monto_anticipo)
                exito = {
                    "titulo": f"{tipo_op} registrado correctamente",
                    "folio": nuevo_folio,
                    "prenda": f"{prenda['modelo']} (Talla {prenda['talla']})",
                    "estado": estado_op,
                    "fecha_limite": limite.strftime("%d/%m/%Y"),
                    "saldo": saldo_rest,
                }
                self._send_html(
                    render_registrar_apartado(
                        user_id,
                        modelo_q=prenda["modelo"],
                        talla_q=prenda["talla"],
                        msg_exito=exito,
                        form_data=form,
                    )
                )
                return
            finally:
                db.close()

        # 3. PANTALLA 2: LIQUIDAR Y ENTREGAR PEDIDO
        if path == "/liquidar":
            id_apartado = int(form.get("id_apartado", 104))
            q = form.get("q", "")
            try:
                pago_recibido = float(form.get("pago_recibido", "0"))
            except ValueError:
                pago_recibido = 0.0

            db = get_db_connection()
            try:
                ap = db.query_one(
                    """
                    SELECT a.id_apartado, a.precio_aplicado, a.estado, a.id_prenda,
                           COALESCE(SUM(p.monto), 0.00) AS abonado
                    FROM APARTADO a
                    LEFT JOIN PAGO p ON a.id_apartado = p.id_apartado
                    WHERE a.id_apartado = ?
                    GROUP BY a.id_apartado, a.precio_aplicado, a.estado, a.id_prenda;
                    """,
                    (id_apartado,),
                )
                if ap["estado"] == "Vencido":
                    err = {
                        "titulo": "Apartado vencido",
                        "detalle": "El apartado superó los 30 días de resguardo. Solicite autorización al Gerente en el módulo de Vencimientos.",
                    }
                    self._send_html(render_liquidar(user_id, q=q, folio_sel=id_apartado, msg_error=err))
                    return

                if ap["estado"] == "En espera":
                    err = {
                        "titulo": "Pedido en espera",
                        "detalle": "La prenda aún no llega al almacén; no puede entregarse hasta que se registre su entrada.",
                    }
                    self._send_html(render_liquidar(user_id, q=q, folio_sel=id_apartado, msg_error=err))
                    return

                saldo = float(Decimal(str(ap["precio_aplicado"])) - Decimal(str(ap["abonado"])))
                if Decimal(str(pago_recibido)) < Decimal(str(saldo)):
                    faltante = float(Decimal(str(saldo)) - Decimal(str(pago_recibido)))
                    err = {
                        "titulo": "Pago incompleto",
                        "detalle": f"El monto recibido (${pago_recibido:.2f}) no cubre el saldo pendiente (${saldo:.2f}). Faltan ${faltante:.2f}.",
                    }
                    self._send_html(render_liquidar(user_id, q=q, folio_sel=id_apartado, msg_error=err))
                    return

                nuevo_pago_id = int(db.query_one("SELECT COALESCE(MAX(id_pago), 500) + 1 AS next_p FROM PAGO;")["next_p"])
                hoy = date(2026, 11, 3).isoformat()
                if saldo > 0:
                    db.execute(
                        "INSERT INTO PAGO (id_pago, monto, fecha, tipo, id_apartado) VALUES (?, ?, ?, 'Liquidacion', ?);",
                        (nuevo_pago_id, saldo, hoy, id_apartado),
                    )
                db.execute("UPDATE APARTADO SET estado = 'Entregado' WHERE id_apartado = ?;", (id_apartado,))
                db.execute(
                    "UPDATE PRENDA SET apartadas = CASE WHEN apartadas > 0 THEN apartadas - 1 ELSE 0 END WHERE id_prenda = ?;",
                    (ap["id_prenda"],),
                )
                db.commit()
                msg_ok = f"Folio #{id_apartado} pagado en su totalidad (${float(ap['precio_aplicado']):.2f}). Estado: Entregado."
                self._send_html(render_liquidar(user_id, q=q, folio_sel=id_apartado, msg_exito=msg_ok))
                return
            finally:
                db.close()

        # 4. PANTALLA 3: VENCIMIENTOS DE APARTADOS 30 DÍAS Y CANCELACIÓN
        if path == "/vencimientos":
            id_apartado = int(form.get("id_apartado", 87))
            accion = form.get("accion", "cancelar")

            if accion == "conservar":
                info = {
                    "titulo": "Apartado conservado",
                    "detalle": f"El apartado #{id_apartado:03d} se mantiene vigente sin cambios en el inventario.",
                }
                self._send_html(render_vencimientos(user_id, folio_sel=id_apartado, msg_info=info))
                return

            db = get_db_connection()
            try:
                ap = db.query_one(
                    """
                    SELECT a.id_apartado, a.id_prenda, p.modelo, p.talla
                    FROM APARTADO a
                    INNER JOIN PRENDA p ON a.id_prenda = p.id_prenda
                    WHERE a.id_apartado = ?;
                    """,
                    (id_apartado,),
                )
                db.execute("UPDATE APARTADO SET estado = 'Cancelado' WHERE id_apartado = ?;", (id_apartado,))
                db.execute(
                    """
                    UPDATE PRENDA
                    SET apartadas = CASE WHEN apartadas > 0 THEN apartadas - 1 ELSE 0 END,
                        existencia = existencia + 1
                    WHERE id_prenda = ?;
                    """,
                    (ap["id_prenda"],),
                )
                db.commit()
                exito = {
                    "titulo": "Apartado cancelado y prenda liberada",
                    "detalle": f"El apartado #{id_apartado:03d} cambió a estado Cancelado. Se reingresó 1 {ap['modelo']} (Talla {ap['talla']}) a la existencia disponible.",
                }
                self._send_html(render_vencimientos(user_id, msg_exito=exito))
                return
            finally:
                db.close()

        self._send_html(render_login({}))


if __name__ == "__main__":
    print(f"INFO:     Iniciando {APP_NAME} ({APP_VERSION}) - 4 Pantallas Prototipo")
    print(f"INFO:     Abra en su navegador: http://{APP_HOST}:{APP_PORT}/login")
    server = HTTPServer((APP_HOST, APP_PORT), UniformaHTTPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nINFO:     Servidor detenido.")
