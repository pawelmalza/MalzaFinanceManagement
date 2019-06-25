from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


def file_size_validator(value):
    file_size = value.size

    if file_size != 32:
        raise ValidationError("Wrong key size, upload valid key")
    else:
        return value


def validate_login_exists(value):
    if User.objects.filter(username=value):
        raise ValidationError(
            "Podana nazwa jest zajęta"
        )


def validate_mail_exists(value):
    if User.objects.filter(email=value):
        raise ValidationError(
            "Podany adres jest zajęty"
        )

