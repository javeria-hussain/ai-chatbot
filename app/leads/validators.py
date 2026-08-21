import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PLACEHOLDER_VALUES = {"n/a", "na", "none", "test", "asdf", "xyz", "-", "."}


def validate_field(field: str, value: str) -> str | None:
    """Returns an error message if invalid, else None."""
    value = value.strip()

    if field in ("name", "phone") and len(value) < 2:
        return f"{field} is very short."

    if value.lower() in PLACEHOLDER_VALUES:
        return f"Ye {field} not valid.Enter correct value."

    if field == "email" and not EMAIL_PATTERN.match(value):
        return "Email format not correct (like: name@example.com)."

    if field == "phone":
        digits = re.sub(r"[^\d]", "", value)
        if len(digits) < 7:
            return "Phone is very short."

    return None