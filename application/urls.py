from django.urls import path

from . import views
from . import userctrl
from . import userprofile
from . import view_post

urlpatterns = [
    path("", views.index, name="index"),
    path("get-post/<str:post_name>", view=view_post.get_post, name="get_post"),
    path("get-posts", view=view_post.get_posts, name="get_posts"),
    path("get-posts/<str:username>", view=view_post.get_posts_by_username, name="get_posts_by_username"),
    path("create-post", view=view_post.create_post, name="create_post"),
    path("login", view=userctrl.verify_password, name="login"),
    path("delete-post/<str:post_name>", view=view_post.delete_post, name="delete_post"),
    path("pal", view=view_post.pal_query, name="pal_query"),
    path("if_username_exist",view=userctrl.if_username_exist,name="if_username_exist"),
    path("Register",view=userctrl.Register,name="Register"),
    path('get-profile', view=userprofile.get_profile, name='get_profile'),
    path('update-profile', view=userprofile.update_profile, name='update_profile'),
]