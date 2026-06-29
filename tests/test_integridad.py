"""
Pruebas de integridad del proyecto BI-RADS.

Verifican las invariantes que sostienen la validez de los resultados:
  1. El dataset curado existe y tiene las columnas esperadas.
  2. La entrada del auditor NO menciona la categoría BI-RADS (no puede "leer" la respuesta).
  3. Ningún registro (ID_R) aparece a la vez en entrenamiento y prueba (chequeo de no-fuga REAL).
  4. (Opcional) La huella SHA-256 del dataset coincide con la registrada.

Nota: el chequeo de no-fuga se hace por ID de registro, no por texto idéntico.
El corpus contiene informes boilerplate (mamografías normales) cuyo texto se repite
entre pacientes distintos; eso es natural y no constituye fuga. La fuga real sería
que el MISMO registro apareciera en train y test, lo cual se verifica aquí.

Uso:
    python tests/test_integridad.py
    # o con pytest:  pytest tests/test_integridad.py -v
"""
import hashlib
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

RAIZ = Path(__file__).resolve().parents[1]
DATASET = RAIZ / "data" / "processed" / "dataset_clean.csv"
SEED = 42
SHA256_ESPERADO = "23ed3e868c190a9274af2b194d11dcf1dc422c8c75919dc4c8b74eb34e113b68"
COLUMNAS_ESPERADAS = {"auditor_input", "texto_input", "BI-RADS", "ID_R"}


def _cargar():
    assert DATASET.exists(), f"No se encuentra el dataset: {DATASET}"
    return pd.read_csv(DATASET, encoding="utf-8")


def test_dataset_existe_y_columnas():
    df = _cargar()
    faltantes = COLUMNAS_ESPERADAS - set(df.columns)
    assert not faltantes, f"Faltan columnas: {faltantes}"
    assert len(df) > 0, "El dataset está vacío."
    print(f"OK · dataset con {len(df)} filas y columnas esperadas.")


def test_auditor_input_sin_categoria():
    df = _cargar()
    patron = re.compile(r"bi[\s\-]?rads", re.IGNORECASE)
    n = int(df["auditor_input"].astype(str).apply(lambda t: bool(patron.search(t))).sum())
    assert n == 0, f"{n} entradas del auditor mencionan 'BI-RADS' (riesgo de fuga de etiqueta)."
    print("OK · 0% de las entradas del auditor mencionan la categoría.")


def test_sin_fuga_train_test():
    """No debe haber el MISMO registro (ID_R) en train y test."""
    df = _cargar()
    X = df["auditor_input"].values
    y = df["BI-RADS"].values
    ids = df["ID_R"].values
    X_tv, X_te, y_tv, y_te, id_tv, id_te = train_test_split(
        X, y, ids, test_size=0.15, random_state=SEED, stratify=y
    )
    X_tr, X_va, y_tr, y_va, id_tr, id_va = train_test_split(
        X_tv, y_tv, id_tv, test_size=0.176, random_state=SEED, stratify=y_tv
    )
    overlap = set(id_tr) & set(id_te)
    assert not overlap, f"{len(overlap)} registros (ID_R) aparecen en train y test (fuga real)."
    print(f"OK · sin solapamiento de registros entre train ({len(id_tr)}) y test ({len(id_te)}).")


def test_sha256_dataset():
    h = hashlib.sha256(DATASET.read_bytes()).hexdigest()
    if h != SHA256_ESPERADO:
        print(f"AVISO · SHA-256 distinto del registrado.\n  esperado: {SHA256_ESPERADO}\n  actual:   {h}")
        print("  Si regeneraste el dataset a propósito, actualiza SHA256_ESPERADO.")
    else:
        print("OK · SHA-256 del dataset coincide con el registrado.")


if __name__ == "__main__":
    fallos = 0
    for p in [test_dataset_existe_y_columnas, test_auditor_input_sin_categoria,
              test_sin_fuga_train_test, test_sha256_dataset]:
        try:
            p()
        except AssertionError as e:
            fallos += 1
            print(f"FALLA · {p.__name__}: {e}")
    print("-" * 50)
    print("Todas las pruebas pasaron." if fallos == 0 else f"{fallos} prueba(s) con fallas.")
    sys.exit(1 if fallos else 0)
