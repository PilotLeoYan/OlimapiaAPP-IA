import qrcode
from qrcode.image import pil

def create_qr(text: str) -> pil.PilImage:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        border=0,
    )

    qr.add_data(text)
    qr.make(fit=True)

    return qr.make_image()


# https://pypi.org/project/qrcode/