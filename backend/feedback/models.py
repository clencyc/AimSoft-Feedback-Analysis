from django.db import models
from django.conf import settings
from django.utils import timezone
import secrets


class Organization(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class FeedbackLink(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='feedback_links',
    )
    token = models.CharField(max_length=128, unique=True, db_index=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    max_submissions = models.IntegerField(null=True, blank=True)
    submission_count = models.IntegerField(default=0)
    rating_dimensions = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.token:
            # generate a reasonably long, URL-safe token
            self.token = secrets.token_urlsafe(32)
        # Ensure a default set of dimensions when empty
        if not self.rating_dimensions:
            self.rating_dimensions = ["Customer support", "Value for money", "Response speed"]
        super().save(*args, **kwargs)

    def is_valid(self):
        if not self.is_active:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        if self.max_submissions is not None and self.submission_count >= self.max_submissions:
            return False
        return True

    def __str__(self):
        return f"Link {self.label or self.token} -> {self.organization}"


class FormQuestion(models.Model):
    """Organization-scoped, ordered question that defines the public form schema.

    question_type: one of csat,nps,rating_scale,single_choice,multi_choice,yes_no,short_text,long_text
    options: JSON blob for question-specific options, e.g. {"choices": [...]} or {"max": 5}
    order: integer for display ordering
    """
    QUESTION_TYPES = [
        ("csat", "CSAT"),
        ("nps", "NPS"),
        ("rating_scale", "Rating scale"),
        ("single_choice", "Single choice"),
        ("multi_choice", "Multiple choice"),
        ("yes_no", "Yes / No"),
        ("short_text", "Short text"),
        ("long_text", "Long text"),
    ]

    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name='form_questions'
    )
    label = models.CharField(max_length=255)
    help_text = models.CharField(max_length=512, null=True, blank=True)
    question_type = models.CharField(max_length=32, choices=QUESTION_TYPES)
    options = models.JSONField(default=dict, blank=True)
    required = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "created_at"]

    def __str__(self):
        return f"Q[{self.id}] {self.label} ({self.question_type})"


class Customer_feedback(models.Model):
    form_id = models.AutoField(primary_key=True)

    # New standardized fields for quick filtering/compat
    csat_score = models.PositiveSmallIntegerField(null=True, blank=True)  # 0-4
    nps_score = models.PositiveSmallIntegerField(null=True, blank=True)   # 0-10

    # Full submission stored as JSON keyed by question id: {"<question_id>": {"value": ...}}
    responses = models.JSONField(null=True, blank=True)

    # Legacy convenience fields kept for compatibility with analytics code
    dimension_ratings = models.JSONField(null=True, blank=True)

    like_most = models.TextField(max_length=500, null=True, blank=True)
    improve = models.TextField(max_length=500, null=True, blank=True)
    additional_comments = models.CharField(max_length=200, null=True, blank=True)

    # Legacy numeric fields for compatibility (kept but optional)
    satisfaction_level = models.IntegerField(null=True, blank=True)
    recommend_others = models.IntegerField(null=True, blank=True)

    product_quality = models.IntegerField(null=True, blank=True)
    ease_of_use = models.IntegerField(null=True, blank=True)
    customer_support = models.IntegerField(null=True, blank=True)
    value_for_money = models.IntegerField(null=True, blank=True)
    delivery_speed = models.IntegerField(null=True, blank=True)

    # characters
    product_service = models.CharField(max_length=255, null=True, blank=True)
    product_improvement = models.CharField(max_length=255, null=True, blank=True)

    # New fields
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='feedbacks')
    submitted_via_link = models.ForeignKey(FeedbackLink, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback Form {self.form_id} (org={self.organization})"
