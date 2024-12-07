# chats/consumers.py
import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatSession, Message
from .utils import get_chatgpt_response
from characters.models import Character

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"
        
        # Verify chat session exists and user has access
        session = await self.get_chat_session()
        if not session:
            await self.close()
            return
            
        self.chat_session = session
        self.character = await self.get_character(session.character_id)
        
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        
        # Send character greeting
        if self.character:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": self.character.greeting_message,
                    "username": self.character.name,
                    "is_ai": True,
                },
            )

    @database_sync_to_async
    def get_chat_session(self):
        try:
            return ChatSession.objects.get(
                room_id=self.room_id,
                user=self.scope["user"],
                is_active=True
            )
        except ChatSession.DoesNotExist:
            return None

    @database_sync_to_async
    def get_character(self, character_id):
        try:
            return Character.objects.get(id=character_id)
        except Character.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, content, is_ai=False):
        return Message.objects.create(
            chat_session=self.chat_session,
            content=content,
            is_ai=is_ai
        )

    @database_sync_to_async
    def get_conversation_history(self):
        messages = Message.objects.filter(
            chat_session=self.chat_session
        ).order_by('-timestamp')[:5]
        
        history = []
        for msg in reversed(messages):
            role = "assistant" if msg.is_ai else "user"
            history.append({"role": role, "content": msg.content})
        return history

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json["message"]
            
            # Save and broadcast user message
            await self.save_message(message, is_ai=False)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": message,
                    "username": self.scope["user"].username,
                    "is_ai": False,
                },
            )

            # Get AI response
            history = await self.get_conversation_history()
            ai_response = await get_chatgpt_response(
                message, 
                history,
                character_id=self.character.id
            )

            # Save and broadcast AI response
            await self.save_message(ai_response, is_ai=True)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": ai_response,
                    "username": self.character.name,
                    "is_ai": True,
                },
            )

        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                "error": "Error processing message"
            }))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "username": event["username"],
            "is_ai": event.get("is_ai", False),
        }))