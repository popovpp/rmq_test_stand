import segno


def make_qr(source: str):
    qrcode = segno.make_qr(source).png_data_uri(
        scale=15,
        border=3,
        dark="darkblue"
    )
    return qrcode
