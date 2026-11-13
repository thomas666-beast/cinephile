from django.urls import reverse
from rest_framework.test import APITestCase
from django.utils import timezone
from datetime import timedelta

from api.tests.factories import make_user, make_plan, make_subscription


class SubscriptionAPITests(APITestCase):
    def setUp(self):
        self.user = make_user(email="sub@example.com", password="TestPass123!")
        self.plan = make_plan(name="Monthly", duration_days=30)
        tokens = self.client.post(reverse("v1:auth-token"), {
            "email": "sub@example.com", "password": "TestPass123!",
        }).data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    def test_plan_list_public(self):
        self.client.credentials()  # unset auth
        resp = self.client.get(reverse("v1:plan-list"))
        self.assertEqual(resp.status_code, 200)

    def test_subscribe_success(self):
        resp = self.client.post(reverse("v1:subscription-create"), {"plan_slug": "monthly"})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["status"], "active")

    def test_double_subscribe_409(self):
        self.client.post(reverse("v1:subscription-create"), {"plan_slug": "monthly"})
        resp = self.client.post(reverse("v1:subscription-create"), {"plan_slug": "monthly"})
        self.assertEqual(resp.status_code, 409)

    def test_me_404_when_none(self):
        resp = self.client.get(reverse("v1:subscription-me"))
        self.assertEqual(resp.status_code, 404)

    def test_me_returns_active(self):
        self.client.post(reverse("v1:subscription-create"), {"plan_slug": "monthly"})
        resp = self.client.get(reverse("v1:subscription-me"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "active")

    def test_lazy_expiry(self):
        # Create an active-but-expired subscription directly
        make_subscription(user=self.user, plan=self.plan, expired=True)
        resp = self.client.get(reverse("v1:subscription-me"))
        self.assertEqual(resp.status_code, 404)
        # The subscription should now be marked EXPIRED in the DB
        from subscriptions.models import Subscription
        sub = Subscription.objects.get(user=self.user)
        self.assertEqual(sub.status, Subscription.Status.EXPIRED)
