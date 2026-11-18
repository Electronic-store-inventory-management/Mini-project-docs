# Electronics Store Inventory Management System
# Updated Requirements Traceability Matrix (RTM)

**Version:** 1.1
**Update date:** 18 November 2026
**Purpose:** Trace requirements to test cases and current verification evidence.

## Status definitions

- **Passed:** Supporting automated or performance evidence exists.
- **Partially verified:** Some related behaviour is tested, but a specified acceptance criterion remains unverified.
- **Pending:** Required evidence or formal evaluation has not been completed.

## 1. Functional requirements

| Requirement | Requirement summary | Existing RTM test ID | Current evidence / status |
|---|---|---|---|
| FR-001 | List inventory components | TC-INV-01 | Inventory listing tests — Passed |
| FR-002 | Add a component | TC-ADD-01 | Valid component creation test — Passed |
| FR-003 | Validate required component details | TC-ADD-02 | Form and model validation tests — Passed |
| FR-004 | Enforce unique component IDs | TC-ADD-03 | Duplicate ID tests — Passed |
| FR-005 | Delete a component | TC-DEL-01 | Authenticated deletion tests — Passed |
| FR-006 | Display component quantity | TC-INV-02 | Inventory quantity display tests — Passed |
| FR-007 | Determine availability from quantity and minimum stock | TC-AVL-01 | Availability status tests — Passed |
| FR-008 | Identify low-stock components | TC-AVL-02 | Low-stock filtering tests — Passed |
| FR-009 | Identify out-of-stock components | TC-AVL-03 | Zero-quantity filtering tests — Passed |
| FR-010 | Generate availability report | TC-AVL-04 | Report generation, filters and export tests — Passed |
| FR-011 | Display dashboard statistics | TC-DSH-01 | Dashboard statistics tests — Passed |
| FR-012 | Display confirmation messages | TC-MSG-01 | Successful operation message tests — Passed |
| FR-013 | Display appropriate error messages | TC-MSG-02 | Validation and missing-record error tests — Passed |
| FR-014 | Restrict operations to authorized users | TC-AUTH-02 | Manager/Staff add and delete restrictions — Passed |
| FR-015 | Support login and logout | TC-AUTH-01 | Authentication, invalid login and logout tests — Passed |
| FR-016 | Search by ID, name and category | TC-INV-03 | Search tests — Passed |

## 2. Non-functional requirements

| Requirement | Requirement summary | Existing RTM test ID | Current evidence / status |
|---|---|---|---|
| NFR-001 | Normal operations under 3 seconds for at least 90% of requests at specified scale | TC-PERF-01 | Locust: 10 users, 10,000 records, 759 requests, 0 failures, P90 140 ms — Passed at tested scale |
| NFR-002 | Authentication before inventory access | TC-AUTH-03 | Protected-page authentication tests — Passed |
| NFR-003 | Restrict add/delete operations | TC-AUTH-02 | Role-based access tests — Passed |
| NFR-004 | At least 99% monthly availability, excluding maintenance | TC-OPS-01 | Operating-hour and maintenance calculations tested; one-month evidence pending — Partially verified |
| NFR-005 | Intuitive user interface | TC-UX-01 | Formal representative-user usability evaluation not recorded — Pending |
| NFR-006 | Valid and consistent data | TC-REL-01 | Model validation, constraints and integrity tests — Passed |
| NFR-007 | Support up to 10,000 records | TC-PERF-02 | 10,000-record performance test — Passed at tested scale |
| NFR-008 | Modular design | TC-MNT-01 | Formal architecture review not recorded — Pending |

## 3. Security requirements

| Requirement | Requirement summary | Existing RTM test ID | Current evidence / status |
|---|---|---|---|
| SR-001 | Store salted password hashes | TC-SEC-01 | Password hash test verifies hashed storage and password checking — Passed |
| SR-002 | Expire inactive sessions after 30 minutes | TC-SEC-02 | `SESSION_COOKIE_AGE = 1800` and `SESSION_SAVE_EVERY_REQUEST = True`; timed expiry test pending — Partially verified |
| SR-003 | Enforce server-side authentication and role checks | TC-SEC-03 | Protected views and role restriction tests — Passed for tested operations |
| SR-004 | Input validation and SQL injection, XSS and CSRF protection | TC-SEC-04 | Input validation and CSRF test evidence exists; dedicated XSS and SQL injection tests pending — Partially verified |
| SR-005 | Audit successful additions/deletions with user, component ID and timestamp; never log passwords | TC-SEC-05 | `AuditLog` model and three audit tests verify ADD/DELETE records in isolated SQLite; MySQL migration verification pending — Passed in automated tests |
| SR-006 | Block further login after five failed attempts for 15 minutes | TC-SEC-06 | Five-failure lockout test and 900-second timeout configuration test — Passed for tested behaviour; elapsed-time expiry test pending |
| SR-007 | Use HTTPS and TLS 1.2 or higher in network deployment | TC-SEC-07 | Deployment-level HTTPS/TLS evidence not available — Pending |

## 4. Sprint update — SR-005 audit logging

The project uses the team's existing `AuditLog` model.

Audit records contain:
- User foreign key.
- Action (`ADD` or `DELETE`).
- Component ID.
- Automatically generated timestamp.

Migration: `inventory/migrations/0003_auditlog.py`

Three audit tests verify successful addition, rejected duplicate addition, and successful deletion. All three passed in the full 116-test suite.

**Environment limitation:** The migration was applied successfully in the isolated in-memory SQLite test database. Verification against the configured MySQL database remains pending because Windows Application Control blocks the MySQL driver DLL.

## 5. Latest regression and coverage evidence

| Evidence | Latest result |
|---|---:|
| Full automated test suite | 116 passed, 0 failed |
| Standard test duration | 14.166 seconds |
| Statement coverage | 93.90% (570/607) |
| Branch coverage | 83.90% (99/118) |
| Combined coverage.py metric | 92.28% |

Supporting files are available in the project's `docs` folder:

- `Unit_Test_Execution_Log.txt`
- `Unit_Test_Report.md`
- `System_Validation_Report.md`
- `Code_Coverage_Report.md`
- `Branch_Coverage_Report.md`
- `Test_Case_Document.md`

## 6. Outstanding evidence

Requirements marked partially verified or pending must remain open until the corresponding tests, operational records, deployment evidence, or formal review are completed. Do not treat the existence of a test-case ID in the original RTM as proof that the requirement has passed.
