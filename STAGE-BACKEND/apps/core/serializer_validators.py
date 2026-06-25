import bleach
from django.utils import timezone
from rest_framework import serializers


def clean_text(value):
    if value is None:
        return value
    return bleach.clean(str(value), tags=[], attributes={}, strip=True).strip()


def clean_text_fields(serializer, attrs):
    for field_name, value in list(attrs.items()):
        field = serializer.fields.get(field_name)
        if isinstance(value, str) and isinstance(field, serializers.CharField):
            attrs[field_name] = clean_text(value)
    return attrs


class SanitizedModelSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        return clean_text_fields(self, attrs)


def validate_not_blank(value, message):
    value = clean_text(value)
    if isinstance(value, str) and not value:
        raise serializers.ValidationError(message)
    return value


def validate_not_future(value, message):
    if value and value > timezone.localdate():
        raise serializers.ValidationError(message)
    return value


def validate_positive(value, message):
    if value is not None and value <= 0:
        raise serializers.ValidationError(message)
    return value


def validate_not_negative(value, message):
    if value is not None and value < 0:
        raise serializers.ValidationError(message)
    return value


def validate_choice(value, allowed_values, message):
    value = clean_text(value)
    if value and value.upper() not in allowed_values:
        raise serializers.ValidationError(message)
    return value
