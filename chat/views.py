import json
from django.http import JsonResponse
from django.db.models import Q

from chat.models import Message
from application.models import User

def index(request):
    return JsonResponse({ "message": "Welcome to the chat API" })

def history(request):
    chatroom = request.GET.get('chatroom')
    username1, username2 = chatroom.split('-')
    user1 = User.objects.get(username=username1)
    user2 = User.objects.get(username=username2)

    messages = Message.objects.filter(
        Q(sender=user1, receiver=user2) | Q(sender=user2, receiver=user1)
    ).order_by('timestamp').values('sender__username','receiver__username', 'content', 'timestamp')

    messages_json = []
    for message in messages:
        message['timestamp'] = message['timestamp'].isoformat()
        messages_json.append({"sender": message['sender__username'], "text": message['content'], "timestamp": message['timestamp']})

    return JsonResponse({ "data": messages_json }, safe=False)

def room(request):
    pass