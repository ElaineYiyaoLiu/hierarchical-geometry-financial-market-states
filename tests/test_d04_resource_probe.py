"""The development resource guard must stop when live monitoring is lost."""
import json
import sys
import unittest
from unittest.mock import Mock, patch

from branch_b.benchmarks import d04_resource_probe as probe


class ResourceMonitorTests(unittest.TestCase):
    def test_unavailable_preflight_starts_no_worker(self):
        with patch.object(sys, "argv", ["probe", "--output", "unused.json"]), \
                patch.object(probe, "current_rss", return_value=None), \
                patch.object(probe.subprocess, "Popen") as start:
            with self.assertRaisesRegex(RuntimeError, "no workers started"):
                probe.main()
            start.assert_not_called()

    def test_lost_live_worker_monitor_terminates_and_reaps(self):
        child = Mock(pid=123, returncode=-15)
        child.poll.return_value = None
        child.communicate.return_value = ("", "")
        with patch.object(probe.subprocess, "Popen", return_value=child), \
                patch.object(probe, "current_rss", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "worker memory monitoring"):
                probe.probe(probe.Path("unused"), probe.CASES[0], 10, 384 * 1024**2, 2)
        child.terminate.assert_called_once()
        child.communicate.assert_called_once_with(timeout=2)

    def test_worker_exit_during_sample_preserves_completed_result(self):
        child = Mock(pid=123, returncode=0)
        child.poll.side_effect = [None, 0, 0]
        child.communicate.return_value = (json.dumps({"outcome": "COMPLETED_EXACT"}), "")
        with patch.object(probe.subprocess, "Popen", return_value=child), \
                patch.object(probe, "current_rss", return_value=None), \
                patch.object(probe.time, "sleep"):
            result = probe.probe(probe.Path("unused"), probe.CASES[0], 10, 384 * 1024**2, 2)
        self.assertEqual(result["outcome"], "COMPLETED_EXACT")
        child.terminate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
