# Informes sintéticos

`sinteticos.csv` contiene 210 descripciones de hallazgos mamográficos generadas con **Gemini** (Google, aplicación web, junio de 2026): 70 de BI-RADS 4, 70 de BI-RADS 5 y 70 de BI-RADS 6. La interfaz web no registra la versión exacta del modelo.

**Cómo se pidieron.** Cada solicitud pedía 70 descripciones de la sección de hallazgos con la estructura de los informes del corpus (técnica, piel y pezón, densidad ACR, hallazgo con localización, tamaño y márgenes) y los rasgos típicos de la categoría. Se prohibía mencionar la conclusión, la categoría o la sigla BI-RADS. Como referencia de estilo, cada solicitud incluyó informes del corpus público y anonimizado; dos de ellos pertenecían al conjunto de prueba.

**Uso.** Solo en entrenamiento, en un experimento exploratorio de una corrida (`notebooks/Auditor_RoBERTa_Sintetico.ipynb`, F1-macro 0,5973). Por lo anterior, ese resultado puede estar sobreestimado y no se adoptó. Validación y prueba contienen solo informes reales.

**Limitación.** Los textos no fueron revisados por radiólogos.

`armar_csv_sinteticos.py` arma el CSV a partir de las tres salidas del modelo.
