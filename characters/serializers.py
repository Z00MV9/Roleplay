from characters.models import Character
from rest_framework import serializers

class CharacterSerializer(serializers.ModelSerializer):
    creator = serializers.ReadOnlyField(source='creator.username')
    
    class Meta:
        model = Character
        fields = ['id', 'name', 'creator', 'avatar', 'description', 
                 'personality', 'category', 'greeting_message', 
                 'is_public', 'chat_count', 'created_at']
        read_only_fields = ['creator', 'chat_count']
        extra_kwargs = {
            'avatar': {'required': False, 'allow_null': True}  # Add allow_null=True
        }
