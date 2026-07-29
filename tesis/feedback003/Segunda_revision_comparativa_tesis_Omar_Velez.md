**SEGUNDA REVISIÓN COMPARATIVA**

Académica, metodológica, técnica, bibliográfica y de redacción

**Sistema Integrado de Inteligencia de Negocio para la Predicción de\
Crisis Crediticias mediante las técnicas de análisis de Inteligencia\
artificial y de negocio**

Autor: Omar Antonio Vélez Bayas

Tutor: Juan Pablo Astudillo León, Ph.D.

Programa: Maestría en Inteligencia Artificial

Versión revisada: PDF de 72 páginas, julio de 2026

Comparación base: informe de primera revisión de 44 páginas

**DICTAMEN: CORRECCIONES MAYORES ANTES DE LA DEFENSA**

*La reestructuración general fue exitosa, pero permanecen bloqueadores
metodológicos, bibliográficos y editoriales.*

# Nota sobre el alcance de esta segunda revisión

La revisión compara la nueva versión de 72 páginas con las observaciones
formuladas en el primer informe. Se examinó el documento completo,
incluidos los elementos preliminares, los seis capítulos, las tablas,
las figuras, la bibliografía y los apéndices. Las referencias de página
corresponden a la numeración física del PDF de 72 páginas.

La valoración distingue entre correcciones resueltas, parcialmente
resueltas y pendientes. También identifica problemas nuevos introducidos
durante la reescritura, especialmente contradicciones internas,
referencias cruzadas incorrectas y fragmentos que conservan el tono de
un informe de revisión en lugar del tono de una tesis terminada.

**Escala de prioridad:**

-   Crítica: puede comprometer la validez de los resultados, el
    cumplimiento académico o la defensa.

-   Alta: debe corregirse para que la metodología, los resultados o la
    presentación sean defendibles.

-   Media: afecta claridad, coherencia, reproducibilidad o calidad
    editorial.

-   Baja: corrección puntual de redacción, formato o estilo.

# 1. Dictamen general

La nueva versión representa un avance sustancial frente al manuscrito
original. Se reorganizaron los capítulos, se separó la metodología de
los resultados, se reformularon la pregunta y los objetivos, se
documentaron las veintiuna características y las ocho reglas de
crisis_flag, se corrigió la dimensión de entrada a 126 valores, se
incorporó un conjunto de validación y se moderaron las afirmaciones de
causalidad y superioridad.

No obstante, la tesis todavía no debe considerarse lista para entrega o
defensa. El resumen y el abstract permanecen vacíos; no se conocen los
conteos exactos de secuencias y particiones; la comparación entre
modelos sigue sin ser equivalente; existe una contradicción sobre la
entrada utilizada por LightGBM; la validez de la etiqueta continúa sin
demostrarse; faltan repeticiones y métricas clave; y el Capítulo 3
conserva cinco preprints pese a la recomendación expresa de sustituirlos
por publicaciones revisadas por pares.

**Cambio de dictamen respecto de la primera revisión:**

La valoración pasa de "reestructuración sustancial" a "correcciones
mayores focalizadas". La arquitectura del documento ya es adecuada; el
trabajo pendiente se concentra en completar evidencia, resolver
inconsistencias y realizar una corrección lingüística y bibliográfica
integral.

  -------------------------------------------------------------------------
  **Área**           **Estado actual** **Hallazgo         **Prioridad**
                                       principal**        
  ------------------ ----------------- ------------------ -----------------
  Elementos          Deficiente        Resumen y abstract Crítica
  preliminares                         vacíos; título y   
                                       declaraciones aún  
                                       contienen errores. 

  Introducción       Adecuado con      Mejor              Media
                     ajustes           delimitación;      
                                       faltan referencias 
                                       y persisten        
                                       errores de estilo. 

  Marco teórico      Parcialmente      Mejor estructura;  Media
                     adecuado          cobertura          
                                       bibliográfica      
                                       todavía limitada y 
                                       redacción          
                                       irregular.         

  Estado del arte    Deficiente        Revisión muy       Alta
                                       breve, cinco       
                                       preprints y        
                                       ausencia de        
                                       literatura         
                                       multi-horizonte,   
                                       BI y contexto      
                                       ecuatoriano.       

  Metodología        Parcial           Documentación      Crítica
                                       ampliada, pero     
                                       faltan conteos     
                                       exactos y existe   
                                       contradicción      
                                       sobre las entradas 
                                       de los modelos.    

  Resultados         Parcial           Interpretación más Crítica
                                       prudente, pero     
                                       comparación no     
                                       equivalente y      
                                       resultados         
                                       incompletos por    
                                       horizonte.         

  Conclusiones       Parcialmente      Tono más prudente; Alta
                     adecuado          contiene           
                                       afirmaciones       
                                       contradictorias o  
                                       excesivas.         

  MLOps/BI           Parcial           La implementación  Alta
                                       está mejor         
                                       descrita, pero no  
                                       se valida          
                                       operación, calidad 
                                       ni utilidad.       

  Tablas y figuras   Parcial           Más diagramas y    Alta
                                       tablas, aunque     
                                       varias son         
                                       ilegibles o tienen 
                                       referencias        
                                       cruzadas erróneas. 

  Bibliografía       Deficiente        25 fuentes; cinco  Alta
                                       son preprints y    
                                       faltan áreas       
                                       esenciales.        

  Redacción y        Deficiente        Persisten          Alta
  formato                              numerosos errores  
                                       gramaticales,      
                                       terminológicos y   
                                       de consistencia.   

  Reproducibilidad   Deficiente        Faltan conteos,    Crítica
                                       semillas en        
                                       CNN/MLP, versiones 
                                       completas, hashes  
                                       y repeticiones.    
  -------------------------------------------------------------------------

