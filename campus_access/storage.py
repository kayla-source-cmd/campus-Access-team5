"""Storage layer (Engineer A): creating, reading, updating, saving, loading requests."""

import json
import os

from campus_access.constants import (
    DEFAULT_PATH,
    ID_MIN_DIGITS,
    ID_PREFIX,
    REQUEST_FIELDS,
    STATUS_REQUESTED,
)
from campus_access.validation import (
    validate_approver,
    validate_card_type,
    validate_fellow_id,
    validate_request_id,
    validate_status,
)

# The one place where all requests live: {"A001": {...}, "A002": {...}}
_requests = {}


def reset_requests():
    """Empty the in-memory storage (used by tests)."""
    _requests.clear()


def _next_id():
    """Next ID, based on the highest number in use, so it survives a reload."""
    highest = 0
    for request_id in _requests:
        highest = max(highest, int(request_id[len(ID_PREFIX):]))
    return "%s%0*d" % (ID_PREFIX, ID_MIN_DIGITS, highest + 1)


def create_request(fellow_id, card_type):
    """Validate input, then create and store a new request. Returns a copy."""
    fellow_id = validate_fellow_id(fellow_id)
    card_type = validate_card_type(card_type)

    request_id = _next_id()
    record = {
        "id": request_id,
        "fellow_id": fellow_id,
        "card_type": card_type,
        "status": STATUS_REQUESTED,
        "approved_by": None,
    }
    _requests[request_id] = record
    return dict(record)


def get_request(request_id):
    """Return a COPY of one request. Raises ValueError if malformed or unknown."""
    validate_request_id(request_id)
    if request_id not in _requests:
        raise ValueError("Request '%s' not found." % request_id)
    return dict(_requests[request_id])


def list_requests():
    """Return copies of all requests, sorted by ID."""
    return [dict(_requests[key]) for key in sorted(_requests)]


def update_request(request_id, **fields):
    """The only way to change a stored request. Only 'status' and 'approved_by'
    may be changed. Everything is checked BEFORE the record is touched."""
    validate_request_id(request_id)
    if request_id not in _requests:
        raise ValueError("Request '%s' not found." % request_id)

    allowed = {"status", "approved_by"}
    unknown = set(fields) - allowed
    if unknown:
        raise ValueError("Cannot update field(s): %s." % ", ".join(sorted(unknown)))
    if not fields:
        raise ValueError("Nothing to update.")

    new_values = {}
    if "status" in fields:
        new_values["status"] = validate_status(fields["status"])
    if "approved_by" in fields:
        new_values["approved_by"] = validate_approver(fields["approved_by"])

    _requests[request_id].update(new_values)
    return dict(_requests[request_id])


def save_requests(path=DEFAULT_PATH):
    """Save all requests to a JSON file. Writes to a temporary file first, so a
    failed save never destroys an existing valid file."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    temp_path = path + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as file:
            json.dump(list_requests(), file, indent=2)
        os.replace(temp_path, path)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def _check_record(record):
    """Validate one record from a file. Returns a clean dict or raises ValueError."""
    if not isinstance(record, dict):
        raise ValueError("Each saved request must be an object.")
    if set(record) != set(REQUEST_FIELDS):
        raise ValueError("A saved request has missing or extra fields.")

    clean = {
        "id": validate_request_id(record["id"]),
        "fellow_id": validate_fellow_id(record["fellow_id"]),
        "card_type": validate_card_type(record["card_type"]),
        "status": validate_status(record["status"]),
        "approved_by": record["approved_by"],
    }

    if clean["status"] == STATUS_REQUESTED:
        if clean["approved_by"] is not None:
            raise ValueError("Request %s: 'requested' cannot have an approver." % clean["id"])
    else:
        clean["approved_by"] = validate_approver(clean["approved_by"])
    return clean


def load_requests(path=DEFAULT_PATH):
    """Load requests from a JSON file. Everything is validated first; the
    in-memory data is replaced only if the whole file is valid.
    Raises FileNotFoundError if the file is missing, ValueError if it is bad."""
    with open(path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError as error:
            raise ValueError("File is not valid JSON: %s" % error)

    if not isinstance(data, list):
        raise ValueError("The file must contain a list of requests.")

    loaded = {}
    for record in data:
        clean = _check_record(record)
        if clean["id"] in loaded:
            raise ValueError("Duplicate request ID %s in file." % clean["id"])
        loaded[clean["id"]] = clean

    _requests.clear()
    _requests.update(loaded)