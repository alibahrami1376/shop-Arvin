from rest_framework.views import exception_handler

from core.forms_persian import translate_error_message


def _translate_value(value):
    if isinstance(value, str):
        return translate_error_message(value)
    if isinstance(value, list):
        return [_translate_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _translate_value(item) for key, item in value.items()}
    return value


def persian_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response
    response.data = _translate_value(response.data)
    return response