# 2. Matriz comparativa de las observaciones principales

  ----------------------------------------------------------------------------------------------
  **ID**         **Observación           **Estado**     **Evidencia en la     **Acción
                 original**                             nueva versión**       restante**
  -------------- ----------------------- -------------- --------------------- ------------------
  P-01           Trazabilidad 20.025 →   Parcial        Se añadió una tabla   Extraer y reportar
                 secuencias → splits                    de etapas y se        números exactos de
                                                        explica la            cada ejecución,
                                                        restricción de 24     split y horizonte.
                                                        meses, pero los       
                                                        conteos clave siguen  
                                                        como guiones y las    
                                                        293 muestras son      
                                                        aproximadas.          

  P-02           Etiqueta heurística y   Parcial        Se publicaron las     Auditar alineación
                 posible leakage                        ocho reglas y se      temporal; ejecutar
                                                        reconoce la           ablación y aclarar
                                                        dependencia de        si es leakage
                                                        variables judiciales, contemporáneo o
                                                        pero no existe        circularidad de la
                                                        validación experta    etiqueta.
                                                        documentada ni        
                                                        ablación.             

  P-03           Separación              Parcial alto   Se documenta 49/21/30 Añadir fechas,
                 train/validation/test                  y early stopping con  tamaños y
                                                        validación. Faltan    protocolo
                                                        fechas de corte       reproducible.
                                                        exactas, conteos y    
                                                        evidencia de que el   
                                                        test no intervino en  
                                                        el ajuste manual.     

  P-04           Repeticiones,           Pendiente      La redacción ya no    Repetir con
                 intervalos y pruebas                   usa significancia,    múltiples semillas
                                                        pero los experimentos y reportar
                                                        siguen siendo de una  dispersión/IC; si
                                                        sola ejecución.       no es posible,
                                                                              limitar
                                                                              formalmente el
                                                                              alcance.

  P-05           Comparabilidad de       Pendiente      Persisten entradas,   Definir un
                 modelos                                balanceo, clipping,   protocolo común o
                                                        semillas y ajuste     presentar el
                                                        diferentes. Además,   estudio como
                                                        el texto se           comparación de
                                                        contradice sobre si   implementaciones
                                                        LightGBM usa 21 o 126 no equivalentes.
                                                        valores.              

  P-06           Métricas para           Parcial        Se discute recall y   Añadir PR-AUC,
                 desbalance y umbral                    se reconoce la falta  F1/F2, matrices,
                                                        de                    calibración y
                                                        PR-AUC/calibración;   umbral basado en
                                                        no se añaden esas     costos.
                                                        evaluaciones ni       
                                                        matrices de           
                                                        confusión.            

  P-07           Evaluación MLOps,       Parcial        Se documentan flujos  Agregar pruebas
                 datamart y dashboards                  y esquemas; las       funcionales,
                                                        capturas solo         integridad,
                                                        demuestran            latencia, fallos,
                                                        implementación.       disponibilidad y
                                                                              usuarios.

  P-08           Causalidad sobre redes  Resuelto en    Se habla de factores  Mantener este tono
                 neuronales              redacción      plausibles y no de    y evitar nuevas
                                                        causas demostradas.   afirmaciones
                                                                              causales.

  P-09           Uso incorrecto de       Resuelto       El capítulo se        Ampliar la
                 "revisión sistemática"  formalmente    denomina revisión     revisión
                                                        narrativa. Sin        estructurada con
                                                        embargo, la cobertura fuentes revisadas
                                                        y calidad de fuentes  por pares.
                                                        siguen siendo         
                                                        insuficientes.        

  P-10           Redacción y tono        Parcial        Se eliminó gran parte Corrección
                 autobiográfico                         de la primera persona lingüística
                                                        y el tono defensivo,  integral y
                                                        pero persisten        homogeneización
                                                        errores frecuentes y  del tono.
                                                        fragmentos propios de 
                                                        una auditoría.        
  ----------------------------------------------------------------------------------------------

# 3. Bloqueadores críticos antes de la defensa

  -----------------------------------------------------------------------------------------
  **ID**         **Página**     **Problema**        **Impacto**         **Corrección
                                                                        obligatoria**
  -------------- -------------- ------------------- ------------------- -------------------
  C-01           PDF 6--7       Resumen y abstract  La tesis carece de  Redactar ambos con
                                contienen           la síntesis         objetivo, datos,
                                únicamente          obligatoria en      unidad de análisis,
                                "\[Pendiente!\]".   español e inglés.   modelos, protocolo,
                                                                        resultados
                                                                        principales,
                                                                        limitaciones y
                                                                        contribución.

  C-02           PDF 33 y 49    Los conteos de      No se puede         Ejecutar el
                                integración,        reproducir ni       pipeline, guardar
                                secuencias, train,  verificar la        los conteos y
                                validación, test y  muestra efectiva.   sustituir todos los
                                muestras por                            guiones y
                                horizonte no están                      aproximaciones.
                                disponibles.                            

  C-03           PDF 36, 40--41 La Figura 4.4       La comparación      Confirmar el código
                                afirma entrada      puede estar basada  y describir
                                común de 6×21, pero en información      exactamente X para
                                el texto indica que distinta.           cada modelo;
                                LightGBM usa solo                       corregir figura,
                                21 características.                     texto y
                                                                        conclusiones.

  C-04           PDF 35--36,    La etiqueta se      El AUC puede        Auditar índices
                 51--54         construye con       reflejar la         temporales y
                                variables           definición          ejecutar
                                judiciales también  heurística más que  experimento sin
                                utilizadas como     anticipación real.  variables
                                predictores; no hay                     judiciales;
                                ablación ni                             documentar expertos
                                validación experta                      y validación.
                                reproducible.                           

  C-05           PDF 37--43, 56 La comparación usa  La conclusión       Equilibrar el
                                pesos, clipping,    comparativa no es   protocolo o
                                semillas, entradas, experimentalmente   reformular como
                                salidas y ajuste    sólida.             comparación
                                diferentes; CNN/MLP                     exploratoria de
                                no tienen                               implementaciones.
                                resultados por                          
                                horizonte                               
                                equivalentes.                           

  C-06           PDF 27--29 y   El Capítulo 3       Contradice la       Sustituirlos por
                 66--67         todavía incluye     corrección          artículos revisados
                                cinco preprints     bibliográfica       por pares de la
                                \[15\]--\[19\].     solicitada y        lista entregada y
                                                    debilita el estado  ampliar la tabla
                                                    del arte.           comparativa.
  -----------------------------------------------------------------------------------------

