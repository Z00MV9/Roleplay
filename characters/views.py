from characters.serializers import CharacterSerializer
from characters import models
from characters.persissions import IsCreatorOrReadOnly
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q

class CharacterViewSet(viewsets.ModelViewSet):
    #throttle_classes = [AnonRateThrottle, UserRateThrottle]
    permission_classes = [IsAuthenticatedOrReadOnly, IsCreatorOrReadOnly]
    serializer_class = CharacterSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'chat_count']

    def get_queryset(self):
        queryset = models.Character.objects.all()
        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(is_public=True) | 
                Q(creator=self.request.user)
            )
        return queryset.filter(is_public=True)

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)