##
## @file mcpDashboards.py
##
## Crea dashboards en Superset via REST API.
## Dashboards: Histórico de Créditos, Predicciones, KPIs, Análisis Dimensional.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

import json
import sys
from pathlib import Path

import psycopg2
import requests

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

SUPERSET_URL = "http://localhost:8088"
SUPERSET_USER = "admin"
SUPERSET_PASS = "admin123"

_session = None


def _get_session():
    """Retorna una sesión requests autenticada con JWT + CSRF."""
    global _session
    if _session:
        return _session

    _session = requests.Session()
    resp = _session.post(
        f"{SUPERSET_URL}/api/v1/security/login",
        json={"username": SUPERSET_USER, "password": SUPERSET_PASS,
              "provider": "db", "refresh": True},
    )
    resp.raise_for_status()
    token = resp.json()["access_token"]
    _session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    })

    csrf_resp = _session.get(f"{SUPERSET_URL}/api/v1/security/csrf_token/")
    if csrf_resp.ok:
        csrf = csrf_resp.json().get("result")
        if csrf:
            _session.headers["X-CSRFToken"] = csrf

    return _session


def limpiar_superset():
    """Elimina TODOS los dashboards y charts existentes."""
    session = _get_session()

    # Eliminar charts
    resp = session.get(f"{SUPERSET_URL}/api/v1/chart/", params={"q": json.dumps({"page_size": 200})})
    if resp.ok:
        charts = resp.json().get("result", [])
        for c in charts:
            session.delete(f"{SUPERSET_URL}/api/v1/chart/{c['id']}")
        print(f"  Charts eliminados: {len(charts)}")

    # Eliminar dashboards
    resp = session.get(f"{SUPERSET_URL}/api/v1/dashboard/", params={"q": json.dumps({"page_size": 200})})
    if resp.ok:
        dashboards = resp.json().get("result", [])
        for d in dashboards:
            session.delete(f"{SUPERSET_URL}/api/v1/dashboard/{d['id']}")
        print(f"  Dashboards eliminados: {len(dashboards)}")


def crear_vistas(conn):
    """Crea vistas SQL que hacen JOIN entre fact y dimensiones."""
    cur = conn.cursor()

    cur.execute("""
        CREATE OR REPLACE VIEW v_creditos AS
        SELECT
            f.id_tiempo, f.id_riesgo, f.id_sector, f.id_sucursal,
            t.mes, t.anio, t.trimestre, t.nombre_mes,
            r.codigo_riesgo, r.descripcion AS riesgo,
            s.codigo_sector, s.descripcion AS sector,
            su.codigo_sucursal,
            f.num_creditos, f.monto_total, f.monto_promedio,
            f.tot_dias_mora_promedio, f.tot_num_moras_promedio,
            f.tasa_mora_90, f.tasa_judicial, f.tasa_cierre,
            f.total_gestion_cobro, f.total_costo_judicial,
            f.tasa_interes_promedio, f.saldo_promedio,
            f.creditos_cerrados, f.num_clientes_unicos,
            f.creditos_por_cliente, f.plazo_promedio,
            f.desviacion_montos, f.coef_variacion_montos,
            f.tasa_crecimiento_creditos, f.tasa_crecimiento_monto,
            f.crisis_flag, f.bloque_id
        FROM fact_creditos_mensual f
        JOIN dim_tiempo t ON f.id_tiempo = t.id_tiempo
        JOIN dim_riesgo r ON f.id_riesgo = r.id_riesgo
        JOIN dim_sector s ON f.id_sector = s.id_sector
        JOIN dim_sucursal su ON f.id_sucursal = su.id_sucursal
    """)
    print("  Vista v_creditos creada.")

    cur.execute("""
        CREATE OR REPLACE VIEW v_predicciones AS
        SELECT
            p.id_tiempo, p.id_riesgo, p.id_sector, p.id_sucursal,
            t.mes AS mes_prediccion, t.anio,
            r.codigo_riesgo, r.descripcion AS riesgo,
            s.codigo_sector, s.descripcion AS sector,
            su.codigo_sucursal,
            p.bloque_id,
            p.prob_h01, p.prob_h02, p.prob_h03, p.prob_h04,
            p.prob_h05, p.prob_h06, p.prob_h07, p.prob_h08,
            p.prob_h09, p.prob_h10, p.prob_h11, p.prob_h12,
            p.prob_h13, p.prob_h14, p.prob_h15, p.prob_h16,
            p.prob_h17, p.prob_h18,
            p.pred_h01, p.pred_h02, p.pred_h03, p.pred_h04,
            p.pred_h05, p.pred_h06, p.pred_h07, p.pred_h08,
            p.pred_h09, p.pred_h10, p.pred_h11, p.pred_h12,
            p.pred_h13, p.pred_h14, p.pred_h15, p.pred_h16,
            p.pred_h17, p.pred_h18,
            p.prob_media, p.pred_media, p.crisis_count, p.fecha_ejecucion
        FROM fact_predicciones p
        JOIN dim_tiempo t ON p.id_tiempo = t.id_tiempo
        JOIN dim_riesgo r ON p.id_riesgo = r.id_riesgo
        JOIN dim_sector s ON p.id_sector = s.id_sector
        JOIN dim_sucursal su ON p.id_sucursal = su.id_sucursal
    """)
    print("  Vista v_predicciones creada.")

    conn.commit()
    cur.close()


