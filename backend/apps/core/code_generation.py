import re


def generate_prefixed_code(model, field_name, prefix, width=5):
    pattern = re.compile(rf"^{re.escape(prefix)}(\d+)$")
    values = model.objects.filter(**{f"{field_name}__startswith": prefix}).values_list(field_name, flat=True)
    last_number = 0

    for value in values:
        match = pattern.match(value or "")
        if match:
            last_number = max(last_number, int(match.group(1)))

    number = last_number + 1
    while True:
        code = f"{prefix}{number:0{width}d}"
        if not model.objects.filter(**{field_name: code}).exists():
            return code
        number += 1
