---
name: math-report
description: Turn a mathematical expression, equation, financial formula, lecture/exercise material (a link, uploaded PDF/DOCX files, or a .rar/.zip archive of them), or dataset the user gives you into a rigorous investigation — derivation, step-by-step explanation, worked example, and (for financial/statistical topics) numeric tables or sensitivity analysis — delivered as a typeset LaTeX (.tex) source file plus a compiled PDF, in English or Hebrew (Hebrew text with English equations). Use this skill whenever the user invokes it by name ("use the math-report skill", "use my math skill"), or asks to investigate/summarize/derive/solve a mathematical or financial equation (e.g. compound interest, amortization, present value, quadratic/polynomial equations, calculus problems, statistics) AND wants the result as a PDF or LaTeX document rather than just a chat explanation.
---

# Math Report

Produce a self-contained, textbook-quality writeup of a mathematical or
financial topic the user hands you, delivered as both a `.tex` source file
and a compiled `.pdf`.

## When this triggers

- The user explicitly says to use this skill (by name, or "my math skill").
- The user gives a mathematical expression, equation, or financial formula
  (e.g. `A = P(1 + r/n)^{nt}`, a quadratic, an amortization schedule) and
  asks for investigation, derivation, solving, or summarization **and**
  wants a document/PDF out of it — not just a chat-window explanation.

If the user just asks a quick math question with no mention of a
document/PDF/report, answer inline instead — don't invoke this skill for
things that don't need a deliverable file.


## Inputs: link, PDFs, or an archive

The material to work from can be given in any of these forms:

- **A link** -- fetch it (WebFetch). If the network policy blocks the host (EGRESS_BLOCKED), tell the
  user the host name and that they can either allow it in the environment's Network access settings or
  upload the files instead (a .rar/.zip avoids any upload-count limit). Don't guess the content.
- **Uploaded files** (PDF, DOCX, TXT/MD) and **archives** (.rar, .zip, .7z, .tar.gz): run
  `scripts/extract_inputs.sh <file-or-dir> <workdir>`. It unpacks archives (installs 7zip-rar if needed),
  and converts every PDF/DOCX/TXT to text under `<workdir>/text/`. Scanned PDFs are OCR'd with
  tesseract when available. Then read the text files (Read tool) -- Hebrew PDFs usually extract fine but
  with bidi marks and visually-ordered formulas, so double-check any formula you rely on.
  Say which of the files the user mentioned are actually present (e.g. "the archive had tirgulim 1-13 but not
  the solutions file") so gaps are visible.
- If the user restricts scope ("only these sections"), obey it and say what was left out.

Read the material fully before writing; a theorem list or summary has to match the actual exercises.
Verify any worked solution you add to the report (sympy) before typesetting it.

## Hebrew (and other RTL) reports

When the user wants the document in Hebrew (equations stay English):

1. Start from `assets/template_hebrew.tex` (XeLaTeX + polyglossia + FreeSerif, colored boxes for
   definitions / theorems / methods / examples). Use full Hebrew words in the text; keep every formula
   in `$...$` or `\[...\]`; never put Hebrew inside math (use `\text` outside math instead).
2. Compile with `scripts/compile_latex.sh file.tex`. It detects Hebrew, uses **XeLaTeX** (not pdflatex),
   and first runs `scripts/fix_rtl_parens.py`, which works around a XeLaTeX+bidi bug: a parenthesis whose
   inner neighbour is math/Latin letters is drawn reversed. The script rewrites those parentheses as
   `\lpar{}`/`\rpar{}` (typed swapped), turns `\ref` into `\rf` (a math-mode number) and writes the macro
   definitions. It edits the file in place (backup: `file.tex.orig`), so deliver the fixed `.tex`.
   Don't write a bare digit next to a parenthesis in Hebrew text (e.g. `(2 לעומת 3)`): wrap numbers
   in `$...$` -- the script warns when it sees one.
3. The compile script ends with `scripts/check_rtl_parens.py`, which reads the PDF text in visual order and
   flags lines whose parentheses are reversed. A couple of hits that are pure math split across lines are
   harmless; anything else means fix the source and recompile.
4. Look at the rendered pages (`pdftoppm -r 100 -png`) before delivering -- tables, boxes and the first
   page are where bidi problems show up. Do not use LuaLaTeX: it garbles Hebrew inside tables/tcolorbox.
5. Tell the user the `.tex` must be compiled with XeLaTeX and needs the FreeSerif/FreeSans fonts
   (the PDF needs nothing).

## Workflow

1. **Understand the ask.** Identify: the expression/equation/topic, what
   operation is wanted (solve, derive, simplify, prove, investigate,
   compare scenarios), and whether it's financial/statistical (which
   usually means numeric examples, tables, or a sensitivity analysis over
   a range of inputs are expected in addition to the symbolic math).

2. **Do the actual math before writing the document.** Don't typeset
   first and compute later — work out every algebraic step and verify
   numeric results independently (e.g. by running Python/sympy for
   financial or statistical computations) so the document only ever
   contains checked results. If an example wasn't specified, invent a
   clean, concrete one — this is what makes a derivation legible.

3. **Write the LaTeX source.** Copy `assets/template.tex` as a starting
   point (it has the preamble and packages already set: `amsmath`,
   `amssymb`, `booktabs` for tables, `hyperref`, etc.) and fill in content
   sections appropriate to the task. A derivation-style report typically
   has:
   - The problem/equation stated plainly
   - Step-by-step derivation, each step's *reason* stated in words (not
     just the algebra) — this is what makes it pedagogically useful
     rather than a bare symbol dump
   - Interpretation of the result (what a discriminant, a growth rate, a
     present-value factor, etc. actually means)
   - A worked numeric example, computed and double-checked
   - For financial/statistical topics: a table (use `booktabs`) comparing
     scenarios — e.g. different compounding periods, deposit schedules,
     or interest rates — and call out the pattern in words, not just the
     numbers
   Use `\boxed{...}` for final results and formulas worth highlighting.

4. **Compile.** Run `scripts/compile_latex.sh <path/to/file.tex>` — it
   picks the engine (XeLaTeX for Hebrew, pdflatex otherwise) and runs it twice (so references resolve) and installs a minimal
   TeX Live automatically the first time it's needed in a fresh
   environment. Check the log output; fix any LaTeX errors and recompile
   before delivering anything.

5. **Deliver both files.** Send the `.tex` and the `.pdf` to the user
   (e.g. with `SendUserFile`) — the `.tex` lets them edit/extend it
   themselves (Overleaf, local LaTeX, etc.), the `.pdf` is the
   ready-to-read/print result.

## Notes

- Keep the tone of the document explanatory, as if teaching the step
  rather than just stating it — that was the whole point of asking for a
  "report" instead of a one-line formula.
- For recurring financial-modeling requests (interest over time, deposit
  schedules, different investment types), reuse the same report structure
  each time so results stay comparable across the user's future asks: Setup → Derivation/Model →
  Worked Example → Scenario Table.
- If the user's expression is ambiguous (e.g. unclear which variable to
  solve for, or what interest compounding convention to assume), make a
  reasonable, clearly-stated assumption and proceed rather than stalling
  on a clarifying question — state the assumption at the top of the
  document.
