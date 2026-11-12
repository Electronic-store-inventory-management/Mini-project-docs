# US-23 – Complete Security Validation

**Issue:** #42
**Branch:** `23-us-23-security-validation`
**Project:** Electronics Store Inventory Management System
**Date:** 12 November 2026

---

## 1. Objective

The objective of this task is to validate the security of the Electronics Store Inventory Management System by testing session management, role-based access control, input validation, SQL injection protection, authentication security, and HTTPS/TLS configuration.

The purpose is to identify potential security weaknesses and document the test results.

## 2. Security Areas Tested

The following security areas were considered:

1. Automatic session expiry.
2. Role-based access restrictions.
3. Input validation.
4. SQL injection protection.
5. Secure authentication handling.
6. HTTPS/TLS configuration.

---

## 3. Session Management and Expiry

### Configuration

The following session settings are configured in `config/settings.py`:

```python
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

### Explanation

- `SESSION_COOKIE_AGE = 1800`: Sets the session cookie age to 30 minutes.
- `SESSION_SAVE_EVERY_REQUEST = True`: Updates the session expiry when a request is made.
- `SESSION_COOKIE_HTTPONLY = True`: Prevents JavaScript from accessing the session cookie.
- `SESSION_COOKIE_SAMESITE = 'Lax'`: Provides protection against certain cross-site request scenarios.

### Tests Performed

Two tests were added to `accounts/tests.py`:

- `test_session_expiry_is_configured_for_30_minutes`
- `test_expired_session_cannot_access_protected_page`

The tests verify the configured session duration and simulate an expired session to check whether a protected page redirects an unauthenticated user to login.

### Result

**Status: PASSED**

The session configuration and expired-session simulation tests passed.

**Note:** The actual 30-minute inactivity period was not tested by waiting for 30 minutes. The tests verify the configuration and simulate an expired session.

---

## 4. Role-Based Access Control

### Implementation

The application uses role-based access restrictions to control which users can perform administrative operations.

The `admin_required` decorator in `inventory/views.py` checks whether the logged-in user has the administrator role.

Administrative operations such as adding and deleting components are restricted to administrators.

### Tests Performed

The existing inventory tests verify that:

- Staff users cannot add components.
- Manager users cannot add components.
- Staff users cannot delete components.
- Manager users cannot delete components.

The tests verify that unauthorized users receive a **403 Forbidden** response.

### Result

**Status: PASSED**

The role-based access restriction tests passed.

---

## 5. Input Validation

### Implementation

Input validation is implemented in `inventory/forms.py` through `ComponentForm`.

The form validates:

- Duplicate component IDs.
- Negative component quantities.
- Invalid unit prices.
- Invalid minimum stock levels.

These validations help prevent incorrect or invalid data from being stored in the database.

### Tests Performed

Existing component form tests were executed to verify that invalid values are rejected.

### Result

**Status: PASSED**

The input validation tests passed.

---

## 6. SQL Injection Protection

### Implementation

Component searching is implemented in `inventory/views.py` using Django ORM queries.

The search functionality uses `Q` objects and `.filter()` with `icontains` lookups instead of constructing raw SQL queries using user input.

This allows Django ORM to handle query parameters safely.

### Test Performed

A new test was added to `ComponentSearchTests` in `inventory/tests.py`:

`test_search_rejects_sql_injection_attempt`

The test sends the following SQL injection-style input:

```text
' OR '1'='1' --
```

It verifies that:

- The search request completes successfully.
- The malicious input does not return all database records.
- No matching components are returned.

### Result

**Status: PASSED**

The SQL injection-style search test passed.

**Note:** This is a targeted regression test. It does not represent a complete security audit of every application endpoint.

---

## 7. Authentication Security

### Implementation

Authentication security is handled through Django's authentication system.

The login functionality uses Django's `AuthenticationForm`.

The application includes:

- Password input fields.
- Generic authentication error messages.
- Login rate limiting after five failed attempts.
- Resetting failed login attempts after successful authentication.
- Password hashing through Django's authentication system.

### Tests Performed

The existing account security tests verify login, logout, CSRF protection, password hashing, role helpers, and login rate limiting.

### Result

**Status: PASSED**

All account security tests passed.

---

## 8. HTTPS/TLS Configuration

### Verification

The local configuration was inspected to check HTTPS-related security settings.

The following deployment-related settings were not found configured in `config/settings.py`:

- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`
- `SECURE_SSL_REDIRECT`
- HTTP Strict Transport Security (HSTS) settings.

### Result

**Status: PENDING**

HTTPS/TLS configuration could not be verified because the deployment environment was not tested.

The production deployment should be configured with HTTPS and appropriate secure cookie and HSTS settings.

---

## 9. Test Execution Summary

The following tests were executed.

| Test Suite | Result |
|---|---:|
| Inventory tests | 58/58 passed |
| Account security tests | 14/14 passed |
| Component search tests | 7/7 passed |
| Complete project test suite | 108/108 passed |

**Important:** Component search tests are included within the inventory test suite. These counts should not be added together.

### Full Test Execution

Command:

```cmd
python manage.py test
```

Output:

```text
Found 108 test(s).
Creating test database for alias 'default'...
System check identified no issues (0 silenced).
............................................................................................................
----------------------------------------------------------------------
Ran 108 tests in 24.382s

OK
Destroying test database for alias 'default'...
```

### Overall Result

**108 out of 108 tests passed successfully.**

No test failures were reported in the complete test suite.

---

## 10. Identified Security Gaps

The following items still require attention:

1. Actual 30-minute inactivity expiry should be verified in a running environment.
2. Additional SQL injection testing should be performed across relevant application inputs and endpoints.
3. HTTPS/TLS should be verified in the deployment environment.
4. Production cookie security and HSTS settings should be reviewed before deployment.

---

## 11. Conclusion

Security validation was performed for the Electronics Store Inventory Management System.

Session management, role-based access control, input validation, SQL injection-style search handling, and authentication security were tested.

The complete Django test suite passed successfully with **108 out of 108 tests**.

HTTPS/TLS deployment verification and additional security checks remain pending.

The results provide evidence that the tested security functionality is working as expected, while the identified gaps should be addressed before production deployment.
