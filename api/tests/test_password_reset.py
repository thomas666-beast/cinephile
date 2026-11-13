import re

from django.core import mail
from django.urls import reverse
from rest_framework.test import APITestCase

from api.tests.factories import make_user


class PasswordResetFlowTests(APITestCase):
    def setUp(self):
        self.user = make_user(email="reset@example.com", password="OldPass123!")

    def test_request_sends_email(self):
        resp = self.client.post(reverse("v1:password-reset-request"), {"email": "reset@example.com"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("reset@example.com", mail.outbox[0].to)
        self.assertIn("reset-password", mail.outbox[0].body)

    def test_request_unknown_email_still_200(self):
        resp = self.client.post(reverse("v1:password-reset-request"), {"email": "noone@example.com"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_full_reset_flow(self):
        self.client.post(reverse("v1:password-reset-request"), {"email": "reset@example.com"})
        body = mail.outbox[0].body
        # Extract uid & token from the link
        m = re.search(r"reset-password\?uid=([^&\s]+)&token=([^\s]+)", body)
        self.assertIsNotNone(m)
        uid, token = m.group(1), m.group(2)

        resp = self.client.post(reverse("v1:password-reset-confirm"), {
            "uid": uid,
            "token": token,
            "new_password": "NewStrongPass456!",
            "confirm_password": "NewStrongPass456!",
        })
        self.assertEqual(resp.status_code, 200)

        # Old password fails
        resp = self.client.post(reverse("v1:auth-token"), {
            "email": "reset@example.com", "password": "OldPass123!",
        })
        self.assertEqual(resp.status_code, 401)

        # New password works
        resp = self.client.post(reverse("v1:auth-token"), {
            "email": "reset@example.com", "password": "NewStrongPass456!",
        })
        self.assertEqual(resp.status_code, 200)

    def test_wrong_token_rejected(self):
        self.client.post(reverse("v1:password-reset-request"), {"email": "reset@example.com"})
        resp = self.client.post(reverse("v1:password-reset-confirm"), {
            "uid": "X",
            "token": "garbage",
            "new_password": "NewStrongPass456!",
            "confirm_password": "NewStrongPass456!",
        })
        self.assertEqual(resp.status_code, 400)
