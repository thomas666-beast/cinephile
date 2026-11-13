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

    def test_cancel_own_subscription(self):
        resp = self.client.post(reverse("v1:subscription-create"), {"plan_slug": "monthly"})
        sub_id = resp.data["id"]
        resp = self.client.post(reverse("v1:subscription-cancel", args=[sub_id]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], "canceled")
        # Now /me/ returns 404
        resp = self.client.get(reverse("v1:subscription-me"))
        self.assertEqual(resp.status_code, 404)


    def test_cannot_cancel_someone_elses(self):
        # Create Bob's subscription
        bob = make_user(email="bob2@example.com")
        bob_plan = make_plan(name="Bob's Plan")
        bob_sub = make_subscription(user=bob, plan=bob_plan)

        # As self.user (from setUp), try to cancel Bob's
        resp = self.client.post(reverse("v1:subscription-cancel", args=[bob_sub.id]))
        self.assertEqual(resp.status_code, 404)

        # Bob's subscription is untouched
        bob_sub.refresh_from_db()
        self.assertEqual(bob_sub.status, "active")


    def test_cancel_already_canceled_409(self):
        resp = self.client.post(reverse("v1:subscription-create"), {"plan_slug": "monthly"})
        sub_id = resp.data["id"]
        self.client.post(reverse("v1:subscription-cancel", args=[sub_id]))
        resp = self.client.post(reverse("v1:subscription-cancel", args=[sub_id]))
        self.assertEqual(resp.status_code, 409)
