from rest_framework import serializers


class SentimentRequestSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=5000)
