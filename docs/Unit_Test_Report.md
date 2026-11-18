# Unit Test Report

**Assessment date:** 18 November 2026

## Execution summary

| Metric | Result |
|---|---:|
| Total automated tests | 116 |
| Passed | 116 |
| Failed | 0 |
| Standard execution time | 13.961 seconds |
| Django system check | No issues |

## Test command

`.venv\Scripts\python.exe manage.py test`

Detailed output: `Unit_Test_Execution_Log.txt`

## Areas covered

- Authentication and login rate limiting.
- Session security and expired-session handling.
- Inventory listing, searching, addition and deletion.
- Validation and data integrity.
- Role-based authorization.
- Dashboard and availability reporting.
- Monthly availability calculations.
- Inventory audit logging.
- Performance and response-time checks.

## Coverage results

- Statement coverage: **93.90% (570/607)**
- Branch coverage: **83.90% (99/118)**
- Combined coverage: **92.28%**

## Environment notes

Automated tests use an isolated in-memory SQLite database.
Coverage.py used its Python tracer because Windows Application Control blocked its C tracer.
The configured MySQL database migration has not been independently verified because Windows blocked the MySQL driver DLL.
