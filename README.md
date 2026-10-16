# Campus Access - The Engineering Challenge

A Python command-line app that manages campus access-card requests. It uses only the Python standard library.

## Team

- Engineer A (kayla-source-cmd): constants.py, validation.py, storage.py, tests/test_storage.py, design docs
- Engineer B (odejeprince-cpu): workflow.py, cli.py, tests/test_workflow.py, tests/test_cli.py

## How it works

Each request has: id, fellow_id, card_type (visitor, student or staff), status and approved_by.

Request IDs look like A001, A002, and so on. They stay unique after the app is closed and reopened.

A request moves through these statuses in order, with no skipping:

requested -> approved -> issued -> returned

"returned" is the final status. If an action fails, the record is left unchanged.

## Run the app

```
python3 main.py
```

## Menu

1. Create request
2. View request
3. Approve request
4. Issue card
5. Return card
6. List requests
7. Save to file
8. Load from file
9. Quit

Wrong input shows a helpful message and lets you try again.

## Saved data

Requests are saved as JSON in `data/requests.json`. If the file is malformed, the app rejects it with a clear message and never replaces it with empty data.

## Run the tests

```
python3 -m unittest discover -s tests -v
```

## Project layout

- `main.py`: starts the menu
- `campus_access/constants.py`: shared constants
- `campus_access/validation.py`: input checks
- `campus_access/storage.py`: creating, updating, saving and loading requests
- `campus_access/workflow.py`: approve, issue and return rules
- `campus_access/cli.py`: the menu
- `tests/`: unit tests
- `docs/`: design decisions and AI learning log