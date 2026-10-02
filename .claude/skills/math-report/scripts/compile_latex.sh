#!/usr/bin/env bash
# Compile a .tex file to PDF. Auto-detects Hebrew/RTL and then uses XeLaTeX (with the
# parenthesis fix); otherwise pdflatex. Installs a minimal TeX Live on first use.
# Usage: compile_latex.sh <file.tex>
set -euo pipefail
TEX_FILE="$1"; DIR="$(dirname "$TEX_FILE")"; BASE="$(basename "$TEX_FILE")"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if grep -qE 'setmainlanguage\{hebrew\}|setmainlanguage\{arabic\}|\{hebrew\}|[א-ת]' "$TEX_FILE"; then
  ENGINE=xelatex
else
  ENGINE=pdflatex
fi

if ! command -v "$ENGINE" >/dev/null 2>&1 || { [ "$ENGINE" = xelatex ] && ! kpsewhich bidi.sty >/dev/null 2>&1; }; then
  echo "installing TeX Live packages for $ENGINE (one-time setup)..."
  PKGS="texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-science"
  [ "$ENGINE" = xelatex ] && PKGS="$PKGS texlive-xetex texlive-lang-other texlive-lang-arabic"
  apt-get install -y --no-install-recommends $PKGS >/dev/null
fi

if [ "$ENGINE" = xelatex ]; then
  python3 "$HERE/fix_rtl_parens.py" "$TEX_FILE"
fi

cd "$DIR"
for i in 1 2; do
  $ENGINE -interaction=nonstopmode "$BASE" > "latex_run$i.log" 2>&1 || { grep -E "^!" -A3 "latex_run$i.log" | head -40; exit 1; }
done
echo "Compiled with $ENGINE: ${BASE%.tex}.pdf"
if [ "$ENGINE" = xelatex ]; then python3 "$HERE/check_rtl_parens.py" "${BASE%.tex}.pdf"; fi
