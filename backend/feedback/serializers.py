from rest_framework import serializers
from .models import Customer_feedback, FeedbackLink, Organization


class AdminCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer_feedback
        fields = '__all__'


class PublicCustomerSerializer(serializers.ModelSerializer):
    # Public form must not accept organization or submitted_via_link
    dimension_ratings = serializers.DictField(child=serializers.IntegerField(), required=False, allow_null=True)

    class Meta:
        model = Customer_feedback
        fields = [
            'csat_score',
            'nps_score',
            'dimension_ratings',
            'like_most',
            'improve',
            'additional_comments',
        ]

    def validate(self, data):
        # ensure required fields present
        if 'csat_score' not in data:
            raise serializers.ValidationError({'csat_score': 'csat_score is required'})
        if 'nps_score' not in data:
            raise serializers.ValidationError({'nps_score': 'nps_score is required'})
        # delegate to field validators
        csat = data.get('csat_score')
        nps = data.get('nps_score')
        if csat is None or not (0 <= csat <= 4):
            raise serializers.ValidationError({'csat_score': 'csat_score must be between 0 and 4'})
        if nps is None or not (0 <= nps <= 10):
            raise serializers.ValidationError({'nps_score': 'nps_score must be between 0 and 10'})
        return data

    def validate_dimension_ratings(self, value):
        if value is None:
            return value
        allowed = self.context.get('allowed_dimensions') or []
        # ensure keys are subset of allowed
        for k in value.keys():
            if k not in allowed:
                raise serializers.ValidationError(f'Unknown dimension: {k}')
            v = value[k]
            if not isinstance(v, int) or not (1 <= v <= 5):
                raise serializers.ValidationError(f'Rating for {k} must be integer 1-5')
        return value

    def validate_dimension_ratings(self, value):
        if value is None:
            return value
        allowed = self.context.get('allowed_dimensions') or []
        # ensure keys are subset of allowed
        for k in value.keys():
            if k not in allowed:
                raise serializers.ValidationError(f'Unknown dimension: {k}')
            v = value[k]
            if not isinstance(v, int) or not (1 <= v <= 5):
                raise serializers.ValidationError(f'Rating for {k} must be integer 1-5')
        return value

    def validate_like_most(self, value):
        if value and len(value) > 500:
            raise serializers.ValidationError('like_most must be <= 500 characters')
        return value

    def validate_improve(self, value):
        if value and len(value) > 500:
            raise serializers.ValidationError('improve must be <= 500 characters')
        return value

    def validate_additional_comments(self, value):
        if value and len(value) > 200:
            raise serializers.ValidationError('additional_comments must be <= 200 characters')
        return value


class FeedbackLinkPublicSerializer(serializers.Serializer):
    organization_name = serializers.CharField()
    label = serializers.CharField(allow_null=True, allow_blank=True)
    rating_dimensions = serializers.ListField(child=serializers.CharField(), allow_empty=True)


class FeedbackLinkSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(queryset=Organization.objects.all())
    expires_at = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = FeedbackLink
        fields = ['id', 'organization', 'token', 'label', 'is_active', 'expires_at', 'max_submissions', 'submission_count', 'rating_dimensions', 'created_at']
        read_only_fields = ('id', 'token', 'submission_count', 'created_at')
