"""Ethiopian phone number normalisation and validation (+2519XXXXXXXX)."""

import re

_DIGITS_ONLY = re.compile(r"[^\d]")
_VALID_E164_ET = re.compile(r"^\+2519\d{8}$")


def normalize_ethiopian_phone(phone: str) -> str:
    if not phone:
        return phone
    digits = _DIGITS_ONLY.sub("", phone)

    if digits.startswith("251") and len(digits) == 12:
        return f"+{digits}"
    if digits.startswith("0") and len(digits) == 10:
        return f"+251{digits[1:]}"
    if len(digits) == 9 and digits.startswith("9"):
        return f"+251{digits}"
    return f"+{digits}" if not phone.startswith("+") else phone


def is_valid_ethiopian_phone(phone: str) -> bool:
    return bool(_VALID_E164_ET.match(normalize_ethiopian_phone(phone)))
