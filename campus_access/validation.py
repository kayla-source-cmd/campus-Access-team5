"""Pure validation helpers. They raise ValueError and never change any data."""

import re

from campus_access.constants import CARD_TYPES, ID_PREFIX, ID_MIN_DIGITS, STATUSES

# [0-9] matches only ASCII digits (unlike \d or str.isdigit, which accept
# other Unicode numerals). fullmatch checks the whole string.
_ID_PATTERN = re.compile(re.escape(ID_PREFIX) + r"[0-9]{%d,}" % ID_MIN_DIGITS)


def validate_fellow_id(fellow_id):
    """Return the fellow ID without surrounding spaces, or raise ValueError."""
    if not isinstance(fellow_id, str):
        raise ValueError("Fellow ID must be text.")
    cleaned = fellow_id.strip()
    if not cleaned:
        raise ValueError("Fellow ID cannot be blank.")
    return cleaned


def validate_card_type(card_type):
    """Return the card type if it is allowed, or raise ValueError."""
    if not isinstance(card_type, str):
        raise ValueError("Card type must be text.")
    if card_type not in CARD_TYPES:
        raise ValueError(
            "Invalid card type '%s'. Allowed: %s." % (card_type, ", ".join(CARD_TYPES))
        )
    return card_type


def validate_request_id(request_id):
    """Return the request ID if it looks like A001, A002, ... or raise ValueError."""
    if not isinstance(request_id, str):
        raise ValueError("Request ID must be text.")
    if not _ID_PATTERN.fullmatch(request_id):
        raise ValueError(
            "Malformed request ID '%s'. Expected something like A001." % request_id
        )
    return request_id


def validate_approver(approved_by):
    """Return the approver ID without surrounding spaces, or raise ValueError."""
    if not isinstance(approved_by, str):
        raise ValueError("Approver ID must be text.")
    cleaned = approved_by.strip()
    if not cleaned:
        raise ValueError("Approver ID cannot be blank.")
    return cleaned


def validate_status(status):
    """Return the status if it is one of the known statuses, or raise ValueError."""
    if status not in STATUSES:
        raise ValueError("Invalid status '%s'." % (status,))
    return status