from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from .serializers import SentimentRequestSerializer
from .services import analyze_sentiment


class SentimentAnalysisView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = SentimentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        text = serializer.validated_data["text"]
        result = analyze_sentiment(text)
        return Response(result, status=status.HTTP_200_OK)
