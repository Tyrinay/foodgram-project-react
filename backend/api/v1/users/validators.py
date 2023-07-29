from django.core import exceptions


def validate_username_me(value):
    if value == 'me':
        raise exceptions.ValidationError(
            'Имя пользователя "me" не разрешено'
        )
    return value
