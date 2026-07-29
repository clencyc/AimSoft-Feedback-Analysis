from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import Customer_feedback, FeedbackLink, Organization
from .serializers import AdminCustomerSerializer, PublicCustomerSerializer, FeedbackLinkPublicSerializer, FeedbackLinkSerializer
from .permissions import IsSuperAdmin


# Legacy/administrative feedback creation (keeps previous behavior for internal forms)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def feedback_create(request):
    serializer = AdminCustomerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


# Admin endpoints for managing feedback links
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated, IsSuperAdmin])
def admin_organization_feedback_links(request, org_id):
    org = get_object_or_404(Organization, id=org_id)
    if request.method == 'GET':
        links = org.feedback_links.all().order_by('-created_at')
        serializer = FeedbackLinkSerializer(links, many=True)
        return Response(serializer.data)

    # POST -> create
    data = request.data.copy()
    data['organization'] = org.id

    # normalize short date-only strings (YYYY-MM-DD) to end-of-day UTC datetimes
    expires = data.get('expires_at')
    if isinstance(expires, str) and len(expires) == 10 and expires.count('-') == 2:
        # append time portion so DRF DateTimeField can parse it unambiguously
        data['expires_at'] = f"{expires}T23:59:59Z"

    serializer = FeedbackLinkSerializer(data=data)
    if serializer.is_valid():
        link = serializer.save(created_by=request.user)
        return Response(FeedbackLinkSerializer(link).data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsSuperAdmin])
def admin_revoke_feedback_link(request, link_id):
    link = get_object_or_404(FeedbackLink, id=link_id)
    link.is_active = False
    link.save()
    return Response({'detail': 'Link revoked'}, status=200)


# Public endpoints (no auth)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@throttle_classes([AnonRateThrottle])
def public_validate_token(request, token):
    link = get_object_or_404(FeedbackLink, token=token)
    if not link.is_valid():
        return Response({'detail': 'Link is invalid or expired'}, status=status.HTTP_410_GONE)
    data = {
        'organization_name': link.organization.name,
        'label': link.label,
        'rating_dimensions': link.rating_dimensions or [],
    }
    return Response(data)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@throttle_classes([AnonRateThrottle])
def public_submit_feedback(request, token):
    link = get_object_or_404(FeedbackLink, token=token)
    if not link.is_valid():
        return Response({'detail': 'Link is invalid or expired'}, status=status.HTTP_410_GONE)

    # Security rule: do not accept organization in payload. Reject if present.
    if 'organization' in request.data or 'organization_id' in request.data:
        return Response({'detail': 'organization field is not allowed'}, status=status.HTTP_400_BAD_REQUEST)

    # Pass allowed dimensions to serializer for validation
    allowed = link.rating_dimensions or []
    serializer = PublicCustomerSerializer(data=request.data, context={'allowed_dimensions': allowed})
    if serializer.is_valid():
        # create the feedback with organization derived from the link
        feedback = Customer_feedback.objects.create(**serializer.validated_data, organization=link.organization, submitted_via_link=link)
        # increment count
        link.submission_count = (link.submission_count or 0) + 1
        link.save()
        return Response({'detail': 'Feedback submitted'}, status=201)
    return Response(serializer.errors, status=400)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsSuperAdmin])
def admin_list_organizations(request):
    orgs = Organization.objects.all().order_by('name')
    data = [{'id': o.id, 'name': o.name} for o in orgs]
    return Response(data)
