# Git Practice: feature branch + a teammate's change + merge conflict

A hands-on exercise in this repository. **You** are a developer working on a feature branch.
**Claude** plays a teammate who merges a change into `main` while you're still working.
You then bring your branch up to date, resolve the conflict, and merge through a Pull Request (PR).

> **master vs main:** it's the same idea. `master` is the old default branch name; GitHub now creates
> `main`. This repository uses `main`, so read "master" as "main" everywhere.

Run all commands in a terminal in `C:\projects\playwright-portfolio`
(PyCharm's Terminal tab works). Run `git status` whenever you're unsure: it always tells you where you are.

---

## The picture

```
main:      A───B───────────C   (C = teammate's change, merged while you work)
                \
your branch:     D             (D = your commit)

after "git merge origin/main" on your branch:

main:      A───B───────────C
                \           \
your branch:     D───────────M  (M = merge commit, contains both changes)
```

The plan: both of you change **the same line** in `config.py` on purpose, so Git can't combine
them by itself → **merge conflict**, the thing to practice. The teammate also changes another file,
which Git will merge automatically.

---

## Step 0. Warm-up: start from an up-to-date `main`

This guide file is new and not committed yet. Commit it straight to `main` (fine for a doc in a solo repo):

```bash
git switch main                       # be on main
git pull                              # get the latest main from GitHub
git add docs/GIT_PRACTICE.md          # stage only this file
git commit -m "Add Git practice guide"
git push                              # send it to GitHub
```

---

## Step 1. Cut your feature branch

```bash
git switch -c feature/last-name-check   # -c = create a new branch from where you are (main) and switch to it
git branch                              # list branches; * marks the current one
```

Naming: `feature/...`, `fix/...`, `test/...` are common prefixes. The `/` is just part of the name.

---

## Step 2. Make your changes

**Change 1** in `config.py`: put your own first name in the test customer. Change this line:

```python
CUSTOMER = {"first_name": "Test", "last_name": "User", "postal_code": "12345"}
```
to:
```python
CUSTOMER = {"first_name": "Jane", "last_name": "User", "postal_code": "12345"}
```

**Change 2** in `tests/test_checkout.py`: add a new test at the end of the file:

```python
@pytest.mark.regression
def test_checkout_requires_last_name(logged_in_page, page):
    logged_in_page.add_to_cart("Sauce Labs Backpack")
    logged_in_page.open_cart()
    CartPage(page).checkout()

    checkout = CheckoutPage(page)
    checkout.fill_customer_info("Jane", "", "12345")

    expect(checkout.error_message).to_contain_text("Last Name is required")
```

Run the tests before committing (a developer's habit: never commit red tests):

```bash
.venv\Scripts\python -m pytest tests/test_checkout.py
```

---

## Step 3. Review and commit

```bash
git status                  # which files changed (red = not staged yet)
git diff                    # the exact lines you changed (press q to exit the viewer)
git add config.py tests/test_checkout.py
git status                  # now green = staged, will go into the commit
git commit -m "Add last name required checkout test"
git log --oneline -3        # your commit is on top
```

---

## Step 4. ⏸ Tell Claude: "teammate, your turn"

Claude will, from a separate copy of the repository (like a teammate's computer):
1. create its own branch from `main`,
2. change the **same `CUSTOMER` line** in `config.py` (a different first name and postal code),
3. add a line to `README.md`,
4. merge that branch into `main` and push it to GitHub.

Wait until Claude says it's done. Your computer knows nothing about it yet.

---

## Step 5. Push your branch and open a Pull Request

```bash
git push -u origin feature/last-name-check
```

- `-u` links your local branch to the GitHub branch, so next time plain `git push` / `git pull` work.
- **This push succeeds** even though `main` changed. A new branch on GitHub doesn't touch `main`.
  The conflict shows up when you try to **combine** your branch with `main`.

The output prints a link "Create a pull request for 'feature/last-name-check'". Open it
(or on GitHub: **Pull requests → New pull request**, base: `main`, compare: `feature/last-name-check`).
Click **Create pull request**.

GitHub will show: **"This branch has conflicts that must be resolved"** with `config.py` listed.
Leave the PR open and go back to the terminal.

---

## Step 6. Bring your branch up to date with `main` (and get the conflict)

```bash
git fetch origin                     # download what's new on GitHub; changes NOTHING in your files
git log --oneline --graph --all -8   # see the picture: origin/main moved ahead
git merge origin/main --no-edit      # combine main into your branch
```

Git reports:

```
Auto-merging README.md
CONFLICT (content): Merge conflict in config.py
Automatic merge failed; fix conflicts and then commit the result.
```

- `README.md` merged automatically: you changed different files/lines, so Git combined them by itself.
- `config.py` conflicts: you both changed the same line, and Git won't guess who is right.

`git status` now lists `config.py` under **"Unmerged paths"**.

---

## Step 7. Resolve the conflict

Open `config.py`. Git has written both versions into the file with markers:

```python
<<<<<<< HEAD
CUSTOMER = {"first_name": "Jane", "last_name": "User", "postal_code": "12345"}
=======
CUSTOMER = {"first_name": "...", "last_name": "User", "postal_code": "..."}
>>>>>>> origin/main
```

| Marker | Meaning |
|---|---|
| `<<<<<<< HEAD` to `=======` | **your** version (your branch) |
| `=======` to `>>>>>>> origin/main` | **their** version (main) |

Decide what the final line should be. It can be yours, theirs, or a mix. For example, keep your first name
and take the teammate's new postal code. Then **delete all three marker lines**, so only valid Python remains:

```python
CUSTOMER = {"first_name": "Jane", "last_name": "User", "postal_code": "<teammate's postal code>"}
```

> **Easier in PyCharm:** Git menu → **Resolve Conflicts…** → double-click `config.py`. A 3-pane window
> shows yours (left), the result (middle) and theirs (right). Click the `>>` / `<<` arrows to take a side,
> or edit the middle, then **Apply**. PyCharm removes the markers for you.

Then tell Git the conflict is solved, and finish the merge:

```bash
git add config.py              # "add" here means: this file is resolved
git status                     # "All conflicts fixed but you are still merging"
.venv\Scripts\python -m pytest # run ALL tests: a merge can break things even without conflicts
git commit --no-edit           # creates the merge commit with Git's default message
git log --oneline --graph -8   # see the merge commit joining both lines
```

Changed your mind in the middle? `git merge --abort` puts everything back to how it was before Step 6.

---

## Step 8. Push the fix and merge the PR

```bash
git push                       # updates your branch on GitHub (the PR updates by itself)
```

On the PR page:
- The conflict message is gone; it shows **"This branch has no conflicts with the base branch"**.
- CI (GitHub Actions) runs the tests on the PR. Wait for the green checks: that's the point of CI,
  nothing gets into `main` without passing tests.
- Click **Merge pull request** → **Confirm merge**, then **Delete branch** (deletes it on GitHub only).

---

## Step 9. Clean up locally

```bash
git switch main                          # back to main
git pull                                 # get the merged result from GitHub
git branch -d feature/last-name-check    # delete your local branch (-d refuses if it isn't merged: safe)
git fetch --prune                        # forget GitHub branches that no longer exist
git log --oneline --graph -10            # the full story
```

Done. That's the everyday team cycle: **branch → commit → push → PR → update from main → resolve → CI → merge → clean up.**

---

## Extra A: what if you had worked directly on `main`?

Without a branch, your `git push` would be **rejected**:

```
! [rejected]        main -> main (fetch first)
hint: Updates were rejected because the remote contains work that you do not have locally.
```

Git never overwrites a teammate's work on push. Fix: `git pull` (= fetch + merge), resolve any conflict the
same way as Step 7, then `git push`. **Never** use `git push --force` on a shared branch: it deletes
the teammate's commits from GitHub.

## Extra B: merge vs rebase

Instead of `git merge origin/main` (Step 6), some teams use:

```bash
git rebase origin/main
```

Rebase replays your commits **on top of** the new main, so history is a straight line with no merge commit.
Conflicts are resolved the same way, then `git add <file>` and `git rebase --continue`
(or `git rebase --abort` to cancel). Because it rewrites your commits, an already pushed branch then needs
`git push --force-with-lease`. Rule of thumb: **merge is safer and simpler; rebase gives cleaner history.**
Use whatever the team agrees on.

## Extra C: if a strange editor opens (Vim)

If you run `git commit` or `git merge` without a message, Git may open the **Vim** editor in the terminal.
To save and exit: press `Esc`, type `:wq`, press `Enter`. To exit without saving: `Esc`, `:q!`, `Enter`.
This guide uses `-m "..."` and `--no-edit` so that doesn't happen.

## Command cheat sheet

| Command | What it does |
|---|---|
| `git status` | Where am I, what's changed, what's staged |
| `git switch -c <name>` | Create a branch and switch to it |
| `git switch <name>` | Switch to an existing branch |
| `git branch` / `git branch -a` | List local / all (incl. GitHub) branches |
| `git diff` | Show unstaged changes |
| `git add <file>` | Stage a file (or mark a conflict as resolved) |
| `git commit -m "msg"` | Save staged changes as a commit |
| `git push -u origin <branch>` | First push of a new branch |
| `git fetch origin` | Download news from GitHub, don't change files |
| `git pull` | fetch + merge into the current branch |
| `git merge origin/main` | Merge GitHub's main into the current branch |
| `git merge --abort` | Cancel a merge in progress |
| `git log --oneline --graph --all` | History as a picture |
| `git branch -d <name>` | Delete a merged local branch |
