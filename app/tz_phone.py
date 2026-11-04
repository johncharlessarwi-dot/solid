"""Customer contact normalization for Tanzanian mobile numbers."""
import re


def normalize_tz_mobile(value):
    if not isinstance(value, str):
        raise ValueError("Mobile phone must be text")
    digits = re.sub(r"[\s()-]", "", value)
    if re.fullmatch(r"\+255[67]\d{8}", digits):
        local = digits[4:]
    elif re.fullmatch(r"255[67]\d{8}", digits):
        local = digits[3:]
    elif re.fullmatch(r"0[67]\d{8}", digits):
        local = digits[1:]
    elif re.fullmatch(r"[67]\d{8}", digits):
        local = digits
    else:
        raise ValueError("Invalid Tanzania mobile number")
    return "+255" + local
