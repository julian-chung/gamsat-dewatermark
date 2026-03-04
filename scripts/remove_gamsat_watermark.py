import fitz
import re
from pathlib import Path

WATERMARK_STRINGS = [
    "John Jacob Jingleheimer Schmidt",
    "DOB: 01-01-1990",
    "john.j.schmidt@gmail.com",
]

GS_LINE = re.compile(r'^/GS\d+ gs$')


def find_watermark_block(lines):
    """Return (start, end) line indices of the q...Q block containing watermark text."""
    anchor_idx = None
    for i, line in enumerate(lines):
        compressed = ''.join(c for c in line if c not in ' \x00()[]').lower()
        for wm in WATERMARK_STRINGS:
            wm_compressed = wm.replace(' ', '').lower()
            if wm_compressed in compressed:
                anchor_idx = i
                break
        if anchor_idx is not None:
            break

    if anchor_idx is None:
        return None, None

    # Walk backwards to find the nearest standalone q
    q_idx = None
    depth = 0
    for i in range(anchor_idx - 1, -1, -1):
        s = lines[i].strip()
        if s == 'Q':
            depth += 1
        elif s == 'q':
            if depth == 0:
                q_idx = i
                break
            depth -= 1

    if q_idx is None:
        return None, None

    # Walk forwards to find the matching standalone Q
    Q_idx = None
    depth = 1
    for i in range(q_idx + 1, len(lines)):
        s = lines[i].strip()
        if s == 'q':
            depth += 1
        elif s == 'Q':
            depth -= 1
            if depth == 0:
                Q_idx = i
                break

    if Q_idx is None:
        return None, None

    # Expand to include adjacent /GS* gs lines (opacity settings for the watermark)
    start = q_idx
    end = Q_idx
    if start > 0 and GS_LINE.match(lines[start - 1].strip()):
        start -= 1
    if end < len(lines) - 1 and GS_LINE.match(lines[end + 1].strip()):
        end += 1

    return start, end


def remove_watermark_from_stream(content_bytes):
    content = content_bytes.decode('latin-1')
    lines = content.split('\n')

    while True:
        start, end = find_watermark_block(lines)
        if start is None:
            break
        lines = lines[:start] + lines[end + 1:]

    return '\n'.join(lines).encode('latin-1')


input_dir = Path(__file__).parent.parent / "pdf" / "input"
output_dir = Path(__file__).parent.parent / "pdf" / "output"
output_dir.mkdir(parents=True, exist_ok=True)

for pdf_path in sorted(input_dir.glob("*.pdf")):
    doc = fitz.open(pdf_path)

    for page in doc:
        for xref in page.get_contents():
            stream = doc.xref_stream(xref)
            new_stream = remove_watermark_from_stream(stream)
            if new_stream != stream:
                doc.update_stream(xref, new_stream)

    out_path = output_dir / pdf_path.name
    doc.save(out_path)
    print(f"Saved: {out_path}")
