

\# System Validation Report



Date: 18 November 2026



Project: Electronics Store Inventory Management System



\## 1. Objective



To validate the Electronics Store Inventory Management System against the functional and non-functional requirements specified in the Software Test Plan.



\## 2. Test Environment



\- Application: Django

\- Automated testing: Django built-in test framework

\- Performance testing: Locust 2.47.0

\- Performance database: MySQL 8.0.46

\- Application server: Waitress

\- Performance database: electronics\_inventory\_perf



\## 3. Automated Test Execution



\- Tests discovered: 103

\- Tests executed: 103

\- Passed: 103

\- Failed: 0

\- Errors: 0

\- Execution time: 20.660 seconds

\- Django system check: No issues identified



The automated test suite covers authentication, dashboard, inventory operations, validation, duplicate component IDs, search, pagination, availability reporting, health checks and system availability.



\## 4. Functional Requirement Validation



| Requirement | Validation Evidence | Status |

|---|---|---|

| FR-001 View inventory | Component listing and search tests | Passed |

| FR-002 Add component | Component addition tests | Passed |

| FR-003 Validate required details | Form validation tests | Passed |

| FR-004 Prevent duplicate IDs | Duplicate ID tests | Passed |

| FR-005 Delete component | Deletion tests | Passed |

| FR-006 Display quantity | Inventory and availability tests | Tested |

| FR-007 Determine availability | Availability status tests | Passed |

| FR-008 Identify low stock | Low-stock tests | Passed |

| FR-009 Identify out of stock | Out-of-stock tests | Passed |

| FR-010 Generate availability report | Report and filtering tests | Passed |

| FR-011 Dashboard statistics | Dashboard tests | Passed |

| FR-012 Confirmation messages | Add and delete operation tests | Tested |

| FR-013 Error messages | Validation and failed-operation tests | Tested |

| FR-014 Restrict inventory operations | Role-based access tests | Passed |



\## 5. Non-Functional Requirement Validation



| Requirement | Evidence | Status |

|---|---|---|

| NFR-001 Response within 3 seconds | Locust performance results | Passed |

| NFR-002 Authentication required | Authentication tests | Passed |

| NFR-003 Authorized add/delete operations | Role restriction tests | Passed |

| NFR-004 System availability | Availability and health-check tests | Partially verified |

| NFR-005 Simple and intuitive interface | No formal usability test evidence | Pending |

| NFR-006 Consistent inventory records | Data integrity tests | Passed |

| NFR-007 Handle increasing records | Load test with 10,000 records | Passed at tested scale |

| NFR-008 Modular structure | Requires architecture review | Pending |



\## 6. Performance and Load Validation



The final performance test simulated 10 concurrent users using 10,000 component records over 120 seconds.



| Metric | Result |

|---|---:|

| Total requests | 759 |

| Failed requests | 0 |

| Average response time | 118.23 ms |

| Aggregate p90 response time | 140 ms |

| Maximum response time | 2,214.47 ms |

| Required response threshold | 3,000 ms |



All operation-specific p90 response times were below the required 3,000 ms threshold.



The performance results satisfy the specified response-time requirement in the tested environment.



\## 7. Security Validation



Automated tests provide evidence for:



\- Successful and unsuccessful authentication.

\- CSRF protection on login.

\- Login rate limiting.

\- Session termination on logout.

\- Password hashing.

\- Role-based restrictions on inventory addition and deletion.

\- Rejection of unauthorized access.



However, complete dedicated security validation has not yet been evidenced.



Further verification is required for session expiry, HTTPS/TLS configuration, injection protection and the remaining security acceptance criteria.



Security validation: Partially verified.



\## 8. Code and Branch Coverage



The coverage run included all 102 Django tests.



\- Application statement coverage: 96.80% (515 of 532 statements).

\- Application branch coverage: 83.64% (92 of 110 branches).

\- Uncovered statements: 17.

\- Uncovered branches: 18.



Detailed results are documented in:



\- Code\_Coverage\_Report.md

\- Branch\_Coverage\_Report.md



\## 9. Outstanding Validation Activities



1\. Complete and document the remaining security validation.

2\. Perform and document usability testing.

3\. Review the modular architecture requirement.

4\. Complete formal acceptance testing and stakeholder sign-off.

5\. Update the Requirements Traceability Matrix.

6\. Update the separate Test Case Document and record individual test-case execution results.

7\. Confirm that no critical defects remain open.



\## 10. Overall Conclusion



The automated Django test suite passed all 103 tests without failures or errors.



The performance benchmark completed with 10 concurrent users, 10,000 component records and zero failed requests. The aggregate p90 response time was 140 ms, satisfying the specified 3-second requirement.



The collected evidence supports successful automated functional testing, data-integrity testing and performance validation at the tested scale.



However, overall system validation should not be declared fully complete until the outstanding security, usability, traceability and formal acceptance activities are documented and approved.



\## 11. Supporting Evidence



\- Unit\_Test\_Report.md

\- Unit\_Test\_Execution\_Log.txt

\- Code\_Coverage\_Report.md

\- Branch\_Coverage\_Report.md

\- coverage-summary.json

\- ../performance\_tests/US24\_Performance\_Report.md

\- ../performance\_tests/results/us24\_final\_stats.csv

## Latest retest update — 18 November 2026

### Regression testing
- Full suite: **105/105 tests passed**
- Standard test execution time: **14.166 seconds**
- No Django system-check issues.

### Latest coverage
- Statement coverage: **96.40% (536/556)**
- Branch coverage: **82.14% (92/112)**
- Combined coverage.py metric: **94.01%**

### SR-005 — Inventory audit logging
- Implemented persistent audit records for successful component additions and deletions.
- Records include the user, username snapshot, action, component ID and timestamp.
- Two dedicated audit tests passed.
- The new migration is `inventory/migrations/0003_inventoryauditlog.py`.
- Migration was applied successfully in the isolated SQLite test database.
- Application to the project's MySQL database has not yet been verified because Windows blocked the MySQL driver DLL.
