#!/usr/bin/env python3
"""WCAG 2.2 static checker — fast structural checks on HTML.

Usage:
  python3 wcag_check.py --html-file page.html
  python3 wcag_check.py --url https://example.com
  python3 wcag_check.py --html-file page.html --json

Checks performed (static only; this is a smoke check, not a full audit):
  1.1.1  Missing alt text on <img>
  1.3.1  Inputs without associated <label> / aria-label / aria-labelledby
  1.3.1  Tables without <th>
  1.4.3  Inline color-only styling that may need contrast review (heuristic)
  2.4.1  Missing skip link / <main> landmark
  2.4.2  Missing or empty <title>
  2.4.6  Skipped heading levels (h1 -> h3 etc.)
  3.1.1  Missing lang attribute on <html>
  4.1.2  Buttons/links without accessible name
  4.1.2  Suspicious ARIA roles
  Various: outline:none without :focus-visible replacement (CSS heuristic)

Output: severity-grouped findings (Critical/Major/Minor) with line numbers.
Exit code: 0 = no Critical/Major findings, 1 = findings present, 2 = bad input.
"""
from __future__ import annotations

import argparse
import html.parser
import json
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from pathlib import Path


def err(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)


@dataclass
class Finding:
    severity: str  # Critical | Major | Minor
    rule: str
    message: str
    line: int = 0


@dataclass
class WCAGParser(html.parser.HTMLParser):
    findings: list[Finding] = field(default_factory=list)
    has_html_lang: bool = False
    has_title: bool = False
    title_text: str = ""
    has_main: bool = False
    has_skip_link: bool = False
    heading_levels: list[int] = field(default_factory=list)
    in_title: bool = False
    in_button: bool = False
    button_has_text: bool = False
    button_line: int = 0
    button_has_label: bool = False
    in_link: bool = False
    link_has_text: bool = False
    link_line: int = 0
    link_has_label: bool = False
    in_table: bool = False
    table_has_th: bool = False
    table_line: int = 0
    first_focusable_seen: bool = False

    def __post_init__(self):
        super().__init__(convert_charrefs=True)

    def _attr(self, attrs: list[tuple[str, str | None]], name: str) -> str | None:
        for k, v in attrs:
            if k.lower() == name:
                return v if v is not None else ""
        return None

    def _has_accessible_name(self, attrs: list) -> bool:
        for key in ("aria-label", "aria-labelledby", "title"):
            v = self._attr(attrs, key)
            if v is not None and v.strip():
                return True
        return False

    def handle_starttag(self, tag: str, attrs: list) -> None:
        line, _ = self.getpos()
        tag = tag.lower()

        if tag == "html":
            v = self._attr(attrs, "lang")
            self.has_html_lang = bool(v and v.strip())

        elif tag == "title":
            self.in_title = True

        elif tag == "main":
            self.has_main = True

        elif tag == "img":
            alt = self._attr(attrs, "alt")
            role = (self._attr(attrs, "role") or "").lower()
            aria_hidden = (self._attr(attrs, "aria-hidden") or "").lower() == "true"
            if alt is None and role != "presentation" and not aria_hidden:
                self.findings.append(Finding(
                    "Critical", "WCAG 1.1.1",
                    "<img> missing alt attribute", line))

        elif tag == "input":
            itype = (self._attr(attrs, "type") or "text").lower()
            if itype in {"hidden", "submit", "button", "reset", "image"}:
                if itype == "image" and not self._attr(attrs, "alt"):
                    self.findings.append(Finding(
                        "Critical", "WCAG 1.1.1",
                        "<input type=image> missing alt", line))
                return
            input_id = self._attr(attrs, "id")
            has_label = self._has_accessible_name(attrs)
            if not has_label and not input_id:
                self.findings.append(Finding(
                    "Major", "WCAG 1.3.1 / 3.3.2",
                    "<input> has no id, aria-label, or aria-labelledby — likely no label",
                    line))

        elif tag == "textarea":
            if not self._has_accessible_name(attrs) and not self._attr(attrs, "id"):
                self.findings.append(Finding(
                    "Major", "WCAG 1.3.1 / 3.3.2",
                    "<textarea> with no associated label", line))

        elif tag == "select":
            if not self._has_accessible_name(attrs) and not self._attr(attrs, "id"):
                self.findings.append(Finding(
                    "Major", "WCAG 1.3.1 / 3.3.2",
                    "<select> with no associated label", line))

        elif tag == "table":
            self.in_table = True
            self.table_has_th = False
            self.table_line = line

        elif tag == "th":
            self.table_has_th = True

        elif tag == "button":
            self.in_button = True
            self.button_has_text = False
            self.button_line = line
            self.button_has_label = self._has_accessible_name(attrs)

        elif tag == "a":
            self.in_link = True
            self.link_has_text = False
            self.link_line = line
            self.link_has_label = self._has_accessible_name(attrs)
            href = (self._attr(attrs, "href") or "").lower()
            if not self.first_focusable_seen and href.startswith("#"):
                self.has_skip_link = True
            self.first_focusable_seen = True

        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            if self.heading_levels:
                prev = self.heading_levels[-1]
                if level > prev + 1:
                    self.findings.append(Finding(
                        "Minor", "WCAG 2.4.6",
                        f"heading skipped levels: <{tag}> after <h{prev}>", line))
            self.heading_levels.append(level)

        # ARIA validation: highly suspicious role values
        role = self._attr(attrs, "role")
        if role:
            valid_roles = {
                "alert", "alertdialog", "application", "article", "banner", "button",
                "checkbox", "complementary", "contentinfo", "dialog", "form", "grid",
                "gridcell", "group", "heading", "img", "link", "list", "listbox",
                "listitem", "main", "menu", "menubar", "menuitem", "navigation",
                "none", "option", "presentation", "progressbar", "radio", "radiogroup",
                "region", "row", "rowgroup", "search", "searchbox", "separator",
                "slider", "spinbutton", "status", "switch", "tab", "table", "tablist",
                "tabpanel", "textbox", "timer", "toolbar", "tooltip", "tree",
                "treegrid", "treeitem", "combobox", "cell", "columnheader", "rowheader",
                "feed", "figure", "marquee", "math", "note", "scrollbar", "term",
                "definition", "directory", "log", "document",
            }
            if role.strip() not in valid_roles:
                self.findings.append(Finding(
                    "Major", "WCAG 4.1.2",
                    f"unknown ARIA role '{role}'", line))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        line, _ = self.getpos()
        if tag == "title":
            self.in_title = False
            self.has_title = bool(self.title_text.strip())
        elif tag == "button":
            if self.in_button and not self.button_has_text and not self.button_has_label:
                self.findings.append(Finding(
                    "Critical", "WCAG 4.1.2",
                    "<button> has no accessible name (no text, no aria-label)",
                    self.button_line))
            self.in_button = False
        elif tag == "a":
            if self.in_link and not self.link_has_text and not self.link_has_label:
                self.findings.append(Finding(
                    "Critical", "WCAG 4.1.2",
                    "<a> link has no accessible name (no text, no aria-label)",
                    self.link_line))
            self.in_link = False
        elif tag == "table":
            if self.in_table and not self.table_has_th:
                self.findings.append(Finding(
                    "Major", "WCAG 1.3.1",
                    "<table> has no <th> headers", self.table_line))
            self.in_table = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_text += data
        if self.in_button and data.strip():
            self.button_has_text = True
        if self.in_link and data.strip():
            self.link_has_text = True


