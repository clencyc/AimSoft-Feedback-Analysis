from django.shortcuts import render
from .models import Customer_feedback
from rest_framework import viewsets
from .serializers import CustomerSerializer

# Create your views here.
class CustomerFeedbackViewSet(viewsets.ModelViewSet):
    queryset = Customer_feedback.objects.all()
    serializer_class = CustomerSerializer