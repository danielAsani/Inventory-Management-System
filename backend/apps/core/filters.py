def parse_bool(value):
    if value in (None, ""):
        return None
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "vrai", "oui", "yes"}:
        return True
    if normalized in {"0", "false", "faux", "non", "no"}:
        return False
    return None
