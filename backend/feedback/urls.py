from django.urls import path
from . import views

urlpatterns = [
    # legacy/admin internal create (auth required)
    path('', views.feedback_create, name='feedback-create'),

    # Admin-only link management
    path('admin/organizations/', views.admin_list_organizations, name='admin-list-organizations'),
    path('admin/organizations/<int:org_id>/feedback-links/', views.admin_organization_feedback_links, name='admin-org-feedback-links'),
    path('admin/feedback-links/<int:link_id>/revoke/', views.admin_revoke_feedback_link, name='admin-revoke-feedback-link'),

    # Public endpoints
    path('public/feedback/<str:token>/', views.public_validate_token, name='public-validate-token'),
    path('public/feedback/<str:token>/submit/', views.public_submit_feedback, name='public-submit-feedback'),

    # Admin form-builder endpoints
    path('admin/organizations/<int:org_id>/form-questions/', views.admin_list_create_form_questions, name='admin-org-form-questions'),
    path('admin/organizations/<int:org_id>/form-questions/reorder/', views.admin_reorder_form_questions, name='admin-org-form-questions-reorder'),
    path('admin/form-questions/<int:question_id>/', views.admin_update_delete_form_question, name='admin-form-question-detail'),
    # Manager dashboard summary endpoint
    path('admin/organizations/<int:org_id>/summary/', views.admin_organization_summary, name='admin-organization-summary'),
]

