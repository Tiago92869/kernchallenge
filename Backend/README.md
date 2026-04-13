Debug local run : 
 - python -m flask --app app run --debug 

After importing any module run this command after: 
 - pip freeze > requirements.txt  

This will save in the requirements.txt all the modules that are installed in this env.
When creating this prohect from scratch you can simple run :
 - pip install -r requirements.txt

To get all the necessary modules installed


Regarding database migration, follow this steps:
- flask db init
- flask db migrate -m "create core tables"
- flask db upgrade


Usefull git command to clean branches besides master
git branch | ForEach-Object { $_.Replace('*','').Trim() } | Where-Object { $_ -and $_ -ne 'master' } | ForEach-Object { git branch -D $_ }


Usefull command to get the test coverage of the system (keep it above 95%)
pytest --cov=app --cov-report=term-missing --cov-report=html


Project is only considered finished if this command passes
pytest --cov=app --cov-fail-under=95


Ruff linting (local and CI)
- Role: Ruff is our static analysis and formatting gate. It catches code quality issues (unused imports, likely bugs, style inconsistencies) early and keeps code consistent before review.
- CI behavior: Every PR runs Ruff lint and Ruff format checks. If any rule fails, the PR check fails.
- Install: pip install ruff
- Run lint: ruff check app tests --config pyproject.toml
- Run format check: ruff format app tests --config pyproject.toml --check
- Auto-fix lint issues: ruff check app tests --config pyproject.toml --fix
- Auto-format code: ruff format app tests --config pyproject.toml
- Full local check (same intent as CI): ruff check app tests --config pyproject.toml ; ruff format app tests --config pyproject.toml --check


Before commit checklist

**Automated Approach (Recommended):**

First, activate your virtual environment:
```bash
# Windows
.venv\Scripts\activate
```

Then run the pre-commit check script:
```bash
python pre-commit-check.py
```

The script will:
1. Run tests and verify 95%+ code coverage (aborts if failed)
2. Check ruff lint violations, auto-fix up to 3 times (stops if persists)
3. Check ruff formatting, auto-format up to 3 times (stops if persists)
4. Display colorized output with fun success summary

**Sample Output:**
```
============================================================
           STEP 1: RUNNING TESTS & COVERAGE CHECK
============================================================
...
✓ All tests passed AND coverage exceeded 95%! 🎉

============================================================
           STEP 2: RUNNING RUFF LINT CHECKS
============================================================
✓ No lint violations found! Clean code detected! 🚀

============================================================
          STEP 3: RUNNING RUFF FORMAT CHECKS
============================================================
✓ All files are properly formatted! ✨

============================================================
           ALL PRE-COMMIT CHECKS PASSED! 🎊
============================================================
```

**Manual Approach:**

If you prefer to run commands individually:
- Run tests: `pytest --cov=app --cov-fail-under=95`
- Run Ruff lint: `ruff check app tests --config pyproject.toml`
- Run Ruff format check: `ruff format app tests --config pyproject.toml --check`
- If Ruff fails, fix automatically:
  - `ruff check app tests --config pyproject.toml --fix`
  - `ruff format app tests --config pyproject.toml`

**Manual Approach:**
- Run tests: pytest --cov=app --cov-fail-under=95
- Run Ruff lint: ruff check app tests --config pyproject.toml
- Run Ruff format check: ruff format app tests --config pyproject.toml --check
- If Ruff fails, fix automatically:
	- ruff check app tests --config pyproject.toml --fix
	- ruff format app tests --config pyproject.toml