def buscar_dataset_id(nombre):
    """Busca el ID de un dataset por nombre."""
    resp = _get_session().get(
        f"{SUPERSET_URL}/api/v1/dataset/",
        params={"q": json.dumps({"filters": [{"col": "table_name", "opr": "eq", "value": nombre}]})},
    )
    resp.raise_for_status()
    result = resp.json().get("result", [])
    if result:
        return result[0].get("id")
    return None


def refrescar_dataset(dataset_id):
    """Refresca el esquema de un dataset para que Superset reconozca las columnas."""
    resp = _get_session().put(f"{SUPERSET_URL}/api/v1/dataset/{dataset_id}/refresh")
    if resp.ok:
        print(f"    Dataset {dataset_id} refrescado.")
    else:
        print(f"    Warning: no se pudo refrescar dataset {dataset_id}: {resp.status_code}")


def crear_dataset_view(table_name):
    """Registra una vista como dataset en Superset."""
    resp = _get_session().post(
        f"{SUPERSET_URL}/api/v1/dataset/",
        json={"table_name": table_name, "schema": "public", "database": 1},
    )
    if resp.ok:
        ds_id = resp.json()["id"]
        print(f"  Dataset '{table_name}' registrado (ID: {ds_id})")
        return ds_id
    elif resp.status_code == 422:
        # Ya existe, buscarlo
        return buscar_dataset_id(table_name)
    else:
        print(f"  ERROR creando dataset '{table_name}': {resp.status_code} {resp.text[:200]}")
        return None


def crear_dashboard(titulo, slug):
    """Crea un dashboard y retorna su ID."""
    resp = _get_session().post(
        f"{SUPERSET_URL}/api/v1/dashboard/",
        json={"dashboard_title": titulo, "slug": slug, "published": True},
    )
    if not resp.ok:
        print(f"  ERROR {resp.status_code}: {resp.text[:200]}")
        resp.raise_for_status()
    dash_id = resp.json()["id"]
    print(f"  Dashboard '{titulo}' creado (ID: {dash_id})")
    return dash_id


def _build_position_json(chart_ids):
    """Genera position_json para acomodar charts en el grid."""
    position = {
        "DASHBOARD_VERSION_KEY": "v2",
        "ROOT_ID": {"type": "ROOT", "id": "ROOT_ID", "children": ["GRID_ID"]},
        "GRID_ID": {"type": "GRID", "id": "GRID_ID", "children": [], "parents": ["ROOT_ID"]},
        "HEADER_ID": {"type": "HEADER", "id": "HEADER_ID", "meta": {"text": "Dashboard"}},
    }

    for i, chart_id in enumerate(chart_ids):
        row_id = f"ROW-{i}"
        chart_key = f"CHART-{chart_id}"
        position["GRID_ID"]["children"].append(row_id)
        position[row_id] = {
            "type": "ROW", "id": row_id,
            "children": [chart_key],
            "parents": ["ROOT_ID", "GRID_ID"],
            "meta": {"background": "BACKGROUND_TRANSPARENT"},
        }
        position[chart_key] = {
            "type": "CHART", "id": chart_key,
            "children": [],
            "parents": ["ROOT_ID", "GRID_ID", row_id],
            "meta": {"width": 12, "height": 50, "chartId": chart_id},
        }

    return position


