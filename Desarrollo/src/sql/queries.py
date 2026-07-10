##
## @file queries.py
##
## Contiene constantes con consultas SQL reutilizables del paquete sql.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

SQL_CREATE_TABLE_CREDITOS = """
    CREATE TABLE IF NOT EXISTS creditos (
        numero_credito INTEGER NOT NULL,
        codigo_act_financiera INTEGER,
        codigo_producto INTEGER,
        fecha_credito TIMESTAMP,
        codigo_perioc VARCHAR(10),
        codigo_orirec VARCHAR(10),
        deb_aut VARCHAR(10),
        cant_soli NUMERIC(18, 2),
        num_cuotas INTEGER,
        tasa_interes NUMERIC(10, 2),
        mora NUMERIC(10, 2),
        tab_amortiza VARCHAR(10),
        tot_dias_mora INTEGER,
        tot_num_moras INTEGER,
        estado_cred VARCHAR(10),
        estado VARCHAR(10),
        per_gracia INTEGER,
        capital_porpagar NUMERIC(18, 2),
        mismodia VARCHAR(10),
        numdias INTEGER,
        oficre INTEGER,
        codigo_sucursal INTEGER,
        pigper VARCHAR(10),
        interes_fijo VARCHAR(10),
        porc_pig NUMERIC(10, 2),
        fecini TIMESTAMP,
        fecfin TIMESTAMP,
        judicial VARCHAR(10),
        codigo_grupo INTEGER,
        codigo VARCHAR(50),
        codigo_destino VARCHAR(50),
        codigo_destino_det VARCHAR(50),
        costo_judicial NUMERIC(18, 2),
        notificaciones NUMERIC(18, 2),
        gestion_cobro VARCHAR(10),
        fecha_gestion_cobro TIMESTAMP,
        desem_parc VARCHAR(10),
        monto_real NUMERIC(18, 2),
        saldo_capital NUMERIC(18, 2),
        PRIMARY KEY (numero_credito)                
    );

    -- Comentarios para documentar los campos
    COMMENT ON TABLE creditos IS 'Tabla de créditos';

    COMMENT ON COLUMN creditos.numero_credito IS 'Número único del crédito';
    COMMENT ON COLUMN creditos.codigo_act_financiera IS 'Código de la actividad financiera';
    COMMENT ON COLUMN creditos.codigo_producto IS 'Código del producto';
    COMMENT ON COLUMN creditos.fecha_credito IS 'Fecha del crédito';
    COMMENT ON COLUMN creditos.codigo_perioc IS 'Código del período';
    COMMENT ON COLUMN creditos.codigo_orirec IS 'Código de origen de recurso';
    COMMENT ON COLUMN creditos.deb_aut IS 'Débito automático';
    COMMENT ON COLUMN creditos.cant_soli IS 'Cantidad solicitada';
    COMMENT ON COLUMN creditos.num_cuotas IS 'Número de cuotas';
    COMMENT ON COLUMN creditos.tasa_interes IS 'Tasa de interés';
    COMMENT ON COLUMN creditos.mora IS 'Mora';
    COMMENT ON COLUMN creditos.tab_amortiza IS 'Tabla de amortización';
    COMMENT ON COLUMN creditos.tot_dias_mora IS 'Total de días en mora';
    COMMENT ON COLUMN creditos.tot_num_moras IS 'Total de número de moras';
    COMMENT ON COLUMN creditos.estado_cred IS 'Estado del crédito';
    COMMENT ON COLUMN creditos.estado IS 'Estado';
    COMMENT ON COLUMN creditos.per_gracia IS 'Período de gracia';
    COMMENT ON COLUMN creditos.capital_porpagar IS 'Capital por pagar';
    COMMENT ON COLUMN creditos.mismodia IS 'Mismo día';
    COMMENT ON COLUMN creditos.numdias IS 'Número de días';
    COMMENT ON COLUMN creditos.oficre IS 'Oficina de crédito';
    COMMENT ON COLUMN creditos.codigo_sucursal IS 'Código de sucursal';
    COMMENT ON COLUMN creditos.pigper IS 'Pigper';
    COMMENT ON COLUMN creditos.interes_fijo IS 'Interés fijo';
    COMMENT ON COLUMN creditos.porc_pig IS 'Porcentaje PIG';
    COMMENT ON COLUMN creditos.fecini IS 'Fecha inicio';
    COMMENT ON COLUMN creditos.fecfin IS 'Fecha fin';
    COMMENT ON COLUMN creditos.judicial IS 'Indicador judicial';
    COMMENT ON COLUMN creditos.codigo_grupo IS 'Código de grupo';
    COMMENT ON COLUMN creditos.codigo IS 'Código';
    COMMENT ON COLUMN creditos.codigo_destino IS 'Código de destino';
    COMMENT ON COLUMN creditos.codigo_destino_det IS 'Código de destino detallado';
    COMMENT ON COLUMN creditos.costo_judicial IS 'Costo judicial';
    COMMENT ON COLUMN creditos.notificaciones IS 'Notificaciones';
    COMMENT ON COLUMN creditos.gestion_cobro IS 'Gestión de cobro';
    COMMENT ON COLUMN creditos.fecha_gestion_cobro IS 'Fecha de gestión de cobro';
    COMMENT ON COLUMN creditos.desem_parc IS 'Desembolso parcial';
    COMMENT ON COLUMN creditos.monto_real IS 'Monto real';
    COMMENT ON COLUMN creditos.saldo_capital IS 'Saldo de capital';
"""

