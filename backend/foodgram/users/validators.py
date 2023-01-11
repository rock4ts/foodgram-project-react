from django.forms import ValidationError


def username_validator(username):
    """
    Validates that username not equal to string 'me'
    """
    if username.lower() == 'me':
        raise ValidationError(
            f"Недопустимое имя пользователя: {username}."
        )
    return username
