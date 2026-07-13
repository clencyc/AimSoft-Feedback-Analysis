from django.urls import path, include
from .views import login, logout, create_user

urlpatterns = [
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("create/", create_user, name="create_user"),
    
]