# gamsat-dewatermark

A short script to remove personal watermarks from ACER GAMSAT preparation PDFs. The watermarks (name, DOB, email) are embedded diagonally across each page and interfere with selecting and copying text.

## How it works

Rather than using rectangle-based redaction (which destroys content underneath diagonal text), the script edits the PDF content stream — locating and removing the `q...Q` graphics state block that contains the watermark, leaving everything else untouched.

## Usage

**1. Install Python** if you don't have it: https://www.python.org/downloads/

**2. Install the dependency** — open a terminal in this folder and run:
```bash
pip install -r requirements.txt
```

**3. Add your PDFs** to the `pdf/input/` folder.

**4. Run the script:**
```bash
python scripts/remove_gamsat_watermark.py
```

Cleaned PDFs will appear in `pdf/output/` with the same filename.

## Configuration

Edit `WATERMARK_STRINGS` at the top of `scripts/remove_gamsat_watermark.py` to match the watermark text in your PDF.

```python
WATERMARK_STRINGS = [
    "Your Name Here",
    "DOB: DD-MM-YYYY",
    "your.email@example.com",
]
```
