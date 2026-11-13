import re

from django.core import mail
from django.urls import reverse
from rest_framework.test import APITestCase

from accounts.models import User
from api.tests.factories import make_user


class PasswordResetFlowTests(APITestCase):
    def setUp(self):
        self.user = make_user(email="reset@example.com", password="OldPass123!")
        mail.outbox.clear()

    def _get_token_from_email(self) -> tuple[str, str]:
        """
        Parse uid and token from the email that was actually sent.
        This is the correct pattern: test what the system actually produces.
        """
        self.assertEqual(len(mail.outbox), 1)
        body = mail.outbox[0].body

        # Extract from URL like: .../reset-password?uid=2&token=abc123
        m = re.search(r"reset-password\?uid=(\d+)&token=([a-z0-9]+)", body)
        self.assertIsNotNone(m, f"Could not find uid & token in email body:\n{body}")
        return m.group(1), m.group(2)

    def test_request_sends_email(self):
        resp = self.client.post(
            reverse("v1:password-reset-request"), {"email": "reset@example.com"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("reset@example.com", mail.outbox[0].to)
        self.assertIn("reset-password", mail.outbox[0].body)

    def test_request_unknown_email_still_200(self):
        resp = self.client.post(
            reverse("v1:password-reset-request"), {"email": "noone@example.com"}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_full_reset_flow(self):
        # 1. Request the reset email
        self.client.post(
            reverse("v1:password-reset-request"), {"email": "reset@example.com"}
        )

        # 2. Extract uid + token from the email body itself
        uid, token = self._get_token_from_email()

        # 3. Confirm the reset
        resp = self.client.post(
            reverse("v1:password-reset-confirm"),
            {
                "uid": uid,
                "token": token,
                "new_password": "NewStrongPass456!",
                "confirm_password": "NewStrongPass456!",
            },
        )
        self.assertEqual(resp.status_code, 200, resp.json())

        # 4. Old password fails
        resp = self.client.post(reverse("v1:auth-token"), {
            "email": "reset@example.com", "password": "OldPass123!",
        })
        self.assertEqual(resp.status_code, 401)

        # 5. New password works
        resp = self.client.post(reverse("v1:auth-token"), {
            "email": "reset@example.com", "password": "NewStrongPass456!",
        })
        self.assertEqual(resp.status_code, 200)

    def test_wrong_token_rejected(self):
        self.client.post(
            reverse("v1:password-reset-request"), {"email": "reset@example.com"}
        )
        uid, _ = self._get_token_from_email()

        resp = self.client.post(reverse("v1:password-reset-confirm"), {
            "uid": uid,
            "token": "garbage-not-a-real-token",
            "new_password": "NewStrongPass456!",
            "confirm_password": "NewStrongPass456!",
        })
        self.assertEqual(resp.status_code, 400)

    def test_wrong_uid_rejected(self):
        self.client.post(
            reverse("v1:password-reset-request"), {"email": "reset@example.com"}
        )
        _, token = self._get_token_from_email()

        resp = self.client.post(reverse("v1:password-reset-confirm"), {
            "uid": "9999999",
            "token": token,
            "new_password": "NewStrongPass456!",
            "confirm_password": "NewStrongPass456!",
        })
        self.assertEqual(resp.status_code, 400)

    def test_mismatched_passwords_rejected(self):
        self.client.post(
            reverse("v1:password-reset-request"), {"email": "reset@example.com"}
        )
        uid, token = self._get_token_from_email()

        resp = self.client.post(reverse("v1:password-reset-confirm"), {
            "uid": uid,
            "token": token,
            "new_password": "NewStrongPass456!",
            "confirm_password": "DifferentPass789!",
        })
        self.assertEqual(resp.status_code, 400)

    def test_weak_password_rejected(self):
        self.client.post(
            reverse("v1:password-reset-request"), {"email": "reset@example.com"}
        )
        uid, token = self._get_token_from_email()

        resp = self.client.post(reverse("v1:password-reset-confirm"), {
            "uid": uid,
            "token": token,
            "new_password": "123",
            "confirm_password": "123",
        })
        self.assertEqual(resp.status_code, 400)

    def test_token_cannot_be_reused(self):
        self.client.post(
            reverse("v1:password-reset-request"), {"email": "reset@example.com"}
        )
        uid, token = self._get_token_from_email()

        # First use — success
        resp = self.client.post(reverse("v1:password-reset-confirm"), {
            "uid": uid,
            "token": token,
            "new_password": "NewStrongPass456!",
            "confirm_password": "NewStrongPass456!",
        })
        self.assertEqual(resp.status_code, 200, resp.json())

        # Second use — same token, must fail
        resp = self.client.post(reverse("v1:password-reset-confirm"), {
            "uid": uid,
            "token": token,
            "new_password": "AnotherPass789!",
            "confirm_password": "AnotherPass789!",
        })
        self.assertEqual(resp.status_code, 400)

    def test_missing_fields_rejected(self):
        resp = self.client.post(reverse("v1:password-reset-confirm"), {
            "uid": "", "token": "", "new_password": "",
        })
        self.assertEqual(resp.status_code, 400)
