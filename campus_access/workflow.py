"""Workflow layer (Engineer B): approve, issue, return.

Every function validates and checks the status BEFORE changing anything,
so a failed operation leaves the stored record exactly as it was.
"""

from campus_access import storage
from campus_access.constants import (
    STATUS_APPROVED,
    STATUS_ISSUED,
    STATUS_REQUESTED,
    STATUS_RETURNED,
)
from campus_access.validation import validate_approver

# Each status maps to the ONLY status it may move to. returned is final.
TRANSITIONS = {
    STATUS_REQUESTED: STATUS_APPROVED,
    STATUS_APPROVED: STATUS_ISSUED,
    STATUS_ISSUED: STATUS_RETURNED,
}


def _require_status(record, expected, action):
    """Raise ValueError unless the record is in the expected status."""
    if record["status"] != expected:
        raise ValueError(
            "Cannot %s %s: status is '%s', expected '%s'."
            % (action, record["id"], record["status"], expected)
        )


def approve_request(request_id, approved_by):
    """requested -> approved. Needs a non-blank approver ID."""
    approved_by = validate_approver(approved_by)
    record = storage.get_request(request_id)
    _require_status(record, STATUS_REQUESTED, "approve")
    return storage.update_request(
        request_id, status=TRANSITIONS[STATUS_REQUESTED], approved_by=approved_by
    )


def issue_card(request_id):
    """approved -> issued. Only allowed when approved_by is non-empty."""
    record = storage.get_request(request_id)
    _require_status(record, STATUS_APPROVED, "issue")
    if not record["approved_by"]:
        raise ValueError("Cannot issue %s: no approver recorded." % request_id)
    return storage.update_request(request_id, status=TRANSITIONS[STATUS_APPROVED])


def return_card(request_id):
    """issued -> returned. Returned is final."""
    record = storage.get_request(request_id)
    _require_status(record, STATUS_ISSUED, "return")
    return storage.update_request(request_id, status=TRANSITIONS[STATUS_ISSUED])