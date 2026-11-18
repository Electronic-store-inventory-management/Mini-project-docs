# Branch Coverage Report

**Assessment date:** 18 November 2026
**Test result:** 105 tests passed, 0 failures.

## Overall branch coverage

- Covered branches: 92/112
- Uncovered branches: 20
- Branch coverage: **82.14%**

## Per-file branch coverage

| Application file | Covered branches | Coverage |
|---|---:|---:|
| `accounts\forms.py` | 7/10 | 70.00% |
| `accounts\views.py` | 1/2 | 50.00% |
| `inventory\forms.py` | 5/8 | 62.50% |
| `inventory\models.py` | 22/22 | 100.00% |
| `inventory\views.py` | 13/16 | 81.25% |
| `reports\management\commands\check_availability.py` | 5/6 | 83.33% |
| `reports\services.py` | 27/36 | 75.00% |
| `reports\views.py` | 12/12 | 100.00% |

## Execution details

Command: `coverage run --branch manage.py test`

All 105 tests passed during the coverage run.
Coverage.py used its Python tracer because Windows Application Control blocked the C tracer.
