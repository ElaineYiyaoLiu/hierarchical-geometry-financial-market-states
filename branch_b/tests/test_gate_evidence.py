"""Development tests for the non-authorizing Branch B evidence checker.

Run only with the project-required Python 3.14 interpreter.
"""
import unittest

from branch_b.tools.check_gate_evidence import REQUIREMENTS, inspect


class GateEvidenceTests(unittest.TestCase):
    def test_missing_evidence_is_unverified(self):
        report = inspect({})
        for gate, keys in REQUIREMENTS.items():
            self.assertEqual(report[gate]["documented"], [])
            self.assertEqual(report[gate]["unverified"], list(keys))
            self.assertFalse(report[gate]["evidence_complete"])
            self.assertEqual(report[gate]["authorization"], "NOT_GRANTED_BY_THIS_TOOL")

    def test_true_without_reference_is_not_enough(self):
        report = inspect({
            "gate_5a": {
                "bounded_revision_approved": {"verified": True},
                "revision_checksums_frozen": {
                    "verified": True, "evidence_ref": "   "
                },
            }
        })
        self.assertIn("bounded_revision_approved", report["gate_5a"]["unverified"])
        self.assertIn("revision_checksums_frozen", report["gate_5a"]["unverified"])

    def test_complete_assertions_still_do_not_authorize(self):
        gate = "gate_5a"
        entries = {
            key: {"verified": True, "evidence_ref": "reviewed-record"}
            for key in REQUIREMENTS[gate]
        }
        report = inspect({gate: entries})[gate]
        self.assertTrue(report["evidence_complete"])
        self.assertEqual(report["authorization"], "NOT_GRANTED_BY_THIS_TOOL")

    def test_unexpected_values_do_not_pass(self):
        report = inspect({
            "gate_5a": {
                "bounded_revision_approved": {
                    "verified": "true", "evidence_ref": "record"
                }
            },
            "pilot_exit": "approved",
        })
        self.assertIn("bounded_revision_approved", report["gate_5a"]["unverified"])
        self.assertFalse(report["pilot_exit"]["evidence_complete"])


if __name__ == "__main__":
    unittest.main()
