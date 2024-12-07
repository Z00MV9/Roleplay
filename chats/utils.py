from characters.models import Character
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
from channels.db import database_sync_to_async

load_dotenv()
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def create_character_prompt(character):
    return f"""You are roleplaying as {character.name}. Here are your core characteristics:

Description: {character.description}
Personality: {character.personality}

IMPORTANT ROLEPLAY INSTRUCTIONS:
1. Always stay in character and respond as {character.name}
2. Your responses should reflect your personality traits: {character.personality}
3. Never break character or acknowledge being an AI
4. Base your responses on your background: {character.description}
5. Keep responses concise but meaningful, focusing on quality interaction
6. If asked about topics outside your character's knowledge or time period, respond as your character would naturally handle such questions

Your character's unique traits and mannerisms should consistently show in your responses. Engage naturally with users while maintaining your distinct personality."""


@database_sync_to_async
def get_character(character_id):
    try:
        return Character.objects.get(id=character_id)
    except Character.DoesNotExist:
        return None


async def get_chatgpt_response(message, conversation_history=None, character_id=None):
    try:
        messages = []

        # Get character information if character_id is provided
        if character_id:
            character = await get_character(character_id)
            if character:
                # Add character prompt as system message
                messages.append(
                    {"role": "system", "content": create_character_prompt(character)}
                )

                # Add greeting message if this is the first message
                if not conversation_history:
                    messages.append(
                        {"role": "assistant", "content": character.greeting_message}
                    )

        if conversation_history:
            messages.extend(conversation_history)

        messages.append({"role": "user", "content": message})

        response = await client.chat.completions.create(
            model="gpt-4o-mini",
             messages=messages,
            max_tokens=150,
            temperature=0.9,  # Higher temperature for more creative and dynamic responses
            presence_penalty=0.7,  # Encourage diverse responses
            frequency_penalty=0.5,  # Reduce repetitive language
            top_p=0.9,  # Maintain focus while allowing creativity
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting ChatGPT response: {str(e)}")
        return "Sorry, I'm having trouble processing your request."
