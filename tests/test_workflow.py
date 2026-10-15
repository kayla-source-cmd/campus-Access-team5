import unittest

from campus_access import storage, workflow


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        storage.reset_requests()
        self.rid = storage.create_request("F001", "visitor")["id"]

    def test_full_workflow(self):
        self.assertEqual(workflow.approve_request(self.rid, "M01")["status"], "approved")
        self.assertEqual(workflow.issue_card(self.rid)["status"], "issued")
        record = workflow.return_card(self.rid)
        self.assertEqual(record["status"], "returned")
        self.assertEqual(record["approved_by"], "M01")

    def test_issue_before_approval_is_rejected_and_record_unchanged(self):
        before = storage.get_request(self.rid)
        with self.assertRaises(ValueError):
            workflow.issue_card(self.rid)
        self.assertEqual(storage.get_request(self.rid), before)

    def test_blank_approver_is_rejected_and_record_unchanged(self):
        before = storage.get_request(self.rid)
        for bad in ("", "   "):
            with self.assertRaises(ValueError):
                workflow.approve_request(self.rid, bad)
        self.assertEqual(storage.get_request(self.rid), before)

    def test_return_before_issue_is_rejected(self):
        workflow.approve_request(self.rid, "M01")
        before = storage.get_request(self.rid)
        with self.assertRaises(ValueError):
            workflow.return_card(self.rid)
        self.assertEqual(storage.get_request(self.rid), before)

    def test_double_return_and_issue_after_return_are_rejected(self):
        workflow.approve_request(self.rid, "M01")
        workflow.issue_card(self.rid)
        workflow.return_card(self.rid)
        before = storage.get_request(self.rid)
        with self.assertRaises(ValueError):
            workflow.return_card(self.rid)
        with self.assertRaises(ValueError):
            workflow.issue_card(self.rid)
        self.assertEqual(storage.get_request(self.rid), before)

    def test_cannot_approve_twice(self):
        workflow.approve_request(self.rid, "M01")
        with self.assertRaises(ValueError):
            workflow.approve_request(self.rid, "M02")
        self.assertEqual(storage.get_request(self.rid)["approved_by"], "M01")

    def test_unknown_and_malformed_ids_are_rejected(self):
        for bad in ("A999", "X001", "A00١", ""):
            with self.assertRaises(ValueError):
                workflow.approve_request(bad, "M01")


if __name__ == "__main__":
    unittest.main()