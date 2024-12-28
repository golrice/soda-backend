from django.urls import path
from . import views

urlpatterns = [
    path('', view=views.index, name='index'),
    path('history/', view=views.history, name='history'),
    path('<str:room_name>/', view=views.room, name='room'),
]