# 4. Revisión de elementos preliminares

  -----------------------------------------------------------------------------------------------
  **ID**      **Página**   **Elemento**   **Observación**    **Recomendación**    **Prioridad**
  ----------- ------------ -------------- ------------------ -------------------- ---------------
  P-01        PDF 1        Título         El título no fue   Usar un título       Alta
                                          modificado y sigue preciso, por         
                                          siendo extenso,    ejemplo: "Sistema    
                                          redundante y poco  integrado de         
                                          natural: "mediante inteligencia de      
                                          las técnicas de    negocio y MLOps para 
                                          análisis de        la predicción        
                                          Inteligencia       multi-horizonte de   
                                          artificial y de    crisis crediticias". 
                                          negocio".                               

  P-02        PDF 2        Autoría        Persisten "así     Corregir a "así      Media
                                          cómo",             como" y              
                                          "responsabilidad   "responsabilidad del 
                                          de el autor" y     autor"; revisar si   
                                          concordancias      corresponde "trabajo 
                                          impropias.         de titulación" y no  
                                                             "integración         
                                                             curricular".         

  P-03        PDF 4        Dedicatoria    Comillas           Normalizar comillas  Baja
                                          tipográficas       y decidir si la      
                                          invertidas y firma firma abreviada es   
                                          "OmarV".           institucionalmente   
                                                             aceptable.           

  P-04        PDF 6        Resumen        Texto vacío.       Completar antes de   Crítica
                                                             cualquier envío o    
                                                             defensa.             

  P-05        PDF 7        Abstract       Texto vacío.       Traducir             Crítica
                                                             académicamente el    
                                                             resumen final y      
                                                             revisar              
                                                             correspondencia      
                                                             exacta.              

  P-06        PDF 8--15    Índices        Se mezclan         Uniformar el idioma  Media
                                          "Contents", "List  conforme a la        
                                          of Tables", "List  plantilla; revisar   
                                          of Figures",       páginas en blanco y  
                                          "Bibliography" y   eliminar encabezados 
                                          "Appendices" con   de páginas           
                                          capítulos en       intencionalmente     
                                          español.           vacías.              
  -----------------------------------------------------------------------------------------------

# 5. Revisión del Capítulo 1: Introducción

La Introducción mejoró de forma clara: elimina el tono autobiográfico,
delimita el prototipo, formula una pregunta medible y reformula los
objetivos causales. La alineación entre pregunta, objetivo general y
contribuciones es ahora mucho más sólida.

  ------------------------------------------------------------------------------------------
  **ID**      **Página**   **Tipo**       **Observación**   **Acción**       **Prioridad**
  ----------- ------------ -------------- ----------------- ---------------- ---------------
  I-01        PDF 17--21   Contexto sin   Las afirmaciones  Añadir fuentes   Alta
                           referencias    sobre             sobre riesgo     
                                          fragmentación,    crediticio, BI,  
                                          tareas manuales e cooperativas     
                                          integración       ecuatorianas y   
                                          tecnológica no se sistemas de      
                                          apoyan en         apoyo a          
                                          bibliografía ni   decisiones.      
                                          evidencia                          
                                          institucional.                     

  I-02        PDF 17       Puntuación     "presenta la      Usar: "presenta  Baja
                                          pregunta, la      la pregunta y la 
                                          hipótesis; y,     hipótesis, y     
                                          establece..."     establece...".   
                                          contiene punto y                   
                                          coma y coma                        
                                          incorrectos.                       

  I-03        PDF 17       Puntuación     "indicadores de   Eliminar el      Baja
                                          morosidad...; se  punto y coma.    
                                          generan" separa                    
                                          indebidamente                      
                                          sujeto y verbo.                    

  I-04        PDF 18       Terminología   "productos de     Usar "sistema    Media
                                          bases de datos" y gestor de bases  
                                          "plataformas del  de datos" y      
                                          ciclo de vida de  "plataforma de   
                                          experimentos de   seguimiento del  
                                          modelos de        ciclo de vida de 
                                          inteligencia      modelos".        
                                          artificial" son                    
                                          expresiones poco                   
                                          naturales.                         

  I-05        PDF 20       Objetivo 2     "perceptrones     Sustituir por    Baja
                                          multicapa;        coma.            
                                          mediante" usa                      
                                          puntuación                         
                                          incorrecta.                        

  I-06        PDF 20       Contribución   Se afirma que la  Delimitar la     Alta
                                          comparación cubre contribución o   
                                          tres familias y   añadir           
                                          documenta la      resultados       
                                          degradación       equivalentes de  
                                          temporal, aunque  CNN y MLP.       
                                          los resultados                     
                                          completos por                      
                                          horizonte solo se                  
                                          muestran para                      
                                          LightGBM.                          

  I-07        PDF 20       Ortografía     "economía social  Corregir a       Baja
                                          y solidara".      "solidaria".     
  ------------------------------------------------------------------------------------------

# 6. Revisión del Capítulo 2: Marco teórico

La reorganización del marco teórico es adecuada y ahora incluye
predicción multi-horizonte, fuga de información, métricas y MLOps. Sin
embargo, la cobertura bibliográfica sigue siendo demasiado breve para
una tesis y la redacción requiere depuración.

  ----------------------------------------------------------------------------------------------
  **ID**      **Página**   **Tipo**       **Observación**   **Acción**           **Prioridad**
  ----------- ------------ -------------- ----------------- -------------------- ---------------
  T-01        PDF 22       Redacción      "Lo que es el     Integrarla al        Baja
                                          origen del        párrafo anterior.    
                                          desbalance" es                         
                                          una oración                            
                                          fragmentaria.                          

  T-02        PDF 23       Definición     La predicción     Citar literatura     Alta
                                          multi-horizonte   multi-periodo o      
                                          se define sin una multi-horizonte.     
                                          fuente                                 
                                          específica.                            

  T-03        PDF 23       Terminología   "CNN (del         Corregir "del        Media
                                          ingles...)", "MLP inglés" y definir    
                                          (del Multilayer   cada acrónimo con    
                                          Perceptron)" y la formulación          
                                          descripción de    estándar.            
                                          LightGBM son                           
                                          gramaticalmente                        
                                          defectuosas.                           

  T-04        PDF 24--25   Fuga de        La explicación es Añadir fuente y      Alta
                           información    pertinente, pero  explicar el          
                                          carece de         alineamiento         
                                          referencia        temporal t → t+h.    
                                          metodológica y no                      
                                          distingue leakage                      
                                          contemporáneo de                       
                                          uso legítimo de                        
                                          información                            
                                          histórica.                             

  T-05        PDF 25--26   AUC-ROC        "Área Bajo la     Usar "área bajo la   Media
                                          Curva y la        curva ROC (Receiver  
                                          Característica    Operating            
                                          Operativa del     Characteristic)".    
                                          Receptor" no es                        
                                          la expansión                           
                                          correcta.                              

  T-06        PDF 25--26   Métricas       Se recomienda     Definir PR-AUC,      Media
                                          PR-AUC y          Brier                
                                          calibración, pero score/calibración,   
                                          estos conceptos   selección de umbral  
                                          no se definen     y costos de error.   
                                          formalmente.                           

  T-07        PDF 26       MLOps          La sección está   Conservar; vincular  Resuelto
                                          bien orientada y  cada concepto con lo 
                                          usa referencias   evaluado realmente   
                                          revisadas por     en el prototipo.     
                                          pares.                                 
  ----------------------------------------------------------------------------------------------