SQL_CREATE_TABLE_AMORTIZACION = """
    CREATE TABLE IF NOT EXISTS amortizacion (
        numero_credito INTEGER NOT NULL,
        ordencal INTEGER,
        fecinical TIMESTAMP,
        fecfincal TIMESTAMP,
        saldocal NUMERIC(18, 2),
        capitalcal NUMERIC(18, 2),
        interescal NUMERIC(18, 2),
        diasintcal INTEGER,
        fechaincal TIMESTAMP,
        moracal NUMERIC(18, 2),
        diasmoracal INTEGER,
        fechamoracal TIMESTAMP,
        rubroscal NUMERIC(18, 2),
        totalcal NUMERIC(18, 2),
        estadocal VARCHAR(10),
        estado VARCHAR(10),
        PRIMARY KEY (numero_credito, ordencal)
    );

    -- Comentarios para documentar los campos
    COMMENT ON TABLE amortizacion IS 'Tabla de amortización de créditos';
    COMMENT ON COLUMN amortizacion.numero_credito IS 'Número del crédito asociado';
    COMMENT ON COLUMN amortizacion.ordencal IS 'Orden de cálculo';
    COMMENT ON COLUMN amortizacion.fecinical IS 'Fecha inicio de cálculo';
    COMMENT ON COLUMN amortizacion.fecfincal IS 'Fecha fin de cálculo';
    COMMENT ON COLUMN amortizacion.saldocal IS 'Saldo de cálculo';
    COMMENT ON COLUMN amortizacion.capitalcal IS 'Capital de cálculo';
    COMMENT ON COLUMN amortizacion.interescal IS 'Interés de cálculo';
    COMMENT ON COLUMN amortizacion.diasintcal IS 'Días de interés de cálculo';
    COMMENT ON COLUMN amortizacion.fechaincal IS 'Fecha de interés de cálculo';
    COMMENT ON COLUMN amortizacion.moracal IS 'Mora de cálculo';
    COMMENT ON COLUMN amortizacion.diasmoracal IS 'Días de mora de cálculo';
    COMMENT ON COLUMN amortizacion.fechamoracal IS 'Fecha de mora de cálculo';
    COMMENT ON COLUMN amortizacion.rubroscal IS 'Rubros de cálculo';
    COMMENT ON COLUMN amortizacion.totalcal IS 'Total de cálculo';
    COMMENT ON COLUMN amortizacion.estadocal IS 'Estado de cálculo';
    COMMENT ON COLUMN amortizacion.estado IS 'Estado'; 
"""

