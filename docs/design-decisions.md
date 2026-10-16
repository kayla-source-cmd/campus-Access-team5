# Design Decisions

## 1. Who checks the workflow order

`update_request` in storage.py does not check workflow order. It only changes `status` and `approved_by`, and it accepts any valid status.

The transition checks (requested -> approved -> issued -> returned) are enforced in workflow.py (Engineer B). `approve_request`, `issue_card` and `return_card` each validate the input, check the current status, and only then call `update_request`.

## 2. A failed operation leaves the record unchanged

All checks run before anything is written. If any check fails, a `ValueError` is raised and `update_request` is never called, so the stored record is exactly as it was. The tests compare the record before and after each failed action.

## 3. Errors use ValueError

Every module reports problems with `ValueError`. The CLI catches it and prints the message, so the user sees a clear message and the app keeps running.

## 4. "returned" is final

There is no way out of "returned". Returning twice, or issuing after a return, is rejected. Skipping a step (for example issuing before approval) is also rejected.

## 5. Request IDs

IDs look like A001, A002 and use ASCII digits only, so look-alike digits from other scripts are rejected. After a file is loaded, the next ID continues after the highest ID in the file, so IDs stay unique across restarts.

## 6. Safe saving and loading

`load_requests` and `save_requests` validate the whole file before accepting it. A malformed file is rejected with a `ValueError`, and a half-valid file loads nothing. A bad file never replaces good data, and it is never replaced with empty data.

At startup, if the data file is corrupt, the CLI stops and leaves the file untouched.

## 7. Copies, not references

`get_request` returns a copy of the record, so code outside storage.py cannot change stored data by accident.

## 8. Standard library only

The app uses only the Python standard library. It is a command-line app, not a web app.

## Ownership

- Engineer A (kayla-source-cmd): constants.py, validation.py, storage.py, tests/test_storage.py, design docs
- Engineer B (odejeprince-cpu): workflow.py, cli.py, tests/test_workflow.py, tests/test_cli.py