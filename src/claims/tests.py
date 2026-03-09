from unittest.mock import patch

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Claim, UserReport


class APISecurityTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="normaluser",
            password="TestPass123!"
        )
        self.admin = User.objects.create_superuser(
            username="adminuser",
            password="AdminPass123!",
            email="admin@example.com"
        )

        self.claim = Claim.objects.create(
            liar_id="test-1",
            label="false",
            statement="Vaccines cause autism.",
            subjects="health",
            speaker="test-speaker",
            speaker_job_title="",
            state="",
            party="",
            barely_true_count=0,
            false_count=1,
            half_true_count=0,
            mostly_true_count=0,
            pants_on_fire_count=1,
            context="test context",
            split="train",
        )

        self.report = UserReport.objects.create(
            statement_text="Vaccines cause autism.",
            speaker="test-speaker",
            report_reason="Misleading health claim",
            risk_score=90,
            risk_level="high",
            status="open",
        )

    def authenticate_user(self, username="normaluser", password="TestPass123!"):
        response = self.client.post(
            "/api/auth/token/",
            {"username": username, "password": password},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # -------------------------
    # Public claims endpoints
    # -------------------------
    def test_claims_list_public(self):
        response = self.client.get("/api/claims/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_claim_detail_public(self):
        response = self.client.get(f"/api/claims/{self.claim.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_claims_by_speaker_public(self):
        response = self.client.get("/api/claims/by-speaker/test-speaker/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # -------------------------
    # Reports permissions / CRUD
    # -------------------------
    def test_reports_list_requires_auth(self):
        response = self.client.get("/api/reports/")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_reports_list_with_auth(self):
        self.authenticate_user()
        response = self.client.get("/api/reports/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_report_create_with_auth(self):
        self.authenticate_user()
        payload = {
            "statement_text": "Earth is flat",
            "speaker": "someone",
            "report_reason": "Scientifically false",
            "risk_score": 95,
            "risk_level": "high",
            "status": "open",
        }
        response = self.client.post("/api/reports/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_report_retrieve_with_auth(self):
        self.authenticate_user()
        response = self.client.get(f"/api/reports/{self.report.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_report_update_blocked_for_non_admin(self):
        self.authenticate_user()
        response = self.client.patch(
            f"/api/reports/{self.report.id}/",
            {"status": "closed"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_report_delete_blocked_for_non_admin(self):
        self.authenticate_user()
        response = self.client.delete(f"/api/reports/{self.report.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_report_update_allowed_for_admin(self):
        self.authenticate_user(username="adminuser", password="AdminPass123!")

        response = self.client.patch(
            f"/api/reports/{self.report.id}/",
            {"status": "resolved"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_report_delete_allowed_for_admin(self):
        self.authenticate_user(username="adminuser", password="AdminPass123!")
        response = self.client.delete(f"/api/reports/{self.report.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    # -------------------------
    # Score endpoint permissions / validation
    # -------------------------
    def test_score_requires_auth(self):
        response = self.client.post("/api/score/", {"text": "vaccines cause autism"}, format="json")
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    @patch("claims.score.search_google_factcheck")
    @patch("claims.score.score_text")
    def test_score_with_auth(self, mock_score_text, mock_search_google_factcheck):
        mock_score_text.return_value = {
            "verdict": "likely_false",
            "credibility_score": 0.10,
            "risk_score": 90,
            "confidence": 0.80,
            "supporting_evidence": [],
            "refuting_evidence": [
                {
                    "id": 1,
                    "url": "/api/claims/1/",
                    "label": "true",
                    "speaker": "tester",
                    "statement": "Vaccines do not cause autism.",
                    "similarity": 0.8,
                    "topic_score": 0.7,
                    "stance_score": 0.8,
                    "oriented_signal": -1.0,
                }
            ],
            "signals": [],
        }
        mock_search_google_factcheck.return_value = {
            "external_credibility_score": 0.20,
            "external_risk_score": 80,
            "external_confidence": 0.70,
            "fact_checks": [
                {
                    "claim_text": "Vaccines cause autism.",
                    "publisher_name": "FactCheck.org",
                    "publisher_site": "factcheck.org",
                    "textual_rating": "False",
                    "review_date": "2025-01-01T00:00:00Z",
                    "url": "https://example.com/factcheck",
                    "credibility_score": 0.2,
                    "relevance": 1.0,
                }
            ],
        }

        self.authenticate_user()
        response = self.client.post("/api/score/", {"text": "vaccines cause autism"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("summary", response.data)
        self.assertIn("local_analysis", response.data)
        self.assertIn("external_analysis", response.data)
        self.assertIn("fusion", response.data)

    def test_score_missing_text(self):
        self.authenticate_user()
        response = self.client.post("/api/score/", {"text": ""}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # -------------------------
    # JWT auth
    # -------------------------
    def test_token_obtain_valid_credentials(self):
        response = self.client.post(
            "/api/auth/token/",
            {"username": "normaluser", "password": "TestPass123!"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_obtain_invalid_credentials(self):
        response = self.client.post(
            "/api/auth/token/",
            {"username": "normaluser", "password": "wrongpass"},
            format="json",
        )
        self.assertIn(response.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])

    def test_claims_filter_by_label(self):
        response = self.client.get("/api/claims/?label=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_claims_search(self):
        response = self.client.get("/api/claims/?search=vaccine")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_claims_ordering(self):
        response = self.client.get("/api/claims/?ordering=speaker")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_claims_pagination(self):
        response = self.client.get("/api/claims/?page=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)

    def test_claims_by_speaker_filtered(self):
        response = self.client.get("/api/claims/by-speaker/test-speaker/?label=false")
        self.assertEqual(response.status_code, status.HTTP_200_OK)