SQL_CREATE_TABLE_JUICIOS = """
    CREATE TABLE IF NOT EXISTS juicios (
    numero_credito INTEGER NOT NULL,
    codigo_tipo_juicio INTEGER,
    tipo_operacion VARCHAR(10),
    valor_demanda NUMERIC(18, 2),
    capital_recuperado NUMERIC(18, 2),
    fecha_proceso TIMESTAMP,
    fecha_recuperado TIMESTAMP,
    fecha_cierre TIMESTAMP,
    estado VARCHAR(10),
    PRIMARY KEY (numero_credito)
    );

    -- Comentarios para documentar los campos
    COMMENT ON TABLE juicios IS 'Tabla de juicios asociados a créditos';

    COMMENT ON COLUMN juicios.numero_credito IS 'Número del crédito asociado';
    COMMENT ON COLUMN juicios.codigo_tipo_juicio IS 'Código del tipo de juicio';
    COMMENT ON COLUMN juicios.tipo_operacion IS 'Tipo de operación';
    COMMENT ON COLUMN juicios.valor_demanda IS 'Valor de la demanda';
    COMMENT ON COLUMN juicios.capital_recuperado IS 'Capital recuperado';
    COMMENT ON COLUMN juicios.fecha_proceso IS 'Fecha del proceso';
    COMMENT ON COLUMN juicios.fecha_recuperado IS 'Fecha de recuperación';
    COMMENT ON COLUMN juicios.fecha_cierre IS 'Fecha de cierre';
    COMMENT ON COLUMN juicios.estado IS 'Estado del juicio';
"""

SCRIPT_CREATE_TABLE_TEMPORAL_CSV = """
    DROP TABLE IF EXISTS pivot_amortizacion;
    CREATE UNLOGGED TABLE pivot_amortizacion AS 
    SELECT * FROM amortizacion; 
   
    DROP TABLE IF EXISTS pivot_creditos;
    CREATE UNLOGGED TABLE pivot_creditos AS 
    SELECT * FROM creditos; 
    
    DROP TABLE IF EXISTS  pivot_juicios;
    CREATE UNLOGGED TABLE pivot_juicios AS 
    SELECT * FROM juicios;
    """

SQL_CREA_DIM_TIEMPO = """
    CREATE TABLE IF NOT EXISTS dim_tiempo (
    id_tiempo SERIAL PRIMARY KEY,
    mes DATE NOT NULL UNIQUE,
    anio INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    mes_del_anio INTEGER NOT NULL,
    nombre_mes VARCHAR(20) NOT NULL);
    """

SQL_CREA_DIM_RIESGO = """
    CREATE TABLE IF NOT EXISTS dim_riesgo (
    id_riesgo SERIAL PRIMARY KEY,
    codigo_riesgo VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(100)
    );
    """
SQL_CREA_DIM_SECTOR = """
    CREATE TABLE IF NOT EXISTS dim_sector (
        id_sector SERIAL PRIMARY KEY,
        codigo_sector VARCHAR(100) NOT NULL UNIQUE,
        descripcion VARCHAR(100)
    );
    """
SQL_CREA_DIM_SUCURSAL = """
    DROP TABLE IF EXISTS dim_sucursal CASCADE;
    CREATE TABLE dim_sucursal (
        id_sucursal SERIAL PRIMARY KEY,
        codigo_sucursal INTEGER NOT NULL UNIQUE,
        codigo_provincia INTEGER DEFAULT 0
    );
    """

SQL_DROP_MV = "DROP MATERIALIZED VIEW IF EXISTS mv_creditos_mensuales;"

