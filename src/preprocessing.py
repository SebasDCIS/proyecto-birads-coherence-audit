"""preprocessing.py — Módulo único de limpieza compartido (proyecto BI-RADS).
Replica EXACTAMENTE la limpieza validada en main. No alterar sin re-validar."""
import re
import pandas as pd

ABREVIATURAS = {
    r'\bcse\b':    'cuadrante superoexterno',
    r'\bcsi\b':    'cuadrante superointerno',
    r'\bcie\b':    'cuadrante inferoexterno',
    r'\bcii\b':    'cuadrante inferointerno',
    r'\bucs\b':    'union de cuadrantes superiores',
    r'\buci\b':    'union de cuadrantes inferiores',
    r'\bgli\b':    'ganglio linfatico intramamario',
    r'\blpm\b':    'ultimo periodo menstrual',
    r'\bfur\b':    'fecha de ultima regla',
    r'\bacr\b':    'american college of radiology',
    r'\bbirads\b': 'bi-rads',
}

MAX_LENGTH = 256
MODELO_BASE = 'dccuchile/bert-base-spanish-wwm-cased'
SEP = ' [SEP] '

# Elimina menciones de la categoría (p. ej. "bi-rads 4", "(bi-rads 0)") del texto.
# Se usa SOLO en la entrada del auditor: debe inferir la categoría, no leerla.
_PATRON_BIRADS = re.compile(r'\(?\s*bi[\s\-]?rads[\s:]*\d*\s*\)?', re.IGNORECASE)


def limpiar_texto(texto):
    if pd.isna(texto) or str(texto).strip() == '':
        return ''
    texto = str(texto)
    texto = re.sub(r'[\r\n\t]+', ' ', texto)
    texto = re.sub(r'-{2,}', ' ', texto)
    texto = texto.lower().strip()
    for patron, expansion in ABREVIATURAS.items():
        texto = re.sub(patron, expansion, texto)
    texto = re.sub(r'[^a-záéíóúüñ0-9\s\.,;:\-\(\)/]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto


def quitar_categoria_birads(texto):
    """Elimina menciones de 'BI-RADS N' del texto de hallazgos para que el
    auditor infiera la categoria en lugar de leerla. Si el texto no contiene
    la categoria, se devuelve sin cambios (no altera el resto del corpus)."""
    s = str(texto)
    if not _PATRON_BIRADS.search(s):
        return s
    s = _PATRON_BIRADS.sub('', s)
    s = re.sub(r'\s+([.,;:)])', r'\1', s)   # espacio antes de puntuacion
    s = re.sub(r'\(\s*\)', '', s)           # parentesis vacios
    s = re.sub(r'\s{2,}', ' ', s).strip()   # espacios dobles
    return s


def construir_inputs(df):
    df = df.copy()
    df['obs_clean']     = df['Observations'].apply(limpiar_texto)
    df['concl_clean']   = df['Conclusion'].apply(limpiar_texto)
    # texto_input (clasificador) conserva la conclusion completa, con su categoria.
    df['texto_input']   = df['obs_clean'] + SEP + df['concl_clean']
    # auditor_input NO debe contener la categoria: se elimina de las observaciones.
    df['auditor_input'] = df['obs_clean'].apply(quitar_categoria_birads)
    return df


def detectar_entorno():
    import torch
    try:
        import google.colab  # noqa
        en_colab = True
    except ImportError:
        en_colab = False
    if torch.cuda.is_available():
        device = 'cuda'
    elif torch.backends.mps.is_available():
        device = 'mps'
    else:
        device = 'cpu'
    return en_colab, device
