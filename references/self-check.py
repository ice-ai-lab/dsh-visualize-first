#!/usr/bin/env python3
"""Check an SVG against the dsh-visualize-first rules.

Usage:
    python3 self-check.py diagram.svg          # check a file
    python3 self-check.py - <<'EOF'            # check inline markup
<svg ...>...</svg>
EOF

Exits 0 when every rule passes, 1 when any rule fails. Prints one line per
finding with the offending element so you can jump straight to it.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
MIN_FONT_SIZE = 11.0
ALLOWED_WEIGHTS = {"400", "500", "normal", "bold"}
BANNED_WORDS = ("gradient", "drop-shadow", "box-shadow", "blur", "glow")
# A viewBox coordinate: optional sign, digits, optional fraction. Anything else
# (a stray "{H}", "auto", an empty token) invalidates the whole attribute.
NUMBER_RE = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)")
# Pictographic ranges. Arrows (U+2190-U+21FF), math operators, and CJK are
# deliberately excluded: they are legitimate in diagrams. Only emoji and
# pictographs are banned, because they render inconsistently across fonts.
EMOJI_RE = re.compile(
    "["
    "\U0001F300-\U0001FAFF"   # symbols, pictographs, emoticons, transport
    "\U00002600-\U000027BF"   # misc symbols and dingbats
    "\U0001F000-\U0001F0FF"   # mahjong, playing cards
    "\U0000FE00-\U0000FE0F"   # variation selectors
    "\U0001F1E6-\U0001F1FF"   # regional indicators (flags)
    "]"
)


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def prop(el: ET.Element, name: str, attr: str | None = None) -> str | None:
    """Read a presentation value from an attribute, falling back to inline style."""
    value = el.get(name)
    if value is not None:
        return value.strip()
    style = el.get("style") or ""
    match = re.search(rf"(?:^|;)\s*{re.escape(name)}\s*:\s*([^;]+)", style)
    return match.group(1).strip() if match else None


def font_size(el: ET.Element, inherited: float | None) -> float | None:
    raw = prop(el, "font-size")
    if raw is None:
        return inherited
    match = re.match(r"([\d.]+)", raw)
    return float(match.group(1)) if match else inherited


def main(source: Path | str) -> int:
    """Check one SVG given as a file path or as raw markup text."""
    findings: list[str] = []
    try:
        if isinstance(source, str):
            root = ET.fromstring(source)
        else:
            root = ET.parse(source).getroot()
    except ET.ParseError as exc:
        print(f"FAIL  XML is not well-formed: {exc}")
        return 1

    if local(root.tag) != "svg":
        findings.append(f"root element is <{local(root.tag)}>, expected <svg>")

    # viewBox must be present and hold four real numbers. A non-numeric token
    # (e.g. a template placeholder left in by an f-string) makes browsers drop
    # the whole viewBox on an <img>, falling back to 300x150 and clipping the
    # drawing. rsvg-convert silently repairs it, so a PNG that looks right does
    # not prove the SVG is right.
    view_box = root.get("viewBox")
    parts: list[str] = []
    if view_box is None:
        findings.append("<svg> has no viewBox")
    else:
        parts = view_box.replace(",", " ").split()
        if len(parts) != 4:
            findings.append(f"viewBox={view_box!r} is not four numbers")
        else:
            bad = [p for p in parts if not NUMBER_RE.fullmatch(p)]
            if bad:
                findings.append(
                    f"viewBox={view_box!r} has non-numeric token(s) {bad}; "
                    "browsers drop the whole viewBox and render at 300x150"
                )
            elif parts[2] not in {"680", "820"}:
                findings.append(
                    f"viewBox width is {parts[2]}, expected 680 or 820 for body width"
                )

    # Explicit pixel width/height matching the viewBox is mandatory: the file
    # renders through <img src="api/file?...">, and a percentage width without
    # an intrinsic height decodes to a blank box.
    width = root.get("width")
    height = root.get("height")
    numbers = len(parts) == 4 and all(NUMBER_RE.fullmatch(p) for p in parts)
    if width == "100%" and height is None:
        findings.append(
            '<svg width="100%"> with no height renders as a blank box in '
            '<img>; write explicit pixel width/height'
        )
    elif numbers and width != parts[2]:
        findings.append(
            f"<svg width={width!r} does not match viewBox width {parts[2]}"
        )
    elif numbers and height != parts[3]:
        findings.append(
            f"<svg height={height!r} does not match viewBox height {parts[3]}"
        )

    # Accessibility: role, then <title> and <desc> as the first children.
    if root.get("role") != "img":
        findings.append('<svg> missing role="img"')
    children = [local(c.tag) for c in root]
    for index, required in enumerate(("title", "desc")):
        if index >= len(children) or children[index] != required:
            findings.append(f"first children must start with <title>, <desc>; got {children[:2]}")

    # Walk the tree tracking inherited font size.
    def visit(el: ET.Element, inherited: float | None) -> None:
        tag = local(el.tag)
        size = font_size(el, inherited)

        if tag == "text":
            if el.text and EMOJI_RE.search(el.text):
                findings.append(
                    f"<text> {el.text!r} contains an emoji; use a CSS shape or SVG path instead"
                )
            if size is None:
                findings.append(f"<text> {el.text!r} has no font-size")
            elif size < MIN_FONT_SIZE:
                findings.append(
                    f"<text> {el.text!r} is {size:g}px, below the {MIN_FONT_SIZE:g}px floor"
                )
            weight = prop(el, "font-weight")
            if weight is not None and weight not in ALLOWED_WEIGHTS:
                findings.append(
                    f"<text> {el.text!r} uses font-weight {weight}, only 400/500 allowed"
                )

        if tag in {"path", "polyline"} and prop(el, "fill") != "none":
            # Connectors must not paint a filled shape.
            stroke = prop(el, "stroke")
            if stroke is not None:
                findings.append(
                    f"<{tag}> has stroke but fill={prop(el, 'fill')!r}; connectors need fill=\"none\""
                )

        for key, value in el.attrib.items():
            lowered = value.lower()
            if any(word in lowered for word in BANNED_WORDS):
                findings.append(f"<{tag} {key}={value!r}> uses a banned effect")
            if key == "transform" and "rotate" in lowered:
                findings.append(f"<{tag} transform={value!r}> rotates text or shape")

        for child in el:
            visit(child, size)

    visit(root, None)

    if findings:
        for finding in findings:
            print(f"FAIL  {finding}")
        print(f"\n{len(findings)} finding(s)")
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        raise SystemExit(2)
    if sys.argv[1] == "-":
        raise SystemExit(main(sys.stdin.read()))
    raise SystemExit(main(Path(sys.argv[1])))
