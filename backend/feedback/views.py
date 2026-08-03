from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from .models import Customer_feedback, FeedbackLink, Organization, FormQuestion
from .serializers import AdminCustomerSerializer, PublicCustomerSerializer, FeedbackLinkPublicSerializer, FeedbackLinkSerializer, FormQuestionSerializer
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

    # Attach form schema for this organization so clients render dynamically
    form_questions = list(link.organization.form_questions.all().order_by('order'))
    # use serializer if available
    try:
        serializer = FormQuestionSerializer(form_questions, many=True)
        form_schema = serializer.data
    except Exception:
        # fallback to simple reconstruction
        form_schema = [
            {
                'id': q.id,
                'label': q.label,
                'question_type': q.question_type,
                'options': q.options,
                'required': q.required,
                'order': q.order,
            }
            for q in form_questions
        ]

    data = {
        'organization_name': link.organization.name,
        'label': link.label,
        'rating_dimensions': link.rating_dimensions or [],
        'form_schema': form_schema,
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
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    validated = serializer.validated_data
    answers = validated.get('answers')

    # If answers provided, validate against form schema
    csat = None
    nps = None
    responses = None
    if answers:
        # answers expected as mapping question_id -> value
        questions = {str(q.id): q for q in link.organization.form_questions.all()}
        errors = {}
        responses = {}
        for qid, q in questions.items():
            present = qid in answers or int(qid) in answers
            val = answers.get(qid, answers.get(int(qid))) if present else None
            if q.required and not present:
                errors[qid] = 'This question is required'
                continue
            if not present:
                continue
            # basic per-type validation
            try:
                if q.question_type == 'csat':
                    v = int(val)
                    if not (0 <= v <= 4):
                        raise ValueError
                    csat = v
                    responses[qid] = {'value': v}
                elif q.question_type == 'nps':
                    v = int(val)
                    if not (0 <= v <= 10):
                        raise ValueError
                    nps = v
                    responses[qid] = {'value': v}
                elif q.question_type == 'rating_scale':
                    maxv = int(q.options.get('max', 5))
                    v = int(val)
                    if not (1 <= v <= maxv):
                        raise ValueError
                    responses[qid] = {'value': v}
                elif q.question_type == 'single_choice':
                    choices = q.options.get('choices', []) or []
                    if val not in choices:
                        raise ValueError
                    responses[qid] = {'value': val}
                elif q.question_type == 'multi_choice':
                    choices = q.options.get('choices', []) or []
                    if not isinstance(val, (list, tuple)):
                        raise ValueError
                    for item in val:
                        if item not in choices:
                            raise ValueError
                    responses[qid] = {'value': list(val)}
                elif q.question_type == 'yes_no':
                    if isinstance(val, bool):
                        v = val
                    elif isinstance(val, str) and val.lower() in ('yes', 'no', 'true', 'false'):
                        v = val.lower() in ('yes', 'true')
                    else:
                        raise ValueError
                    responses[qid] = {'value': v}
                elif q.question_type in ('short_text', 'long_text'):
                    if not isinstance(val, str):
                        raise ValueError
                    # basic length guard
                    maxlen = 500 if q.question_type == 'long_text' else 200
                    if len(val) > maxlen:
                        raise ValueError
                    responses[qid] = {'value': val}
                else:
                    responses[qid] = {'value': val}
            except Exception:
                errors[qid] = f'Invalid answer for question type {q.question_type}'
        if errors:
            return Response({'detail': 'Invalid answers', 'errors': errors}, status=400)

    # Build feedback record using csat/nps when available and storing full responses
    feedback_kwargs = {}
    if csat is not None:
        feedback_kwargs['csat_score'] = csat
    if nps is not None:
        feedback_kwargs['nps_score'] = nps
    if responses is not None:
        feedback_kwargs['responses'] = responses

    # Merge legacy direct fields if present (serializer already validated them)
    for k in ('like_most', 'improve', 'additional_comments', 'dimension_ratings'):
        if k in validated:
            feedback_kwargs[k] = validated[k]

    feedback = Customer_feedback.objects.create(**feedback_kwargs, organization=link.organization, submitted_via_link=link)
    # increment count
    link.submission_count = (link.submission_count or 0) + 1
    link.save()
    return Response({'detail': 'Feedback submitted'}, status=201)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, IsSuperAdmin])
def admin_list_organizations(request):
    orgs = Organization.objects.all().order_by('name')
    data = [{'id': o.id, 'name': o.name} for o in orgs]
    return Response(data)


# Admin form-builder endpoints
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated, IsSuperAdmin])
def admin_list_create_form_questions(request, org_id):
    org = get_object_or_404(Organization, id=org_id)
    if request.method == 'GET':
        qs = org.form_questions.all().order_by('order')
        serializer = FormQuestionSerializer(qs, many=True)
        return Response(serializer.data)

    # POST -> create
    data = request.data.copy()
    data['organization'] = org.id
    # Normalize options None -> {} so DB NOT NULL constraints are satisfied
    if 'options' in data and data.get('options') is None:
        data['options'] = {}
    serializer = FormQuestionSerializer(data=data)
    if serializer.is_valid():
        q = serializer.save()
        return Response(FormQuestionSerializer(q).data, status=201)
    # Debug info for failing POSTs
    try:
        print("[DEBUG] admin_list_create_form_questions payload:", data)
        print("[DEBUG] serializer errors:", serializer.errors)
    except Exception:
        pass
    return Response(serializer.errors, status=400)


@api_view(['PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated, IsSuperAdmin])
def admin_update_delete_form_question(request, question_id):
    q = get_object_or_404(FormQuestion, id=question_id)
    if request.method == 'DELETE':
        q.delete()
        return Response({'detail': 'Deleted'}, status=200)
    # PUT -> update
    data = request.data.copy()
    # do not allow changing organization via this endpoint
    data.pop('organization', None)
    # Normalize options None -> {} to avoid DB constraint errors
    if 'options' in data and data.get('options') is None:
        data['options'] = {}
    serializer = FormQuestionSerializer(q, data=data, partial=True)
    if serializer.is_valid():
        q = serializer.save()
        return Response(FormQuestionSerializer(q).data)
    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsSuperAdmin])
def admin_reorder_form_questions(request, org_id):
    """Accepts JSON {"order": [id1, id2, ...]} to set display order."""
    org = get_object_or_404(Organization, id=org_id)
    order = request.data.get('order')
    if not isinstance(order, list):
        return Response({'detail': 'order must be a list of question IDs'}, status=400)
    # Fetch only those questions belonging to org
    qs = {q.id: q for q in org.form_questions.all()}
    for idx, qid in enumerate(order):
        try:
            qid_int = int(qid)
        except Exception:
            continue
        q = qs.get(qid_int)
        if q:
            q.order = idx
            q.save()
    return Response({'detail': 'Reordered'})
