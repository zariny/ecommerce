from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class TestUserRegistrationView(APITestCase):
    def setUp(self):
        self.auth_cookies = ["access_token", "refresh_token", "expiry_date"]
        self.registration_url = "/api/register/"

    def test_successful_registration_returns_cookies(self):
        new_user_email = "newuser@email.com"
        response = self.client.post(
            self.registration_url,
            {
                "email": new_user_email,
                "password": "strong-password",
                "password_again": "strong-password"
            }
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["email"], new_user_email)
        self.assertTrue(User.objects.filter(email=new_user_email).exists())

        for cookie in self.auth_cookies:
            self.assertIn(cookie, response.cookies, "%s not set during registration." % cookie)

    def test_invalid_registration_does_not_set_cookies(self):
        new_user_email = "newuser@email.com"
        response = self.client.post(
            self.registration_url,
            {
                "email": new_user_email,
                "password": "string-password",
                "password_again": "wrong-password"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(email=new_user_email).exists())

        for cookie in self.auth_cookies:
            self.assertNotIn(cookie, response.cookies, "%s not set during registration." % cookie)
