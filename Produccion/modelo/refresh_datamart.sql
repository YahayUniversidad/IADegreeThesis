-- ============================================================================
-- refresh_datamart.sql
-- Refresca las dimensiones y la tabla de hechos histórica (fact_creditos_mensual).
-- Diseñado para ejecutarse periódicamente (vía cron / pg_cron) de forma idempotente.
-- 
-- Ejecutar con:
--   psql -h 192.168.0.97 -U usuario -d analisis_db -f refresh_datamart.sql
-- ============================================================================

BEGIN;

-- --------------------------------------------------------------------------
-- 1. REFRESCAR DIMENSIONES (solo inserta nuevos valores)
-- --------------------------------------------------------------------------

INSERT INTO dim_tiempo (mes, anio, trimestre, mes_del_anio, nombre_mes)
SELECT DISTINCT
    DATE_TRUNC('month', fecha_credito)::DATE          AS mes,
    EXTRACT(YEAR FROM fecha_credito)::INTEGER          AS anio,
    EXTRACT(QUARTER FROM fecha_credito)::INTEGER       AS trimestre,
    EXTRACT(MONTH FROM fecha_credito)::INTEGER         AS mes_del_anio,
    TO_CHAR(DATE_TRUNC('month', fecha_credito), 'TMMonth') AS nombre_mes
FROM CABECERA_PRESTAMOS
WHERE fecha_credito >= '2015-07-01'
ON CONFLICT (mes) DO NOTHING;

INSERT INTO dim_riesgo (codigo_riesgo, descripcion)
SELECT DISTINCT
    COALESCE(codigo_riesgo, 'SIN_RIESGO'),
    COALESCE(codigo_riesgo, 'SIN_RIESGO')
FROM CABECERA_PRESTAMOS
ON CONFLICT (codigo_riesgo) DO NOTHING;

INSERT INTO dim_sector (codigo_sector, descripcion)
SELECT DISTINCT
    COALESCE(act_economica_nvl1, 'SIN_SECTOR'),
    COALESCE(act_economica_nvl1, 'SIN_SECTOR')
FROM CABECERA_PRESTAMOS
ON CONFLICT (codigo_sector) DO NOTHING;

INSERT INTO dim_sucursal (codigo_sucursal, codigo_provincia)
SELECT DISTINCT
    codigo_sucursal::INTEGER,
    codigo_provincia::INTEGER
FROM CABECERA_PRESTAMOS
ON CONFLICT (codigo_sucursal, codigo_provincia) DO NOTHING;

-- --------------------------------------------------------------------------
-- 2. REFRESCAR FACT_CREDITOS_MENSUAL
--    Replica la lógica de query_bloques_18m + calcular_crisis_flag_mejorado
--    Usa upsert (ON CONFLICT) para ser idempotente
-- --------------------------------------------------------------------------

