# Branch Coverage Report

**Assessment date:** 18 November 2026
**Test result:** 116/116 passed, 0 failures.

## Overall branch coverage

- Covered branches: 99/118
- Uncovered branches: 19
- Branch coverage: **83.90%**

## Per-file branch coverage

| Application file | Covered branches | Coverage |
|---|---:|---:|
| `accounts\forms.py` | 7/10 | 70.00% |
| `accounts\views.py` | 1/2 | 50.00% |
| `inventory\forms.py` | 5/8 | 62.50% |
| `inventory\models.py` | 22/22 | 100.00% |
| `inventory\views.py` | 13/14 | 92.86% |
| `reports\management\commands\check_availability.py` | 5/6 | 83.33% |
| `reports\services.py` | 34/44 | 77.27% |
| `reports\views.py` | 12/12 | 100.00% |

## Execution details

Command: `coverage run --branch manage.py test`

All 116 tests passed during the coverage run.
Coverage.py used its Python tracer because Windows Application Control blocked its C tracer.
