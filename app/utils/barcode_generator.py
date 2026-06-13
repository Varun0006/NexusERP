import io
import barcode
from barcode.writer import ImageWriter


def generate_barcode(code, format="code128"):
    try:
        barcode_class = barcode.get_barcode_class(format)
        barcode_instance = barcode_class(code, writer=ImageWriter())
        buffer = io.BytesIO()
        barcode_instance.write(buffer)
        buffer.seek(0)
        return buffer
    except Exception:
        return None


def generate_ean13(code):
    return generate_barcode(code, "ean13")
