from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from users.models import User

from ..mixins import SubscriptionMixin
from ..pagination import CustomPagination
from .serializers import CustomUserSerializer, SubscribeListSerializer


class UserViewSet(UserViewSet, SubscriptionMixin):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']
    pagination_class = CustomPagination

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated, ]
    )
    def subscribe(self, request, id=None):
        """Добавление/удаление автора рецепта в подписки."""
        return self.toggle_subscription(request, id)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeListSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
