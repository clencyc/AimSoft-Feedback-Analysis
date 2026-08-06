from django.urls import path

from .views import SentimentAnalysisView

urlpatterns = [
    path("analyze/", SentimentAnalysisView.as_view(), name="sentiment-analyze"),
]