INSERT INTO fact_creditos_mensual (
    id_tiempo, id_riesgo, id_sector, id_sucursal,
    num_creditos, monto_total, monto_promedio,
    dias_mora_promedio, num_moras_promedio,
    tasa_mora_90, tasa_judicial, tasa_cierre,
    total_gestion_cobro, total_costo_judicial,
    tasa_interes_promedio, saldo_promedio,
    creditos_cerrados, num_clientes_unicos,
    creditos_por_cliente, plazo_promedio,
    desviacion_montos, coef_variacion_montos,
    antiguedad_promedio_meses,
    tasa_crecimiento_creditos, tasa_crecimiento_monto,
    crisis_flag, bloque_id
)
WITH datos_mensuales AS (
    SELECT 
        DATE_TRUNC('month', cp.fecha_credito)::DATE  AS mes,
        COALESCE(cp.codigo_riesgo, 'SIN_RIESGO')     AS riesgo,
        COALESCE(cp.act_economica_nvl1, 'SIN_SECTOR') AS sector,
        cp.codigo_provincia,
        cp.codigo_sucursal,
        COUNT(*)                                     AS num_creditos,
        SUM(cp.monto_acreditado)                     AS monto_total,
        AVG(cp.monto_acreditado)                     AS monto_promedio,
        AVG(cp.tot_dias_mora)                        AS dias_mora_promedio,
        AVG(cp.tot_num_moras)                        AS num_moras_promedio,
        COUNT(CASE WHEN cp.tot_dias_mora > 90 THEN 1 END)  AS creditos_mora_90,
        COUNT(CASE WHEN cp.judicial = 'S' THEN 1 END)      AS creditos_judiciales,
        SUM(cp.gestion_cobro)                        AS total_gestion_cobro,
        SUM(cp.costo_judicial)                       AS total_costo_judicial,
        AVG(cp.tasa_interes)                         AS tasa_interes_promedio,
        AVG(COALESCE(cp.saldo_capital, 0))           AS saldo_promedio,
        COUNT(CASE WHEN cp.estado_cred IN ('C', 'L') THEN 1 END) AS creditos_cerrados,
        COUNT(DISTINCT cp.codigo_socio)              AS num_clientes_unicos,
        EXTRACT(MONTH FROM cp.fecha_credito)         AS mes_del_ano,
        AVG(cp.num_cuotas)                           AS plazo_promedio,
        STDDEV(cp.monto_acreditado)                  AS desviacion_montos,
        AVG(EXTRACT(MONTH FROM AGE(CURRENT_DATE, cp.fecha_credito))) AS antiguedad_promedio_meses
    FROM CABECERA_PRESTAMOS cp
    WHERE cp.fecha_credito >= '2015-07-01' 
    GROUP BY 
        DATE_TRUNC('month', cp.fecha_credito), 
        cp.codigo_riesgo, 
        cp.act_economica_nvl1, 
        cp.codigo_provincia, 
        cp.codigo_sucursal, 
        EXTRACT(MONTH FROM cp.fecha_credito)
),
datos_con_lag AS (
    SELECT 
        *,
        LAG(num_creditos, 1) OVER (
            PARTITION BY riesgo, sector ORDER BY mes
        ) AS num_creditos_mes_anterior,
        LAG(monto_total, 1) OVER (
            PARTITION BY riesgo, sector ORDER BY mes
        ) AS monto_mes_anterior
    FROM datos_mensuales
),
datos_enriquecidos AS (
    SELECT 
        mes,
        riesgo,
        sector,
        codigo_provincia,
        codigo_sucursal,
        num_creditos,
        monto_total,
        monto_promedio,
        dias_mora_promedio,
        num_moras_promedio,
        ROUND((creditos_mora_90::NUMERIC / NULLIF(num_creditos, 0)) * 100, 2)    AS tasa_mora_90,
        ROUND((creditos_judiciales::NUMERIC / NULLIF(num_creditos, 0)) * 100, 2)  AS tasa_judicial,
        ROUND((creditos_cerrados::NUMERIC / NULLIF(num_creditos, 0)) * 100, 2)    AS tasa_cierre,
        total_gestion_cobro,
        total_costo_judicial,
        tasa_interes_promedio,
        saldo_promedio,
        creditos_cerrados,
        num_clientes_unicos,
        ROUND(num_creditos::NUMERIC / NULLIF(num_clientes_unicos, 0), 2)           AS creditos_por_cliente,
        mes_del_ano,
        ROUND(plazo_promedio::NUMERIC, 2)                                          AS plazo_promedio,
        ROUND(COALESCE(desviacion_montos, 0)::NUMERIC, 2)                          AS desviacion_montos,
        ROUND((COALESCE(desviacion_montos, 0)::NUMERIC / NULLIF(monto_promedio, 0)) * 100, 2) AS coef_variacion_montos,
        ROUND(antiguedad_promedio_meses::NUMERIC, 2)                               AS antiguedad_promedio_meses,
        num_creditos_mes_anterior,
        ROUND(
            ((num_creditos::NUMERIC - COALESCE(num_creditos_mes_anterior, num_creditos)) 
             / NULLIF(num_creditos_mes_anterior, 0)) * 100, 2
        )                                                                            AS tasa_crecimiento_creditos,
        monto_mes_anterior,
        ROUND(
            ((monto_total::NUMERIC - COALESCE(monto_mes_anterior, monto_total)) 
             / NULLIF(monto_mes_anterior, 0)) * 100, 2
        )                                                                            AS tasa_crecimiento_monto
    FROM datos_con_lag
    WHERE num_creditos >= 10
),
-- Cálculo del crisis_flag en SQL (equivalente a calcular_crisis_flag_mejorado en Python)
datos_con_crisis AS (
    SELECT *,
        CASE 
            WHEN (
                CASE WHEN tasa_mora_90 > 15 THEN 3 ELSE 0 END +
                CASE WHEN tasa_judicial > 5 THEN 2 ELSE 0 END +
                CASE WHEN dias_mora_promedio > 45 THEN 2 ELSE 0 END +
                CASE WHEN total_gestion_cobro > monto_total * 0.08 THEN 1 ELSE 0 END +
                CASE WHEN creditos_cerrados::NUMERIC / NULLIF(num_creditos, 0) > 0.3 THEN 1 ELSE 0 END +
                CASE WHEN num_creditos < 50 AND tasa_mora_90 > 20 THEN 2 ELSE 0 END +
                CASE WHEN creditos_por_cliente > 3 THEN 1 ELSE 0 END +
                CASE WHEN tasa_crecimiento_creditos < -20 THEN 1 ELSE 0 END +
                CASE WHEN coef_variacion_montos > 100 THEN 1 ELSE 0 END +
                CASE WHEN plazo_promedio > 36 AND tasa_mora_90 > 10 THEN 1 ELSE 0 END +
                CASE WHEN antiguedad_promedio_meses > 60 AND tasa_judicial > 3 THEN 1 ELSE 0 END
            ) >= 4 THEN 1 
            ELSE 0 
        END AS crisis_flag
    FROM datos_enriquecidos
)
SELECT
    dt.id_tiempo,
    dr.id_riesgo,
    ds.id_sector,
    dsu.id_sucursal,
    d.num_creditos,
    d.monto_total,
    d.monto_promedio,
    d.dias_mora_promedio,
    d.num_moras_promedio,
    d.tasa_mora_90,
    d.tasa_judicial,
    d.tasa_cierre,
    d.total_gestion_cobro,
    d.total_costo_judicial,
    d.tasa_interes_promedio,
    d.saldo_promedio,
    d.creditos_cerrados,
    d.num_clientes_unicos,
    d.creditos_por_cliente,
    d.plazo_promedio,
    d.desviacion_montos,
    d.coef_variacion_montos,
    d.antiguedad_promedio_meses,
    d.tasa_crecimiento_creditos,
    d.tasa_crecimiento_monto,
    d.crisis_flag,
    d.riesgo || '_' || d.sector || '_' || d.codigo_sucursal::VARCHAR AS bloque_id
