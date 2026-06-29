# Auditoría de Coherencia Diagnóstica BI-RADS mediante Procesamiento de Lenguaje Natural

Sistema de **auditoría automática de coherencia** en informes mamográficos. Detecta cuándo los hallazgos descritos por el radiólogo y la categoría BI-RADS asignada no concuerdan (*disociación semántica*), para señalar posibles incoherencias antes de la entrega del informe.

**Autores:** Sebastián Inostroza, Robinson Moreno · Programa de Doctorado en Ciencias e Ingeniería para la Salud, Universidad de Valparaíso.

---

## Contexto

El sistema BI-RADS asigna a cada mamografía una categoría (0–6) que define la conducta clínica. Su utilidad depende de que esa categoría concuerde con los hallazgos descritos. Cuando no concuerdan, una lesión sospechosa puede quedar registrada como benigna. Este proyecto entrena un modelo que infiere la categoría a partir de la sola descripción de los hallazgos y la contrasta con la declarada, generando una alerta cuando la discrepancia cruza la frontera entre zona segura (BI-RADS 0–3) y zona de riesgo (4–6).

---

## Estructura del repositorio

```
proyecto-birads-coherence-audit/
├── README.md
├── requirements.txt
├── .gitignore
├── src/
│   └── preprocessing.py                      # Módulo único de limpieza (fuente de verdad)
├── notebooks/
│   ├── 01_Curaduria_Preprocesamiento.ipynb   # Curaduría + EDA + dataset_clean.csv (SHA-256)
│   ├── BETO_BIRADS.ipynb                      # Clasificador (baseline) + Auditor BETO (sin fuga)
│   ├── Auditor_RoBERTa_Clinico.ipynb         # Auditor RoBERTa clínico (mejor 7 clases)
│   ├── Auditor_RoBERTa_FocalLoss.ipynb       # Experimento: focal loss
│   ├── Auditor_RoBERTa_Sintetico.ipynb       # Experimento: datos sintéticos (LLM)
│   ├── Auditor_RigoBERTa_Clinical.ipynb      # Experimento: RigoBERTa Clinical (XLM-R large, 2025)
│   ├── Balanceo_LogitAdj_LDAM.ipynb          # Balanceo: logit adjustment y LDAM
│   ├── Balanceo_MultiSemilla.ipynb           # Balanceo: comparación multi-semilla (media ± desv.)
│   ├── Evaluacion_Zonas.ipynb                # Evaluación por zonas del modelo de 7 clases
│   ├── Auditor_Zona_Binario.ipynb            # Modelo binario directo de zona (resultado principal)
│   ├── Zona_Binario_MultiSemilla.ipynb       # Verificación multi-semilla del AUC
│   ├── Ajuste_Umbral_Zona.ipynb              # Selección del punto de operación
│   ├── armar_csv_sinteticos.py               # Arma el CSV de informes sintéticos
│   └── colab/
│       ├── Colab_RoBERTa_512tokens.ipynb     # Experimento 512 tokens (GPU)
│       └── Colab_Hipotesis_256_vs_512.ipynb  # Hipótesis truncación: 256 vs 512 (GPU)
├── data/
│   ├── raw/                                   # Corpus original (4.357 informes)
│   ├── processed/                            # dataset_clean.csv (versionado por SHA-256)
│   └── synthetic/                           # sinteticos.csv (no validado clínicamente)
├── results/
│   ├── figures/                             # Figuras del análisis exploratorio
│   └── *.pt                                 # Modelos entrenados
└── tests/
    └── test_integridad.py                   # Pruebas de integridad y de no-fuga
```

---

## Instalación

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Hardware de referencia: Mac M4 (16 GB), aceleración MPS. Compatible con CUDA y CPU. Los experimentos más pesados (RigoBERTa, 512 tokens) se ejecutan en Google Colab (carpeta `notebooks/colab/`).

---

## Uso

Orden recomendado:

