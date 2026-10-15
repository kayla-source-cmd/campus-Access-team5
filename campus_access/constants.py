"""Shared constants for the Campus Access project."""

CARD_TYPES = ("visitor", "student", "staff")

STATUS_REQUESTED = "requested"
STATUS_APPROVED = "approved"
STATUS_ISSUED = "issued"
STATUS_RETURNED = "returned"
STATUSES = (STATUS_REQUESTED, STATUS_APPROVED, STATUS_ISSUED, STATUS_RETURNED)

REQUEST_FIELDS = ("id", "fellow_id", "card_type", "status", "approved_by")

ID_PREFIX = "A"
ID_MIN_DIGITS = 3

DEFAULT_PATH = "data/requests.json"