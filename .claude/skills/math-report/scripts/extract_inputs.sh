#!/usr/bin/env bash
# Turn user-supplied input files (.rar/.zip/.7z/.tar*, .pdf, .docx, .txt/.md) into plain text.
# Usage: extract_inputs.sh <input-file-or-dir> <out-dir>
# Result: <out-dir>/files/... (extracted originals) and <out-dir>/text/*.txt (one per document)
set -uo pipefail
IN="$1"; OUT="$2"; mkdir -p "$OUT/files" "$OUT/text"
need() { command -v "$1" >/dev/null 2>&1; }

case "${IN,,}" in
  *.rar|*.7z|*.zip|*.tar|*.tar.gz|*.tgz|*.tar.bz2)
    if ! need 7z; then apt-get install -y --no-install-recommends 7zip p7zip-rar >/dev/null 2>&1 || apt-get install -y --no-install-recommends p7zip-full p7zip-rar >/dev/null 2>&1; fi
    7z x -y -o"$OUT/files" "$IN" >/dev/null ;;
  *) if [ -d "$IN" ]; then cp -r "$IN"/. "$OUT/files/"; else cp "$IN" "$OUT/files/"; fi ;;
esac

# nested archives (one level)
find "$OUT/files" -type f \( -iname '*.rar' -o -iname '*.zip' -o -iname '*.7z' \) | while read -r a; do
  7z x -y -o"${a%.*}_x" "$a" >/dev/null 2>&1; done

find "$OUT/files" -type f | sort | while read -r f; do
  b="$(basename "$f")"; t="$OUT/text/${b%.*}.txt"
  case "${f,,}" in
    *.pdf)  pdftotext -layout "$f" "$t" 2>/dev/null
            # scanned PDF (almost no text)? OCR if tesseract is available
            if [ "$(wc -c < "$t")" -lt 200 ] && need tesseract && need pdftoppm; then
              tmp="$(mktemp -d)"; pdftoppm -r 200 -png "$f" "$tmp/p"
              for p in "$tmp"/p*.png; do tesseract "$p" - -l heb+eng 2>/dev/null; done > "$t"; rm -rf "$tmp"
            fi ;;
    *.docx) python3 - "$f" "$t" <<'PY'
import sys, zipfile, re
z = zipfile.ZipFile(sys.argv[1]); x = z.read('word/document.xml').decode('utf8')
x = re.sub(r'</w:p>', '\n', x); open(sys.argv[2], 'w').write(re.sub(r'<[^>]+>', '', x))
PY
            ;;
    *.txt|*.md|*.tex|*.csv) cp "$f" "$t" ;;
  esac
done
echo "extracted files:"; find "$OUT/files" -type f | sort
echo "text outputs (chars):"; wc -c "$OUT"/text/*.txt 2>/dev/null
