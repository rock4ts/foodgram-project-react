from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .validators import username_validator


class User(AbstractUser):
    username = models.CharField(
        unique=True, max_length=150, verbose_name='Имя пользователя',
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message=(
                    'Username may only consist of letters,',
                    'digits and @/./+/-/_'
                ),
            ),
            username_validator,
        ]
    )
    password = models.CharField(
        max_length=150, verbose_name="Пароль"
    )
    email = models.EmailField(
        max_length=254, verbose_name="Электронная почта", unique=True
    )
    first_name = models.CharField(
        max_length=150, verbose_name="Имя"
    )
    last_name = models.CharField(
        max_length=150, verbose_name="Фамилия"
    )

    def __str__(self):
        return self.username


class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name="Подписчики"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="followers",
        verbose_name="Авторы"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["follower", "author"],
                name="unique_follow_constraint"
            ),
            models.CheckConstraint(
                check=~models.Q(follower=models.F("author")),
                name="self_follow_constraint"
            )
        ]

    def __str__(self):
        return f'{self.follower.username} follows {self.author.username}'
