from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

from .models import Organization, FeedbackLink, Customer_feedback

User = get_user_model()


class PublicFeedbackLinkTests(APITestCase):
    def setUp(self):
        self.super = User.objects.create_superuser(username='admin', email='a@a.com', password='pass')
        self.org = Organization.objects.create(name='TestOrg')
        # fresh link with custom rating dimensions
        self.link = FeedbackLink.objects.create(organization=self.org, label='Test Link', created_by=self.super, rating_dimensions=["Customer support","Value for money"])
        self.token = self.link.token

    def test_valid_full_submission_increments_count(self):
        url = f"/api/public/feedback/{self.token}/submit/"
        payload = {
            "csat_score": 4,
            "nps_score": 9,
            "dimension_ratings": {"Customer support": 5, "Value for money": 3},
            "like_most": "Great service",
            "improve": "Faster replies",
            "additional_comments": "OK"
        }
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.link.refresh_from_db()
        self.assertEqual(self.link.submission_count, 1)
        fb = Customer_feedback.objects.filter(organization=self.org).last()
        self.assertIsNotNone(fb)
        self.assertEqual(fb.submitted_via_link.id, self.link.id)
        self.assertEqual(fb.csat_score, 4)
        self.assertEqual(fb.nps_score, 9)

    def test_minimal_submission_csat_nps_only_succeeds(self):
        url = f"/api/public/feedback/{self.token}/submit/"
        payload = {"csat_score": 3, "nps_score": 7}
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

    def test_missing_csat_or_nps_is_rejected(self):
        url = f"/api/public/feedback/{self.token}/submit/"
        resp1 = self.client.post(url, {"nps_score": 5}, format='json')
        resp2 = self.client.post(url, {"csat_score": 2}, format='json')
        self.assertEqual(resp1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp2.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dimension_ratings_with_unknown_key_rejected(self):
        url = f"/api/public/feedback/{self.token}/submit/"
        payload = {"csat_score": 4, "nps_score": 8, "dimension_ratings": {"Unknown": 3}}
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_additional_comments_over_limit_rejected(self):
        url = f"/api/public/feedback/{self.token}/submit/"
        payload = {"csat_score": 4, "nps_score": 8, "additional_comments": "x" * 201}
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reject_organization_field_in_payload(self):
        url = f"/api/public/feedback/{self.token}/submit/"
        payload = {"csat_score": 4, "nps_score": 8, "organization": 999}
        resp = self.client.post(url, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