# 7. Revisión del Capítulo 3: Estado del arte

El cambio de "revisión sistemática" a "revisión narrativa" es correcto.
No obstante, el capítulo ocupa apenas tres páginas de contenido y
continúa lejos del nivel esperado para sustentar la novedad del trabajo.

  --------------------------------------------------------------------------------------------------------------
  **ID**      **Página**   **Tipo**          **Observación**    **Acción**                       **Prioridad**
  ----------- ------------ ----------------- ------------------ -------------------------------- ---------------
  EA-01       PDF 27       Método de         Se menciona Google Presentar una revisión           Alta
                           búsqueda          Scholar, arXiv y   estructurada mínima:             
                                             "bases             Scopus/WoS/IEEE/ScienceDirect,   
                                             científicas", sin  fecha, cadenas, criterios y      
                                             bases específicas, número final.                    
                                             fecha exacta,                                       
                                             cadenas completas                                   
                                             o criterios.                                        

  EA-02       PDF 27--28   Preprints         Las referencias    Sustituir por publicaciones      Alta
                                             \[15\]--\[19\]     revisadas por pares; no basta    
                                             siguen siendo      con reconocer que la revisión es 
                                             preprints de       narrativa.                       
                                             arXiv.                                              

  EA-03       PDF 27--29   Cobertura         No se incluye      Añadir Duffie et al., Duan et    Alta
                                             literatura         al., Orth, Blumenstock et al.,   
                                             específica sobre   Bai et al. u otros trabajos      
                                             predicción         publicados.                      
                                             multi-periodo,                                      
                                             supervivencia o                                     
                                             multi-horizonte.                                    

  EA-04       PDF 27--29   BI/datamart       No se analiza      Añadir March y Hevner, Trieu,    Alta
                                             literatura sobre   Phillips-Wren y revisiones de    
                                             integración de BI, adopción/valor BI.               
                                             data warehouses,                                    
                                             dashboards y apoyo                                  
                                             a decisiones.                                       

  EA-05       PDF 27--29   Contexto local    No se incorporan   Añadir artículos revisados por   Alta
                                             fuentes sobre      pares y normativa SEPS           
                                             cooperativas,      relevante.                       
                                             economía popular y                                  
                                             solidaria o                                         
                                             regulación                                          
                                             ecuatoriana.                                        

  EA-06       PDF 29       Tabla 3.1         Solo compara cinco Ampliar a 15--25 estudios y usar Alta
                                             trabajos. "MLP     columnas: datos, unidad, modelo, 
                                             obtiene mejor      horizonte, split temporal,       
                                             resultado" no es   desbalance, métricas, XAI,       
                                             una limitación y   MLOps, BI y limitaciones reales. 
                                             "benchmark                                          
                                             clásico" tampoco.                                   

  EA-07       PDF 29       Posicionamiento   La frase           Usar "implementaciones evaluadas Alta
                                             "experimentos      bajo el protocolo disponible"    
                                             controlados" no    hasta equilibrar el experimento. 
                                             concuerda con                                       
                                             semillas no                                         
                                             fijadas, ajustes                                    
                                             desiguales y                                        
                                             entradas                                            
                                             posiblemente                                        
                                             distintas.                                          
  --------------------------------------------------------------------------------------------------------------

# 8. Revisión exhaustiva del Capítulo 4: Metodología

