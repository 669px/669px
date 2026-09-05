#!/usr/bin/env python3
"""Rebuild assets/profile.svg with cinematic terminal animation."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "assets" / "profile.svg"
# Always read original from git if current is broken — caller restores first
OUT = ROOT / "assets" / "profile.svg"

DUR = 16.0


def reveal(start_s: float, fade_s: float = 0.2) -> str:
    t0 = start_s / DUR
    t1 = min((start_s + fade_s) / DUR, 0.87)
    return (
        f'<animate attributeName="opacity" values="0;0;1;1" '
        f'keyTimes="0;{t0:.4f};{t1:.4f};1" dur="{DUR:g}s" '
        f'repeatCount="indefinite" calcMode="spline" '
        f'keySplines="0 0 1 1;0.25 0.1 0.25 1;0 0 1 1"/>'
    )


def slide_reveal(start_s: float, fade_s: float = 0.28) -> str:
    t0 = start_s / DUR
    t1 = min((start_s + fade_s) / DUR, 0.87)
    return (
        f'<animate attributeName="opacity" values="0;0;1;1" '
        f'keyTimes="0;{t0:.4f};{t1:.4f};1" dur="{DUR:g}s" '
        f'repeatCount="indefinite" calcMode="spline" '
        f'keySplines="0 0 1 1;0.2 0.75 0.2 1;0 0 1 1"/>\n'
        f'          <animateTransform attributeName="transform" type="translate" '
        f'values="0 7;0 7;0 0;0 0" keyTimes="0;{t0:.4f};{t1:.4f};1" '
        f'dur="{DUR:g}s" repeatCount="indefinite" calcMode="spline" '
        f'keySplines="0 0 1 1;0.2 0.75 0.2 1;0 0 1 1"/>'
    )


def extract_top_groups(s: str) -> list[str]:
    groups: list[str] = []
    i = 0
    n = len(s)
    while i < n:
        start = s.find("<g", i)
        if start == -1:
            break
        if start + 2 < n and s[start + 2] not in " >":
            i = start + 2
            continue
        depth = 0
        j = start
        while j < n:
            if s.startswith("<g", j) and (j + 2 >= n or s[j + 2] in " >"):
                gt = s.find(">", j)
                if gt == -1:
                    return groups
                if s[gt - 1] != "/":
                    depth += 1
                j = gt + 1
                continue
            if s.startswith("</g>", j):
                depth -= 1
                j += 4
                if depth == 0:
                    groups.append(s[start:j])
                    i = j
                    break
                continue
            j += 1
        else:
            break
    return groups


def unwrap_row(group: str) -> str:
    m = re.match(
        r'<g opacity="0"><animate attributeName="opacity"[^/]*/>\s*(.*)</g>\s*$',
        group,
        re.S,
    )
    if not m:
        raise ValueError(f"row unwrap failed: {group[:120]}")
    return m.group(1).strip()


def main() -> None:
    src = SRC.read_text()

    arch_lines = re.findall(
        r'<text x="30" y="(\d+)" xml:space="preserve">(.*?)</text>', src
    )
    m = re.search(
        r'<g font-size="13">(.*)</g>\s*\n\s*<rect x="400" y="436"',
        src,
        re.S,
    )
    if not m:
        raise SystemExit("could not locate rows block")
    rows_raw = extract_top_groups(m.group(1))
    rows = [unwrap_row(r) for r in rows_raw]

    assert len(arch_lines) == 18, len(arch_lines)
    assert len(rows) == 12, len(rows)

    lines: list[str] = []
    a = lines.append

    a('<?xml version="1.0" encoding="UTF-8"?>')
    a(
        '<svg width="960" height="480" viewBox="0 0 960 480" '
        'xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="numan@dev — fastfetch">'
    )
    a("  <defs>")
    a('    <clipPath id="round"><rect x="0" y="0" width="960" height="480" rx="12"/></clipPath>')
    a('    <radialGradient id="bg" cx="28%" cy="0%" r="95%">')
    a('      <stop offset="0%" stop-color="#1a2330"/>')
    a('      <stop offset="55%" stop-color="#0d1219"/>')
    a('      <stop offset="100%" stop-color="#070a0e"/>')
    a("    </radialGradient>")
    a('    <radialGradient id="vignette" cx="50%" cy="45%" r="78%">')
    a('      <stop offset="55%" stop-color="#000" stop-opacity="0"/>')
    a('      <stop offset="100%" stop-color="#000" stop-opacity="0.28"/>')
    a("    </radialGradient>")
    a('    <linearGradient id="scanGrad" x1="0" y1="0" x2="0" y2="1">')
    a('      <stop offset="0%" stop-color="#7ee787" stop-opacity="0"/>')
    a('      <stop offset="45%" stop-color="#7ee787" stop-opacity="0.045"/>')
    a('      <stop offset="100%" stop-color="#7ee787" stop-opacity="0"/>')
    a("    </linearGradient>")
    a('    <filter id="softGlow" x="-20%" y="-20%" width="140%" height="140%">')
    a('      <feGaussianBlur stdDeviation="0.55" result="b"/>')
    a("      <feMerge><feMergeNode in=\"b\"/><feMergeNode in=\"SourceGraphic\"/></feMerge>")
    a("    </filter>")
    a('    <pattern id="scanlines" width="960" height="4" patternUnits="userSpaceOnUse">')
    a('      <rect width="960" height="1" fill="#000" fill-opacity="0.1"/>')
    a("    </pattern>")
    a("  </defs>")
    a("")
    a('  <g clip-path="url(#round)">')
    a('    <rect width="960" height="480" fill="url(#bg)"/>')
    a("")
    a("    <!-- power-on flash -->")
    a('    <rect width="960" height="480" fill="#9be9a8" opacity="0">')
    a(
        f'      <animate attributeName="opacity" values="0;0.16;0;0" '
        f'keyTimes="0;0.01;0.035;1" dur="{DUR:g}s" repeatCount="indefinite"/>'
    )
    a("    </rect>")
    a("")
    a("    <!-- window chrome -->")
    a('    <g opacity="0">')
    a(
        f'      <animate attributeName="opacity" values="0;0;1;1;0;0" '
        f'keyTimes="0;0.018;0.045;0.88;0.94;1" dur="{DUR:g}s" '
        f'repeatCount="indefinite" calcMode="spline" '
        f'keySplines="0 0 1 1;0.4 0 0.2 1;0 0 1 1;0.4 0 0.2 1;0 0 1 1"/>'
    )
    a('      <rect x="0" y="0" width="960" height="34" fill="#161b22"/>')
    a('      <rect x="0" y="33" width="960" height="1" fill="#30363d"/>')
    a('      <circle cx="20" cy="17" r="6" fill="#ff5f56"/>')
    a('      <circle cx="42" cy="17" r="6" fill="#ffbd2e"/>')
    a('      <circle cx="64" cy="17" r="6" fill="#27c93f"/>')
    a(
        '      <text x="480" y="21" fill="#8b949e" font-size="12" '
        "font-family=\"Consolas, 'SF Mono', Menlo, monospace\" "
        'text-anchor="middle">numan@dev — fastfetch</text>'
    )
    a("    </g>")
    a("")
    a("    <!-- stage -->")
    a(
        "    <g id=\"stage\" font-family=\"Consolas, 'SF Mono', Menlo, monospace\">"
    )
    a(
        f'      <animate attributeName="opacity" values="0;0;1;1;0;0" '
        f'keyTimes="0;0.04;0.07;0.875;0.94;1" dur="{DUR:g}s" '
        f'repeatCount="indefinite" calcMode="spline" '
        f'keySplines="0 0 1 1;0.4 0 0.2 1;0 0 1 1;0.4 0 0.2 1;0 0 1 1"/>'
    )
    a("")
    a('      <g font-size="12" fill="#4fc3f7" filter="url(#softGlow)">')
    a(
        '        <animate attributeName="fill" values="#4fc3f7;#7aa2f7;#4fc3f7" '
        'dur="7s" repeatCount="indefinite"/>'
    )

    arch_t0 = 0.72
    for i, (y, text) in enumerate(arch_lines):
        t = arch_t0 + i * 0.052
        a(f'        <text x="30" y="{y}" xml:space="preserve" opacity="0">')
        a(f"          {reveal(t, 0.1)}")
        a(f"          {text}")
        a("        </text>")

    a("      </g>")
    a("")
    a(
        '      <text x="400" y="70" fill="#7ee787" font-size="14" '
        'font-weight="bold" opacity="0">'
    )
    a(f"        {reveal(0.85, 0.18)}")
    a("        numan@dev")
    a("      </text>")
    a('      <text x="400" y="88" fill="#484f58" font-size="13" opacity="0">')
    a(f"        {reveal(0.98, 0.16)}")
    a("        -----------------------------------------------")
    a("      </text>")
    a("")
    a('      <g font-size="13">')
    row_t0 = 1.25
    for i, body in enumerate(rows):
        t = row_t0 + i * 0.30
        a('        <g opacity="0">')
        a(f"          {slide_reveal(t)}")
        for bline in body.splitlines():
            a(f"          {bline}")
        a("        </g>")
    a("      </g>")
    a("")

    cursor_t = 1.25 + 11 * 0.30 + 0.35
    a('      <g opacity="0">')
    a(f"        {reveal(cursor_t, 0.12)}")
    a('        <rect x="400" y="436" width="9" height="14" fill="#7ee787">')
    a(
        '          <animate attributeName="opacity" values="1;1;0;0" '
        'keyTimes="0;0.45;0.5;1" dur="1.05s" repeatCount="indefinite"/>'
    )
    a("        </rect>")
    a("      </g>")
    a("    </g>")
    a("")
    a("    <!-- CRT scan sweep -->")
    a(
        '    <rect x="0" y="-80" width="960" height="80" fill="url(#scanGrad)" '
        'opacity="0.7" pointer-events="none">'
    )
    a(
        '      <animateTransform attributeName="transform" type="translate" '
        'values="0 -80;0 520" dur="5.5s" repeatCount="indefinite"/>'
    )
    a(
        f'      <animate attributeName="opacity" values="0;0.7;0.7;0" '
        f'keyTimes="0;0.06;0.88;1" dur="{DUR:g}s" repeatCount="indefinite"/>'
    )
    a("    </rect>")
    a("")
    a(
        '    <rect width="960" height="480" fill="url(#scanlines)" '
        'opacity="0.35" pointer-events="none">'
    )
    a(
        f'      <animate attributeName="opacity" values="0;0;0.35;0.35;0;0" '
        f'keyTimes="0;0.04;0.08;0.88;0.94;1" dur="{DUR:g}s" '
        f'repeatCount="indefinite"/>'
    )
    a("    </rect>")
    a(
        '    <rect width="960" height="480" fill="url(#vignette)" '
        'pointer-events="none">'
    )
    a(
        f'      <animate attributeName="opacity" values="0;0;1;1;0;0" '
        f'keyTimes="0;0.04;0.08;0.88;0.94;1" dur="{DUR:g}s" '
        f'repeatCount="indefinite"/>'
    )
    a("    </rect>")
    a("")
    a(
        '    <rect x="0.5" y="0.5" width="959" height="479" rx="11.5" '
        'fill="none" stroke="#30363d" stroke-opacity="0.55"/>'
    )
    a("  </g>")
    a("</svg>")

    text = "\n".join(lines) + "\n"
    OUT.write_text(text)

    import xml.etree.ElementTree as ET

    ET.parse(OUT)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
