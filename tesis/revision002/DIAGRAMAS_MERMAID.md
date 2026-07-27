---
marp: false
---

# Diagramas Conceptuales para la Tesis

Estos diagramas se pueden convertir a imagenes usando: - **Mermaid Live Editor**: https://mermaid.live/ - **VS Code extension**: Mermaid Preview - **Overleaf**: Con paquete `mermaid` o exportando desde mermaid.live

------------------------------------------------------------------------

## 1. Ventana Temporal de Entrada (6 meses × 21 features)

``` mermaid
graph LR
    subgraph "Ventana de Entrada"
        M1["mes t-5<br/>21 features"]
        M2["mes t-4<br/>21 features"]
        M3["mes t-3<br/>21 features"]
        M4["mes t-2<br/>21 features"]
        M5["mes t-1<br/>21 features"]
        M6["mes t<br/>21 features"]
    end

    M1 --> M2 --> M3 --> M4 --> M5 --> M6

    subgraph "Etiquetas Futuras"
        H1["h=1"]
        H6["h=6"]
        H12["h=12"]
        H18["h=18"]
    end

    M6 --> H1
    M6 --> H6
    M6 --> H12
    M6 --> H18
```

------------------------------------------------------------------------

## 2. Division de Datos (Train / Validation / Test)

``` mermaid
graph LR
    A["Datos Completos<br/>20,025 bloques-mes"] -->|"70%"| B["Entrenamiento<br/>49% del total"]
    A -->|"30%"| C["Prueba<br/>30% del total"]
    B -->|"30% del train"| D["Validacion<br/>21% del total"]
```

### Diagrama de Linea de Tiempo

``` mermaid
timeline
    title Division Temporal de Datos
    2015-2022 : Entrenamiento (70%)
              : Validacion (21%)
    2023-2026 : Prueba (30%)
```

------------------------------------------------------------------------

## 3. Comparacion de Arquitecturas de Modelos

``` mermaid
graph TB
    Input["Entrada<br/>6 meses × 21 features<br/>= 126 valores"]

    Input --> LGBM
    Input --> CNN
    Input --> MLP

    subgraph LGBM ["LightGBM"]
        L1["Modelo 1<br/>h=1 mes"]
        L2["Modelo 2<br/>h=3 meses"]
        L3["..."]
        L18["Modelo 18<br/>h=18 meses"]
        L1 --> L2 --> L3 --> L18
    end

    subgraph CNN ["CNN"]
        C1["Conv1D(64)<br/>kernel=3"]
        C2["Conv1D(128)<br/>kernel=3"]
        C3["Dense(128,64)"]
        C4["18 salidas<br/>sigmoide"]
        C1 --> C2 --> C3 --> C4
    end

    subgraph MLP ["MLP"]
        P1["Flatten<br/>126 valores"]
        P2["Dense(128)"]
        P3["Dense(64)"]
        P4["18 salidas<br/>sigmoide"]
        P1 --> P2 --> P3 --> P4
    end

    L18 --> Out1["18 predicciones<br/>independientes"]
    C4 --> Out2["18 predicciones<br/>simultaneas"]
    P4 --> Out3["18 predicciones<br/>simultaneas"]
```

------------------------------------------------------------------------

## 4. Arquitectura del Sistema Completo

``` mermaid
graph TB
    subgraph Fuentes["Fuentes de Datos"]
        F1["CABECERA_PRESTAMOS<br/>~500K registros"]
        F2["AMORTIZACAL_PRESTAMOS<br/>~2M registros"]
        F3["RECUPERACION_PRESTAMOS<br/>~100K registros"]
    end

    subgraph ETL["Proceso ETL"]
        E1["Integracion<br/>(JOIN + UPSERT)"]
        E2["Agregacion Mensual<br/>riesgo-sector-sucursal"]
        E3["21 Features<br/>+ crisis_flag"]
    end

    subgraph Storage["Almacenamiento"]
        S1["PostgreSQL 15<br/>mv_creditos_mensuales"]
        S2["Datamart Estrella<br/>dim_tiempo, dim_riesgo..."]
    end

    subgraph Modelos["Modelos"]
        M1["LightGBM<br/>18 clasificadores"]
        M2["CNN<br/>1 red, 18 salidas"]
        M3["MLP<br/>1 red, 18 salidas"]
    end

    subgraph MLOps["MLOps"]
        O1["Apache Airflow<br/>Orquestacion"]
        O2["MLflow<br/>Registro"]
    end

    subgraph Visual["Visualizacion"]
        V1["Apache Superset<br/>7 Dashboards"]
        V2["fact_predicciones<br/>18 horizontes"]
    end

    F1 --> E1
    F2 --> E1
    F3 --> E1
    E1 --> E2
    E2 --> E3
    E3 --> S1
    S1 --> S2
    S2 --> M1
    S2 --> M2
    S2 --> M3
    M1 --> O2
    M2 --> O2
    M3 --> O2
    O2 --> V2
    S2 --> V1
    V2 --> V1
    O1 --> M1
    O1 --> M2
    O1 --> M3
```