La Metodología es el capítulo que más mejoró. Ahora contiene fuentes,
unidad de análisis, diccionario, reglas de etiqueta, arquitectura de
modelos, split, recursos y reproducibilidad. Sin embargo, varios
elementos siguen siendo descripciones de información ausente y no
evidencia metodológica completa.

  -------------------------------------------------------------------------------------------------------------
  **ID**      **Página**   **Tema**               **Observación**         **Acción**            **Prioridad**
  ----------- ------------ ---------------------- ----------------------- --------------------- ---------------
  M-01        PDF 30       Diseño                 "El estudio es          Corregir a "práctico" Media
                                                  practico" carece de     y describirlo como    
                                                  tilde y la denominación estudio cuantitativo  
                                                  experimental debe       aplicado con          
                                                  matizarse por la        comparación           
                                                  ausencia de             experimental          
                                                  repeticiones y control  exploratoria.         
                                                  equivalente.                                  

  M-02        PDF 31       Sección 4.3            El título "Síntesis     Renombrar             Media
                                                  comparativa" no         "Arquitectura general 
                                                  corresponde al diagrama y flujo del sistema". 
                                                  de arquitectura.                              

  M-03        PDF 31       Figura 4.1             Usa "Modelo 1/2/3", no  Redibujar en vector,  Alta
                                                  identifica              eliminar marca y      
                                                  CNN/MLP/LightGBM y      mostrar Airflow,      
                                                  conserva una marca      MLflow, PostgreSQL,   
                                                  tenue                   modelos, datamart y   
                                                  "MermaidEditor.io".     Superset.             

  M-04        PDF 32--34   Referencias cruzadas   Se menciona "Tabla      Corregir todas las    Alta
                                                  4.2b", luego se indica  referencias           
                                                  que la Tabla 4.3        automáticas con       
                                                  contiene el             etiquetas LaTeX.      
                                                  diccionario, aunque                           
                                                  corresponde a la 4.4.                         

  M-05        PDF 33       Trazabilidad           La tabla mantiene       Sustituir por conteos Crítica
                                                  guiones en los conteos  exactos de filas      
                                                  más importantes.        integradas, bloques   
                                                                          elegibles, secuencias 
                                                                          y splits.             

  M-06        PDF 33       Muestra efectiva       "Aproximadamente 293" y Verificar y reportar  Crítica
                                                  "debe verificarse" no   el número exacto,     
                                                  son aceptables en una   fecha de extracción y 
                                                  versión final.          criterio que lo       
                                                                          produce.              

  M-07        PDF 33--34   Ventanas               No se explica qué       Documentar            Alta
                                                  ocurre con meses        ordenamiento,         
                                                  faltantes, bloques      agrupación,           
                                                  discontinuos, nuevas    continuidad,          
                                                  sucursales o cambios de relleno/eliminación y 
                                                  categoría.              generación de         
                                                                          ventanas.             

  M-08        PDF 35       Reglas de etiqueta     Las condiciones 1/2 y   Confirmar si son      Crítica
                                                  6/7 son umbrales        reglas independientes 
                                                  anidados y podrían      o alternativas;       
                                                  acumular pesos          incluir pseudocódigo  
                                                  simultáneamente.        exacto y ejemplos.    

  M-09        PDF 34--35   Nombres de variables   La tabla usa            Unificar nombres con  Alta
                                                  total_costo_judicial y  el código.            
                                                  total_gestion_cobro;                          
                                                  las reglas usan                               
                                                  costo_judicial y                              
                                                  gestión_cobro.                                

  M-10        PDF 35       Validación experta     Se afirma validación    Documentar perfil,    Crítica
                                                  por juicio experto,     número de expertos,   
                                                  pero no se identifican  procedimiento y       
                                                  expertos, proceso,      criterio de           
                                                  acuerdos o acta.        aprobación, o retirar 
                                                                          la afirmación.        

  M-11        PDF 35--36   Leakage/circularidad   El documento denomina   Auditar índices;      Crítica
                                                  "target leakage" a toda distinguir fuga       
                                                  reutilización de        contemporánea,        
                                                  variables judiciales.   circularidad de       
                                                  Si los predictores son  constructo y          
                                                  históricos y la         predictibilidad       
                                                  etiqueta es futura,     histórica.            
                                                  puede ser una señal                           
                                                  autorregresiva, no                            
                                                  leakage directo.                              

  M-12        PDF 35       Figura 4.2             El diagrama es ilegible Rediseñar como tabla  Alta
                                                  en tamaño de impresión  de reglas o diagrama  
                                                  y repite lo que ya está en dos niveles, con   
                                                  en la lista.            texto legible.        

  M-13        PDF 36--41   Entrada de LightGBM    Figura 4.4 afirma       Confirmar si LightGBM Crítica
                                                  entrada común 6×21;     usa el último mes,    
                                                  sección 4.7.3 indica 21 estadísticas de       
                                                  características por     ventana o 126         
                                                  horizonte.              valores; corregir     
                                                                          todo el documento.    

  M-14        PDF 37--40   Equidad del protocolo  CNN usa sample weights  Implementar           Crítica
                                                  y clipping; MLP no usa  condiciones           
                                                  pesos; LightGBM usa     comparables o         
                                                  scale_pos_weight, no    declarar              
                                                  clipping y semilla      explícitamente que se 
                                                  fija.                   comparan pipelines    
                                                                          heterogéneos.         

  M-15        PDF 39       Explicación MLP        "Puede explicar" es     Añadir experimento    Alta
                                                  razonable, pero no debe controlado con y sin  
                                                  presentarse como        ponderación.          
                                                  diagnóstico sin                               
                                                  ejecutar MLP con pesos.                       

  M-16        PDF 41--42   Ajuste                 No se documenta espacio Añadir tabla de       Crítica
                                                  de búsqueda, número de  tuning y garantizar   
                                                  configuraciones,        separación del test.  
                                                  criterio ni presupuesto                       
                                                  por modelo.                                   

  M-17        PDF 42--43   Split                  Se dan proporciones,    Reportar fechas       Alta
                                                  pero no cortes          exactas y tamaños;    
                                                  temporales exactos ni   aclarar cómo se forma 
                                                  conteos. La figura      validación dentro de  
                                                  2015--2022/2023--2026   2015--2022.           
                                                  debe reconciliarse con                        
                                                  70/30.                                        

  M-18        PDF 42--43   Semillas               CNN y MLP no fijan      Fijar semillas y      Crítica
                                                  semilla y no hay        ejecutar múltiples    
                                                  repeticiones.           corridas.             

  M-19        PDF 45--46   Umbral                 El umbral 0,5 es de     Optimizar con         Alta
                                                  implementación, no      validación y costos   
                                                  validado para negocio.  de falsos             
                                                                          negativos/falsos      
                                                                          positivos.            

  M-20        PDF 45--48   Reproducibilidad       Faltan hashes de        Completar entorno,    Alta
                                                  datos/código, versiones commit, fecha,        
                                                  de TensorFlow y         dependencias y        
                                                  LightGBM, modelo exacto archivos de           
                                                  del CPU y artefactos de configuración.        
                                                  ejecución.                                    

  M-21        PDF 48       Versiones              "Ubuntu Linux 24.02",   Copiar las versiones  Alta
                                                  "MLflow 3.14" y         directamente de       
                                                  "Superset 6.10" parecen comandos del entorno  
                                                  formatos/versiones que  y preservar puntos    
                                                  deben verificarse.      completos.            

  M-22        PDF 48       Resultados en          Los tiempos de 5        Trasladar a           Media
                           metodología            minutos y 2 horas son   Resultados y añadir   
                                                  resultados obtenidos.   protocolo de          
                                                                          medición.             
  -------------------------------------------------------------------------------------------------------------

# 9. Revisión exhaustiva del Capítulo 5: Resultados

