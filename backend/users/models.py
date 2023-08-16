from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CheckConstraint, UniqueConstraint

from foodgram.settings import MAX_USERNAME_LENGTH


class User(AbstractUser):
    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True,
    )

    username = models.CharField(
        'Username',
        max_length=MAX_USERNAME_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='uq_username_email'
            ),
        ]

    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Follower"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name='Author'
    )

    class Meta:
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='uq_user_author'
            ),
            CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='prevent_self_follow',
            )
        ]