def actualizar_dashboard_layout(dash_id, chart_ids):
    """Actualiza el position_json de un dashboard con sus charts."""
    position = _build_position_json(chart_ids)
    resp = _get_session().put(
        f"{SUPERSET_URL}/api/v1/dashboard/{dash_id}",
        json={"position_json": json.dumps(position)},
    )
    if resp.ok:
        print(f"    Layout actualizado con {len(chart_ids)} charts")
    else:
        print(f"    Warning layout: {resp.status_code} {resp.text[:100]}")


def crear_chart(datasource_id, nombre, viz_type, params, dashboard_ids=None):
    """Crea un chart y retorna su ID."""
    # Defaults que Superset necesita para ejecutar la query
    params_full = {
        "time_range": "No filter",
        "row_limit": 10000,
        "order_desc": True,
        "url_params": {},
        "extra_form_data": {},
        "dashboards": [],
    }
    params_full.update(params)

    # Adaptar viz_type al formato correcto
    viz_type, params_full = _fix_viz_type(viz_type, params_full)

    # Guardar query_context para que Superset sepa cómo generar la SQL
    columns = []
    for col in params_full.get("columns", params_full.get("groupby", [])):
        if isinstance(col, dict):
            columns.append(col)
        else:
            columns.append(col)

    # Pie charts usan 'metric' (singular), otros usan 'metrics' (plural)
    metrics_for_query = params_full.get("metrics", [])
    if not metrics_for_query and params_full.get("metric"):
        metrics_for_query = [params_full["metric"]]

    query_context = {
        "datasource": {"id": datasource_id, "type": "table"},
        "force": False,
        "form_data": params_full,
        "queries": [{
            "columns": columns,
            "metrics": metrics_for_query,
            "time_range": params_full.get("time_range", "No filter"),
            "row_limit": params_full.get("row_limit", 10000),
            "order_desc": params_full.get("order_desc", True),
        }],
        "result_format": "json",
        "result_type": "full",
    }

    payload = {
        "slice_name": nombre,
        "datasource_id": datasource_id,
        "datasource_type": "table",
        "viz_type": viz_type,
        "params": json.dumps(params_full),
        "query_context": json.dumps(query_context),
    }
    if dashboard_ids:
        payload["dashboards"] = dashboard_ids

    resp = _get_session().post(f"{SUPERSET_URL}/api/v1/chart/", json=payload)
    if not resp.ok:
        print(f"    ERROR chart '{nombre}': {resp.status_code} {resp.text[:150]}")
        return None
    chart_id = resp.json()["id"]
    print(f"    Chart '{nombre}' creado (ID: {chart_id})")
    return chart_id


def _fix_viz_type(viz_type, params):
    """Adapta viz_type al formato correcto de Superset 6.1."""
    if viz_type == "bar":
        return "echarts_timeseries_bar", params
    if viz_type == "line":
        return "echarts_timeseries_line", params
    return viz_type, params


def listar_dashboards():
    """Lista dashboards existentes."""
    resp = _get_session().get(f"{SUPERSET_URL}/api/v1/dashboard/")
    resp.raise_for_status()
    dashboards = resp.json().get("result", [])
    print(f"\nDashboards existentes ({len(dashboards)}):")
    for d in dashboards:
        print(f"  - ID: {d.get('id')}, Titulo: {d.get('dashboard_title', 'N/A')}")
    return dashboards


# ── Dashboard 1: Histórico de Créditos ──────────────────────────

