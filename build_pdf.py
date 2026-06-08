"""Build a styled PDF from Mumz_Assistant_QA.md using markdown + fpdf2 (pure Python)."""
import re
from pathlib import Path

import markdown as md
from fpdf import FPDF, HTMLMixin

BASE = Path(__file__).resolve().parent
SRC = BASE / "Mumz_Assistant_QA.md"
OUT = BASE / "Mumz_Assistant_QA.pdf"

text = SRC.read_text(encoding="utf-8")

# Normalise any non-latin-1 characters so the core PDF fonts render cleanly.
replacements = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "…": "...", "→": "->",
    " ": " ", "•": "-", "️": "", "\U0001f338": "",
}
for bad, good in replacements.items():
    text = text.replace(bad, good)
# Drop anything still outside latin-1 to avoid encoder errors.
text = text.encode("latin-1", "ignore").decode("latin-1")

html_body = md.markdown(text, extensions=["tables", "fenced_code", "sane_lists"])


class PDF(FPDF, HTMLMixin):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150)
        self.cell(0, 8, "Mumz Assistant - Interview Q&A", align="L")
        self.cell(0, 8, f"Page {self.page_no()}", align="R")
        self.ln(10)
        self.set_text_color(0)

    def footer(self):
        pass


pdf = PDF(format="A4")
pdf.set_auto_page_break(auto=True, margin=18)
pdf.set_margins(18, 18, 18)
pdf.add_page()

# fpdf2's write_html honours a subset of tags + inline styles.
styled = f"""
<style>
h1 {{ color: #b5377e; font-size: 20pt; }}
h2 {{ color: #b5377e; font-size: 14pt; }}
h3 {{ color: #333333; font-size: 12pt; }}
b {{ color: #1a1a1a; }}
td, th {{ border: 0.5px solid #cccccc; padding: 3px; }}
th {{ background-color: #f4d9e8; }}
</style>
{html_body}
"""

pdf.write_html(styled)
pdf.output(str(OUT))
print(f"WROTE {OUT}  ({OUT.stat().st_size // 1024} KB, {pdf.page_no()} pages)")
