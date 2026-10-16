"""Command-line menu (Engineer B)."""

from campus_access import storage, workflow
from campus_access.constants import DEFAULT_PATH

MENU = """
=== Campus Access ===
1. Create request
2. View request
3. Approve request
4. Issue card
5. Return card
6. List requests
7. Save to file
8. Load from file
9. Quit
"""


def _show(record):
    print("  ID:          %s" % record["id"])
    print("  Fellow ID:   %s" % record["fellow_id"])
    print("  Card type:   %s" % record["card_type"])
    print("  Status:      %s" % record["status"])
    print("  Approved by: %s" % record["approved_by"])


def _create():
    fellow_id = input("Fellow ID: ")
    card_type = input("Card type (visitor/student/staff): ").strip().lower()
    record = storage.create_request(fellow_id, card_type)
    print("Created:")
    _show(record)


def _view():
    _show(storage.get_request(input("Request ID: ").strip()))


def _approve():
    request_id = input("Request ID: ").strip()
    approver = input("Approver ID: ")
    print("Approved:")
    _show(workflow.approve_request(request_id, approver))


def _issue():
    print("Issued:")
    _show(workflow.issue_card(input("Request ID: ").strip()))


def _return():
    print("Returned:")
    _show(workflow.return_card(input("Request ID: ").strip()))


def _list():
    records = storage.list_requests()
    if not records:
        print("No requests yet.")
    for record in records:
        print("%s | %s | %s | %s | %s" % (
            record["id"], record["fellow_id"], record["card_type"],
            record["status"], record["approved_by"]))


def _quit(path):
    """Offer to save, then leave. Returns after the user has answered."""
    try:
        answer = input("Save before quitting? (y/n): ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        answer = "n"
    if answer == "y":
        try:
            storage.save_requests(path)
            print("Saved to %s." % path)
        except (ValueError, OSError) as error:
            print("Could not save: %s" % error)
    print("Goodbye.")


def run_menu(path=DEFAULT_PATH):
    """Main loop. Bad input prints a helpful message and lets the user retry."""
    try:
        storage.load_requests(path)
    except FileNotFoundError:
        pass  # first run: start empty
    except ValueError as error:
        # Never continue with empty data: a later save would overwrite the bad file.
        print("Cannot start: %s" % error)
        print("Nothing was changed. Fix or move the file, then run again.")
        return

    actions = {
        "1": _create, "2": _view, "3": _approve, "4": _issue,
        "5": _return, "6": _list,
        "7": lambda: (storage.save_requests(path), print("Saved to %s." % path)),
        "8": lambda: (storage.load_requests(path), print("Loaded from %s." % path)),
    }

    while True:
        print(MENU)
        try:
            choice = input("Choose an option (1-9): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            choice = "9"

        if choice == "9":
            _quit(path)
            return
        if choice not in actions:
            print("Invalid option '%s'. Please enter a number from 1 to 9." % choice)
            continue
        try:
            actions[choice]()
        except (ValueError, OSError) as error:
            print("Error: %s" % error)
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.")