def crear_dashboard_historico_credidos(ds_id):
    print("\n=== Dashboard 1: Histórico de Créditos ===")
    dash_id = crear_dashboard("Histórico de Créditos", "historico-creditos")

    charts = [
        ("Evolución de Créditos", "line", {
            "x_axis": "mes", "time_grain_sqla": "P1M",
            "groupby": [],
            "metrics": [{"label": "total_creditos", "expressionType": "SQL", "sqlExpression": "SUM(num_creditos)"}],
        }),
        ("Monto Total Promedio", "line", {
            "x_axis": "mes", "time_grain_sqla": "P1M",
            "groupby": [],
            "metrics": [{"label": "monto_avg", "expressionType": "SQL", "sqlExpression": "AVG(monto_total)"}],
        }),
        ("Tasa de Mora 90+", "line", {
            "x_axis": "mes", "time_grain_sqla": "P1M",
            "groupby": [],
            "metrics": [{"label": "mora_avg", "expressionType": "SQL", "sqlExpression": "AVG(tasa_mora_90)"}],
        }),
        ("Crisis por Mes", "bar", {
            "x_axis": "mes", "time_grain_sqla": "P1M",
            "groupby": [],
            "metrics": [{"label": "crisis_count", "expressionType": "SQL", "sqlExpression": "SUM(crisis_flag)"}],
        }),
        ("Créditos por Sector", "pie", {
            "groupby": ["sector"],
            "metric": {"label": "total_creditos", "expressionType": "SQL", "sqlExpression": "SUM(num_creditos)"},
        }),
        ("Top Sucursales por Monto", "table", {
            "groupby": ["codigo_sucursal"],
            "metrics": [{"label": "monto_total", "expressionType": "SQL", "sqlExpression": "SUM(monto_total)"}],
            "row_limit": 10,
            "order_desc": True,
        }),
    ]

    chart_ids = []
    for nombre, viz, params in charts:
        cid = crear_chart(ds_id, nombre, viz, params, [dash_id])
        if cid:
            chart_ids.append(cid)
    actualizar_dashboard_layout(dash_id, chart_ids)


# ── Dashboard 2: Predicciones ───────────────────────────────────

def crear_dashboard_predicciones(ds_id):
    print("\n=== Dashboard 2: Predicciones ===")
    dash_id = crear_dashboard("Predicciones Crediticias", "predicciones-crediticias")

    charts = [
        ("Probabilidad Promedio de Crisis", "line", {
            "x_axis": "mes_prediccion", "time_grain_sqla": "P1M",
            "groupby": [],
            "metrics": [{"label": "prob_avg", "expressionType": "SQL", "sqlExpression": "AVG(prob_media)"}],
        }),
        ("Predicciones de Crisis por Mes", "bar", {
            "x_axis": "mes_prediccion", "time_grain_sqla": "P1M",
            "groupby": [],
            "metrics": [{"label": "n_crisis", "expressionType": "SQL", "sqlExpression": "SUM(pred_media)"}],
        }),
        ("Top Bloques en Riesgo", "table", {
            "columns": ["bloque_id"],
            "metrics": [{"label": "prob_avg", "expressionType": "SQL", "sqlExpression": "AVG(prob_media)"}],
            "row_limit": 20,
        }),
    ]

    chart_ids = []
    for nombre, viz, params in charts:
        cid = crear_chart(ds_id, nombre, viz, params, [dash_id])
        if cid:
            chart_ids.append(cid)
    actualizar_dashboard_layout(dash_id, chart_ids)


# ── Dashboard 3: KPIs Generales ─────────────────────────────────

