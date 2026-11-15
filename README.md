# Playwright + Python UI Test Framework

UI test automation framework for the demo store [saucedemo.com](https://www.saucedemo.com),
built with **Playwright**, **pytest** and the **Page Object Model**.

## What's covered

| Area | Tests |
|---|---|
| Login | Successful login, locked-out user, data-driven invalid logins (empty form, missing password, wrong password) |
| Cart | Add item updates badge, cart lists added items, remove item |
| Checkout | Full end-to-end purchase, required-field validation |

Tests are tagged `smoke` (critical path) or `regression` (wider coverage).

## Tech stack

- Python 3.13
- [Playwright for Python](https://playwright.dev/python/) with `pytest-playwright`
- pytest (fixtures, markers, parametrization)
- pytest-html for reports

## Project structure

```
pages/              Page Objects: locators and actions for each page
  base_page.py
  login_page.py
  inventory_page.py
  cart_page.py
  checkout_page.py
tests/              Test cases, grouped by feature
  conftest.py       Shared fixtures (e.g. logged_in_page)
  test_login.py
  test_cart.py
  test_checkout.py
config.py           Test data (users, customer details)
pytest.ini          Run settings: base URL, browser, reports, markers
```

## Design decisions

- **Page Object Model:** tests describe *what* happens; page classes hold *how* (locators). A UI change is fixed in one place.
- **Stable locators:** elements are found by the site's `data-test` attributes, not by CSS paths that break easily.
- **Fixtures for setup:** `logged_in_page` gives each test a logged-in session without repeating login steps.
- **Web-first assertions:** `expect(...)` waits automatically, so there are no `sleep()` calls.
- **Evidence on failure:** screenshots, video and a Playwright trace are kept only for failed tests.

## How to run

```bash
# 1. Create and activate a virtual environment (Windows)
py -3.13 -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies and the browser
pip install -r requirements.txt
playwright install chromium

# 3. Run tests
pytest                      # all tests
pytest -m smoke             # smoke tests only
pytest --headed             # watch the browser
pytest --browser firefox    # another browser (run: playwright install firefox)
pytest --browser chromium --browser firefox --browser webkit   # all three engines
```

After a run, open `reports/report.html` for the HTML report.
To inspect a failed test step by step: `playwright show-trace test-results/<test-folder>/trace.zip`.

## Documentation

- [Maintenance guide](docs/MAINTENANCE.md): running tests (CLI, PyCharm, batch, browsers), updating Playwright, reports and traces, troubleshooting
- [Learning notes](docs/LEARNING_NOTES.md): locator strategy, codegen, debugging, cross-browser / cross-OS approach, roadmap

## Planned next steps

- API tests with Playwright's `request` context
- GitHub Actions CI pipeline
- Cross-browser runs