SQL_CREATE_MV = """
CREATE MATERIALIZED VIEW mv_creditos_mensuales AS

WITH datos_crudos AS (
    SELECT
        c.numero_credito,
        c.codigo_act_financiera,
        c.codigo_producto,
        c.fecha_credito,
        c.cant_soli,
        c.num_cuotas,
        c.tasa_interes,
        c.mora,
        c.tot_dias_mora,
        c.tot_num_moras,
        c.estado_cred,
        c.judicial,
        c.capital_porpagar,
        c.codigo_sucursal,
        c.porc_pig,
        c.costo_judicial,
        c.notificaciones,
        c.gestion_cobro,
        c.monto_real,
        c.saldo_capital,
        a.capitalcal,
        a.interescal,
        a.moracal,
        a.rubroscal,
        a.totalcal,
        j.valor_demanda,
        j.capital_recuperado
    FROM creditos c
    JOIN amortizacion a ON c.numero_credito = a.numero_credito
    LEFT JOIN juicios j ON c.numero_credito = j.numero_credito
    WHERE c.fecha_credito >= '2005-01-01'
),

datos_mensuales AS (
    SELECT
        DATE_TRUNC('month', fecha_credito)::DATE AS mes,
        COALESCE(codigo_act_financiera::TEXT, 'SIN_RIESGO') AS riesgo,
        COALESCE(codigo_producto::TEXT, 'SIN_SECTOR') AS sector,
        codigo_sucursal,
        COUNT(*) AS num_creditos,
        SUM(COALESCE(cant_soli, 0)) AS monto_total,
        SUM(COALESCE(monto_real, 0)) AS monto_promedio,
        AVG(COALESCE(num_cuotas, 0)) AS plazo_promedio,
        AVG(COALESCE(tasa_interes, 0)) AS tasa_interes_promedio,
        AVG(COALESCE(saldo_capital, 0)) AS saldo_promedio,
        SUM(COALESCE(costo_judicial, 0)) AS total_costo_judicial,
        SUM(COALESCE(gestion_cobro::NUMERIC, 0)) AS total_gestion_cobro,
        SUM(COALESCE(notificaciones::NUMERIC, 0)) AS total_notificaciones,
        AVG(COALESCE(tot_dias_mora, 0)) AS tot_dias_mora_promedio,
        AVG(COALESCE(tot_num_moras, 0)) AS tot_num_moras_promedio,
        AVG(COALESCE(mora, 0)) AS mora_promedio,
        COUNT(CASE WHEN judicial = 'S' THEN 1 END) AS creditos_judiciales,
        COUNT(CASE WHEN estado_cred IN ('C', 'L') THEN 1 END) AS creditos_cerrados,
        COUNT(CASE WHEN tot_dias_mora > 90 THEN 1 END) AS creditos_mora_90,
        STDDEV(COALESCE(cant_soli, 0)) AS desviacion_montos,
        COUNT(DISTINCT numero_credito) AS num_clientes_unicos
    FROM datos_crudos
    GROUP BY
        DATE_TRUNC('month', fecha_credito),
        codigo_act_financiera,
        codigo_producto,
        codigo_sucursal
),

datos_enriquecidos AS (
    SELECT
        mes,
        riesgo,
        sector,
        codigo_sucursal,
        num_creditos,
        monto_total,
        ROUND(monto_promedio::NUMERIC, 2) AS monto_promedio,
        ROUND(plazo_promedio::NUMERIC, 2) AS plazo_promedio,
        ROUND(tasa_interes_promedio::NUMERIC, 2) AS tasa_interes_promedio,
        ROUND(saldo_promedio::NUMERIC, 2) AS saldo_promedio,
        ROUND(total_costo_judicial::NUMERIC, 2) AS total_costo_judicial,
        ROUND(total_gestion_cobro::NUMERIC, 2) AS total_gestion_cobro,
        ROUND(total_notificaciones::NUMERIC, 2) AS total_notificaciones,
        ROUND(tot_dias_mora_promedio::NUMERIC, 2) AS tot_dias_mora_promedio,
        ROUND(tot_num_moras_promedio::NUMERIC, 2) AS tot_num_moras_promedio,
        ROUND(mora_promedio::NUMERIC, 2) AS mora_promedio,
        creditos_judiciales,
        creditos_cerrados,
        num_clientes_unicos,
        ROUND((creditos_judiciales::NUMERIC / NULLIF(num_creditos, 0)) * 100, 2) AS tasa_judicial,
        ROUND((creditos_cerrados::NUMERIC / NULLIF(num_creditos, 0)) * 100, 2) AS tasa_cierre,
        ROUND((creditos_mora_90::NUMERIC / NULLIF(num_creditos, 0)) * 100, 2) AS tasa_mora_90,
        ROUND(COALESCE(desviacion_montos, 0)::NUMERIC, 2) AS desviacion_montos,
        ROUND((COALESCE(desviacion_montos, 0)::NUMERIC / NULLIF(monto_promedio, 0)) * 100, 2) AS coef_variacion_montos,
        ROUND(num_creditos::NUMERIC / NULLIF(num_clientes_unicos, 0), 2) AS creditos_por_cliente,
        ROUND(
            ((num_creditos::NUMERIC - COALESCE(LAG(num_creditos, 1) OVER (
                PARTITION BY riesgo, sector ORDER BY mes
            ), num_creditos))
            / NULLIF(LAG(num_creditos, 1) OVER (
                PARTITION BY riesgo, sector ORDER BY mes
            ), 0)) * 100, 2
        ) AS tasa_crecimiento_creditos,
        ROUND(
            ((monto_total::NUMERIC - COALESCE(LAG(monto_total, 1) OVER (
                PARTITION BY riesgo, sector ORDER BY mes
            ), monto_total))
            / NULLIF(LAG(monto_total, 1) OVER (
                PARTITION BY riesgo, sector ORDER BY mes
            ), 0)) * 100, 2
        ) AS tasa_crecimiento_monto,
        CASE
            WHEN (
                CASE WHEN (creditos_judiciales::NUMERIC / NULLIF(num_creditos, 0)) * 100 > 5 THEN 3 ELSE 0 END +
                CASE WHEN (creditos_judiciales::NUMERIC / NULLIF(num_creditos, 0)) * 100 > 2 THEN 1 ELSE 0 END +
                CASE WHEN total_costo_judicial > 0
                     AND (total_costo_judicial / NULLIF(num_creditos, 0)) > (monto_promedio * 0.1)
                     THEN 2 ELSE 0 END +
                CASE WHEN total_gestion_cobro > 0
                     AND (total_gestion_cobro / NULLIF(num_creditos, 0)) > (monto_promedio * 0.05)
                     THEN 1 ELSE 0 END +
                CASE WHEN (creditos_cerrados::NUMERIC / NULLIF(num_creditos, 0)) * 100 > 30 THEN 2
                     WHEN (creditos_cerrados::NUMERIC / NULLIF(num_creditos, 0)) * 100 > 20 THEN 1
                     ELSE 0 END +
                CASE WHEN plazo_promedio > 36 THEN 1 ELSE 0 END +
                CASE WHEN plazo_promedio > 60 THEN 1 ELSE 0 END +
                CASE WHEN tasa_interes_promedio > 15 THEN 1 ELSE 0 END
            ) >= 5 THEN 1
            ELSE 0
        END AS crisis_flag
    FROM datos_mensuales
)

SELECT
    mes,
    riesgo,
    sector,
    codigo_sucursal,
    num_creditos,
    monto_total,
    monto_promedio,
    plazo_promedio,
    tasa_interes_promedio,
    saldo_promedio,
    total_costo_judicial,
    total_gestion_cobro,
    total_notificaciones,
    tot_dias_mora_promedio,
    tot_num_moras_promedio,
    mora_promedio,
    creditos_judiciales,
    creditos_cerrados,
    num_clientes_unicos,
    tasa_judicial,
    tasa_cierre,
    tasa_mora_90,
    desviacion_montos,
    coef_variacion_montos,
    creditos_por_cliente,
    tasa_crecimiento_creditos,
    tasa_crecimiento_monto,
    crisis_flag,
    riesgo || '_' || sector || '_' || codigo_sucursal::TEXT AS bloque_id
FROM datos_enriquecidos;
"""

