from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from api.tests.factories import make_user

User = get_user_model()


class RegisterTests(APITestCase):
    def test_register_success(self):
        resp = self.client.post(reverse("v1:auth-register"), {
            "email": "new@example.com",
            "password": "VeryStrongPass123!",
            "password_confirm": "VeryStrongPass123!",
            "first_name": "New",
        })
        self.assertEqual(resp.status_code, 201)
        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.role, User.Role.VIEWER)

    def test_register_cannot_set_role(self):
        resp = self.client.post(reverse("v1:auth-register"), {
            "email": "sneaky@example.com",
            "password": "VeryStrongPass123!",
            "password_confirm": "VeryStrongPass123!",
            "role": "admin",
        })
        self.assertEqual(resp.status_code, 201)
        user = User.objects.get(email="sneaky@example.com")
        self.assertEqual(user.role, User.Role.VIEWER)  # forced viewer

    def test_password_mismatch_rejected(self):
        resp = self.client.post(reverse("v1:auth-register"), {
            "email": "x@example.com",
            "password": "VeryStrongPass123!",
            "password_confirm": "DifferentPass123!",
        })
        self.assertEqual(resp.status_code, 400)

    def test_weak_password_rejected(self):
        resp = self.client.post(reverse("v1:auth-register"), {
            "email": "x@example.com",
            "password": "123",
            "password_confirm": "123",
        })
        self.assertEqual(resp.status_code, 400)


class TokenTests(APITestCase):
    def setUp(self):
        self.user = make_user(email="a@example.com", password="TestPass123!")

    def test_login_success(self):
        resp = self.client.post(reverse("v1:auth-token"), {
            "email": "a@example.com", "password": "TestPass123!",
        })
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)
        self.assertIn("refresh", resp.data)

    def test_login_wrong_password(self):
        resp = self.client.post(reverse("v1:auth-token"), {
            "email": "a@example.com", "password": "wrong",
        })
        self.assertEqual(resp.status_code, 401)

    def test_logout_blacklists_refresh(self):
        tokens = self.client.post(reverse("v1:auth-token"), {
            "email": "a@example.com", "password": "TestPass123!",
        }).data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        resp = self.client.post(reverse("v1:auth-logout"), {"refresh": tokens["refresh"]})
        self.assertEqual(resp.status_code, 205)

        # Try to refresh — should fail
        resp = self.client.post(reverse("v1:auth-token-refresh"), {"refresh": tokens["refresh"]})
        self.assertEqual(resp.status_code, 401)


class MeTests(APITestCase):
    def setUp(self):
        self.user = make_user(email="me@example.com", password="TestPass123!")
        tokens = self.client.post(reverse("v1:auth-token"), {
            "email": "me@example.com", "password": "TestPass123!",
        }).data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    def test_get_me(self):
        resp = self.client.get(reverse("v1:auth-me"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["email"], "me@example.com")

    def test_patch_ignores_role(self):
        resp = self.client.patch(reverse("v1:auth-me"), {"role": "admin"})
        self.assertEqual(resp.status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, "viewer")