------------------------------------------------------------------------

## 5. Flujo de Entrenamiento

``` mermaid
flowchart TD
    A["Datos de mv_creditos_mensuales"] --> B["Preprocesamiento<br/>Clipping q01-q99"]
    B --> C["Generacion Secuencias<br/>6 meses × 21 features"]
    C --> D["Division Temporal<br/>70% train / 30% test"]
    D --> E["Extraccion Validacion<br/>30% del train"]
    
    E --> F["LightGBM<br/>18 modelos independientes"]
    E --> G["CNN<br/>1 red, 18 salidas"]
    E --> H["MLP<br/>1 red, 18 salidas"]
    
    F --> I["Evaluacion<br/>AUC-ROC promedio"]
    G --> I
    H --> I
    
    I --> J{"Seleccion<br/>Mejor AUC-ROC?"}
    J -->|LightGBM| K["Guardar en MLflow"]
    K --> L["Modelo Seleccionado"]
```

------------------------------------------------------------------------

## 6. Flujo de Inferencia Diaria

``` mermaid
flowchart TD
    A["DAG 06:00 Diario"] --> B["Refresh<br/>mv_creditos_mensuales"]
    B --> C["Cargar Modelo<br/>desde MLflow"]
    C --> D["Generar Predicciones<br/>18 horizontes"]
    D --> E["UPSERT<br/>fact_predicciones"]
    E --> F["Actualizar<br/>Apache Superset"]
```

------------------------------------------------------------------------

## 7. Definicion de crisis_flag (8 condiciones)

``` mermaid
graph TD
    A["datos del bloque-mes"] --> B{"Condicion 1<br/>tasa_judicial > 5%?"}
    A --> C{"Condicion 2<br/>tasa_judicial > 2%?"}
    A --> D{"Condicion 3<br/>costo_judicial > 10% monto?"}
    A --> E{"Condicion 4<br/>gestion_cobro > 5% monto?"}
    A --> F{"Condicion 5<br/>tasa_cierre > 30%?"}
    A --> G{"Condicion 6<br/>plazo > 36 meses?"}
    A --> H{"Condicion 7<br/>plazo > 60 meses?"}
    A --> I{"Condicion 8<br/>tasa_interes > 15%?"}
    
    B -->|"SI (peso=3)"| J["Suma de Pesos"]
    C -->|"SI (peso=1)"| J
    D -->|"SI (peso=2)"| J
    E -->|"SI (peso=1)"| J
    F -->|"SI (peso=2)"| J
    G -->|"SI (peso=1)"| J
    H -->|"SI (peso=1)"| J
    I -->|"SI (peso=1)"| J
    
    B -->|"NO (0)"| J
    C -->|"NO (0)"| J
    D -->|"NO (0)"| J
    E -->|"NO (0)"| J
    F -->|"NO (0)"| J
    G -->|"NO (0)"| J
    H -->|"NO (0)"| J
    I -->|"NO (0)"| J
    
    J --> K{"Suma >= 5?"}
    K -->|"SI"| L["crisis_flag = 1"]
    K -->|"NO"| M["crisis_flag = 0"]
```

------------------------------------------------------------------------

## 8. Esquema Estrella del Datamart

### 8a. Estrella para fact_creditos_mensual

