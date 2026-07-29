from django.contrib import admin
from .models import Organization, FeedbackLink, Customer_feedback


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')


@admin.register(FeedbackLink)
class FeedbackLinkAdmin(admin.ModelAdmin):
    list_display = ('id', 'label', 'organization', 'is_active', 'submission_count', 'max_submissions', 'expires_at', 'created_at')
    readonly_fields = ('token', 'submission_count', 'created_at')


@admin.register(Customer_feedback)
class CustomerFeedbackAdmin(admin.ModelAdmin):
    list_display = ('form_id', 'organization', 'satisfaction_level', 'created_at')
