from django.urls import path

from . import views
from . import userctrl
from . import userprofile
urlpatterns = [
    path("", views.index, name="index"),
    path("get-post/<str:post_name>", view=views.get_post, name="get_post"),
    path("get-posts", view=views.get_posts, name="get_posts"),
    path("create-post", view=views.create_post, name="create_post"),
    path("login", view=userctrl.verify_password, name="login"),
    path("if_username_exist",view=userctrl.if_username_exist,name="if_username_exist"),
    path("Register",view=userctrl.Register,name="Register"),
    path('get-profile', view=userprofile.get_profile, name='get_profile'),
]