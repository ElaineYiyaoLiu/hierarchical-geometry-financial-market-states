from branch_b.paired import paired_replicate_contrasts


def test_paired_contrast_is_computed_at_replicate_level():
    out = paired_replicate_contrasts(
        {"r1": 0.75, "r2": 0.50},
        {"r1": 0.25, "r2": 0.50},
    )
    assert out == {"r1": 0.5, "r2": 0.0}
