from django.shortcuts import render
from .models import Customer_feedback
from rest_framework import viewsets, permissions
from .serializers import CustomerSerializer
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def feedback_create(request):
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)