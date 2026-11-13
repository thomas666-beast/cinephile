from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APITestCase

from api.tests.factories import make_user


class PasswordResetFlowTests(APITestCase):
    def setUp(self):
        self.user = make_user(email="reset@example.com", password="OldPass123!")
        mail.outbox.clear()

    def _uid_token(self):
        """Generate a fresh uid/token pair the same way the view does."""
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        return uid, token

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
        # Request the email (fires the signal, exercises the endpoint)
        self.client.post(
            reverse("v1:password-reset-request"), {"email": "reset@example.com"}
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("reset-password", mail.outbox[0].body)

        # Generate the same kind of uid/token the email would contain
        uid, token = self._uid_token()

        resp = self.client.post(reverse("v1:password-reset-confirm"), {
            "uid": uid,
            "token": token,
            "new_password": "NewStrongPass456!",
            "confirm_password": "NewStrongPass456!",
        })
        self.assertEqual(resp.status_code, 200, resp.json())

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
        uid, _ = self._uid_token()
        resp = self.client.post(reverse("v1:password-reset-confirm"), {
            "uid": uid,
            "token": "garbage",
            "new_password": "NewStrongPass456!",
            "confirm_password": "NewStrongPass456!",
        })
        self.assertEqual(resp.status_code, 400)

    def test_mismatched_passwords_rejected(self):
        uid, token = self._uid_token()
        resp = self.client.post(reverse("v1:password-reset-confirm"), {
            "uid": uid,
            "token": token,
            "new_password": "NewStrongPass456!",
            "confirm_password": "DifferentPass789!",
        })
        self.assertEqual(resp.status_code, 400)
