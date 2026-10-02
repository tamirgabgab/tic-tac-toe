#!/usr/bin/env python3
"""Make Hebrew/RTL .tex compile correctly under XeLaTeX.

XeLaTeX+bidi mirrors a parenthesis only when its inner neighbour is RTL text.
When the inner neighbour is math or Latin letters, the glyph comes out reversed.
This script rewrites exactly those parentheses as \\lpar{} / \\rpar{} (typed swapped),
turns \\ref{..} into \\rf{..} (a math-mode number) and injects the macro definitions.
In-place and idempotent; the original is saved as <file>.orig once.
Usage: fix_rtl_parens.py file.tex
"""
import re, sys, shutil, os

path = sys.argv[1]
src = open(path, encoding='utf-8').read()
if not os.path.exists(path + '.orig'):
    shutil.copy(path, path + '.orig')

head, sep, body = src.partition(r'\begin{document}')
if not sep:
    sys.exit("no \\begin{document}")

# 1. macro definitions
defs = ""
if r'\newcommand{\lpar}' not in head:
    defs += ("% XeLaTeX+bidi does not mirror a parenthesis whose inner neighbour is math/Latin text;\n"
             "% such parentheses are typed swapped: \\lpar = opening, \\rpar = closing.\n"
             "\\newcommand{\\lpar}{)}\\newcommand{\\rpar}{(}\n")
if r'\newcommand{\rf}' not in head:
    defs += "\\newcommand{\\rf}[1]{$\\mathrm{\\ref{#1}}$}\n"
if defs:
    head = head.rstrip('\n') + '\n' + defs + '\n'

body = body.replace('\\ref{', '\\rf{')

# 2. tokenise into text / math
tokens = []; buf = ''; i = 0; n = len(body)
def flush():
    global buf
    if buf: tokens.append(('t', buf)); buf = ''
while i < n:
    c = body[i]
    if body.startswith(r'\[', i):
        flush(); j = body.index(r'\]', i) + 2; tokens.append(('m', body[i:j])); i = j; continue
    m = re.match(r'\\begin\{(equation\*?|align\*?|gather\*?)\}', body[i:])
    if m:
        flush(); end = body.index(r'\end{%s}' % m.group(1), i) + len(r'\end{%s}' % m.group(1))
        tokens.append(('m', body[i:end])); i = end; continue
    if c == '%':                       # comment: leave alone
        j = body.find('\n', i); j = n if j < 0 else j
        buf += body[i:j]; i = j; continue
    if c == '\\' and i + 1 < n:
        buf += body[i:i+2]; i += 2; continue
    if c == '$':
        flush(); j = i + 1
        while body[j] != '$' or body[j-1] == '\\': j += 1
        tokens.append(('m', body[i:j+1])); i = j + 1; continue
    buf += c; i += 1
flush()

LTR_CMDS = ('rf',); SKIP_CMDS = ('emph', 'textbf', 'textit', 'textrm')
is_ltr = lambda ch: ch.isascii() and ch.isalpha()

def next_is_ltr(k, pos):
    while k < len(tokens):
        kind, s = tokens[k]
        if kind == 'm': return True
        pos = re.compile(r'\s*').match(s, pos).end()
        while pos < len(s):
            ch = s[pos]
            if ch == '\\':
                mm = re.match(r'\\([A-Za-z]+)', s[pos:])
                if mm:
                    if mm.group(1) in LTR_CMDS: return True
                    if mm.group(1) in SKIP_CMDS:
                        pos += mm.end()
                        while pos < len(s) and s[pos] in ' {': pos += 1
                        continue
                return False
            if ch == '{': pos += 1; continue
            return is_ltr(ch)
        k += 1; pos = 0
    return False

def prev_is_ltr(k, pos):
    while k >= 0:
        kind, s = tokens[k]
        if kind == 'm': return True
        seg = s[:pos].rstrip()
        if seg:
            if re.search(r'\\rf\{[^}]*\}$', seg): return True
            last = seg[-1]
            if last == '}':
                inner = seg[:-1].rstrip()
                if inner: return is_ltr(inner[-1])
                return k > 0 and tokens[k-1][0] == 'm'
            return is_ltr(last)
        k -= 1; pos = len(tokens[k][1]) if k >= 0 else 0
    return False

out = []; count = 0; warn = []
for k, (kind, s) in enumerate(tokens):
    if kind == 'm': out.append(s); continue
    res = []
    for pos, ch in enumerate(s):
        if ch == '(' and next_is_ltr(k, pos+1): res.append(r'\lpar{}'); count += 1
        elif ch == ')' and prev_is_ltr(k, pos): res.append(r'\rpar{}'); count += 1
        else: res.append(ch)
    t = ''.join(res)
    for m in re.finditer(r'[^\n]{0,25}(\(\s*\d|\d\s*\))[^\n]{0,25}', s):
        warn.append(m.group(0))
    out.append(t)

open(path, 'w', encoding='utf-8').write(head + sep + ''.join(out))
print(f"fix_rtl_parens: swapped {count} parentheses")
for w in warn:
    print("  WARNING bare digit next to a parenthesis (wrap the number in $...$):", repr(w))
