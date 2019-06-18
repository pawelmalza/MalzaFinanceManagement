from django.core.exceptions import ValidationError

def file_size_validator(value):

    file_size = value.size

    if file_size != 32:
        raise ValidationError("Wrong key size, upload valid key")
    else:
        return value