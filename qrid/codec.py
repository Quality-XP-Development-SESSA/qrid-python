import base64
import binascii
import io
import json
from typing import TypedDict


class QRIdPayload(TypedDict):
    v: int
    id: str
    company: str
    email: str
    address: str
    activity_code: str


def decode_qr_id(encoded: str) -> QRIdPayload:
    """Decode a base64-encoded QR ID string into its structured payload.

    Mirrors QRId\\Codec::decodeQRId() in qrid/codec (PHP).

    Args:
        encoded: The base64 string read from a MergeID QR code.

    Returns:
        A TypedDict with keys: v, id, company, email, address, activity_code.

    Raises:
        ValueError: When the base64 input is malformed.
        json.JSONDecodeError: When the decoded content is not valid JSON.
    """
    trimmed = encoded.strip()
    try:
        json_bytes = base64.b64decode(trimmed, validate=True)
    except binascii.Error:
        raise ValueError(
            "Invalid base64 input: could not decode the provided string."
        )
    return json.loads(json_bytes.decode("utf-8"))


def encode_qr_id(
    id: str,
    company: str,
    email: str,
    address: str,
    activity_code: str = "",
) -> str:
    """Encode invoice identity fields and return an SVG QR code string.

    Mirrors QRId\\Codec::encodeQRId() in qrid/codec (PHP).
    Requires the encode extra: pip install 'qrid[encode]'

    Args:
        id:            Tax / company registration ID.
        company:       Company legal name (UTF-8).
        email:         Primary billing or contact e-mail address.
        address:       Physical address of the company.
        activity_code: Installation or activity code. May be blank, which
            signals a consuming system to generate an electronic ticket
            instead.

    Returns:
        An SVG markup string containing the generated QR code.

    Raises:
        ImportError: When the segno package is not installed.
    """
    try:
        import segno
    except ImportError:
        raise ImportError(
            "segno is required for encode_qr_id(). "
            "Install with: pip install 'qrid[encode]'"
        )

    payload: QRIdPayload = {
        "v": 1,
        "id": id,
        "company": company,
        "email": email,
        "address": address,
        "activity_code": activity_code,
    }
    encoded = base64.b64encode(
        json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ).decode()

    qr = segno.make_qr(encoded)
    buf = io.BytesIO()
    qr.save(buf, kind="svg", nl=False)
    return buf.getvalue().decode("utf-8")
