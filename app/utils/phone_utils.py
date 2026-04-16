import re


def normalize_ethiopian_phone(phone: str) -> str:
    """
    Normalizes Ethiopian phone numbers to E.164 format (+251XXXXXXXXX).
    Accepts: 0911234567, 911234567, +251911234567, 251911234567
    """
    digits = re.sub(r"[^\d]", "", phone)

    if digits.startswith("251") and len(digits) == 12:
        return f"+{digits}"

    if digits.startswith("0") and len(digits) == 10:
        return f"+251{digits[1:]}"

    if len(digits) == 9 and digits[0] == "9":
        return f"+251{digits}"

    return f"+{digits}" if not phone.startswith("+") else phone


def is_valid_ethiopian_phone(phone: str) -> bool:
    normalized = normalize_ethiopian_phone(phone)
    return bool(re.match(r"^\+2519\d{8}$", normalized))
