"""Check that raw-HTML embeds in the built site point at files that exist.

MkDocs validates the links it generates from Markdown, but raw HTML written
directly into a page (an ``<iframe src="...">``, an ``<img src="...">``, an
``<a href="...">``, or a ``<script src="...">``) is opaque to that check. A
relative path in one of these attributes can be wrong, and the build will
still succeed. This is exactly how a broken iframe embed once shipped: the
``src`` resolved one directory too deep and MkDocs never noticed.

This script walks the built site under ``site/`` (the directory is located
relative to this file, so the script works regardless of the current working
directory), scans every ``*.html`` file, extracts the ``src`` and ``href``
values of ``iframe``, ``img``, ``a``, and ``script`` tags, and reports any
local, file-shaped target that does not exist on disk.

Run it from the repository root after a build:

    python3 code/check_embeds.py

It expects ``site/`` to already exist (run ``./env/bin/mkdocs build`` first
if it does not) and exits with status 1 if any target is missing, or 0
otherwise.
"""

import os
import re
import sys
from urllib.parse import urlsplit

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
SITE_DIR = os.path.join(REPO_ROOT, "site")
MKDOCS_YML = os.path.join(REPO_ROOT, "mkdocs.yml")

# Matches src="..." or href="..." (single or double quotes) on iframe, img,
# a, script, audio, and source tags (the last two ahead of the planned audio
# demos). This is a simple attribute scan, not a full HTML parse, but it is
# enough for the flat, machine-generated markup MkDocs emits.
ATTR_PATTERN = re.compile(
    r"""<(?:iframe|img|a|script|audio|source)\b[^>]*?\b(?:src|href)\s*=\s*(["'])(.*?)\1""",
    re.IGNORECASE | re.DOTALL,
)

SKIP_PREFIXES = (
    "http://",
    "https://",
    "//",
    "#",
    "mailto:",
    "data:",
    "javascript:",
)


def find_html_files(root):
    """Yield the paths of every ``*.html`` file under root, recursively."""
    for dirpath, _dirnames, filenames in os.walk(root):
        for name in filenames:
            if name.endswith(".html"):
                yield os.path.join(dirpath, name)


def extract_targets(html_text):
    """Yield the raw attribute values of embed-like tags in html_text."""
    for match in ATTR_PATTERN.finditer(html_text):
        yield match.group(2)


def is_checkable(value):
    """Return True if value is a local, file-shaped target worth checking."""
    if not value:
        return False
    if value.startswith(SKIP_PREFIXES):
        return False
    stripped = value.split("?", 1)[0].split("#", 1)[0]
    last_segment = stripped.rsplit("/", 1)[-1]
    if last_segment in ("", ".", ".."):
        return False
    return "." in last_segment


def site_base_path():
    """Return the URL path prefix the site deploys under, from mkdocs.yml.

    The site_url in mkdocs.yml carries a base path (for example,
    "/effects-cookbook/" on GitHub Pages), and MkDocs writes root-relative
    links with that prefix. Returns "" if mkdocs.yml or site_url is absent.
    """
    try:
        with open(MKDOCS_YML, "r", encoding="utf-8") as handle:
            for line in handle:
                match = re.match(r"^site_url:\s*(\S+)", line)
                if match:
                    return urlsplit(match.group(1)).path.rstrip("/")
    except OSError:
        pass
    return ""


def resolve_target(value, page_path, site_dir, base_path):
    """Resolve an attribute value to an absolute path, per MkDocs conventions.

    A value starting with "/" resolves against the site root, after any
    site_url base path (for example, "/effects-cookbook") is stripped.
    Otherwise, it resolves against the directory containing the page that
    references it.
    """
    stripped = value.split("?", 1)[0].split("#", 1)[0]
    if stripped.startswith("/"):
        if base_path and stripped.startswith(base_path + "/"):
            stripped = stripped[len(base_path):]
        return os.path.normpath(os.path.join(site_dir, stripped.lstrip("/")))
    page_dir = os.path.dirname(page_path)
    return os.path.normpath(os.path.join(page_dir, stripped))


def main():
    if not os.path.isdir(SITE_DIR):
        print("No site/ directory found. Run ./env/bin/mkdocs build first.")
        return 2

    checked = 0
    missing = 0
    base_path = site_base_path()

    for page_path in sorted(find_html_files(SITE_DIR)):
        with open(page_path, "r", encoding="utf-8") as handle:
            html_text = handle.read()

        page_rel = os.path.relpath(page_path, SITE_DIR)

        for value in extract_targets(html_text):
            if not is_checkable(value):
                continue

            checked += 1
            target = resolve_target(value, page_path, SITE_DIR, base_path)
            site_root = os.path.normpath(SITE_DIR)

            is_outside_site = (
                os.path.commonpath([site_root, target]) != site_root
            )
            if is_outside_site or not os.path.isfile(target):
                missing += 1
                print(f"MISSING  {page_rel}  ->  {value}")

    print(f"Checked {checked} target(s), {missing} missing.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
