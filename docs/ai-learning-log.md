# AI Learning Log

Each engineer records 2 learning cycles. Each cycle has: what I was trying to do, what went wrong or what I asked, what I learned, and how I checked it.

## Engineer A (kayla-source-cmd)

### Cycle 1: Not knowing how to use GitHub tools or merge a pull request

**What I was trying to do:** Get my storage work into `main` through a pull request.

**What went wrong:** I had little experience finding my way around GitHub (the Pull requests tab, Files changed, Review changes) and I did not know how to merge a pull request.

**What I learned:** A pull request is how work moves from a branch into `main`. A reviewer reads the Files changed tab, approves with Review changes, and then the pull request can be merged with the Merge pull request button.

**How I checked:** I merged PR #2 (my storage work) into `main`, and the page showed it as merged. I also reviewed Engineer B's PR #1 using the same steps.

### Cycle 2: Not knowing CLI commands and finding Python code hard to read

**What I was trying to do:** Run the project and review Engineer B's code from the command line.

**What went wrong:** I did not have experience with CLI commands, and I found it hard to read Python code.

**What I learned:** Running the tests with `python3 -m unittest discover -s tests -v` shows which tests pass. Reading code slowly, one function at a time, makes it easier to follow, and I can check what each import is used for.

**How I checked:** I ran the tests on Engineer B's branch and all 26 storage tests passed. While reading `storage.py` I noticed that `STATUS_APPROVED` was imported but never used, and I pointed it out in my review.

## Engineer B (odejeprince-cpu)

### Cycle 1: Terminal text pasted into a Python file

**What I was trying to do:** Add 2 new tests to `tests/test_workflow.py`.

**What went wrong:** After pasting the AI's code, the test run showed `SyntaxError: invalid character '➜'`. Only 31 tests ran instead of 39, and the workflow tests failed to load. The terminal prompt text had been copied into line 63 of the file along with the code.

**What I learned:** Python reads every character in a .py file, so anything that is not code breaks the whole file. When copying, I take only the code and never the terminal prompt. A traceback tells me the file name and line number, so I can go straight to the problem.

**How I checked:** I fixed the file and ran `python3 -m unittest discover -s tests -v` again. The count was still 37, so I ran `tail -n 15 tests/test_workflow.py` and saw the new tests were missing. I pasted the full file again and the run showed 39 tests, OK.

### Cycle 2: Pull blocked by uncommitted changes

**What I was trying to do:** After PR #4 was merged, update my local `main` with `git pull origin main`.

**What went wrong:** Git stopped with "Your local changes to the following files would be overwritten by merge: README.md". My local `main` had an uncommitted copy of the README.

**What I learned:** Git will not overwrite files that have unsaved changes. `git status` shows which files changed, and `git diff` shows exactly which lines changed. The same text was already saved in my merged PR, so the extra copy was safe to discard with `git restore README.md`.

**How I checked:** I read the `git diff` output first to confirm it was the same README text. After `git restore`, `git pull origin main` finished with "Fast-forward" and changed only README.md (61 insertions).