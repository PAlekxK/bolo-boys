"""Generate the Bolo Boys QR code.

Plain black-on-white, no embellishments. Encodes https://www.boloboys.band/.
Outputs a high-res PNG and a vector SVG to assets/qr/.
"""
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_M
from qrcode.image.svg import SvgPathImage

URL = "https://www.boloboys.band/"
OUT_DIR = Path(__file__).resolve().parent.parent / "assets" / "qr"
OUT_PNG = OUT_DIR / "boloboys-band.png"
OUT_SVG = OUT_DIR / "boloboys-band.svg"

QR_PX = 1200  # PNG canvas size


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_M,
        box_size=20,
        border=4,
    )
    qr.add_data(URL)
    qr.make(fit=True)

    png = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    png = png.resize((QR_PX, QR_PX))
    png.save(OUT_PNG, "PNG", optimize=True)
    print(f"Wrote {OUT_PNG} ({QR_PX}x{QR_PX}) — encoding {URL}")

    svg = qr.make_image(image_factory=SvgPathImage)
    svg.save(str(OUT_SVG))
    print(f"Wrote {OUT_SVG} (vector) — encoding {URL}")


if __name__ == "__main__":
    main()
