# 🏥 Auditoría de Coherencia Diagnóstica BI-RADS con BETO

**Autores:** Sebastián Inostroza · Robinson Moreno  
**Institución:** Universidad de Valparaíso, Chile  
**Año:** 2026

---

## ¿Qué hace este proyecto?

Detecta **disociación semántica** en informes de mamografía:
cuando un radiólogo describe hallazgos de alto riesgo
pero asigna una categoría BI-RADS baja.

```

Entrada:  Informe completo (texto libre)
"mamas densas tipo C, nódulo espiculado..."
"BI-RADS 1. Control anual."
Sistema:  Extrae BI-RADS asignado → 1
Predice BI-RADS esperado → 4
Detecta discrepancia → 3 categorías
Salida:   🔴 ALERTA CRÍTICA — SUBESTIMACIÓN DE RIESGO
El texto sugiere BI-RADS 4 pero se asignó BI-RADS 1.
Posible subestimación oncológica.


```
---

## Arquitectura del Sistema

```

[Informe completo]
↓
Extractor BI-RADS (regex escalable) → BI-RADS asignado
↓
Extractor Observations (regex)      → texto descriptivo
↓
BETO Auditor (fine-tuned)           → BI-RADS predicho
↓
Motor de Auditoría                  → nivel de alerta


```
---

## Resultados

---

## Resultados

| Componente | Métrica | Valor |
|---|---|---|
| Extractor BI-RADS | Aciertos | 4354/4357 (99.93%) |
| Clasificador BETO | F1 Macro | 0.8786 |
| Clasificador BETO | Accuracy | 98.01% |
| Auditor BETO | F1 Macro | 0.9078 |
| Auditor BETO | Accuracy | 92.97% |
| Estado del arte (López-Úbeda 2024) | F1 | 0.74 |
| **Mejora sobre estado del arte** | **ΔF1** | **+0.17** |

---

## Niveles de Alerta del Motor de Auditoría

| Alerta | Condición | Acción |
|---|---|---|
| ✅ COHERENTE | Discrepancia = 0 | Ninguna |
| 🟡 REVISIÓN SUGERIDA | Discrepancia = 1 | Revisar antes de firmar |
| 🟠 SOBREESTIMACIÓN | Predicho < asignado en 2+ | Verificar hallazgos |
| 🔴 ALERTA CRÍTICA | Predicho > asignado en 2+ | Revisión inmediata |

---

## Extractor BI-RADS Escalable

Cubre todas las variaciones encontradas en sistemas clínicos latinoamericanos:

```

BI-RADS 2       → estándar
BI-RADS® 2      → símbolo marca registrada
BI-RADS O       → letra O en lugar de 0
BI-RADS 4A/4B/4C → subcategorías
BI-RADAS 4      → error tipográfico real
BR4, BR-4       → abreviaciones
Categoría 2     → escritura alternativa
BI-RADS II      → números romanos


```

---

## Dataset

4.357 informes mamográficos en español (Paraguay, 2019-2024).  
Fuente: Vázquez Noguera et al. (2025) — *Data in Brief*.  
⚠️ No incluido en el repositorio por privacidad clínica.


---

## Instalación

```bash
git clone https://github.com/SebasDCIS/proyecto-birads-coherence-audit.git
cd proyecto-birads-coherence-audit
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Estructura

```

├── notebooks/
│   └── BETO_BIRADS.ipynb   ← pipeline completo paso a paso
├── results/
│   ├── figures/
│   │   └── evaluacion_final.png
│   └── metrics/
│       └── metricas_finales.json
└── requirements.txt

```

---

## Referencias

- Vázquez Noguera et al. (2025). *Data in Brief*. https://doi.org/10.1016/j.dib.2025.111549
- López-Úbeda et al. (2024). *Clinical Radiology*. https://doi.org/10.1016/j.crad.2023.09.009
- Dratsch et al. (2023). *Radiology*. https://doi.org/10.1148/radiol.222176
- Hussain et al. (2024). *BMC Medical Informatics*. https://doi.org/10.1186/s12911-024-02717-7