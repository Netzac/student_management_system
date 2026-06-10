from django.core.exceptions import ObjectDoesNotExist

def get_lookup_field_value(obj, lookup_expr):
    """
    Resolves a Django ORM lookup expression like 'course__name' or 'parent__phone'
    to get the actual value from an object for export purposes.
    """
    parts = lookup_expr.split('__')
    current = obj
    try:
        for part in parts:
            current = getattr(current, part)
        return current
    except (AttributeError, ObjectDoesNotExist):
        return None

def safe_str(value):
    """Safely converts a value to string, handling None and special cases."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    return str(value)

def get_model_verbose_name(model):
    """Helper to get model's verbose name nicely."""
    return model._meta.verbose_name.title()
