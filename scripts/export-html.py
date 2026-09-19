#!/usr/bin/env python3
"""
Render STRx-ble-advertising.md to a single self-contained HTML file.

The images under docs/img are embedded as data URIs and the mermaid packet
diagrams are rendered in the browser, so the output can be handed out as one
file. Requires markdown-it-py, installed on first run if missing.

Copyright (c) 2025 SIMARINE d.o.o.
"""

import base64
import mimetypes
import re
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
MD_FILE = PROJECT_ROOT / "STRx-ble-advertising.md"
HTML_FILE = PROJECT_ROOT / "STRx-ble-advertising.html"

HEADING_PATTERN = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t]*$", re.MULTILINE)
IMG_SRC_PATTERN = re.compile(r'(<img\b[^>]*\bsrc=")([^"]+)(")')
MERMAID_PATTERN = re.compile(r'<pre><code class="language-mermaid">(.*?)</code></pre>', re.DOTALL)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        }});
    </script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        h1, h2, h3, h4 {{ color: #2c3e50; margin-top: 1.5em; }}
        h1 {{ border-bottom: 2px solid #3498db; padding-bottom: 0.3em; }}
        h2 {{ border-bottom: 1px solid #bdc3c7; padding-bottom: 0.2em; }}
        table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px 12px; text-align: left; }}
        th {{ background-color: #3498db; color: white; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
        }}
        pre {{ background-color: #f4f4f4; padding: 15px; border-radius: 5px; overflow-x: auto; }}
        pre code {{ background-color: transparent; padding: 0; }}
        .mermaid {{ background-color: #fff; padding: 10px; margin: 1em 0; }}
        ul, ol {{ padding-left: 2em; }}
        li {{ margin: 0.3em 0; }}
        img {{
            height: auto;
            vertical-align: top;
            margin: 0 8px 8px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
{content}
</body>
</html>
"""


def check_renderer_installed() -> None:
    """Install markdown-it-py if it is missing."""
    try:
        import markdown_it  # noqa: F401
    except ImportError:
        print("Installing markdown-it-py...", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown-it-py", "-q"])


def first_heading(md_text: str) -> str:
    """Title of the document, its first heading."""
    match = HEADING_PATTERN.search(md_text)
    return match.group(1) if match else MD_FILE.stem


def slugify(text: str) -> str:
    """Heading anchor id: lowercase, words joined by dashes."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    return re.sub(r"[-\s]+", "-", text)


def embed_images(html_content: str) -> str:
    """Inline every local image as a data URI, remote sources are left alone."""

    def replace(match: re.Match) -> str:
        src = match.group(2)
        if re.match(r"^(?:[a-z]+:|//)", src):
            return match.group(0)
        path = PROJECT_ROOT / src
        if not path.is_file():
            raise FileNotFoundError(f"image {src} referenced by the documentation")
        mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        data = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"{match.group(1)}data:{mime};base64,{data}{match.group(3)}"

    return IMG_SRC_PATTERN.sub(replace, html_content)


def convert_mermaid_blocks(html_content: str) -> str:
    """Turn fenced mermaid blocks into elements Mermaid.js renders."""

    def replace(match: re.Match) -> str:
        content = match.group(1)
        content = content.replace("&lt;", "<").replace("&gt;", ">")
        content = content.replace("&amp;", "&").replace("&quot;", '"')
        return f'<pre class="mermaid">{content}</pre>'

    return MERMAID_PATTERN.sub(replace, html_content)


def render_markdown(md_text: str) -> str:
    """Render CommonMark with tables to an HTML body with linkable headings."""
    check_renderer_installed()
    from markdown_it import MarkdownIt

    md = MarkdownIt("commonmark").enable(["table", "strikethrough"])
    used_ids: dict[str, int] = {}

    def heading_open(self, tokens, idx, options, env):
        slug = slugify(tokens[idx + 1].content)
        count = used_ids.get(slug, 0)
        used_ids[slug] = count + 1
        tokens[idx].attrSet("id", slug if count == 0 else f"{slug}_{count}")
        return self.renderToken(tokens, idx, options, env)

    md.add_render_rule("heading_open", heading_open)
    return embed_images(convert_mermaid_blocks(md.render(md_text)))


def main() -> int:
    """Render the specification and report the output file."""
    if not MD_FILE.exists():
        print(f"Error: {MD_FILE} not found", file=sys.stderr)
        return 1

    md_text = MD_FILE.read_text(encoding="utf-8")
    title = first_heading(md_text)
    try:
        html = HTML_TEMPLATE.format(title=title, content=render_markdown(md_text))
    except FileNotFoundError as missing:
        print(f"Error: {missing} not found", file=sys.stderr)
        return 1

    HTML_FILE.write_text(html, encoding="utf-8")
    print(f"Generated {HTML_FILE.name} ({title})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
