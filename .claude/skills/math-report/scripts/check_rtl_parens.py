#!/usr/bin/env python3
"""Verify parentheses in a compiled RTL PDF (visual order, left->right): every
balanced line must never close before it opens. Prints suspicious lines.
Usage: check_rtl_parens.py file.pdf"""
import re, subprocess, sys
txt = subprocess.run(['pdftotext', '-raw', sys.argv[1], '-'], capture_output=True, text=True).stdout
bad = []; tot = 0
for line in txt.split('\n'):
    line = re.sub('[\u202a-\u202e\u200e\u200f]', '', line)
    o, c = line.count('('), line.count(')')
    if o != c or not o: continue
    tot += 1; d = 0
    for ch in line:
        d += (ch == '(') - (ch == ')')
        if d < 0: bad.append(line); break
print(f"checked {tot} balanced lines, suspicious: {len(bad)}")
for b in bad: print("  ", b[:120])
