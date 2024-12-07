from django.db import models
from django.conf import settings

class Character(models.Model):
    name = models.CharField(max_length=100)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='character_avatars/', null=True, blank=True)
    description = models.TextField()
    personality = models.TextField()
    category = models.CharField(max_length=50)
    greeting_message = models.TextField()
    is_public = models.BooleanField(default=True)
    chat_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-created_at']
