from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("get-post/<str:post_name>", view=views.get_post, name="get_post"),
    path("get-posts", view=views.get_posts, name="get_posts"),
    path("create-post", view=views.create_post, name="create_post"),
]