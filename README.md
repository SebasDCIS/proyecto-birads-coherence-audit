# 🏥 Auditoría de Coherencia Diagnóstica BI-RADS con BETO

**Autores:** Sebastián Inostroza · Robinson Moreno  
**Institución:** Universidad de Valparaíso, Chile  
**Año:** 2025

---

## ¿Qué hace este proyecto?

Detecta **disociación semántica** en informes de mamografía:
cuando un radiólogo describe hallazgos de alto riesgo
pero asigna una categoría BI-RADS baja.

```

Texto:    "nódulo espiculado, márgenes irregulares, mama densa tipo C"
BI-RADS:   2 (Benigno) ← ⚠️ CONTRADICCIÓN
Sistema:  🔴 ALERTA CRÍTICA — posible subestimación oncológica


```

---

## Resultados

| Modelo | F1 Macro | Accuracy |
|--------|----------|----------|
| BETO Clasificador | 0.8786 | 98.01% |
| BETO Auditor | 0.8781 | — |
| Estado del arte (López-Úbeda 2024) | 0.74 | — |

---

## Dataset

4.357 informes mamográficos en español (Paraguay, 2019-2024).  
Fuente: Vázquez Noguera et al. (2025) — *Data in Brief*.

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
│   └── BETO_BIRADS.ipynb   ← pipeline completo
├── results/
│   ├── figures/             ← gráficos
│   └── metrics/             ← métricas JSON
└── requirements.txt

```