``` mermaid
erDiagram
    DIM_TIEMPO {
        int id_tiempo PK
        date mes
        int anio
        int trimestre
        varchar nombre_mes
    }
    
    DIM_RIESGO {
        int id_riesgo PK
        varchar codigo_riesgo
        varchar descripcion
    }
    
    DIM_SECTOR {
        int id_sector PK
        varchar codigo_sector
        varchar descripcion
    }
    
    DIM_SUCURSAL {
        int id_sucursal PK
        int codigo_sucursal
        int codigo_provincia
    }
    
    FACT_CREDITOS {
        int id_tiempo FK
        int id_riesgo FK
        int id_sector FK
        int id_sucursal FK
        int num_creditos
        decimal monto_total
        decimal monto_promedio
        decimal tasa_judicial
        decimal tasa_cierre
        int crisis_flag
        varchar bloque_id
    }
    
    DIM_TIEMPO ||--o{ FACT_CREDITOS : "periodo"
    DIM_RIESGO ||--o{ FACT_CREDITOS : "clasifica"
    DIM_SECTOR ||--o{ FACT_CREDITOS : "agrupa"
    DIM_SUCURSAL ||--o{ FACT_CREDITOS : "ubicacion"
```

### 8b. Estrella para fact_predicciones

``` mermaid
erDiagram
    DIM_TIEMPO {
        int id_tiempo PK
        date mes
        int anio
    }
    
    DIM_RIESGO {
        int id_riesgo PK
        varchar codigo_riesgo
    }
    
    DIM_SECTOR {
        int id_sector PK
        varchar codigo_sector
    }
    
    DIM_SUCURSAL {
        int id_sucursal PK
        int codigo_sucursal
    }
    
    FACT_PREDICCIONES {
        int id_tiempo FK
        int id_riesgo FK
        int id_sector FK
        int id_sucursal FK
        varchar bloque_id
        decimal prob_h01
        decimal prob_h02
        decimal prob_h18
        int pred_h01
        int pred_h02
        int pred_h18
        decimal prob_media
        timestamp fecha_ejecucion
    }
    
    DIM_TIEMPO ||--o{ FACT_PREDICCIONES : "predice para"
    DIM_RIESGO ||--o{ FACT_PREDICCIONES : "clasifica"
    DIM_SECTOR ||--o{ FACT_PREDICCIONES : "agrupa"
    DIM_SUCURSAL ||--o{ FACT_PREDICCIONES : "ubicacion"
```

### Diagrama de Integracion (ambos esquemas)

``` mermaid
graph TB
    subgraph Dimensiones["Dimensiones Compartidas"]
        DT["dim_tiempo<br/>mes, anio, trimestre"]
        DR["dim_riesgo<br/>codigo_riesgo"]
        DS["dim_sector<br/>codigo_sector"]
        DU["dim_sucursal<br/>codigo_sucursal"]
    end
    
    subgraph Hechos["Tablas de Hechos"]
        FC["fact_creditos_mensual<br/>num_creditos, monto_total<br/>tasa_judicial, crisis_flag"]
        FP["fact_predicciones<br/>prob_h01-h18<br/>pred_h01-h18"]
    end
    
    DT --> FC
    DR --> FC
    DS --> FC
    DU --> FC
    
    DT --> FP
    DR --> FP
    DS --> FP
    DU --> FP
    
    FC -.->|"crisis_flag<br/>etiqueta real"| FP
    FP -.->|"predicciones<br/>modelo"| FC
```

------------------------------------------------------------------------

## Instrucciones para Convertir a Imagenes

### Opcion 1: Mermaid Live Editor (Recomendado)

1.  Ir a https://mermaid.live/
2.  Copiar el codigo de cada diagrama
3.  Pegar en el editor
4.  Exportar como PNG o SVG

### Opcion 2: VS Code

1.  Instalar extension "Mermaid Preview"
2.  Crear archivo .md con los diagramas
3.  Ctrl+Shift+V para previsualizar
4.  Click derecho -\> Export

### Opcion 3: Comando CLI

``` bash
# Instalar mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Convertir archivo .md a imagenes
mmdc -i diagramas.md -o diagramas.png
```

### Opcion 4: Python con mermaid-py

``` python
import mermaid as md
from mermaid.graph import Graph

graph = Graph("diagram", "graph LR; A-->B")
render = md.Mermaid(graph)
render.to_png("output.png")
```

------------------------------------------------------------------------

## Notas para la Tesis

-   **Formato recomendado**: SVG (vectorial) o PNG de alta resolucion (300 DPI)
-   **Tamano**: Ancho minimo 800px para impresion
-   **Colores**: Usar tonos neutros o sin color para impresion B/N
-   **Leyenda**: Incluir leyenda en cada figura
-   **Caption**: Agregar caption descriptivo debajo de cada imagen