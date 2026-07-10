import base64
import json

import pytest

from qrid import QRIdPayload, decode_qr_id, encode_qr_id


# ── helpers ───────────────────────────────────────────────────────────────────

def encode(payload: dict) -> str:
    return base64.b64encode(
        json.dumps(payload, ensure_ascii=False).encode("utf-8")
    ).decode()


def sample_payload(**overrides) -> QRIdPayload:
    p: QRIdPayload = {
        "v": 1,
        "id": "3101679980",
        "company": "Acme Corp S.A.",
        "email": "billing@acme.example",
        "address": "123 Main St, San José, Costa Rica",
        "activity_code": "ACT-001",
    }
    p.update(overrides)  # type: ignore[typeddict-item]
    return p


# ── decode_qr_id ──────────────────────────────────────────────────────────────

class TestDecodeQRId:
    def test_returns_all_fields(self):
        result = decode_qr_id(encode(sample_payload()))

        assert result["v"] == 1
        assert result["activity_code"] == "ACT-001"
        assert result["id"] == "3101679980"
        assert result["company"] == "Acme Corp S.A."
        assert result["email"] == "billing@acme.example"
        assert result["address"] == "123 Main St, San José, Costa Rica"

    def test_handles_utf8(self):
        result = decode_qr_id(
            encode(sample_payload(
                company="Société Générale",
                address="Paseo Colón, San José, Costa Rica",
            ))
        )

        assert result["company"] == "Société Générale"
        assert result["address"] == "Paseo Colón, San José, Costa Rica"

    def test_trims_surrounding_whitespace(self):
        result = decode_qr_id("  " + encode(sample_payload()) + "  ")
        assert result["activity_code"] == "ACT-001"

    def test_raises_value_error_on_invalid_base64(self):
        with pytest.raises(ValueError, match="Invalid base64 input"):
            decode_qr_id("not-valid-base64!!!")

    def test_raises_on_non_json_payload(self):
        with pytest.raises(json.JSONDecodeError):
            decode_qr_id(base64.b64encode(b"not json").decode())


# ── encode_qr_id ──────────────────────────────────────────────────────────────

class TestEncodeQRId:
    def test_returns_svg_string(self):
        svg = encode_qr_id(
            id="3101679980",
            company="Acme Corp S.A.",
            email="billing@acme.example",
            address="123 Main St",
            activity_code="ACT-001",
        )

        assert isinstance(svg, str)
        assert "<svg" in svg.lower()

    def test_defaults_activity_code_to_blank(self):
        svg = encode_qr_id(
            id="3101679980",
            company="Acme Corp S.A.",
            email="billing@acme.example",
            address="123 Main St",
        )

        assert isinstance(svg, str)
        assert "<svg" in svg.lower()

    def test_round_trip(self):
        p = sample_payload()
        encoded = base64.b64encode(
            json.dumps(p, ensure_ascii=False).encode("utf-8")
        ).decode()

        decoded = decode_qr_id(encoded)

        assert decoded["activity_code"] == p["activity_code"]
        assert decoded["id"] == p["id"]
        assert decoded["company"] == p["company"]

    def test_round_trip_blank_activity_code(self):
        p = sample_payload(activity_code="")
        encoded = base64.b64encode(
            json.dumps(p, ensure_ascii=False).encode("utf-8")
        ).decode()

        decoded = decode_qr_id(encoded)

        assert decoded["activity_code"] == ""