La interpretación es considerablemente más prudente. Se corrige la tabla
que confundía el horizonte de un mes con promedios y se discute el
recall en horizontes largos. Sin embargo, la evidencia comparativa
continúa incompleta.

  --------------------------------------------------------------------------------------------------------
  **ID**      **Página**   **Tema**         **Observación**        **Acción**              **Prioridad**
  ----------- ------------ ---------------- ---------------------- ----------------------- ---------------
  R-01        PDF 49       Muestra          Se reconoce que 20.025 No mantener el capítulo Crítica
                                            registros no equivalen con una muestra         
                                            a secuencias, pero la  "aproximada".           
                                            cifra sigue sin                                
                                            verificarse.                                   

  R-02        PDF 51       Texto            Se afirma "Sin las     Actualizar el párrafo y Alta
                           desactualizado   ocho reglas... no es   discutir las reglas     
                                            posible", aunque las   disponibles.            
                                            reglas aparecen en la                          
                                            sección 4.6.                                   

  R-03        PDF 51       Figura 5.2       Caption contiene       Corregir.               Baja
                                            "variablepredictora"                           
                                            sin espacio.                                   

  R-04        PDF 52--53   Resultados por   Solo se tabulan 1, 3,  Incluir tabla completa  Alta
                           horizonte        6, 12 y 18 meses,      de 18 horizontes en el  
                                            aunque se afirma       capítulo o apéndice     
                                            disponer de 18         reproducible.           
                                            horizontes.                                    

  R-05        PDF 52--56   F1-score         La metodología declara Añadir F1 por horizonte Alta
                                            F1, pero las tablas de y modelo.               
                                            resultados no lo                               
                                            reportan.                                      

  R-06        PDF 54--56   CNN y MLP        Solo se presentan      Reportar por horizonte  Crítica
                                            métricas globales; no  y explicar              
                                            se definen su          macro/micro/promedio,   
                                            agregación ni          umbral y conjunto       
                                            resultados por cada    usado.                  
                                            salida.                                        

  R-07        PDF 55       Loss CNN         Una                    Revisar implementación  Alta
                                            binary_crossentropy    y añadir curvas AUC/PR  
                                            alrededor de 12,5      o matrices por          
                                            requiere verificar     horizonte.              
                                            reducción, sample                              
                                            weights y dimensiones;                         
                                            el valor no puede                              
                                            interpretarse                                  
                                            aisladamente.                                  

  R-08        PDF 56       Tabla 5.4        La propia tabla        Rehacer con mismas      Crítica
                                            reconoce unidades no   unidades y horizontes,  
                                            equivalentes; por      o presentarla como      
                                            tanto, no puede        resumen descriptivo no  
                                            sostener una           comparable.             
                                            comparación                                    
                                            concluyente.                                   

  R-09        PDF 56       Selección        LightGBM se selecciona Presentar selección     Alta
                                            por AUC promedio pese  provisional y           
                                            a ajuste desigual y    condicionada a          
                                            posible circularidad   ablación/validación.    
                                            de etiqueta.                                   

  R-10        PDF 56       Ejecuciones      Las diferencias entre  Añadir identificadores  Alta
                                            ejecución inicial y    MLflow, fecha, hash de  
                                            automatizada no tienen datos y parámetros; de  
                                            datos, splits o        lo contrario, eliminar  
                                            configuración          comparación.            
                                            trazables.                                     

  R-11        PDF 57--58   Figuras          El texto menciona      Corregir referencias    Alta
                                            Figuras 5.9--5.11,     cruzadas.               
                                            pero solo existe                               
                                            Figura 5.9 en el                               
                                            capítulo; las otras                            
                                            están en el Apéndice                           
                                            A.                                             

  R-12        PDF 58       Evaluación BI    La limitación está     Añadir casos de prueba, Alta
                                            correctamente          consultas, tiempos,     
                                            reconocida; faltan     integridad y usuarios   
                                            pruebas.               si se desea reivindicar 
                                                                   utilidad.               

  R-13        PDF 59       Texto            Se afirma ausencia de  Reescribir la           Alta
                           desactualizado   reglas, diccionario y  fortaleza/debilidad con 
                                            validación, aunque ya  las limitaciones que    
                                            se documentaron.       realmente permanecen:   
                                                                   conteos, validación     
                                                                   experta, ablation,      
                                                                   semillas y              
                                                                   equivalencia.           

  R-14        PDF 52--59   Baselines        No se incluyen         Agregar al menos un     Media
                                            baselines simples      baseline interpretable  
                                            (regresión logística,  y trivial para          
                                            predicción             contextualizar          
                                            mayoritaria,           AUC/recall.             
                                            persistencia del                               
                                            último estado).                                
  --------------------------------------------------------------------------------------------------------

# 10. Revisión del Capítulo 6: Conclusiones

  ----------------------------------------------------------------------------------------------------
  **ID**      **Página**   **Tema**         **Observación**    **Acción**              **Prioridad**
  ----------- ------------ ---------------- ------------------ ----------------------- ---------------
  C6-01       PDF 60       Síntesis         Se afirma          Sustituir               Alta
                                            "documentar        "completamente" por     
                                            completamente"     "ampliamente" o         
                                            reglas,            enumerar lo que aún     
                                            características,   falta.                  
                                            arquitecturas y                            
                                            split, aunque                              
                                            faltan conteos,                            
                                            validación de                              
                                            etiqueta y                                 
                                            detalles de                                
                                            tuning.                                    

  C6-02       PDF 61       Objetivo 2       Se indica que      Corregir la             Alta
                                            LightGBM tiene     contradicción.          
                                            "tuning                                    
                                            documentado", pero                         
                                            la sección 4.8                             
                                            declara que la                             
                                            búsqueda no se                             
                                            documentó.                                 

  C6-03       PDF 61--62   Contribuciones   Se presenta una    Delimitar a             Alta
                                            comparación de     "implementación de tres 
                                            tres enfoques para enfoques y comparación  
                                            18 horizontes,     con métricas            
                                            aunque CNN/MLP no  disponibles".           
                                            tienen resultados                          
                                            equivalentes por                           
                                            horizonte.                                 

  C6-04       PDF 62       Ética            La anonimización,  Añadir descripción de   Alta
                                            acceso restringido gobernanza o aprobación 
                                            y uso de datos     institucional, sin      
                                            reales deben       revelar datos           
                                            sustentarse con    sensibles.              
                                            procedimiento,                             
                                            autorización y                             
                                            resguardo.                                 

  C6-05       PDF 62       Redacción        "como como         Corregir.               Baja
                                            características"                           
                                            duplica palabra.                           

  C6-06       PDF 62--63   Leakage          La afirmación es   Usar "riesgo de         Crítica
                           confirmado       demasiado          circularidad y posible  
                                            categórica sin     fuga, sujeto a          
                                            demostrar si la    auditoría temporal".    
                                            misma observación                          
                                            temporal                                   
                                            interviene en X e                          
                                            y.                                         

  C6-07       PDF 63       Trabajo futuro   "al menos 10"      Usar "múltiples         Media
                                            semillas aparece   semillas" o justificar  
                                            sin justificación. el número mediante      
                                                               diseño de               
                                                               potencia/estabilidad.   

  C6-08       PDF 60--64   Estado final     Las conclusiones   Mantener coherencia en  Alta
                                            reconocen          todo el documento.      
                                            limitaciones                               
                                            graves que impiden                         
                                            uso productivo;                            
                                            esto es correcto,                          
                                            pero debe                                  
                                            reflejarse también                         
                                            en resumen y                               
                                            contribuciones.                            
  ----------------------------------------------------------------------------------------------------

