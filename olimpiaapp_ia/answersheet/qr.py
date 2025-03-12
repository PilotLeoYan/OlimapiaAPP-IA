import qrcode


def create_qr(text: str) -> None:
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_H
    )

    qr.add_data('Some data')
    qr.make(fit=True)

    return qr


# https://pypi.org/project/qrcode/