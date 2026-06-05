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
Sistema:  Extrae BI-RADS asignado  → 1 (zona SEGURA)
Predice BI-RADS esperado  → 4 (zona RIESGO)
Detecta cruce de zona     → CRÍTICO
Salida:   🔴 ALERTA CRÍTICA — CRUCE DE ZONA
El texto sugiere BI-RADS 4 (zona de biopsia)
pero se asignó BI-RADS 1 (zona segura).
Revisión inmediata requerida.


```
---

## Arquitectura del Sistema

```

[Informe completo — texto libre]
↓
Extractor BI-RADS (regex escalable)
↓
Extractor Observations (regex)
↓
BETO Auditor (fine-tuned en español)
↓
Motor de Auditoría con Zonificación Clínica
↓
ALERTA


```
---

## Zonificación Clínica

El motor no usa solo distancia numérica.
Clasifica el BI-RADS en zonas clínicas:

```

ZONA SEGURA:  BI-RADS 0, 1, 2, 3  → vigilancia / benigno
ZONA RIESGO:  BI-RADS 4, 5, 6     → biopsia / maligno

```
Cualquier cruce entre zonas genera alerta crítica,
independientemente de la distancia numérica:

```

BI-RADS 3 → BI-RADS 4  (distancia=1) → 🔴 ALERTA CRÍTICA
BI-RADS 1 → BI-RADS 2  (distancia=1) → 🟡 REVISIÓN SUGERIDA

```
---

## Niveles de Alerta

| Alerta | Condición | Acción clínica |
|--------|-----------|----------------|
| ✅ COHERENTE | Sin discrepancia | Ninguna |
| 🟡 REVISIÓN SUGERIDA | Discrepancia leve, misma zona | Revisar antes de firmar |
| 🟠 ALERTA — SOBREESTIMACIÓN | Cruce zona riesgo → segura | Verificar hallazgos |
| 🔴 ALERTA CRÍTICA | Cruce zona segura → riesgo | Revisión inmediata |

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

## Extractor BI-RADS Escalable

Cubre todas las variaciones encontradas en sistemas
clínicos latinoamericanos:


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

---

## Hallazgo adicional

El extractor detectó 3 posibles errores de digitación
en el dataset original — el texto dice BI-RADS 2
pero la columna registra BI-RADS 1.
Documentado como limitación del dataset fuente.

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

## Uso

```python
# Auditar un informe completo
resultado = mvp_auditoria_v2(informe_texto)
imprimir_resultado_v2(resultado)
```

---

## Estructura del Repositorio


```

├── notebooks/
│   └── BETO_BIRADS.ipynb    ← pipeline completo paso a paso
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