"""Tests for the committed SVG figures.

SVG is strict XML: one raw < or & in a label makes the browser reject the
whole image, and the site ships a broken figure without any build error. A
legend reading "phase < 0.5" did exactly this once. The generator now escapes
text and validates each document before writing; this test guards the
committed artifacts themselves, so hand edits and stale files are caught by
CI as well.

Run from the repo root:  python3 -m unittest discover -s code
"""

import glob
import os
import unittest
import xml.etree.ElementTree as ET

IMG_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..",
                                        "prototype", "img"))


class TestCommittedFigures(unittest.TestCase):
    def test_every_svg_is_well_formed_xml(self):
        paths = sorted(glob.glob(os.path.join(IMG_DIR, "*.svg")))
        self.assertGreaterEqual(len(paths), 13, "expected the book's figures")
        for path in paths:
            with self.subTest(figure=os.path.basename(path)):
                ET.parse(path)

    def test_every_svg_carries_title_and_desc(self):
        ns = "{http://www.w3.org/2000/svg}"
        for path in sorted(glob.glob(os.path.join(IMG_DIR, "*.svg"))):
            with self.subTest(figure=os.path.basename(path)):
                root = ET.parse(path).getroot()
                self.assertIsNotNone(root.find(f"{ns}title"))
                self.assertIsNotNone(root.find(f"{ns}desc"))
