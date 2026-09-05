#!/usr/bin/env python3
"""Build a clean, static, lag-free profile SVG (cursor blink only)."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_CANDIDATES = [
    Path("/tmp/src.svg"),
    ROOT / "assets" / "profile.original.svg",
]
OUT = ROOT / "assets" / "profile.svg"

DX = 70
ARCH_SIZE = 10.5
W, H = 1000, 480


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


def shift_body(body: str) -> str:
    def xa(m: re.Match[str]) -> str:
        attr, val = m.group(1), int(m.group(2))
        if val >= 390:
            return f'{attr}="{val + DX}"'
        return m.group(0)

    body = re.sub(r'\b(x)="(\d+)"', xa, body)

    def tr(m: re.Match[str]) -> str:
        x, y = int(m.group(1)), m.group(2)
        if x >= 390:
            return f"translate({x + DX},{y})"
        return m.group(0)

    return re.sub(r"translate\((\d+),(\d+(?:\.\d+)?)\)", tr, body)


def normalize_icon_y(body: str) -> str:
    ym = re.search(r'<text[^>]*y="(\d+)"', body) or re.search(r'y="(\d+)"', body)
    if not ym:
        return body
    iy = int(ym.group(1)) - 12

    def fix_tr(m: re.Match[str], iy: int = iy) -> str:
        return f"translate({m.group(1)},{iy})"

    body = re.sub(r"translate\((\d+),\d+(?:\.\d+)?\)", fix_tr, body)
    body = re.sub(
        rf'(<rect x="{400 + DX}" y=")(\d+)"',
        lambda m: f"{m.group(1)}{iy}\"",
        body,
    )
    return body


def main() -> None:
    src_path = next((p for p in SRC_CANDIDATES if p.exists()), None)
    if src_path is None:
        raise SystemExit(
            "Need pristine source at /tmp/src.svg (git show c3306c5:assets/profile.svg)"
        )
    src = src_path.read_text()

    arch_lines = re.findall(
        r'<text x="30" y="(\d+)" xml:space="preserve">(.*?)</text>', src
    )
    m = re.search(
        r'<g font-size="13">(.*)</g>\s*\n\s*<rect x="400" y="436"',
        src,
        re.S,
    )
    if not m:
        raise SystemExit("rows block not found")

    rows: list[str] = []
    for g in extract_top_groups(m.group(1)):
        mm = re.match(
            r'<g opacity="0"><animate[^/]*/>\s*(.*)</g>\s*$', g, re.S
        )
        if not mm:
            raise SystemExit("row unwrap failed")
        body = mm.group(1).strip()
        body = re.sub(r"\s*<animate\b[^/]*/>", "", body)
        body = re.sub(r"\s*<animateTransform\b[^/]*/>", "", body)
        rows.append(normalize_icon_y(shift_body(body)))

    assert len(arch_lines) == 18 and len(rows) == 12
    hx = 400 + DX

    lines: list[str] = []
    a = lines.append
    a('<?xml version="1.0" encoding="UTF-8"?>')
    a(
        f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
        'xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="numan@dev — fastfetch">'
    )
    a("  <defs>")
    a(
        f'    <clipPath id="round">'
        f'<rect x="0" y="0" width="{W}" height="{H}" rx="12"/>'
        f"</clipPath>"
    )
    a('    <radialGradient id="bg" cx="28%" cy="0%" r="90%">')
    a('      <stop offset="0%" stop-color="#151b23"/>')
    a('      <stop offset="100%" stop-color="#0a0d12"/>')
    a("    </radialGradient>")
    a("  </defs>")
    a('  <g clip-path="url(#round)">')
    a(f'    <rect width="{W}" height="{H}" fill="url(#bg)"/>')
    a(f'    <rect x="0" y="0" width="{W}" height="34" fill="#161b22"/>')
    a('    <circle cx="20" cy="17" r="6" fill="#ff5f56"/>')
    a('    <circle cx="42" cy="17" r="6" fill="#ffbd2e"/>')
    a('    <circle cx="64" cy="17" r="6" fill="#27c93f"/>')
    a(
        f'    <text x="{W // 2}" y="21" fill="#8b949e" font-size="12" '
        "font-family=\"Consolas, 'SF Mono', Menlo, monospace\" "
        'text-anchor="middle">numan@dev — fastfetch</text>'
    )
    a("")
    a("    <g font-family=\"Consolas, 'SF Mono', Menlo, monospace\">")
    a(f'      <g font-size="{ARCH_SIZE}" fill="#58a6ff">')
    for y, text in arch_lines:
        a(f'        <text x="24" y="{y}" xml:space="preserve">{text}</text>')
    a("      </g>")
    a(
        f'      <text x="{hx}" y="70" fill="#7ee787" font-size="14" '
        'font-weight="bold">numan@dev</text>'
    )
    a(
        f'      <text x="{hx}" y="88" fill="#3d444d" font-size="13">'
        "-----------------------------------------------</text>"
    )
    a('      <g font-size="13">')
    for body in rows:
        a("        <g>")
        for line in body.splitlines():
            a(f"          {line}")
        a("        </g>")
    a("      </g>")
    a(f'      <rect x="{hx}" y="436" width="9" height="14" fill="#7ee787">')
    a(
        '        <animate attributeName="opacity" values="1;1;0;0" '
        'keyTimes="0;0.48;0.5;1" dur="1.1s" repeatCount="indefinite"/>'
    )
    a("      </rect>")
    a("    </g>")
    a("  </g>")
    a("</svg>")

    text = "\n".join(lines) + "\n"
    text = text.replace(
        '<tspan fill="#58a6ff">OS: </tspan>',
        '<tspan fill="#58a6ff">Role: </tspan>',
    )
    OUT.write_text(text)
    ET.parse(OUT)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes, {text.count('<animate')} animates)")


if __name__ == "__main__":
    main()