SQL_CREATE_IDX_MV = """
CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_creditos_mensuales_pk
    ON mv_creditos_mensuales(mes, riesgo, sector, codigo_sucursal);
"""

SQL_INSERT_DIM_TIEMPO = """
INSERT INTO dim_tiempo (mes, anio, trimestre, mes_del_anio, nombre_mes)
SELECT DISTINCT
    mes,
    EXTRACT(YEAR FROM mes)::INTEGER,
    EXTRACT(QUARTER FROM mes)::INTEGER,
    EXTRACT(MONTH FROM mes)::INTEGER,
    TO_CHAR(mes, 'TMMonth')
FROM mv_creditos_mensuales
ON CONFLICT (mes) DO NOTHING;
"""

SQL_INSERT_DIM_RIESGO = """
INSERT INTO dim_riesgo (codigo_riesgo, descripcion)
SELECT DISTINCT riesgo, riesgo
FROM mv_creditos_mensuales
ON CONFLICT (codigo_riesgo) DO NOTHING;
"""

SQL_INSERT_DIM_SECTOR = """
INSERT INTO dim_sector (codigo_sector, descripcion)
SELECT DISTINCT sector, sector
FROM mv_creditos_mensuales
ON CONFLICT (codigo_sector) DO NOTHING;
"""

