"""Verify the delivered public fixture bytes and real loader failure behavior."""
from branch_b.integration.week10.verify import verify


def test_week10_handoff_fixtures_and_boundary_examples():
    result=verify()
    assert result['valid_observable_files']==9
    assert result['negative_loader_cases']==7
    assert result['scientific_authorization'] is False
