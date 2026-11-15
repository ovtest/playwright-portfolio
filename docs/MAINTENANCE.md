# Framework Maintenance Guide

How to run, update and troubleshoot this framework.
All commands are run from the project folder (`C:\projects\playwright-portfolio`).

---

## 1. Environment setup

The project uses its own virtual environment (`.venv`) made from Python 3.13.
It is separate from other Python installs on the machine, so other projects are not affected.

Set up from scratch (new machine, or after deleting `.venv`):

```bash
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\playwright install chromium
```

- `py -3.13` uses the Windows Python launcher to pick Python 3.13, whatever is first on PATH.
- No system environment variables (PATH) need to be changed.

---

## 2. Running tests

### From a terminal (Command Prompt / PowerShell)

Using `.venv\Scripts\python` means no activation is needed:

```bash
.venv\Scripts\python -m pytest                          # all tests
.venv\Scripts\python -m pytest -m smoke                 # only tests tagged smoke
.venv\Scripts\python -m pytest -m regression            # only regression tests
.venv\Scripts\python -m pytest tests\test_login.py      # one file
.venv\Scripts\python -m pytest -k checkout              # tests whose name contains "checkout"
.venv\Scripts\python -m pytest --headed                 # show the browser
.venv\Scripts\python -m pytest --headed --slowmo 500    # show the browser, slowed down (ms per action)
```

If the terminal prompt starts with `(.venv)`, the environment is active and plain `pytest ...` works.
To activate manually: `.venv\Scripts\activate`
(If PowerShell says "running scripts is disabled", use the full `.venv\Scripts\python -m pytest` form
or a Command Prompt terminal instead. No need to change Windows security settings.)

### From PyCharm

1. Settings → Project → Python Interpreter → select `.venv\Scripts\python.exe`.
2. Settings → Tools → Python Integrated Tools → Default test runner = **pytest**.
3. Click the green ▶ next to a test / at the top of a file, or right-click the `tests` folder → Run.
4. Headed mode: Run configuration dropdown → Edit Configurations → Additional Arguments: `--headed`.
   (For all new runs: Edit configuration templates → Python tests → pytest.)
5. Debug: click in the left margin to set a breakpoint, then choose Debug instead of Run.

Useful PyCharm shortcuts: **Shift Shift** = search everything; **Alt+F1** = Select In (e.g. open in Explorer).

### From a batch file (double-click)

Save as `run_tests.bat` in the project folder. `%*` passes extra options (e.g. `run_tests.bat -m smoke`).

```bat
@echo off
cd /d %~dp0
.venv\Scripts\python -m pytest %*
pause
```

### In CI (GitHub Actions)

Defined in `.github/workflows/tests.yml`. On every push / pull request to `main` it runs the suite on
a fresh Linux machine, once per browser (Chromium, Firefox, WebKit) in parallel.

- **See results:** repo page → **Actions** tab → click a run. Green ✔ / red ✘ per browser job.
  The badge at the top of the README shows the latest result.
- **Reports:** at the bottom of a run's page, under **Artifacts**: `report-<browser>` (HTML report, every run)
  and `test-results-<browser>` (screenshots / videos / traces, only when a test failed). Kept 14 days.
  Download, unzip, open `report.html`; open traces with `playwright show-trace`.
- **Run manually:** Actions tab → "Playwright Tests" → **Run workflow**.
- **Change browsers / OS:** edit the `matrix:` section of the workflow file
  (see "Cross-browser and cross-OS strategy" in [LEARNING_NOTES.md](LEARNING_NOTES.md)).
- CI installs the exact versions from `requirements.txt`, so keep it pinned and up to date (section 4).
- Free for public repositories.

---

## 3. Browsers

### Choosing a browser