SQL_INSERT_DIM_SUCURSAL = """
INSERT INTO dim_sucursal (codigo_sucursal, codigo_provincia)
SELECT DISTINCT codigo_sucursal, 0
FROM mv_creditos_mensuales
ON CONFLICT (codigo_sucursal) DO NOTHING;
"""

SQL_UPSERT_FACT_CREDITOS = """
INSERT INTO fact_creditos_mensual (
    id_tiempo, id_riesgo, id_sector, id_sucursal,
    num_creditos, monto_total, monto_promedio,
    tot_dias_mora_promedio, tot_num_moras_promedio,
    tasa_mora_90, tasa_judicial, tasa_cierre,
    total_gestion_cobro, total_costo_judicial,
    tasa_interes_promedio, saldo_promedio,
    creditos_cerrados, num_clientes_unicos,
    creditos_por_cliente, plazo_promedio,
    desviacion_montos, coef_variacion_montos,
    tasa_crecimiento_creditos, tasa_crecimiento_monto,
    crisis_flag, bloque_id
)
SELECT
    dt.id_tiempo,
    dr.id_riesgo,
    ds.id_sector,
    dsu.id_sucursal,
    mv.num_creditos,
    mv.monto_total,
    mv.monto_promedio,
    mv.tot_dias_mora_promedio,
    mv.tot_num_moras_promedio,
    mv.tasa_mora_90,
    mv.tasa_judicial,
    mv.tasa_cierre,
    mv.total_gestion_cobro,
    mv.total_costo_judicial,
    mv.tasa_interes_promedio,
    mv.saldo_promedio,
    mv.creditos_cerrados,
    mv.num_clientes_unicos,
    mv.creditos_por_cliente,
    mv.plazo_promedio,
    mv.desviacion_montos,
    mv.coef_variacion_montos,
    mv.tasa_crecimiento_creditos,
    mv.tasa_crecimiento_monto,
    mv.crisis_flag,
    mv.bloque_id
FROM mv_creditos_mensuales mv
JOIN dim_tiempo dt ON dt.mes = mv.mes
JOIN dim_riesgo dr ON dr.codigo_riesgo = mv.riesgo
JOIN dim_sector ds ON ds.codigo_sector = mv.sector
JOIN dim_sucursal dsu ON dsu.codigo_sucursal = mv.codigo_sucursal
ON CONFLICT (id_tiempo, id_riesgo, id_sector, id_sucursal) DO UPDATE SET
    num_creditos               = EXCLUDED.num_creditos,
    monto_total                = EXCLUDED.monto_total,
    monto_promedio             = EXCLUDED.monto_promedio,
    tot_dias_mora_promedio     = EXCLUDED.tot_dias_mora_promedio,
    tot_num_moras_promedio     = EXCLUDED.tot_num_moras_promedio,
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
    tasa_crecimiento_creditos  = EXCLUDED.tasa_crecimiento_creditos,
    tasa_crecimiento_monto     = EXCLUDED.tasa_crecimiento_monto,
    crisis_flag                = EXCLUDED.crisis_flag,
    bloque_id                  = EXCLUDED.bloque_id;
"""

