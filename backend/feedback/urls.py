from django.urls import path
from . import views

urlpatterns = [
    path('', views.feedback_create, name='feedback-create'),   # Simple function view
]