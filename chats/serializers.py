# chats/serializers.py
from rest_framework import serializers
from .models import ChatSession, Message
from characters.serializers import CharacterSerializer

class ChatSessionSerializer(serializers.ModelSerializer):
    character = CharacterSerializer(read_only=True)
    websocket_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'room_id', 'character', 'created_at', 'websocket_url']
        read_only_fields = ['room_id', 'created_at', 'websocket_url']
    
    def get_websocket_url(self, obj):
        request = self.context.get('request')
        if request is None:
            return None
        
        protocol = 'wss' if request.is_secure() else 'ws'
        return f"{protocol}://{request.get_host()}/ws/chat/{obj.room_id}/"

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'content', 'is_ai', 'timestamp']