def crear_dashboard_kpis(ds_credito_id, ds_pred_id):
    print("\n=== Dashboard 3: KPIs Generales ===")
    dash_id = crear_dashboard("KPIs Generales", "kpis-generales")

    charts = [
        (ds_credito_id, "Total Créditos", "big_number_total", {
            "metric": {"label": "total", "expressionType": "SQL", "sqlExpression": "COUNT(*)"},
        }),
        (ds_credito_id, "Créditos con Crisis", "big_number_total", {
            "metric": {"label": "crisis", "expressionType": "SQL", "sqlExpression": "SUM(crisis_flag)"},
        }),
        (ds_pred_id, "Total Predicciones", "big_number_total", {
            "metric": {"label": "total", "expressionType": "SQL", "sqlExpression": "COUNT(*)"},
        }),
        (ds_pred_id, "Probabilidad Promedio", "big_number_total", {
            "metric": {"label": "prob_avg", "expressionType": "SQL",
                       "sqlExpression": "ROUND(AVG(prob_media)::numeric, 4)"},
        }),
    ]

    chart_ids = []
    for ds_id_chart, nombre, viz, params in charts:
        cid = crear_chart(ds_id_chart, nombre, viz, params, [dash_id])
        if cid:
            chart_ids.append(cid)
    actualizar_dashboard_layout(dash_id, chart_ids)


# ── Dashboard 4: Análisis Dimensional ───────────────────────────

def crear_dashboard_analisis_dimensional(ds_id):
    print("\n=== Dashboard 4: Análisis Dimensional ===")
    dash_id = crear_dashboard("Análisis Dimensional", "analisis-dimensional")

    charts = [
        ("Créditos por Riesgo", "table", {
            "groupby": ["riesgo"],
            "metrics": [{"label": "total_creditos", "expressionType": "SQL", "sqlExpression": "SUM(num_creditos)"}],
            "order_desc": True,
        }),
        ("Mora por Sector", "table", {
            "groupby": ["sector"],
            "metrics": [{"label": "mora_avg", "expressionType": "SQL", "sqlExpression": "AVG(tasa_mora_90)"}],
            "order_desc": True,
        }),
        ("Evolución por Riesgo", "line", {
            "x_axis": "mes", "time_grain_sqla": "P1M",
            "groupby": ["riesgo"],
            "metrics": [{"label": "total_creditos", "expressionType": "SQL", "sqlExpression": "SUM(num_creditos)"}],
        }),
    ]

    chart_ids = []
    for nombre, viz, params in charts:
        cid = crear_chart(ds_id, nombre, viz, params, [dash_id])
        if cid:
            chart_ids.append(cid)
    actualizar_dashboard_layout(dash_id, chart_ids)


# ── Main ─────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("CREACIÓN DE DASHBOARDS EN SUPERSET VIA REST API")
    print("=" * 60)

    # 0. Limpiar todo lo existente
    print("\n--- Limpiando Superset ---")
    limpiar_superset()

    # 1. Crear vistas SQL (v_creditos, v_predicciones)
    print("\n--- Creando vistas SQL ---")
    conn = psycopg2.connect(
        host="192.168.0.97", port=5432,
        dbname="postgres_db", user="postgres_usr", password="admin123",
    )
    conn.autocommit = True
    crear_vistas(conn)
    conn.close()

    # 2. Buscar/crear datasets para las vistas
    print("\n--- Configurando datasets ---")
    ds_creditos = buscar_dataset_id("v_creditos")
    if not ds_creditos:
        ds_creditos = crear_dataset_view("v_creditos")
    if ds_creditos:
        refrescar_dataset(ds_creditos)
        print(f"  v_creditos → ID: {ds_creditos}")

    ds_predicciones = buscar_dataset_id("v_predicciones")
    if not ds_predicciones:
        ds_predicciones = crear_dataset_view("v_predicciones")
    if ds_predicciones:
        refrescar_dataset(ds_predicciones)
        print(f"  v_predicciones → ID: {ds_predicciones}")

    if not ds_creditos or not ds_predicciones:
        print("\nNo se pudieron configurar los datasets.")
        return

    # 3. Crear dashboards
    crear_dashboard_historico_credidos(ds_creditos)
    crear_dashboard_predicciones(ds_predicciones)
    crear_dashboard_kpis(ds_creditos, ds_predicciones)
    crear_dashboard_analisis_dimensional(ds_creditos)

    # 4. Verificar
    print("\n" + "=" * 60)
    listar_dashboards()
    print("\nAbrir http://localhost:8088 para ver los dashboards.")
    print("=" * 60)


if __name__ == "__main__":
    main()
