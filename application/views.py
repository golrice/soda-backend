import json
from django.http import HttpResponse, JsonResponse
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from application.models import User

# 祖宗之法不可变
# Create your views here.
def index(request):
    return HttpResponse("Hello, world.")