1. `01_Curaduria_Preprocesamiento.ipynb` — genera `data/processed/dataset_clean.csv` y su huella SHA-256.
2. `BETO_BIRADS.ipynb` — clasificador baseline y auditor BETO.
3. `Auditor_RoBERTa_Clinico.ipynb` — auditor con el mejor modelo (7 clases).
4. `Auditor_Zona_Binario.ipynb` — clasificador binario de zona (resultado principal).
5. `Zona_Binario_MultiSemilla.ipynb` — verificación del AUC con varias semillas.
6. `Ajuste_Umbral_Zona.ipynb` — selección del punto de operación.

Experimentos comparativos (opcionales): focal loss, datos sintéticos, RigoBERTa, logit adjustment / LDAM, evaluación por zonas, 512 tokens.

---

## Resultados

### Auditor (7 clases) — comparación de modelos

| Modelo | F1-macro (test real) |
|---|---|
| BETO (español general) | 0,4773 |
| **RoBERTa clínico (español)** | **0,5871** (una corrida) · 0,54 ± 0,04 (multi-semilla) |
| RigoBERTa Clinical (XLM-R large, 2025) | 0,4702 |

### Comparación de métodos de balanceo (RoBERTa clínico)

| Método | F1-macro |
|---|---|
| Ponderación de clases | 0,5871 (corrida) · 0,48 ± 0,05 (multi-semilla) |
| **Logit Adjustment** (Menon 2021) | 0,5865 (corrida) · **0,54 ± 0,04** (multi-semilla) |
| Focal loss | 0,5070 |
| Datos sintéticos (LLM) | 0,5494 |
| LDAM + DRW (Cao 2019) | 0,4747 |

Logit adjustment fue consistentemente mejor en la comparación multi-semilla (ganó en las tres semillas).

### Resultado principal — modelo binario de zona (multi-semilla)

| Métrica | Valor |
|---|---|
| **AUC-ROC** | **0,92 ± 0,03** |
| Sensibilidad | 0,70 |
| Especificidad | 0,97 |

El AUC es la métrica principal por ser independiente del umbral y robusta frente al desbalance. Las cifras se reportan como media ± desviación sobre tres semillas.

---

## Decisiones metodológicas

- **El auditor nunca ve la conclusión.** Su entrada son solo las observaciones, verificadas sin mención de la categoría. Infiere desde los hallazgos en lugar de copiar la etiqueta.
- **Sin fuga de datos.** La augmentación se aplica solo al conjunto de entrenamiento; el test es real e independiente. La integridad se verifica en `tests/`.
- **Reproducibilidad.** Módulo único de limpieza (`src/preprocessing.py`) y dataset versionado por SHA-256.
- **Reporte con varianza.** Con clases muy pequeñas, una sola corrida es inestable. Las cifras finales se reportan como media ± desviación sobre varias semillas.
- **Métrica según la tarea.** F1-macro para la formulación multiclase; AUC-ROC más sensibilidad/especificidad para la formulación binaria de zona.

---

## Hallazgos sobre balanceo y contexto

- Ningún método de balanceo supera la limitación de fondo (73 casos reales de riesgo). Se evaluaron ponderación de clases, focal loss, datos sintéticos, logit adjustment y LDAM.
- Logit adjustment iguala o supera levemente a la ponderación de clases; LDAM se desestabiliza con clases tan pequeñas.
- Ampliar la ventana de contexto de 256 a 512 tokens no mejora el auditor: en la entrada del auditor (observaciones) casi ningún informe supera los 256 tokens.

---

## Limitaciones y trabajo futuro

Las categorías de riesgo (BI-RADS 4–6) suman 73 informes en todo el corpus, lo que limita el desempeño y mantiene el trabajo en el nivel de prueba de concepto. Líneas futuras: incorporar más casos reales de riesgo, validación clínica prospectiva con radiólogos, e integración multimodal con variables clínicas estructuradas.

---

## Datos

Corpus público de informes mamográficos en español: Vázquez Noguera et al. (2025), *Data in Brief*. Los informes sintéticos en `data/synthetic/` fueron generados por un modelo de lenguaje y no están validados clínicamente; se usan solo en entrenamiento.
