# Code Coverage Report

**Assessment date:** 18 November 2026
**Test result:** 105 tests passed, 0 failures.

## Overall statement coverage

- Covered statements: 536/556
- Statement coverage: **96.40%**
- Combined coverage.py metric: **94.01%**

Coverage excludes test files, migrations, manage.py and config files.

## Per-file statement coverage

| Application file | Covered statements | Coverage |
|---|---:|---:|
| `accounts\__init__.py` | 0/0 | 100.00% |
| `accounts\admin.py` | 10/10 | 100.00% |
| `accounts\apps.py` | 3/3 | 100.00% |
| `accounts\forms.py` | 40/40 | 100.00% |
| `accounts\models.py` | 22/23 | 95.65% |
| `accounts\urls.py` | 3/3 | 100.00% |
| `accounts\views.py` | 19/20 | 95.00% |
| `dashboard\__init__.py` | 0/0 | 100.00% |
| `dashboard\admin.py` | 1/1 | 100.00% |
| `dashboard\apps.py` | 4/4 | 100.00% |
| `dashboard\models.py` | 1/1 | 100.00% |
| `dashboard\urls.py` | 4/4 | 100.00% |
| `dashboard\views.py` | 15/15 | 100.00% |
| `inventory\__init__.py` | 0/0 | 100.00% |
| `inventory\admin.py` | 8/8 | 100.00% |
| `inventory\apps.py` | 3/3 | 100.00% |
| `inventory\forms.py` | 29/32 | 90.62% |
| `inventory\models.py` | 81/84 | 96.43% |
| `inventory\urls.py` | 4/4 | 100.00% |
| `inventory\views.py` | 76/80 | 95.00% |
| `reports\__init__.py` | 0/0 | 100.00% |
| `reports\admin.py` | 17/17 | 100.00% |
| `reports\apps.py` | 4/4 | 100.00% |
| `reports\management\__init__.py` | 0/0 | 100.00% |
| `reports\management\commands\__init__.py` | 0/0 | 100.00% |
| `reports\management\commands\check_availability.py` | 36/37 | 97.30% |
| `reports\models.py` | 19/23 | 82.61% |
| `reports\services.py` | 94/97 | 96.91% |
| `reports\urls.py` | 4/4 | 100.00% |
| `reports\views.py` | 39/39 | 100.00% |

## Execution details

Command: `coverage run --branch manage.py test`

All 105 tests passed during the coverage run.
Coverage.py used its Python tracer because Windows Application Control blocked the C tracer.
