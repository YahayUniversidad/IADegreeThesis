-- ============================================================================
-- 03_crear_datamart.sql
-- Crea el esquema estrella del datamart sobre analisis_db
-- Tablas de dimensiones + fact tables para Superset
-- Se ejecuta una sola vez al inicializar PostgreSQL
-- ============================================================================

-- --------------------------------------------------------------------------
-- DIMENSIONES
-- --------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_tiempo (
    id_tiempo SERIAL PRIMARY KEY,
    mes DATE NOT NULL UNIQUE,
    anio INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    mes_del_anio INTEGER NOT NULL,
    nombre_mes VARCHAR(20) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_riesgo (
    id_riesgo SERIAL PRIMARY KEY,
    codigo_riesgo VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_sector (
    id_sector SERIAL PRIMARY KEY,
    codigo_sector VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS dim_sucursal (
    id_sucursal SERIAL PRIMARY KEY,
    codigo_sucursal INTEGER NOT NULL,
    codigo_provincia INTEGER,
    UNIQUE(codigo_sucursal, codigo_provincia)
);

-- --------------------------------------------------------------------------
-- TABLA DE HECHOS: HISTÓRICO
-- Una fila por mes-riesgo-sector-sucursal con todas las features + crisis_flag
-- --------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_creditos_mensual (
    id_tiempo INTEGER NOT NULL,
    id_riesgo INTEGER NOT NULL,
    id_sector INTEGER NOT NULL,
    id_sucursal INTEGER NOT NULL,
    num_creditos INTEGER NOT NULL,
    monto_total NUMERIC(18,2),
    monto_promedio NUMERIC(18,2),
    dias_mora_promedio NUMERIC(10,2),
    num_moras_promedio NUMERIC(10,2),
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
    coef_variacion_montos NUMERIC(8,2),
    antiguedad_promedio_meses NUMERIC(8,2),
    tasa_crecimiento_creditos NUMERIC(8,2),
    tasa_crecimiento_monto NUMERIC(8,2),
    crisis_flag INTEGER DEFAULT 0,
    bloque_id VARCHAR(200) NOT NULL,
    PRIMARY KEY (id_tiempo, id_riesgo, id_sector, id_sucursal)
);

-- --------------------------------------------------------------------------
-- TABLA DE HECHOS: PREDICCIONES
-- Poblada por predict.py; una fila por bloque-horizonte
-- --------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_predicciones_mensual (
    id SERIAL PRIMARY KEY,
    id_riesgo INTEGER NOT NULL,
    id_sector INTEGER NOT NULL,
    id_sucursal INTEGER NOT NULL,
    bloque_id VARCHAR(200) NOT NULL,
    mes_base DATE NOT NULL,
    mes_predicho DATE NOT NULL,
    horizonte_meses INTEGER NOT NULL,
    prob_crisis NUMERIC(8,4) NOT NULL,
    flag_crisis_predicha INTEGER DEFAULT 0,
    fecha_prediccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------------------------------------------------------
-- ÍNDICES PARA RENDIMIENTO DE CONSULTAS SUPERSET
-- --------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_fcm_tiempo ON fact_creditos_mensual(id_tiempo);
CREATE INDEX IF NOT EXISTS idx_fcm_riesgo ON fact_creditos_mensual(id_riesgo);
CREATE INDEX IF NOT EXISTS idx_fcm_sector ON fact_creditos_mensual(id_sector);
CREATE INDEX IF NOT EXISTS idx_fcm_sucursal ON fact_creditos_mensual(id_sucursal);
CREATE INDEX IF NOT EXISTS idx_fcm_bloque ON fact_creditos_mensual(bloque_id);
CREATE INDEX IF NOT EXISTS idx_fcm_crisis ON fact_creditos_mensual(crisis_flag);

CREATE INDEX IF NOT EXISTS idx_fpm_bloque ON fact_predicciones_mensual(bloque_id);
CREATE INDEX IF NOT EXISTS idx_fpm_riesgo ON fact_predicciones_mensual(id_riesgo);
CREATE INDEX IF NOT EXISTS idx_fpm_sector ON fact_predicciones_mensual(id_sector);
CREATE INDEX IF NOT EXISTS idx_fpm_sucursal ON fact_predicciones_mensual(id_sucursal);
CREATE INDEX IF NOT EXISTS idx_fpm_mes_predicho ON fact_predicciones_mensual(mes_predicho);
CREATE INDEX IF NOT EXISTS idx_fpm_horizonte ON fact_predicciones_mensual(horizonte_meses);
CREATE INDEX IF NOT EXISTS idx_fpm_fecha_pred ON fact_predicciones_mensual(fecha_prediccion);
CREATE UNIQUE INDEX IF NOT EXISTS idx_fpm_unique 
    ON fact_predicciones_mensual(bloque_id, mes_predicho, fecha_prediccion);
