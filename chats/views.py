# chats/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils.crypto import get_random_string
from .models import ChatSession, Message
from .serializers import ChatSessionSerializer, MessageSerializer

class ChatSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing chat sessions and messages.
    """
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user, is_active=True)
    
    def create(self, request):
        character_id = request.data.get('character_id')
        if not character_id:
            return Response(
                {'error': 'character_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check for existing active session
        existing_session = ChatSession.objects.filter(
            user=request.user,
            character_id=character_id,
            is_active=True
        ).first()
        
        if existing_session:
            serializer = self.get_serializer(existing_session)
            return Response(serializer.data)
        
        # Create new session
        room_id = get_random_string(32)
        session = ChatSession.objects.create(
            user=request.user,
            character_id=character_id,
            room_id=room_id
        )
        
        serializer = self.get_serializer(session)
        return Response(serializer.data)
    
    @action(detail=True)
    def messages(self, request, pk=None):
        """Get paginated message history for a session"""
        session = self.get_object()
        messages = Message.objects.filter(chat_session=session).order_by('-timestamp')
        page = self.paginate_queryset(messages)
        
        if page is not None:
            serializer = MessageSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True)
    def context(self, request, pk=None):
        """Get recent conversation context"""
        session = self.get_object()
        messages = Message.objects.filter(
            chat_session=session
        ).order_by('-timestamp')[:5]
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)