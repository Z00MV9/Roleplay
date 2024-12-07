# api/v1/urls.py
from django.urls import path, include
from characters.views import CharacterViewSet
from chats.views import ChatSessionViewSet  # Import chat_room view
from rest_framework.routers import DefaultRouter
from custom_auth.views import LoginView, LogoutView, RegisterView, UserDetailView
from django.views.generic import TemplateView

# Create router for ViewSet based views
router = DefaultRouter()
router.register(r'chats', ChatSessionViewSet, basename='chats')
router.register(r'characters', CharacterViewSet, basename='characters')

# Combine router URLs with regular paths
urlpatterns = [
    path('', include(router.urls)),
    path('chat/', TemplateView.as_view(template_name='chats/chat.html'), name='chat'),
    path('auth/', include([
        path('register/', RegisterView.as_view(), name='auth_register'),
        path('login/', LoginView.as_view(), name='login'),
        path('logout/', LogoutView.as_view(), name='logout'),
        path('user/', UserDetailView.as_view(), name='auth_user_detail'),
    ])),
    path('oauth/', include('oauth2_provider.urls')),
]