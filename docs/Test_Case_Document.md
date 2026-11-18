# Electronics Store Inventory Management System
# Updated Test Case Document

**Version:** 1.1
**Update date:** 18 November 2026
**Scope:** Sprint updates and regression testing
**Execution result:** 116 tests passed, 0 failures

## 1. Purpose

This document updates the existing test cases against the current system requirements and sprint changes. It includes inventory, authentication, dashboard, reporting, performance, and security-related test coverage.

## 2. Test environment and execution

- Framework: Django
- Automated test command: `manage.py test`
- Test database: Isolated in-memory SQLite
- Latest regression run: 116 tests passed in 13.961 seconds
- Django system check: No issues
- Statement coverage: 93.90% (570/607)
- Branch coverage: 83.90% (99/118)
- Combined coverage.py metric: 92.28%

The MySQL migration for the new audit-log table has not yet been verified against the project's configured MySQL database because Windows Application Control blocks the MySQL driver DLL.

## 3. Functional test cases

| Test Case ID | Requirement | Test scenario | Expected result | Latest result |
|---|---|---|---|---|
| TC-INV-01 | FR-001 | View component inventory | Inventory records are displayed to an authenticated user | Passed |
| TC-INV-02 | FR-006 | View component quantities | Correct component quantities are displayed | Passed |
| TC-INV-03 | FR-016 | Search by component ID, name, or category | Matching records are returned; unmatched queries show no results | Passed |
| TC-ADD-01 | FR-002 | Add a valid component | Component is saved and success confirmation is shown | Passed |
| TC-ADD-02 | FR-003 | Submit missing or invalid component details | Invalid data is rejected with validation errors | Passed |
| TC-ADD-03 | FR-004 | Add a duplicate component ID | Duplicate ID is rejected | Passed |
| TC-DEL-01 | FR-005 | Delete an existing component | Component is deleted after an authorized POST request | Passed |
| TC-AVL-01 | FR-007 | Check availability using quantity and minimum stock level | Correct availability status is returned | Passed |
| TC-AVL-02 | FR-008 | View low-stock components | Components at or below the minimum stock level are identified | Passed |
| TC-AVL-03 | FR-009 | View out-of-stock components | Components with zero quantity are identified | Passed |
| TC-AVL-04 | FR-010 | Generate availability report | Availability report and supported filters are returned | Passed |
| TC-DSH-01 | FR-011 | View dashboard statistics | Dashboard counts reflect inventory data | Passed |
| TC-MSG-01 | FR-012 | Complete successful inventory operation | Appropriate confirmation message is displayed | Passed |
| TC-MSG-02 | FR-013 | Submit invalid data or request a missing record | Appropriate error is returned | Passed |
| TC-AUTH-01 | FR-015 | Login with valid and invalid credentials; logout | Valid login succeeds, invalid login is rejected, and logout clears the session | Passed |
| TC-AUTH-02 | FR-014, NFR-003 | Manager or Staff attempts restricted add/delete operation | Unauthorized operation is denied | Passed |
| TC-AUTH-03 | NFR-002 | Access protected inventory page without authentication | User is redirected to login or denied access | Passed |

## 4. Non-functional test cases

| Test Case ID | Requirement | Test scenario | Expected result | Latest result |
|---|---|---|---|---|
| TC-PERF-01 | NFR-001 | Performance test with 10 concurrent users and 10,000 records | Normal operations meet the 3-second response requirement | Passed at tested scale |
| TC-PERF-02 | NFR-007 | Exercise inventory with 10,000 component records | System supports the tested record volume | Passed at tested scale |
| TC-OPS-01 | NFR-004 | Test operating-hour availability and maintenance incident calculations | Availability calculations handle operating hours and maintenance correctly | Partially verified; one-month uptime evidence pending |
| TC-UX-01 | NFR-005 | Evaluate usability with representative users | Usability feedback is collected and evaluated | Pending formal user evaluation |
| TC-REL-01 | NFR-006 | Test validation, integrity constraints, and invalid data handling | Invalid or inconsistent records are rejected | Passed |
| TC-MNT-01 | NFR-008 | Review modularity and maintainability against architecture criteria | Architecture review confirms modular design | Pending formal review |

### Performance evidence

The recorded Locust performance run used 10 concurrent users and 10,000 component records over 120 seconds.

- Requests: 759
- Failed requests: 0
- Average response time: 118.23 ms
- Aggregate P90 response time: 140 ms
- Maximum response time: 2214.47 ms
- Required response time: less than 3000 ms

These results demonstrate performance at the tested workload; they do not establish performance at every possible deployment scale.

## 5. Security test cases

| Test Case ID | Requirement | Test scenario | Expected result | Latest result |
|---|---|---|---|---|
| TC-SEC-01 | SR-001 | Verify stored passwords | Passwords are stored as hashes, not plaintext | Passed |
| TC-SEC-02 | SR-002 | Verify 30-minute inactivity session expiry | Inactive session expires after the configured period | Partially verified; configuration is 1800 seconds, timed expiry test pending |
| TC-SEC-03 | SR-003 | Access inventory endpoints without authentication or with unauthorized roles | Server-side authentication and role restrictions are enforced | Passed for tested protected operations |
| TC-SEC-04 | SR-004 | Test validation and CSRF protection | Invalid input is rejected and CSRF protection is enforced | Partially verified; dedicated XSS and SQL injection tests pending |
| TC-SEC-05 | SR-005 | Add and delete components and inspect audit records | Each successful operation records user, action, component ID, and timestamp | Passed in isolated SQLite tests; MySQL migration verification pending |
| TC-SEC-06 | SR-006 | Submit repeated failed login attempts | Further login attempts are blocked after five failures for the configured 15-minute period | Passed for lockout behaviour and 900-second timeout configuration; elapsed-time expiry test pending |
| TC-SEC-07 | SR-007 | Verify deployed HTTPS and TLS configuration | Deployment uses HTTPS and TLS 1.2 or higher | Pending deployment verification |

### Merged US-21 audit test evidence

The team's existing `AuditLog` implementation is used.

Three tests are included in `inventory.tests.InventoryAuditLogTests`:

1. `test_successful_add_creates_audit_log`
2. `test_failed_add_does_not_create_audit_log`
3. `test_successful_delete_creates_audit_log`

All three passed in the full 116-test suite.

## 6. Overall execution summary

| Metric | Result |
|---|---:|
| Automated tests | 116 |
| Passed | 116 |
| Failed | 0 |
| Statement coverage | 93.90% |
| Branch coverage | 83.90% |
| Combined coverage | 92.28% |

Refer to `Unit_Test_Execution_Log.txt`, `Unit_Test_Report.md`, `System_Validation_Report.md`, `Code_Coverage_Report.md`, and `Branch_Coverage_Report.md` for supporting evidence.

## 7. Outstanding verification

The following must not be reported as fully passed until evidence is available:

- Monthly 99% availability evidence for NFR-004.
- Formal usability evaluation for NFR-005.
- Architecture review for NFR-008.
- Timed inactivity-expiry test for SR-002.
- Dedicated XSS and SQL injection testing for SR-004.
- MySQL migration verification for SR-005.
- Actual elapsed 15-minute lockout expiry test for SR-006.
- Deployment HTTPS/TLS verification for SR-007.
