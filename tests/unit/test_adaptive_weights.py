from core.prompts.adaptive_weights import AdaptiveWeightEngine


def test_weight_engine_load_empty(tmp_path):
    engine = AdaptiveWeightEngine(path=str(tmp_path / "weights.json"))

    result = engine.get({"builder": 1.0})

    assert "builder" in result


def test_weight_update(tmp_path):
    file = tmp_path / "weights.json"

    engine = AdaptiveWeightEngine(path=str(file))

    engine.update({"builder": 1.0}, 0.8)

    assert file.exists()


def test_weight_adjustment(tmp_path):
    file = tmp_path / "weights.json"

    engine = AdaptiveWeightEngine(path=str(file))

    engine.update({"builder": 1.0}, 1.0)

    updated = engine.get({"builder": 1.0})

    assert updated["builder"] >= 1.0


def test_weight_clamping(tmp_path):
    from core.prompts.adaptive_weights import AdaptiveWeightEngine

    engine = AdaptiveWeightEngine(path=str(tmp_path / "w.json"))

    # push beyond upper bound
    for _ in range(20):
        engine.update({"builder": 1.0}, 1.0)

    assert engine.weights["builder"] <= 0.5

    # push below lower bound
    for _ in range(20):
        engine.update({"builder": 1.0}, 0.0)

    assert engine.weights["builder"] >= -0.5


def test_weight_engine_applies_only_known_keys(tmp_path):
    from core.prompts.adaptive_weights import AdaptiveWeightEngine

    engine = AdaptiveWeightEngine(path=str(tmp_path / "w.json"))

    # learned weight for unknown key
    engine.weights = {"unknown": 0.5}

    result = engine.get({"builder": 1.0})

    # ✅ should NOT apply unknown key
    assert "builder" in result
    assert result["builder"] == 1.0


def test_weight_engine_empty_base(tmp_path):
    from core.prompts.adaptive_weights import AdaptiveWeightEngine

    engine = AdaptiveWeightEngine(path=str(tmp_path / "w.json"))

    engine.weights = {"builder": 0.5}

    result = engine.get({})  # ✅ empty base

    assert result == {}


def test_weight_engine_no_weights(tmp_path):
    from core.prompts.adaptive_weights import AdaptiveWeightEngine

    engine = AdaptiveWeightEngine(path=str(tmp_path / "w.json"))

    # ✅ weights are empty (default case)
    result = engine.get({"builder": 1.0})

    assert result["builder"] == 1.0
