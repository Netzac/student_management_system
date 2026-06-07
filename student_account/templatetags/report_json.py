import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe


register = template.Library()

_JSON_SCRIPT_ESCAPES = {
    ord(">"): "\\u003E",
    ord("<"): "\\u003C",
    ord("&"): "\\u0026",
}


@register.filter
def jsonify(value):
    """Serialize report data for safe inline JavaScript assignment."""
    json_value = json.dumps(value, cls=DjangoJSONEncoder).translate(_JSON_SCRIPT_ESCAPES)
    return mark_safe(json_value)


@register.filter
def get_item(value, key):
    if isinstance(value, dict):
        return value.get(key)
    return getattr(value, key, None)