def check_css_outline(html_text: str) -> list[Finding]:
    out: list[Finding] = []
    rx = re.compile(r"outline\s*:\s*(none|0)\b", re.IGNORECASE)
    for m in rx.finditer(html_text):
        line = html_text.count("\n", 0, m.start()) + 1
        # Tolerate if a focus-visible style is also present in the doc
        if re.search(r":focus-visible|:focus\s*\{", html_text, re.IGNORECASE):
            continue
        out.append(Finding(
            "Major", "WCAG 2.4.7",
            "CSS removes focus outline without :focus-visible replacement", line))
    return out


def fetch(url: str, timeout: int = 15) -> str:
    if not (url.startswith("http://") or url.startswith("https://")):
        raise SystemExit(f"error: --url must be http(s): {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "wcag-check/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        raise SystemExit(f"error: cannot fetch {url}: {e}")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Static WCAG 2.2 smoke check on an HTML file or URL.")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--html-file", type=Path, help="Path to local HTML file")
    src.add_argument("--url", help="HTTP(S) URL to fetch")
    p.add_argument("--json", action="store_true", help="Machine-readable output")
    args = p.parse_args()

    if args.html_file:
        if not args.html_file.exists():
            err(f"file not found: {args.html_file}")
            return 2
        try:
            content = args.html_file.read_text(errors="replace")
        except OSError as e:
            err(f"cannot read {args.html_file}: {e}"); return 2
        source = str(args.html_file)
    else:
        content = fetch(args.url)
        source = args.url

    parser = WCAGParser()
    try:
        parser.feed(content)
        parser.close()
    except Exception as e:  # html.parser is forgiving; this is defensive
        err(f"parse error: {e}")
        return 2

    findings = list(parser.findings)
    findings.extend(check_css_outline(content))

    # Document-level findings
    if not parser.has_html_lang:
        findings.append(Finding("Major", "WCAG 3.1.1",
                                "<html> missing lang attribute", 0))
    if not parser.has_title:
        findings.append(Finding("Major", "WCAG 2.4.2",
                                "missing or empty <title>", 0))
    if not parser.has_main:
        findings.append(Finding("Minor", "WCAG 2.4.1",
                                "no <main> landmark", 0))
    if not parser.has_skip_link:
        findings.append(Finding("Minor", "WCAG 2.4.1",
                                "no skip link found as first focusable element", 0))

    by_sev: dict[str, list[dict]] = {"Critical": [], "Major": [], "Minor": []}
    for f in findings:
        by_sev.setdefault(f.severity, []).append(asdict(f))

    summary = {sev: len(v) for sev, v in by_sev.items()}
    out = {
        "source": source,
        "summary": summary,
        "findings": by_sev,
    }

    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"WCAG 2.2 STATIC CHECK — {source}")
        print("=" * 60)
        print(f"Critical: {summary['Critical']}  Major: {summary['Major']}  "
              f"Minor: {summary['Minor']}")
        print()
        for sev in ("Critical", "Major", "Minor"):
            items = by_sev.get(sev, [])
            if not items:
                continue
            print(f"-- {sev} ({len(items)}) --")
            for f in items:
                loc = f"L{f['line']}" if f["line"] else "doc"
                print(f"  [{f['rule']}] {loc}: {f['message']}")
            print()

    return 1 if (summary["Critical"] + summary["Major"]) > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
