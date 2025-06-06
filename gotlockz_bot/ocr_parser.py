"""OCR parsing utilities."""

from PIL import Image
import pytesseract


def parse_image(path: str) -> str:
    """Extract text from an image file."""
    img = Image.open(path)
    return pytesseract.image_to_string(img)