| Command | Runs on |
|---|---|
| `pytest` | Chromium (default) |
| `pytest --browser firefox` | Firefox only |
| `pytest --browser webkit` | WebKit (Safari's engine) only |
| `pytest --browser chromium --browser firefox --browser webkit` | All three; each test runs once per browser |
| `pytest --browser-channel chrome` | Real installed Google Chrome |
| `pytest --browser-channel msedge` | Real installed Microsoft Edge |

Note: `--browser` is intentionally **not** set in `pytest.ini`. The option adds up, so setting it there
would add Chromium to every run, even `pytest --browser firefox`.

### Installing more browsers

Only Chromium is installed right now. To add the others (~200 MB):

```bash
.venv\Scripts\playwright install firefox webkit
```

Browsers are stored in `%LOCALAPPDATA%\ms-playwright`, shared by all projects on the machine.

### Auto-updates: Playwright browsers vs your own browsers

- **Playwright's browsers** (chromium / firefox / webkit) are separate copies, not your everyday browsers.
  Your browsers' auto-update does **not** change them. Each Playwright version comes with fixed,
  tested browser versions, so tests don't break overnight.
- **Real Chrome / Edge** (`--browser-channel`) auto-update as usual. Usually nothing breaks.
  Rarely, a very new Chrome needs a newer Playwright; then update Playwright (section 4).
- Unlike Selenium, there is no separate driver (ChromeDriver etc.) to keep in sync.

---

## 4. Updating Playwright and packages

Playwright releases roughly monthly. Update **on purpose** every month or two, then run the tests:

```bash
.venv\Scripts\python -m pip install -U playwright pytest-playwright pytest pytest-html
.venv\Scripts\playwright install chromium         # downloads browsers matching the new version
.venv\Scripts\python -m pytest                     # confirm everything still passes
```

(Add `firefox webkit` to the install command if those are installed.)

Check installed versions:

```bash
.venv\Scripts\python -m pip list
.venv\Scripts\playwright --version
```

### Pinning versions (recommended before publishing / CI)

`requirements.txt` currently lists packages without versions, so a fresh install gets whatever is newest
that day. Professional projects pin exact versions and update them deliberately:

```bash
.venv\Scripts\python -m pip freeze > requirements.txt
```

This writes lines like `playwright==1.65.2`. After a deliberate update (above), run it again and commit.

---

## 5. Reports, screenshots, logs

| What | Where | When |
|---|---|---|
| HTML report | `reports\report.html` | Every run (rebuilt each time); made by the **pytest-html** plugin |
| Error details / logs | PyCharm Run panel, and the expanded row in the HTML report | Every run |
| Screenshot (.png) | `test-results\<test-name>\` | Only for failed tests |
| Video (.webm) | `test-results\<test-name>\` | Only for failed tests |
| Trace (`trace.zip`) | `test-results\<test-name>\` | Only for failed tests |

These rules come from `pytest.ini` (`--screenshot=only-on-failure`, `--video=retain-on-failure`,
`--tracing=retain-on-failure`). `reports/` and `test-results/` are in `.gitignore`.

Open the report: double-click it in Explorer, or `start reports\report.html`.
(Don't use PyCharm's browser icons: they go through PyCharm's built-in web server and may show 404.)

Open a trace (timeline of every step with page snapshots, network, console):

```bash
.venv\Scripts\playwright show-trace test-results\<folder-name>\trace.zip
```

---

## 6. Recording locators: Codegen

Included with Playwright, nothing extra to install:

```bash
.venv\Scripts\playwright codegen https://www.saucedemo.com
```

- Opens a browser + the Playwright Inspector. Set **Target** to **Pytest**.
- **Pick locator** shows the best locator for any element you hover.
- Nothing is saved automatically; copy useful locators into the right Page Object.

---

## 7. Git

- Git is a local program; `git init` needs no account. GitHub (a website) is needed only to publish.
- Before the first commit, set the name/email that label your commits (not a login).
  GitHub offers a private "noreply" email so your real email isn't public:

```bash
git config --global user.name "Your Name"
git config --global user.email "your-noreply-address@users.noreply.github.com"
```

- `.gitignore` keeps `.venv/`, `reports/`, `test-results/`, caches and IDE settings out of the repo.

---

## 8. Troubleshooting

| Problem | Cause / fix |
|---|---|
| `pytest` not found | The terminal isn't using `.venv`. Use `.venv\Scripts\python -m pytest`, or set the PyCharm interpreter to `.venv` and open a **new** terminal tab. |
| PowerShell: "running scripts is disabled" | Activation script blocked by Windows policy. Use the full `.venv\Scripts\python -m pytest` form or a Command Prompt terminal. |
| PyCharm opens report as 404 | Built-in web server issue. Open the file from Explorer instead. |
| `Executable doesn't exist ... playwright install` | Browser for this Playwright version isn't downloaded. Run `.venv\Scripts\playwright install <browser>`. |
| PytestRemovedIn10Warning about `base_url` | Comes from the pytest-base-url plugin, not this code. Harmless; should disappear after a future plugin update. |
| Locator matches several elements (strict mode error) | Make the locator more specific: scope into a container or use `.filter(has_text=...)`. |

---

## 9. Machine notes (this PC)

- Several Python installs exist (3.14 default on PATH, python.org 3.13, Microsoft Store 3.13).
  This project uses python.org 3.13 via `.venv`. Other projects (e.g. `C:\projects\pyapp`,
  `PycharmProjects\JupyterProject`) have their own environments and are untouched.
- Important: a `.venv` is **not** a full copy of Python. It points back to the Python it was made from
  and stops working if that Python is uninstalled. Known links:

  | Environment | Built from |
  |---|---|
  | this project's `.venv` | python.org 3.13 (`AppData\Local\Programs\Python\Python313`) |
  | `C:\projects\pyapp\.venv` | Python 3.14 (`C:\Python314`) |
  | `PycharmProjects\JupyterProject\.venv` | Microsoft Store Python 3.13 |

- Possible future cleanup, in a safe order: first check which Python each project's `.venv` uses
  (the `home =` line in `.venv\pyvenv.cfg`), recreate any `.venv` on a Python you're keeping
  (`py -3.13 -m venv .venv` + reinstall its requirements), and only then uninstall unused Pythons and tidy PATH.
  Projects that run inside Docker don't depend on the Windows Pythons at all.
