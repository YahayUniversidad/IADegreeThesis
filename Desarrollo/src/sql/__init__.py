##
## @file __init__.py
##
## Contiene constantes y funciones principales del paquete sql.
##
## @author omar.velez@yachaytech.edu.ec
## @version julio 2026
##

from .utilidades import ejeucta_script_generico

__all__ = [
    "ejeucta_script_generico",
    "SQL_CREATE_TABLE_CREDITOS",
    "SQL_CREATE_TABLE_AMORTIZACION",
    "SQL_CREATE_TABLE_JUCIO",
    "SCRIPT_CREATE_TABLE_TEMPORAL_CSV",
]

"""Constantes con consultas SQL reutilizables del paquete."""

# Consultas y scripts SQL para la creación de tablas y otras operaciones en la base de datos.
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