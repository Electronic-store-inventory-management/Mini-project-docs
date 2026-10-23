from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class AuthenticationTests(TestCase):
    """
    Automated test suite verifying acceptance criteria for US-01:
    1. Unauthenticated users cannot access protected pages and are redirected to login.
    2. Successful login with valid credentials creates session and redirects to intended page.
    3. Failed login with invalid credentials shows safe error message and denies access.
    4. Authenticated users can access protected inventory landing page.
    5. Logout terminates session and revokes access to protected pages.
    6. CSRF verification is enforced on authentication forms.
    7. Passwords are encrypted using Django password hashing.
    8. User roles (Admin, Manager, Staff) are modeled and verified.
    9. Rate limiting blocks repeated failed logins per SAD Section 3.9 & SRS AC-SR-006.
    """

    @classmethod
    def setUpTestData(cls):
        cls.password = 'SecurePass123!'
        cls.staff_user = User.objects.create_user(
            username='staff_john',
            password=cls.password,
            email='john@example.com',
            role=User.Role.STAFF
        )
        cls.manager_user = User.objects.create_user(
            username='manager_mary',
            password=cls.password,
            email='mary@example.com',
            role=User.Role.MANAGER
        )
        cls.admin_user = User.objects.create_user(
            username='admin_boss',
            password=cls.password,
            email='boss@example.com',
            role=User.Role.ADMIN
        )

    def setUp(self):
        cache.clear()
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.landing_url = reverse('inventory:landing')

    def tearDown(self):
        cache.clear()

    # 1. Accessing a protected page while logged out
    def test_unauthenticated_access_to_landing_page_redirects_to_login(self):
        response = self.client.get(self.landing_url)
        self.assertEqual(response.status_code, 302)
        expected_redirect = f"{self.login_url}?next={self.landing_url}"
        self.assertRedirects(response, expected_redirect)

    def test_unauthenticated_access_to_root_redirects_to_login(self):
        response = self.client.get('/', follow=False)
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')

    # 2. Successful login with valid credentials
    def test_successful_login_redirects_to_landing_page(self):
        response = self.client.post(self.login_url, {
            'username': 'staff_john',
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.landing_url)
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.staff_user.pk)

    # 3. Successful login with 'next' redirect parameter
    def test_successful_login_honors_next_parameter(self):
        target_url = f"{self.landing_url}?tab=recent"
        response = self.client.post(f"{self.login_url}?next={target_url}", {
            'username': 'staff_john',
            'password': self.password,
            'next': target_url,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, target_url)

    # 4. Failed login with invalid credentials
    def test_failed_login_with_incorrect_password(self):
        response = self.client.post(self.login_url, {
            'username': 'staff_john',
            'password': 'WrongPassword999',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertContains(response, "Invalid username or password")

    def test_failed_login_with_nonexistent_user(self):
        response = self.client.post(self.login_url, {
            'username': 'nonexistent_user',
            'password': 'SomePassword123!',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertContains(response, "Invalid username or password")

    # 5. Access to the protected landing page after authentication
    def test_authenticated_user_can_access_landing_page(self):
        self.client.force_login(self.staff_user)
        response = self.client.get(self.landing_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inventory/landing.html')
        self.assertContains(response, 'staff_john')
        self.assertContains(response, 'Staff')

    # 6. Logout and subsequent denial of protected-page access
    def test_logout_terminates_session_and_denies_landing_access(self):
        self.client.force_login(self.staff_user)
        landing_response = self.client.get(self.landing_url)
        self.assertEqual(landing_response.status_code, 200)

        # Perform POST logout
        logout_response = self.client.post(self.logout_url)
        self.assertEqual(logout_response.status_code, 302)
        self.assertRedirects(logout_response, self.login_url)

        # Verify session is cleared
        self.assertNotIn('_auth_user_id', self.client.session)

        # Subsequent request to protected landing page must redirect to login
        subsequent_response = self.client.get(self.landing_url)
        self.assertEqual(subsequent_response.status_code, 302)
        self.assertRedirects(subsequent_response, f"{self.login_url}?next={self.landing_url}")

    # 7. CSRF handling
    def test_login_post_requires_csrf_token(self):
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(self.login_url, {
            'username': 'staff_john',
            'password': self.password,
        })
        self.assertEqual(response.status_code, 403)

    # 8. Password hashing security
    def test_password_is_hashed_and_not_stored_plaintext(self):
        user = User.objects.get(username='staff_john')
        self.assertNotEqual(user.password, self.password)
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
        self.assertTrue(user.check_password(self.password))
        self.assertFalse(user.check_password('WrongPassword'))

    # 9. Role-Based Authorization Foundation
    def test_user_roles_and_helper_methods(self):
        self.assertEqual(self.staff_user.role, User.Role.STAFF)
        self.assertTrue(self.staff_user.is_staff_role)
        self.assertFalse(self.staff_user.is_admin_role)
        self.assertFalse(self.staff_user.is_manager_role)

        self.assertEqual(self.manager_user.role, User.Role.MANAGER)
        self.assertTrue(self.manager_user.is_manager_role)
        self.assertFalse(self.manager_user.is_admin_role)
        self.assertFalse(self.manager_user.is_staff_role)

        self.assertEqual(self.admin_user.role, User.Role.ADMIN)
        self.assertTrue(self.admin_user.is_admin_role)
        self.assertFalse(self.admin_user.is_manager_role)
        self.assertFalse(self.admin_user.is_staff_role)

    # 10. Login Rate Limiting (SAD Section 3.9 & SRS AC-SR-006)
    def test_login_rate_limiting_blocks_after_5_failed_attempts(self):
        # 5 failed attempts
        for i in range(5):
            res = self.client.post(self.login_url, {
                'username': 'staff_john',
                'password': f'WrongGuess{i}',
            })
            self.assertEqual(res.status_code, 200)

        # 6th attempt must be blocked by rate limit
        blocked_res = self.client.post(self.login_url, {
            'username': 'staff_john',
            'password': 'WrongGuess5',
        })
        self.assertEqual(blocked_res.status_code, 200)
        self.assertContains(blocked_res, "Too many failed login attempts")

        # Even with correct password, account remains locked out
        locked_valid_res = self.client.post(self.login_url, {
            'username': 'staff_john',
            'password': self.password,
        })
        self.assertEqual(locked_valid_res.status_code, 200)
        self.assertContains(locked_valid_res, "Too many failed login attempts")