FROM datos_con_crisis d
JOIN dim_tiempo dt ON dt.mes = d.mes
JOIN dim_riesgo dr ON dr.codigo_riesgo = d.riesgo
JOIN dim_sector ds ON ds.codigo_sector = d.sector
JOIN dim_sucursal dsu 
    ON dsu.codigo_sucursal = d.codigo_sucursal::INTEGER 
    AND dsu.codigo_provincia IS NOT DISTINCT FROM d.codigo_provincia::INTEGER
ON CONFLICT (id_tiempo, id_riesgo, id_sector, id_sucursal) DO UPDATE SET
    num_creditos               = EXCLUDED.num_creditos,
    monto_total                = EXCLUDED.monto_total,
    monto_promedio             = EXCLUDED.monto_promedio,
    dias_mora_promedio         = EXCLUDED.dias_mora_promedio,
    num_moras_promedio         = EXCLUDED.num_moras_promedio,
    tasa_mora_90               = EXCLUDED.tasa_mora_90,
    tasa_judicial              = EXCLUDED.tasa_judicial,
    tasa_cierre                = EXCLUDED.tasa_cierre,
    total_gestion_cobro        = EXCLUDED.total_gestion_cobro,
    total_costo_judicial       = EXCLUDED.total_costo_judicial,
    tasa_interes_promedio      = EXCLUDED.tasa_interes_promedio,
    saldo_promedio             = EXCLUDED.saldo_promedio,
    creditos_cerrados          = EXCLUDED.creditos_cerrados,
    num_clientes_unicos        = EXCLUDED.num_clientes_unicos,
    creditos_por_cliente       = EXCLUDED.creditos_por_cliente,
    plazo_promedio             = EXCLUDED.plazo_promedio,
    desviacion_montos          = EXCLUDED.desviacion_montos,
    coef_variacion_montos      = EXCLUDED.coef_variacion_montos,
    antiguedad_promedio_meses  = EXCLUDED.antiguedad_promedio_meses,
    tasa_crecimiento_creditos  = EXCLUDED.tasa_crecimiento_creditos,
    tasa_crecimiento_monto     = EXCLUDED.tasa_crecimiento_monto,
    crisis_flag                = EXCLUDED.crisis_flag,
    bloque_id                  = EXCLUDED.bloque_id;

COMMIT;
