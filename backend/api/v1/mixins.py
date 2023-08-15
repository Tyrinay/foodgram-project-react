from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response

from recipes.models import User
from users.models import Follow


class SubscriptionMixin:
    def toggle_subscription(self, request, id):
        """Добавление/удаление автора рецепта в подписки."""
        author = get_object_or_404(User, pk=id)
        user = request.user
        if user.is_authenticated:
            subscription, created = Follow.objects.get_or_create(
                user=user,
                author=author
            )
            if not created:
                subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
