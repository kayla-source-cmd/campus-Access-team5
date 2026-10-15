import json
import os
import tempfile
import unittest
from unittest.mock import patch

from campus_access import storage


def good_record(request_id="A001", status="requested", approved_by=None):
    return {
        "id": request_id,
        "fellow_id": "F001",
        "card_type": "visitor",
        "status": status,
        "approved_by": approved_by,
    }


class StorageTestCase(unittest.TestCase):
    """Base class: empty storage and a private temporary folder for every test."""

    def setUp(self):
        storage.reset_requests()
        self.tmp = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.tmp.name, "requests.json")

    def tearDown(self):
        self.tmp.cleanup()

    def write_json(self, data):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(data, file)

    def write_text(self, text):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write(text)


class CreateRequestTests(StorageTestCase):
    def test_valid_creation_has_all_five_fields(self):
        record = storage.create_request("F001", "visitor")
        self.assertEqual(record, {
            "id": "A001",
            "fellow_id": "F001",
            "card_type": "visitor",
            "status": "requested",
            "approved_by": None,
        })

    def test_ids_increase(self):
        self.assertEqual(storage.create_request("F001", "visitor")["id"], "A001")
        self.assertEqual(storage.create_request("F002", "student")["id"], "A002")

    def test_all_card_types_are_accepted(self):
        for card_type in ("visitor", "student", "staff"):
            storage.create_request("F001", card_type)
        self.assertEqual(len(storage.list_requests()), 3)

    def test_blank_fellow_id_is_rejected_and_nothing_is_stored(self):
        for bad in ("", "   "):
            with self.assertRaises(ValueError):
                storage.create_request(bad, "visitor")
        self.assertEqual(storage.list_requests(), [])

    def test_invalid_card_type_is_rejected_and_nothing_is_stored(self):
        with self.assertRaises(ValueError):
            storage.create_request("F001", "alien")
        self.assertEqual(storage.list_requests(), [])

    def test_wrong_input_types_are_rejected(self):
        with self.assertRaises(ValueError):
            storage.create_request(123, "visitor")
        with self.assertRaises(ValueError):
            storage.create_request("F001", None)
        self.assertEqual(storage.list_requests(), [])


class LookupAndUpdateTests(StorageTestCase):
    def test_get_request_returns_a_copy(self):
        storage.create_request("F001", "visitor")
        copy = storage.get_request("A001")
        copy["status"] = "returned"
        self.assertEqual(storage.get_request("A001")["status"], "requested")

    def test_unknown_id_is_rejected(self):
        with self.assertRaises(ValueError):
            storage.get_request("A999")

    def test_malformed_ids_are_rejected(self):
        storage.create_request("F001", "visitor")
        # "A00١" and "A００１" contain non-ASCII digits and must be refused
        for bad in ("", "a001", "A1", "X001", "A00١", "A００１", "A001 ", None, 1):
            with self.assertRaises(ValueError, msg=repr(bad)):
                storage.get_request(bad)

    def test_update_with_blank_approver_leaves_record_unchanged(self):
        storage.create_request("F001", "visitor")
        before = storage.get_request("A001")
        with self.assertRaises(ValueError):
            storage.update_request("A001", status="approved", approved_by="  ")
        self.assertEqual(storage.get_request("A001"), before)

    def test_update_cannot_change_protected_fields(self):
        storage.create_request("F001", "visitor")
        before = storage.get_request("A001")
        with self.assertRaises(ValueError):
            storage.update_request("A001", id="A002")
        with self.assertRaises(ValueError):
            storage.update_request("A001", card_type="staff")
        self.assertEqual(storage.get_request("A001"), before)


class SaveAndLoadTests(StorageTestCase):
    def test_round_trip_keeps_all_data(self):
        storage.create_request("F001", "visitor")
        storage.update_request("A001", status="approved", approved_by="M01")
        expected = storage.list_requests()
        storage.save_requests(self.path)
        storage.reset_requests()
        storage.load_requests(self.path)
        self.assertEqual(storage.list_requests(), expected)

    def test_new_id_after_reload_is_a002_not_a001(self):
        storage.create_request("F001", "visitor")
        storage.save_requests(self.path)
        storage.reset_requests()
        storage.load_requests(self.path)
        self.assertEqual(storage.create_request("F002", "staff")["id"], "A002")

    def test_next_id_follows_highest_id_in_file(self):
        self.write_json([good_record("A005")])
        storage.load_requests(self.path)
        self.assertEqual(storage.create_request("F002", "staff")["id"], "A006")

    def test_missing_file_raises_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            storage.load_requests(self.path)

    def test_empty_file_is_rejected(self):
        self.write_text("")
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_corrupted_json_is_rejected(self):
        self.write_text("{ this is not json")
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_wrong_top_level_type_is_rejected(self):
        self.write_json({"A001": good_record()})
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_missing_key_is_rejected(self):
        record = good_record()
        del record["status"]
        self.write_json([record])
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_extra_key_is_rejected(self):
        record = good_record()
        record["extra"] = "surprise"
        self.write_json([record])
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_duplicate_ids_are_rejected(self):
        self.write_json([good_record("A001"), good_record("A001")])
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_invalid_status_is_rejected(self):
        self.write_json([good_record(status="flying")])
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_inconsistent_approver_is_rejected(self):
        # requested must not have an approver; approved/issued/returned must
        self.write_json([good_record(status="requested", approved_by="M01")])
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)
        self.write_json([good_record(status="approved", approved_by=None)])
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)

    def test_bad_file_does_not_wipe_existing_records(self):
        storage.create_request("F001", "visitor")
        before = storage.list_requests()
        self.write_text("{ not json")
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)
        self.assertEqual(storage.list_requests(), before)

    def test_half_valid_file_loads_nothing(self):
        storage.create_request("F001", "visitor")
        before = storage.list_requests()
        self.write_json([good_record("A007"), {"id": "A008"}])
        with self.assertRaises(ValueError):
            storage.load_requests(self.path)
        self.assertEqual(storage.list_requests(), before)

    def test_failed_save_does_not_overwrite_a_valid_file(self):
        storage.create_request("F001", "visitor")
        storage.save_requests(self.path)
        with open(self.path, encoding="utf-8") as file:
            original = file.read()

        storage.create_request("F002", "staff")
        with patch("campus_access.storage.json.dump", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                storage.save_requests(self.path)

        with open(self.path, encoding="utf-8") as file:
            self.assertEqual(file.read(), original)
        self.assertFalse(os.path.exists(self.path + ".tmp"))


if __name__ == "__main__":
    unittest.main()