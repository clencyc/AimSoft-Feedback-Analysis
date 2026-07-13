from rest_framework import serializers
from .models import Customer_feedback

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer_feedback
        fields = '__all__'