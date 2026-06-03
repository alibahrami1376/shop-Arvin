import re

from django.core.exceptions import ValidationError
from accounts.messages import PHONE_REQUIRED,INVALID_PHONE_NUMBER,PERSIAN_NUMBER,LATIN_NUMBER

def validate_iranian_cellphone_number(value:str):
    """
    Validate an Iranian mobile phone number (11 digits, starts with 09).
    """
    if value is None:
        raise ValidationError(PHONE_REQUIRED)
    # Persian numbers to Latin    
    trans = str.maketrans(PERSIAN_NUMBER, LATIN_NUMBER)
    s = value.translate(trans)
    pattern = r"^09\d{9}$"
    if not re.match(pattern, s):
        raise ValidationError(INVALID_PHONE_NUMBER)
    return s
