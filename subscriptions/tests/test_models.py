from django.db import IntegrityError
from django.test import TestCase
from datetime import timedelta

from django.utils import timezone
from api.tests.factories import make_user, make_plan, make_subscription
from subscriptions.models import Subscription


class SubscriptionIsActiveTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.plan = make_plan()

    def test_active_and_not_expired(self):
        s = make_subscription(user=self.user, plan=self.plan)
        self.assertTrue(s.is_active)

    def test_active_but_expired(self):
        s = make_subscription(user=self.user, plan=self.plan, expired=True)
        self.assertFalse(s.is_active)

    def test_one_active_per_user(self):
        make_subscription(user=self.user, plan=self.plan)
        with self.assertRaises(IntegrityError):
            make_subscription(user=self.user, plan=self.plan)
