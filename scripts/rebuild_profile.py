#!/usr/bin/env python3
"""Rebuild assets/profile.svg — clean, lightweight terminal reveal (no CRT gimmicks)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Prefer pristine original if available; else current file must be the pre-cinematic one
ORIG = Path("/tmp/profile-original.svg")
SRC = ORIG if ORIG.exists() else ROOT / "assets" / "profile.svg"
OUT = ROOT / "assets" / "profile.svg"

DUR = 10.0


def reveal(start_s: float, fade_s: float = 0.18) -> str:
    t0 = start_s / DUR
    t1 = min((start_s + fade_s) / DUR, 0.82)
    return (
        f'<animate attributeName="opacity" values="0;0;1;1" '
        f'keyTimes="0;{t0:.4f};{t1:.4f};1" dur="{DUR:g}s" '
        f'repeatCount="indefinite"/>'
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
        raise SystemExit("could not locate rows block in source SVG")
    rows = [unwrap_row(r) for r in extract_top_groups(m.group(1))]

    assert len(arch_lines) == 18, len(arch_lines)
    assert len(rows) == 12, len(rows)

    L: list[str] = []
    a = L.append

    a('<?xml version="1.0" encoding="UTF-8"?>')
    a(
        '<svg width="960" height="480" viewBox="0 0 960 480" '
        'xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="numan@dev — fastfetch">'
    )
    a("  <defs>")
    a(
        '    <clipPath id="round">'
        '<rect x="0" y="0" width="960" height="480" rx="12"/>'
        "</clipPath>"
    )
    a('    <radialGradient id="bg" cx="30%" cy="0%" r="90%">')
    a('      <stop offset="0%" stop-color="#151b23"/>')
    a('      <stop offset="100%" stop-color="#0a0d12"/>')
    a("    </radialGradient>")
    a("  </defs>")
    a("")
    a('  <g clip-path="url(#round)">')
    a('    <rect width="960" height="480" fill="url(#bg)"/>')
    a('    <rect x="0" y="0" width="960" height="34" fill="#161b22"/>')
    a('    <circle cx="20" cy="17" r="6" fill="#ff5f56"/>')
    a('    <circle cx="42" cy="17" r="6" fill="#ffbd2e"/>')
    a('    <circle cx="64" cy="17" r="6" fill="#27c93f"/>')
    a(
        '    <text x="480" y="21" fill="#8b949e" font-size="12" '
        "font-family=\"Consolas, 'SF Mono', Menlo, monospace\" "
        'text-anchor="middle">numan@dev — fastfetch</text>'
    )
    a("")
    a(
        "    <g id=\"stage\" font-family=\"Consolas, 'SF Mono', Menlo, monospace\">"
    )
    # Soft loop fade only — cheap, professional
    a(
        f'      <animate attributeName="opacity" values="1;1;0;0" '
        f'keyTimes="0;0.78;0.88;1" dur="{DUR:g}s" repeatCount="indefinite"/>'
    )
    a("")
    # Arch: one group fade + subtle color pulse (not per-line = far less work)
    a('      <g font-size="12" fill="#4fc3f7" opacity="0">')
    a(
        '        <animate attributeName="fill" values="#4fc3f7;#6cb6f5;#4fc3f7" '
        'dur="8s" repeatCount="indefinite"/>'
    )
    a(f"        {reveal(0.15, 0.35)}")
    for y, text in arch_lines:
        a(f'        <text x="30" y="{y}" xml:space="preserve">{text}</text>')
    a("      </g>")
    a("")
    a(
        '      <text x="400" y="70" fill="#7ee787" font-size="14" '
        'font-weight="bold" opacity="0">'
    )
    a(f"        {reveal(0.35, 0.2)}")
    a("        numan@dev")
    a("      </text>")
    a('      <text x="400" y="88" fill="#30363d" font-size="13" opacity="0">')
    a(f"        {reveal(0.42, 0.18)}")
    a("        -----------------------------------------------")
    a("      </text>")
    a("")
    a('      <g font-size="13">')
    # Stagger rows with opacity only — no transforms (avoids overlap / lag)
    row_t0 = 0.55
    for i, body in enumerate(rows):
        t = row_t0 + i * 0.22
        a('        <g opacity="0">')
        a(f"          {reveal(t, 0.16)}")
        for bline in body.splitlines():
            a(f"          {bline}")
        a("        </g>")
    a("      </g>")
    a("")
    cursor_t = row_t0 + 11 * 0.22 + 0.25
    a(f'      <rect x="400" y="436" width="9" height="14" fill="#7ee787" opacity="0">')
    a(f"        {reveal(cursor_t, 0.1)}")
    a(
        '        <animate attributeName="opacity" values="1;0" dur="0.9s" '
        'begin="0s" repeatCount="indefinite"/>'
    )
    # Wait - stacking two opacity animates on same element fights. Wrap cursor.
    a("      </rect>")
    a("    </g>")
    a("  </g>")
    a("</svg>")

    # Fix cursor: use wrapper group for appear, inner rect for blink
    text = "\n".join(L) + "\n"
    text = text.replace(
        f'      <rect x="400" y="436" width="9" height="14" fill="#7ee787" opacity="0">\n'
        f"        {reveal(cursor_t, 0.1)}\n"
        '        <animate attributeName="opacity" values="1;0" dur="0.9s" '
        'begin="0s" repeatCount="indefinite"/>\n'
        "      </rect>",
        f'      <g opacity="0">\n'
        f"        {reveal(cursor_t, 0.1)}\n"
        '        <rect x="400" y="436" width="9" height="14" fill="#7ee787">\n'
        '          <animate attributeName="opacity" values="1;1;0;0" '
        'keyTimes="0;0.5;0.5;1" dur="1s" repeatCount="indefinite"/>\n'
        "        </rect>\n"
        "      </g>",
    )

    OUT.write_text(text)
    import xml.etree.ElementTree as ET

    ET.parse(OUT)
    anim_count = text.count("<animate")
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes, {anim_count} animates)")


if __name__ == "__main__":
    main()
