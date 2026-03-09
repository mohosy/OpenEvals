from openevals_runner.scoring import normalize_judge_score, weighted_average


def test_normalize_judge_score_maps_1_to_5_into_zero_to_one() -> None:
    assert normalize_judge_score(1) == 0
    assert normalize_judge_score(3) == 0.5
    assert normalize_judge_score(5) == 1


def test_weighted_average_uses_weights() -> None:
    assert weighted_average([(0.0, 1), (1.0, 3)]) == 0.75