# 11. Auditoría de tablas, figuras y referencias cruzadas

  ----------------------------------------------------------------------------
  **Elemento**      **Página**        **Evaluación**      **Acción
                                                          recomendada**
  ----------------- ----------------- ------------------- --------------------
  Tabla 3.1         PDF 29            Legible, pero       Ampliar y corregir
                                      insuficiente y con  categorías.
                                      "limitaciones" mal  
                                      definidas.          

  Figura 4.1        PDF 31            Diagrama genérico,  Rediseñar sin marca
                                      título de sección   y con componentes
                                      inadecuado y marca  reales.
                                      de editor visible.  

  Tabla 4.3         PDF 33            Contiene guiones en Completar valores
                                      los conteos         exactos.
                                      críticos.           

  Tabla 4.4         PDF 34            Texto pequeño y     Considerar
                                      referencia          orientación
                                      incorrecta desde el horizontal o
                                      párrafo anterior.   dividir; corregir
                                                          referencia.

  Figura 4.2        PDF 35            Texto del diagrama  Sustituir por
                                      prácticamente       tabla/pseudocódigo o
                                      ilegible a tamaño   figura de mayor
                                      de impresión.       tamaño.

  Figura 4.4        PDF 41            Visualmente clara,  Corregir después de
                                      pero su caption     confirmar las
                                      contradice la       entradas.
                                      sección LightGBM.   

  Tabla 4.7         PDF 48            Versiones           Completar y
                                      incompletas o       reformular.
                                      dudosas; caption    
                                      poco académico ("pc 
                                      de uso doméstico"). 

  Figura 5.1        PDF 50            Legible, aunque los Aumentar tipografía
                                      rótulos son         y usar lenguaje
                                      pequeños y el       descriptivo.
                                      análisis de         
                                      "severa"            
                                      multicolinealidad   
                                      requiere criterio.  

  Figura 5.4        PDF 53            Aporta visión de 18 Añadir tabla
                                      horizontes, pero    completa en
                                      los valores exactos apéndice.
                                      no están tabulados. 

  Figuras 5.7--5.9  PDF 57--58        Capturas de         Recortar interfaz y
                                      navegador; prueban  acompañar con casos
                                      existencia, no      de prueba.
                                      funcionamiento.     

  Referencias       PDF 57            No existen 5.10 y   Usar 5.9 y A.1--A.3.
  5.9--5.11                           5.11 en el          
                                      capítulo.           

  Apéndice A        PDF 69--72        La evidencia        Añadir URL/commit o
                                      complementaria está instrucciones
                                      mejor organizada,   institucionales de
                                      pero las rutas      acceso.
                                      locales no permiten 
                                      reproducibilidad    
                                      externa.            
  ----------------------------------------------------------------------------

# 12. Revisión bibliográfica

La bibliografía aumentó de 23 a 25 referencias y sustituyó varios
preprints de MLOps por artículos de IEEE Access. Sin embargo, el
objetivo de eliminar preprints no se cumplió: las referencias \[15\] a
\[19\] siguen registradas como arXiv. El Capítulo 3 tampoco incorporó la
mayor parte de la lista de artículos revisados por pares proporcionada
previamente.

  -----------------------------------------------------------------------
  **Dimensión**           **Estado**              **Recomendación**
  ----------------------- ----------------------- -----------------------
  Calidad de fuentes      Cinco preprints         Sustituir por versiones
                          \[15\]--\[19\].         publicadas o eliminar.

  Cobertura credit        Incluye benchmarks      Conservar y ampliar con
  scoring                 clave de Lessmann,      revisiones sistemáticas
                          Moscato y Gunnarsson.   recientes y estudios de
                                                  CNN/microcrédito.

  Multi-horizonte         Prácticamente ausente.  Añadir literatura
                                                  multi-periodo,
                                                  supervivencia y riesgo
                                                  temporal.

  MLOps                   Buena base general con  Conectar explícitamente
                          Testi, Kreuzberger,     con pruebas y
                          Sculley y Breck.        gobernanza del
                                                  prototipo.

  BI/datamart             Solo libros generales.  Añadir artículos sobre
                                                  valor de BI, data
                                                  warehousing y decision
                                                  support.

  Contexto ecuatoriano    Ausente.                Añadir cooperativas,
                                                  SFPS, SEPS y riesgo
                                                  crediticio local.

  Estilo                  Capitalización          Normalizar con BibTeX y
                          irregular de títulos y  verificar metadatos.
                          herramientas; URLs sin  
                          DOI.                    
  -----------------------------------------------------------------------

# 13. Revisión gramatical y de estilo: ejemplos representativos

  -----------------------------------------------------------------------
  **Página**              **Texto actual**        **Corrección sugerida**
  ----------------------- ----------------------- -----------------------
  PDF 1                   "TITULO"                "TÍTULO"

  PDF 2                   "así cómo" / "de el     "así como" / "del
                          autor"                  autor"

  PDF 17                  "la hipótesis; y,       "la hipótesis y
                          establece"              establece"

  PDF 17                  "cartera vencida; se    "cartera vencida se
                          generan"                generan"

  PDF 20                  "perceptrones           "perceptrones multicapa
                          multicapa; mediante"    mediante"

  PDF 20                  "economía social y      "economía social y
                          solidara"               solidaria"

  PDF 22                  "Lo que es el origen    Integrar la idea en la
                          del desbalance."        oración anterior.

  PDF 23                  "del ingles"            "del inglés"

  PDF 23                  "set de datos"          "conjunto de datos"

  PDF 25                  "Área Bajo la Curva y   "área bajo la curva ROC
                          la Característica       (Receiver Operating
                          Operativa del Receptor" Characteristic)"

  PDF 30                  "El estudio es          "El estudio es
                          practico"               práctico"

  PDF 33                  "mediante la            "mediante la
                          combinaciones"          combinación"

  PDF 34                  "veintiun               "veintiuna
                          características"        características"

  PDF 36                  "AUC individual \> 0,   "AUC-ROC individual \>
                          9"                      0,9"

  PDF 51                  "variablepredictora"    "variable predictora"

  PDF 62                  "como como              "como características"
                          características"        

  PDF 63                  "dvc o git-lfs"         "DVC o Git LFS"
  -----------------------------------------------------------------------

Estos ejemplos no constituyen una corrección exhaustiva. La tesis
necesita una revisión línea por línea después de resolver los cambios
metodológicos, para evitar corregir texto que posteriormente será
reemplazado.

# 14. Plan priorizado de correcciones

  --------------------------------------------------------------------------------------------------
  **Orden**   **Prioridad**   **Acción**         **Capítulo**     **Esfuerzo**   **Impacto**
  ----------- --------------- ------------------ ---------------- -------------- -------------------
  1           Crítica         Completar resumen  Preliminares     Bajo           Requisito formal
                              y abstract.                                        indispensable.

  2           Crítica         Confirmar entradas 4--6             Medio          Determina la
                              reales de                                          validez de la
                              LightGBM, CNN y                                    comparación.
                              MLP y corregir                                     
                              contradicciones.                                   

  3           Crítica         Generar conteos    4--5             Medio          Permite
                              exactos de                                         reproducibilidad.
                              integración,                                       
                              ventanas, splits y                                 
                              horizontes.                                        

  4           Crítica         Auditar etiqueta y 4--6             Alto           Protege validez del
                              alineación                                         resultado.
                              temporal; ejecutar                                 
                              ablación sin                                       
                              variables                                          
                              judiciales.                                        

  5           Crítica         Equilibrar         4--5             Alto           Hace defendible la
                              comparación:                                       hipótesis.
                              semillas, pesos,                                   
                              tuning y                                           
                              resultados por                                     
                              horizonte.                                         

  6           Alta            Reemplazar cinco   3/Bibliografía   Medio          Fortalece novedad y
                              preprints y                                        rigor.
                              ampliar Capítulo                                   
                              3.                                                 

  7           Alta            Añadir tabla       5                Alto           Mejora evaluación
                              completa de 18                                     bajo desbalance.
                              horizontes, F1,                                    
                              PR-AUC, matrices y                                 
                              calibración.                                       

  8           Alta            Eliminar           5--6             Bajo           Asegura coherencia
                              contradicciones y                                  interna.
                              textos                                             
                              desactualizados de                                 
                              capítulos 5 y 6.                                   

  9           Alta            Corregir           Todo             Medio          Mejora presentación
                              referencias                                        académica.
                              cruzadas, figuras                                  
                              ilegibles y marca                                  
                              de editor.                                         

  10          Alta            Completar          4/Apéndice       Medio          Fortalece
                              versiones, hashes,                                 reproducibilidad.
                              commits y                                          
                              evidencia MLflow.                                  

  11          Media           Revisión           Todo             Medio          Eleva calidad
                              lingüística                                        previa a defensa.
                              integral en                                        
                              español e inglés.                                  

  12          Media           Añadir pruebas     5/Apéndice       Alto           Sustenta la
                              funcionales de                                     contribución
                              MLOps/BI y                                         sistémica.
                              usuarios cuando                                    
                              sea viable.                                        
  --------------------------------------------------------------------------------------------------

# 15. Checklist para autorizar la defensa

  -----------------------------------------------------------------------
  **Comprobación**                    **Estado actual**
  ----------------------------------- -----------------------------------
  Resumen y abstract completos y      No
  equivalentes                        

  Título, autoría y preliminares      No
  corregidos                          

  Conteos exactos de datos, ventanas  No
  y splits                            

  Entradas de los tres modelos        No
  claramente documentadas             

  Reglas de crisis_flag validadas y   No
  temporalmente auditadas             

  Ablación sin variables judiciales   No

  Resultados equivalentes de los tres No
  modelos por horizonte               

  Semillas/repeticiones y             No
  variabilidad                        

  PR-AUC, F1, calibración y umbral    No

  Capítulo 3 sin preprints y con      No
  cobertura suficiente                

  Referencias cruzadas y figuras      No
  corregidas                          

  Contradicciones internas eliminadas No

  Revisión lingüística completa       No

  Código, versiones y commits         Parcial
  preservados                         

  Evidencia de implementación         Sí, como prototipo
  MLOps/BI                            

  Pregunta y objetivos delimitados    Sí

  Estructura general de capítulos     Sí

  Conclusiones prudentes y limitadas  Parcial
  al caso                             
  -----------------------------------------------------------------------

# 16. Dictamen final

La nueva versión evidencia un trabajo serio de corrección y mejora de
manera sustancial la estructura, la delimitación y la transparencia de
las limitaciones. La tesis tiene una base técnica valiosa y una
arquitectura de integración que puede constituir una contribución
aplicada pertinente.

Sin embargo, los problemas pendientes ya no son principalmente de
organización, sino de validez experimental y coherencia documental. La
ausencia de conteos exactos, la incertidumbre sobre las entradas de los
modelos, la etiqueta heurística no validada, la comparación no
equivalente, los resultados incompletos y los preprints restantes
impiden recomendar la defensa en el estado actual.

**Recomendación:**

Autorizar la defensa únicamente después de resolver los seis
bloqueadores críticos, completar el resumen y el abstract, eliminar las
contradicciones internas y realizar una corrección lingüística final. Si
no es posible ejecutar nuevos experimentos, la tesis debe reformularse
explícitamente como estudio de implementación y auditoría de un
prototipo, reduciendo el alcance de la comparación predictiva y de las
conclusiones.
