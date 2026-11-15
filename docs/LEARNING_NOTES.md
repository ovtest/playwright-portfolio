# Learning Notes

Concepts behind this framework, collected while building it. Useful for revision and interview prep.

---

## 1. How the framework is organised

| Piece | File(s) | Purpose |
|---|---|---|
| Page Objects | `pages/*.py` | Locators and actions for one page. Tests say *what*, page classes know *how*. A UI change is fixed in one place. |
| Fixtures | `tests/conftest.py` | Reusable setup a test requests by name, e.g. `logged_in_page` starts a test already logged in. `page` (a fresh browser tab per test) comes from pytest-playwright. |
| Tests | `tests/test_*.py` | Test cases grouped by feature. |
| Test data | `config.py` | Users and customer details in one place. |
| Run settings | `pytest.ini` | Base URL, reports, failure evidence, markers. |
| Markers | `@pytest.mark.smoke` / `regression` | Tags for running subsets: `pytest -m smoke`. |
| Parametrize | `@pytest.mark.parametrize` | Run one test with several data sets (data-driven testing). See `test_invalid_login_shows_error`. |
| Assertions | `expect(...)` | "Web-first" assertions that wait automatically (default 5 s), so no `sleep()` is needed. |

### About the test site

[saucedemo.com](https://www.saucedemo.com) is a public practice site by Sauce Labs. Its demo users are
printed on the login page (password `secret_sauce`), and each simulates a scenario:

- `standard_user`: normal user
- `locked_out_user`: always gets "locked out" (negative tests)
- `problem_user`, `performance_glitch_user`, `error_user`, `visual_user`: deliberate bugs, slowness, visual issues

Nothing is real: no real accounts, orders or payments. In a real job, test credentials would be private
and kept out of the code (environment variables or a git-ignored `.env` file). A good future improvement.

---

## 2. Locators: how elements are found

Same principle as Selenium: a person chooses the locator and stores it in a variable (in the Page Object).
The site marks elements with `data-test="..."` attributes; `conftest.py` tells `get_by_test_id()` to read
`data-test` instead of the default `data-testid`.

### Selenium vs Playwright

| Selenium | Playwright | Example |
|---|---|---|
| By.ID / By.CSS_SELECTOR | `page.locator("css")` | `page.locator("#user-name")` |
| By.XPATH | `page.locator("xpath=...")` | still supported |
| Custom attribute | `get_by_test_id()` | `get_by_test_id("checkout")` |
| By.LINK_TEXT / text XPath | `get_by_text()` | `get_by_text("Products")` |
| (none) | `get_by_role()` | `get_by_role("button", name="Add to cart")` |
| (none) | `get_by_label()`, `get_by_placeholder()` | form fields by label / hint text |

Recommended priority: **role** → **test id** → label/placeholder/text → CSS/XPath as a last resort.
Avoid position-based paths like `/div[3]/div[2]/span`; they break when the layout changes.

### Behaviour differences from Selenium

- **Lazy:** a locator is a saved "recipe"; the page is searched only when you act (`.click()`, `.fill()`).
  That's why Page Objects can define all locators up front.
- **Auto-waiting:** before acting, Playwright waits until the element is attached, visible, enabled and stable.
  No `WebDriverWait` / `sleep` needed.
- **Strict mode:** if a locator matches 2+ elements when you act, Playwright raises an error instead of
  silently using the first one.

### "Smart" locators on complex pages (tables, lists, containers)

Narrow down step by step, the way a person reads the page, instead of writing one complex XPath:

```python
# Table: "Edit" button in the row containing "Order 1042"
page.get_by_role("row").filter(has_text="Order 1042").get_by_role("button", name="Edit").click()

# Card list: the product card with this name (used in pages/inventory_page.py)
self.items.filter(has_text=product_name).get_by_role("button", name="Add to cart")

# Section scoping: search only inside the "Shipping" panel
shipping = page.locator("section").filter(has=page.get_by_role("heading", name="Shipping"))
shipping.get_by_label("City").fill("Austin")
```

Equivalent relative XPath for comparison: `//tr[contains(., 'Order 1042')]//button[text()='Edit']`.

### Codegen

`playwright codegen <url>` records your clicks and writes code with locators (see MAINTENANCE.md for the command).

How it chooses: tries test id → role + name → label/placeholder/alt → text → CSS, and keeps the first
candidate that matches exactly one element. If nothing is unique, it adds `.nth(n)` / `.first`.

Good at: well-built pages, forms, menus. Weak at: repeated items (gives fragile `.nth(3)`), text that
changes (prices, dates, names), poor HTML (falls back to long CSS). It finds *an* element, not your intent.

Workflow: record or Pick locator → look for warning signs (`.nth()`, `.first`, long CSS, changing text) →
rewrite with filter/scoping → move into the Page Object.
Interview line: *"I use codegen to find locators fast, then review them and move them into Page Objects."*

(Selenium's equivalent recorder is Selenium IDE, a browser extension whose exports usually need heavy cleanup.)

---

## 3. Debugging failures

1. Read the error in the PyCharm Run panel or the HTML report (e.g. "expected 2, got 1").
2. Look at the screenshot / video in `test-results\<test-name>\`.
3. Open the **trace** (`playwright show-trace ...`): step-by-step timeline with page snapshots before and
   after each action, network calls and console messages. Playwright's best debugging tool.
4. Run with `--headed` and a PyCharm breakpoint + Debug to pause the browser at a specific step.

Practice idea: change an expected value to make a test fail on purpose, then inspect all of the above.

---

## 4. Cross-browser and cross-OS strategy

### What Playwright can run

| Target | How | Notes |
|---|---|---|
| Latest Chrome | `--browser-channel chrome` | Real installed Chrome |
| Latest Edge | `--browser-channel msedge` | Real installed Edge |
| Chrome/Edge beta/dev | `chrome-beta`, `msedge-dev`, ... | Catch problems before users get the update |
| Firefox | `--browser firefox` | Playwright-patched Firefox build, very close but not the branded release |
| Safari | `--browser webkit` | Safari's *engine*, not Safari. Real Safari can't be driven by Playwright (only Selenium + safaridriver on a Mac). |
| Older browser versions | install an older Playwright version | Awkward: each Playwright release comes with one fixed browser version |

Engines: Chromium = Chrome + Edge, Firefox, WebKit = Safari. WebKit runs on Windows too.

### Multiple operating systems: CI matrix

GitHub Actions provides Windows, several macOS versions and Linux machines (free for public repos).
A matrix runs every combination in parallel:

```yaml
strategy:
  matrix:
    os: [windows-latest, macos-14, macos-15]
    browser: [chromium, firefox, webkit]
```

### Real Safari, older versions, exact OS versions: cloud device labs

BrowserStack, Sauce Labs, LambdaTest support Playwright. Tests stay the same; the browser connection
points to their machine with the requested OS + browser version (like Selenium Grid). Paid; trials and
open-source plans exist. Check each provider's docs for what "Safari" means with Playwright.

### Recommended risk-based plan (good interview answer)

- **Every push:** Chromium, Firefox, WebKit on Linux. Fast, cheap, catches most issues.
- **Nightly / before release:** CI matrix on Windows + macOS, including real Chrome and Edge.
- **Occasionally / customer-specific bugs:** older versions and real Safari on a cloud lab.

Speed-up for bigger suites: `pytest-xdist` + `-n auto` runs tests in parallel.

---

## 5. Roadmap for this project

- [x] Configure git name/email, first commit, publish on GitHub
- [x] Pin package versions in `requirements.txt`
- [x] GitHub Actions CI (Linux, Chromium / Firefox / WebKit matrix) + status badge in README
- [ ] Extend CI: Windows / macOS jobs with real Chrome and Edge (`--browser-channel`)
- [ ] Screenshot of the HTML report in README
- [ ] API tests with Playwright's `request` context (e.g. restful-booker.herokuapp.com)
- [ ] Practice: product sorting test (record with codegen, refactor into `inventory_page.py`)
- [ ] Practice: Page Object for the-internet.herokuapp.com "Sortable Data Tables"
- [ ] Move test credentials to environment variables / `.env`
