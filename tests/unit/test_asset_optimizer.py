import json

from core.prompts.asset_optimizer import AssetOptimizer


def test_optimizer_runs(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()

    registry = {
        "generated_at": "now",
        "archetypes": {"builder": [{"source": "file1", "file": "path", "confidence": 100}]},
    }

    report = {
        "results": [
            {
                "source": "file1",
                "scores": {"builder": 1000},
            }
        ]
    }

    (raw / "archetype_registry.json").write_text(json.dumps(registry))
    (raw / "archetype_classification_report.json").write_text(json.dumps(report))

    optimizer = AssetOptimizer(
        input_dir=str(raw),
        output_dir=str(tmp_path / "out"),
    )

    result = optimizer.run()

    assert "builder" in result["archetypes"]


def test_optimizer_filters_low_confidence(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()

    registry = {
        "generated_at": "now",
        "archetypes": {"builder": [{"source": "file1", "file": "path", "confidence": 10}]},
    }

    report = {"results": []}

    (raw / "archetype_registry.json").write_text(json.dumps(registry))
    (raw / "archetype_classification_report.json").write_text(json.dumps(report))

    optimizer = AssetOptimizer(
        input_dir=str(raw),
        output_dir=str(tmp_path / "out"),
    )

    result = optimizer.run()

    assert "builder" not in result["archetypes"]


def test_optimizer_missing_report_entry(tmp_path):
    raw = tmp_path / "raw"
    raw.mkdir()

    registry = {
        "generated_at": "now",
        "archetypes": {"builder": [{"source": "file1", "file": "path", "confidence": 50}]},
    }

    # ✅ no matching report entry
    report = {"results": []}

    (raw / "archetype_registry.json").write_text(json.dumps(registry))
    (raw / "archetype_classification_report.json").write_text(json.dumps(report))

    optimizer = AssetOptimizer(
        input_dir=str(raw),
        output_dir=str(tmp_path / "out"),
    )

    result = optimizer.run()

    # ✅ should skip entry completely
    assert "builder" not in result["archetypes"]


def test_optimizer_extracts_prompt_text(tmp_path):
    import json

    from core.prompts.asset_optimizer import AssetOptimizer

    raw = tmp_path / "raw"
    raw.mkdir()

    dna_file = tmp_path / "dna.json"

    dna_file.write_text(
        json.dumps({"identity": {"role": "a test agent"}, "mission": {"primary": "test mission"}})
    )

    registry = {
        "generated_at": "now",
        "archetypes": {"builder": [{"source": "x", "file": str(dna_file), "confidence": 100}]},
    }

    report = {"results": [{"source": "x", "scores": {"builder": 100}}]}

    (raw / "archetype_registry.json").write_text(json.dumps(registry))
    (raw / "archetype_classification_report.json").write_text(json.dumps(report))

    optimizer = AssetOptimizer(
        input_dir=str(raw),
        output_dir=str(tmp_path / "out"),
    )

    result = optimizer.run()

    text = result["archetypes"]["builder"][0]["text"]

    assert "test agent" in text
    assert "test mission" in text


def test_optimizer_falls_back_to_source_when_file_missing(tmp_path):
    from core.prompts.asset_optimizer import AssetOptimizer

    raw = tmp_path / "raw"
    raw.mkdir()

    registry = {
        "generated_at": "now",
        "archetypes": {
            "builder": [
                {
                    "source": "fallback source text",
                    "file": "non_existent.json",
                    "confidence": 100,
                }
            ]
        },
    }

    report = {"results": [{"source": "fallback source text", "scores": {"builder": 100}}]}

    (raw / "archetype_registry.json").write_text(json.dumps(registry))
    (raw / "archetype_classification_report.json").write_text(json.dumps(report))

    optimizer = AssetOptimizer(
        input_dir=str(raw),
        output_dir=str(tmp_path / "out"),
    )

    result = optimizer.run()

    text = result["archetypes"]["builder"][0]["text"]

    assert "fallback source text" in text


def test_optimizer_skips_when_no_text_or_source(tmp_path):
    from core.prompts.asset_optimizer import AssetOptimizer

    raw = tmp_path / "raw"
    raw.mkdir()

    registry = {
        "generated_at": "now",
        "archetypes": {"builder": [{"file": None, "confidence": 100}]},
    }

    report = {"results": []}

    (raw / "archetype_registry.json").write_text(json.dumps(registry))
    (raw / "archetype_classification_report.json").write_text(json.dumps(report))

    optimizer = AssetOptimizer(
        input_dir=str(raw),
        output_dir=str(tmp_path / "out"),
    )

    result = optimizer.run()

    assert result["archetypes"] == {}


def test_optimizer_real_dna_extraction(tmp_path):
    from core.prompts.asset_optimizer import AssetOptimizer

    raw = tmp_path / "raw"
    raw.mkdir()

    dna_file = tmp_path / "dna.json"

    dna_file.write_text(
        json.dumps(
            {
                "identity": {"role": "test agent"},
                "mission": {"primary": "test mission"},
                "capabilities": ["coding"],
            }
        )
    )

    registry = {
        "generated_at": "now",
        "archetypes": {
            "builder": [
                {
                    "source": "fallback",
                    "file": str(dna_file),
                    "confidence": 100,
                }
            ]
        },
    }

    report = {"results": [{"source": "fallback", "scores": {"builder": 100}}]}

    (raw / "archetype_registry.json").write_text(json.dumps(registry))
    (raw / "archetype_classification_report.json").write_text(json.dumps(report))

    optimizer = AssetOptimizer(
        input_dir=str(raw),
        output_dir=str(tmp_path / "out"),
    )

    result = optimizer.run()

    text = result["archetypes"]["builder"][0]["text"]

    assert "test agent" in text
    assert "test mission" in text
    assert "coding" in text


def test_optimizer_fallback_source(tmp_path):
    from core.prompts.asset_optimizer import AssetOptimizer

    raw = tmp_path / "raw"
    raw.mkdir()

    registry = {
        "generated_at": "now",
        "archetypes": {"builder": [{"source": "fallback", "file": "bad.json", "confidence": 100}]},
    }

    report = {"results": [{"source": "fallback", "scores": {"builder": 100}}]}

    (raw / "archetype_registry.json").write_text(json.dumps(registry))
    (raw / "archetype_classification_report.json").write_text(json.dumps(report))

    opt = AssetOptimizer(input_dir=str(raw), output_dir=str(tmp_path / "out"))
    result = opt.run()

    assert "fallback" in result["archetypes"]["builder"][0]["text"]