SQL_CREA_FACT_CREDITOS = """
    DROP TABLE IF EXISTS fact_creditos_mensual CASCADE;
    CREATE TABLE fact_creditos_mensual (
        id_tiempo INTEGER NOT NULL,
        id_riesgo INTEGER NOT NULL,
        id_sector INTEGER NOT NULL,
        id_sucursal INTEGER NOT NULL,
        num_creditos INTEGER NOT NULL,
        monto_total NUMERIC(18,2),
        monto_promedio NUMERIC(18,2),
        tot_dias_mora_promedio NUMERIC(10,2),
        tot_num_moras_promedio NUMERIC(10,2),
        tasa_mora_90 NUMERIC(8,2),
        tasa_judicial NUMERIC(8,2),
        tasa_cierre NUMERIC(8,2),
        total_gestion_cobro NUMERIC(18,2),
        total_costo_judicial NUMERIC(18,2),
        tasa_interes_promedio NUMERIC(8,2),
        saldo_promedio NUMERIC(18,2),
        creditos_cerrados INTEGER,
        num_clientes_unicos INTEGER,
        creditos_por_cliente NUMERIC(8,2),
        plazo_promedio NUMERIC(8,2),
        desviacion_montos NUMERIC(18,2),
        coef_variacion_montos NUMERIC(15,2),
        tasa_crecimiento_creditos NUMERIC(15,2),
        tasa_crecimiento_monto NUMERIC(15,2),
        crisis_flag INTEGER DEFAULT 0,
        bloque_id VARCHAR(200) NOT NULL,
        PRIMARY KEY (id_tiempo, id_riesgo, id_sector, id_sucursal)
    );
    """

SQL_REFRESH_DIM_TIEMPO = """
INSERT INTO dim_tiempo (mes, anio, trimestre, mes_del_anio, nombre_mes)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (mes) DO NOTHING;
"""

SQL_REFRESH_DIM_RIESGO = """
INSERT INTO dim_riesgo (codigo_riesgo, descripcion)
VALUES (%s, %s) ON CONFLICT (codigo_riesgo) DO NOTHING;
"""

SQL_REFRESH_DIM_SECTOR = """
INSERT INTO dim_sector (codigo_sector, descripcion)
VALUES (%s, %s) ON CONFLICT (codigo_sector) DO NOTHING;
"""

SQL_REFRESH_DIM_SUCURSAL = """
INSERT INTO dim_sucursal (codigo_sucursal, codigo_provincia)
VALUES (%s, 0) ON CONFLICT (codigo_sucursal) DO NOTHING;
"""

SQL_INSERT_PREDICCIONES = """
INSERT INTO fact_predicciones (
    id_tiempo, id_riesgo, id_sector, id_sucursal,
    bloque_id,
    prob_h01, prob_h02, prob_h03, prob_h04, prob_h05, prob_h06,
    prob_h07, prob_h08, prob_h09, prob_h10, prob_h11, prob_h12,
    prob_h13, prob_h14, prob_h15, prob_h16, prob_h17, prob_h18,
    pred_h01, pred_h02, pred_h03, pred_h04, pred_h05, pred_h06,
    pred_h07, pred_h08, pred_h09, pred_h10, pred_h11, pred_h12,
    pred_h13, pred_h14, pred_h15, pred_h16, pred_h17, pred_h18,
    prob_media, pred_media, crisis_count, fecha_ejecucion
) VALUES (
    (SELECT id_tiempo FROM dim_tiempo WHERE mes = %s),
    (SELECT id_riesgo FROM dim_riesgo WHERE codigo_riesgo = %s),
    (SELECT id_sector FROM dim_sector WHERE codigo_sector = %s),
    (SELECT id_sucursal FROM dim_sucursal WHERE codigo_sucursal = %s),
    %s,
    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
    %s, %s, %s, %s
)
ON CONFLICT (id_tiempo, id_riesgo, id_sector, id_sucursal)
DO UPDATE SET
    bloque_id = EXCLUDED.bloque_id,
    prob_h01 = EXCLUDED.prob_h01, prob_h02 = EXCLUDED.prob_h02,
    prob_h03 = EXCLUDED.prob_h03, prob_h04 = EXCLUDED.prob_h04,
    prob_h05 = EXCLUDED.prob_h05, prob_h06 = EXCLUDED.prob_h06,
    prob_h07 = EXCLUDED.prob_h07, prob_h08 = EXCLUDED.prob_h08,
    prob_h09 = EXCLUDED.prob_h09, prob_h10 = EXCLUDED.prob_h10,
    prob_h11 = EXCLUDED.prob_h11, prob_h12 = EXCLUDED.prob_h12,
    prob_h13 = EXCLUDED.prob_h13, prob_h14 = EXCLUDED.prob_h14,
    prob_h15 = EXCLUDED.prob_h15, prob_h16 = EXCLUDED.prob_h16,
    prob_h17 = EXCLUDED.prob_h17, prob_h18 = EXCLUDED.prob_h18,
    pred_h01 = EXCLUDED.pred_h01, pred_h02 = EXCLUDED.pred_h02,
    pred_h03 = EXCLUDED.pred_h03, pred_h04 = EXCLUDED.pred_h04,
    pred_h05 = EXCLUDED.pred_h05, pred_h06 = EXCLUDED.pred_h06,
    pred_h07 = EXCLUDED.pred_h07, pred_h08 = EXCLUDED.pred_h08,
    pred_h09 = EXCLUDED.pred_h09, pred_h10 = EXCLUDED.pred_h10,
    pred_h11 = EXCLUDED.pred_h11, pred_h12 = EXCLUDED.pred_h12,
    pred_h13 = EXCLUDED.pred_h13, pred_h14 = EXCLUDED.pred_h14,
    pred_h15 = EXCLUDED.pred_h15, pred_h16 = EXCLUDED.pred_h16,
    pred_h17 = EXCLUDED.pred_h17, pred_h18 = EXCLUDED.pred_h18,
    prob_media = EXCLUDED.prob_media,
    pred_media = EXCLUDED.pred_media,
    crisis_count = EXCLUDED.crisis_count,
    fecha_ejecucion = EXCLUDED.fecha_ejecucion;
"""

