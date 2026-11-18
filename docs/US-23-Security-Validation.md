# US-23 – Complete Security Validation

**Issue:** #42
**Pull Request:** #48
**Branch:** `23-us-23-security-validation`
**Project:** Electronics Store Inventory Management System

## 1. Objective

The objective of this task is to validate the security of the Electronics Store Inventory Management System by testing session management, role-based access control, input validation, SQL injection protection, authentication security, and HTTPS/TLS configuration.

## 2. Session Management and Expiry

### Existing Configuration

The 30-minute session expiry configuration already existed in `config/settings.py` before this PR.

```python
SESSION_COOKIE_AGE = 1800
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

### Changes in This PR

This PR adds automated tests to validate the existing configuration:

- `test_session_expiry_is_configured_for_30_minutes`
- `test_expired_session_cannot_access_protected_page`

The tests verify the configured session age and simulate an expired session accessing a protected page.

### Result

**Status: PARTIALLY VERIFIED – DEFERRED ACCEPTANCE CRITERION**

The configuration and expired-session simulation tests pass.

Actual automatic expiry after 30 minutes of inactivity has not been verified by waiting for the full inactivity period. This verification remains deferred.

## 3. Role-Based Access Control

The application uses the `admin_required` decorator to restrict administrative operations.

Tests verify that staff and manager users cannot add or delete components.

Unauthorized requests receive a 403 Forbidden response.

**Status: PASSED**

## 4. Input Validation

The `ComponentForm` validates:

- Duplicate component IDs.
- Negative component quantities.
- Negative unit prices.
- Negative minimum stock levels.

**Status: PASSED**

## 5. SQL Injection Protection

### Implementation

Component search uses Django ORM queries with `Q` objects and `filter()` lookups rather than constructing raw SQL queries from user input.

### Tests Performed

The component search test now checks five representative SQL injection-style inputs:

1. `' OR '1'='1' --`
2. `'; DROP TABLE components; --`
3. `" OR "1"="1`
4. `1' UNION SELECT NULL --`
5. `admin' --`

For each input, the test verifies that:

- The request returns HTTP 200.
- No components are returned.
- The submitted search query is preserved.

### Result

**Status: PASSED – TARGETED REGRESSION TESTING**

All five representative inputs are covered by the automated search test.

This is targeted testing of the component search functionality, not a complete security audit of every application endpoint.

## 6. Authentication Security

The application uses Django's authentication system and `AuthenticationForm`.

Security tests cover:

- Login and logout.
- Password hashing.
- CSRF protection.
- Role helper functions.
- Login rate limiting after five failed attempts.
- Resetting failed login attempts after successful authentication.

**Status: PASSED**

## 7. HTTPS/TLS Configuration

HTTPS/TLS deployment verification has not been completed because a deployment environment was not available for testing.

The following production settings require deployment-level review:

- `SESSION_COOKIE_SECURE`
- `CSRF_COOKIE_SECURE`
- `SECURE_SSL_REDIRECT`
- HTTP Strict Transport Security (HSTS).

**Status: DEFERRED – DEPLOYMENT VERIFICATION**

HTTPS/TLS must be verified after deployment. It is not marked as completed.

## 8. Test Execution Summary

| Test Suite | Result |
|---|---:|
| Component search tests | 7/7 passed |
| Inventory tests | 58/58 passed |
| Account security tests | 14/14 passed |
| Complete project test suite | 108/108 passed |

Note: Component search tests are included within the inventory test suite. These results are not additive.

### Complete Project Test

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
Ran 108 tests in 19.430s

OK
Destroying test database for alias 'default'...
```

**Overall Result: 108/108 tests passed.**

## 9. Deferred Acceptance Criteria

The following items remain open:

1. Actual automatic session expiry after 30 minutes of inactivity.
2. HTTPS/TLS verification in the deployment environment.
3. Broader security testing beyond the component search injection regression tests.

## 10. Conclusion

Security validation tests were added and executed for the Electronics Store Inventory Management System.

The tests cover session configuration, expired-session handling, role-based access, input validation, representative SQL injection inputs, and authentication security.

The complete project test suite passed with 108 out of 108 tests.

Actual 30-minute inactivity verification and HTTPS/TLS deployment verification remain deferred and are not claimed as completed.
