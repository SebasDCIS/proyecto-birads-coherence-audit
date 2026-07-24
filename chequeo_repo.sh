#!/usr/bin/env bash
# ---------------------------------------------------------------
#  Chequeo del repositorio  ·  proyecto-birads-coherence-audit
#  Solo lee informacion. No modifica, no confirma, no envia nada.
#  Uso:  bash chequeo_repo.sh
# ---------------------------------------------------------------

cd "$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "No estas dentro de un repositorio git."; exit 1; }

linea(){ printf '\n\033[1;34m%s\033[0m\n' "── $1 ──────────────────────────────────────────"; }

linea "1. Rama y sincronizacion"
git status -sb | head -1
echo "Commits locales sin enviar:"
git log origin/main..HEAD --oneline 2>/dev/null | sed 's/^/   /' || echo "   (no se pudo comparar con origin)"
[ -z "$(git log origin/main..HEAD --oneline 2>/dev/null)" ] && echo "   ninguno"

linea "2. Cambios sin confirmar"
if [ -z "$(git status --porcelain)" ]; then
  echo "   arbol de trabajo limpio"
else
  git status --porcelain | sed 's/^/   /'
fi

linea "3. Historial y etiquetas"
echo "Total de commits: $(git rev-list --count HEAD)"
echo "Ultimos 5:"
git log -5 --pretty=format:'   %h  %ad  %s' --date=short
echo ""
TAGS=$(git tag | tr '\n' ' '); echo "Etiquetas: ${TAGS:-ninguna}"
echo "Ramas:"
git branch -a | sed 's/^/   /'

linea "4. Exclusion de modelos entrenados"
echo "Reglas .pt en .gitignore:"
grep -n '\.pt' .gitignore 2>/dev/null | sed 's/^/   /' || echo "   NINGUNA REGLA (revisar)"
echo "Archivos .pt rastreados por git (deberia decir ninguno):"
PTS=$(git ls-files | grep '\.pt$')
if [ -n "$PTS" ]; then echo "$PTS" | sed 's/^/   ATENCION: /'; else echo "   ninguno"; fi
echo "Peso total de modelos en disco:"
du -ch $(git status --ignored --porcelain 2>/dev/null | grep '\.pt$' | sed 's/^!! //') 2>/dev/null | tail -1 | sed 's/^/   /'

linea "5. Inventario del proyecto"
for d in data notebooks src tests results demo; do
  if [ -d "$d" ]; then
    printf '   %-12s %s archivos\n' "$d/" "$(find $d -type f | wc -l | tr -d ' ')"
  else
    printf '   %-12s NO EXISTE\n' "$d/"
  fi
done
echo "   cuadernos: $(find notebooks -name '*.ipynb' 2>/dev/null | wc -l | tr -d ' ')"

linea "6. Coherencia del README"
if grep -qi 'BETO' README.md 2>/dev/null; then
  echo "   ATENCION: el README menciona BETO."
  grep -ni 'BETO' README.md | head -5 | sed 's/^/      /'
  echo "   El modelo final es RoBERTa clinico. Conviene actualizarlo."
else
  echo "   sin menciones a BETO"
fi
grep -qi 'RoBERTa' README.md 2>/dev/null && echo "   menciona RoBERTa: si" || echo "   menciona RoBERTa: NO"
grep -qi 'netlify\|github.io' README.md 2>/dev/null && echo "   enlace a la demo: si" || echo "   enlace a la demo: NO"

linea "7. Interfaz publicada"
DEMO=$(ls demo/*.html 2>/dev/null | head -1)
if [ -n "$DEMO" ]; then
  echo "   archivo: $DEMO"
  grep -q 'estaNegado' "$DEMO" && echo "   maneja negaciones: SI (version corregida)" \
                               || echo "   maneja negaciones: NO (version con el error)"
  grep -q '1889' "$DEMO" && echo "   matriz de confusion real: si" || echo "   matriz de confusion real: NO"
else
  echo "   no se encontro html en demo/"
fi

linea "8. Pruebas de integridad"
if [ -f tests/test_integridad.py ]; then
  python tests/test_integridad.py 2>&1 | sed 's/^/   /'
else
  echo "   no se encontro tests/test_integridad.py"
fi

linea "Fin del chequeo"
echo "Este script no modifico nada. Copia la salida completa para revisarla."
