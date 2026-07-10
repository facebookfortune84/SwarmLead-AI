from core.workflows.feedback_loop import FeedbackLoop


def test_feedback_loop_updates_weights(tmp_path):
    from core.prompts.adaptive_weights import AdaptiveWeightEngine

    loop = FeedbackLoop()

    loop.engine = AdaptiveWeightEngine(path=str(tmp_path / "weights.json"))

    result = loop.record_result(
        {"builder": 1.0},
        1.0,
    )

    assert result["updated"] is True
    assert "builder" in result["weights"]


def test_feedback_loop_get_weights(tmp_path):
    from core.prompts.adaptive_weights import AdaptiveWeightEngine

    loop = FeedbackLoop()

    loop.engine = AdaptiveWeightEngine(path=str(tmp_path / "weights.json"))

    loop.record_result({"planner": 1.0}, 1.0)

    weights = loop.get_weights()

    assert "planner" in weights


def test_feedback_loop_negative_score(tmp_path):
    from core.prompts.adaptive_weights import AdaptiveWeightEngine

    loop = FeedbackLoop()

    loop.engine = AdaptiveWeightEngine(path=str(tmp_path / "weights.json"))

    loop.record_result({"builder": 1.0}, 0.0)

    assert loop.get_weights()["builder"] < 0