SQL_CREA_FACT_PREDICCIONES = """
    DROP TABLE IF EXISTS fact_predicciones CASCADE;
    CREATE TABLE fact_predicciones (
        id_prediccion    SERIAL PRIMARY KEY,
        id_tiempo        INTEGER NOT NULL REFERENCES dim_tiempo(id_tiempo),
        id_riesgo        INTEGER NOT NULL REFERENCES dim_riesgo(id_riesgo),
        id_sector        INTEGER NOT NULL REFERENCES dim_sector(id_sector),
        id_sucursal      INTEGER NOT NULL REFERENCES dim_sucursal(id_sucursal),
        bloque_id        VARCHAR(50) NOT NULL,
        prob_h01  NUMERIC(10,6), prob_h02  NUMERIC(10,6), prob_h03  NUMERIC(10,6),
        prob_h04  NUMERIC(10,6), prob_h05  NUMERIC(10,6), prob_h06  NUMERIC(10,6),
        prob_h07  NUMERIC(10,6), prob_h08  NUMERIC(10,6), prob_h09  NUMERIC(10,6),
        prob_h10  NUMERIC(10,6), prob_h11  NUMERIC(10,6), prob_h12  NUMERIC(10,6),
        prob_h13  NUMERIC(10,6), prob_h14  NUMERIC(10,6), prob_h15  NUMERIC(10,6),
        prob_h16  NUMERIC(10,6), prob_h17  NUMERIC(10,6), prob_h18  NUMERIC(10,6),
        pred_h01  INTEGER, pred_h02  INTEGER, pred_h03  INTEGER,
        pred_h04  INTEGER, pred_h05  INTEGER, pred_h06  INTEGER,
        pred_h07  INTEGER, pred_h08  INTEGER, pred_h09  INTEGER,
        pred_h10  INTEGER, pred_h11  INTEGER, pred_h12  INTEGER,
        pred_h13  INTEGER, pred_h14  INTEGER, pred_h15  INTEGER,
        pred_h16  INTEGER, pred_h17  INTEGER, pred_h18  INTEGER,
        prob_media     NUMERIC(10,6),
        pred_media     INTEGER,
        crisis_count   INTEGER,
        fecha_ejecucion TIMESTAMP,
        UNIQUE (id_tiempo, id_riesgo, id_sector, id_sucursal)
    );
    """