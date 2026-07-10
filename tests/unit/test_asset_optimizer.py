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


def test_optimizer_dna_full_field_coverage(tmp_path):
    import json

    from core.prompts.asset_optimizer import AssetOptimizer

    raw = tmp_path / "raw"
    raw.mkdir()

    dna = tmp_path / "dna.json"

    dna.write_text(
        json.dumps(
            {
                "identity": {"role": "architect"},
                "mission": {"primary": "build"},
                "topology": {"domains": ["realms2riches.com"]},
                "reasoning_framework": ["explore"],
                "capabilities": ["coding"],
                "communication_policy": {"collaborates_with": ["Builder"]},
                "constraints": ["policy"],
                "governance": {
                    "evidence_required": True,
                    "audit_logging": True,
                },
            }
        )
    )

    registry = {
        "generated_at": "now",
        "archetypes": {
            "builder": [
                {
                    "source": "x",
                    "file": str(dna),
                    "confidence": 100,
                }
            ]
        },
    }

    report = {
        "results": [
            {
                "source": "x",
                "scores": {"builder": 100},
            }
        ]
    }

    (raw / "archetype_registry.json").write_text(json.dumps(registry))
    (raw / "archetype_classification_report.json").write_text(json.dumps(report))

    opt = AssetOptimizer(
        input_dir=str(raw),
        output_dir=str(tmp_path / "out"),
    )

    result = opt.run()

    text = result["archetypes"]["builder"][0]["text"]

    assert "architect" in text
    assert "build" in text
    assert "realms2riches.com" in text
    assert "explore" in text
    assert "coding" in text
    assert "Builder" in text
    assert "policy" in text
    assert "evidence_required" in text


def test_optimizer_extract_prompt_exception(tmp_path):
    from core.prompts.asset_optimizer import AssetOptimizer

    raw = tmp_path / "raw"
    raw.mkdir()

    (raw / "archetype_registry.json").write_text('{"generated_at":"x","archetypes":{}}')

    (raw / "archetype_classification_report.json").write_text('{"results":[]}')

    opt = AssetOptimizer(
        input_dir=str(raw),
        output_dir=str(tmp_path / "out"),
    )

    result = opt._extract_prompt_from_dna("does_not_exist.json")

    assert result == ""


def test_optimizer_get_report_miss(tmp_path):
    from core.prompts.asset_optimizer import AssetOptimizer

    raw = tmp_path / "raw"
    raw.mkdir()

    (raw / "archetype_registry.json").write_text('{"generated_at":"x","archetypes":{}}')

    (raw / "archetype_classification_report.json").write_text('{"results":[]}')

    opt = AssetOptimizer(input_dir=str(raw), output_dir=str(tmp_path / "out"))
    assert opt._get_report("missing") is None


def test_optimizer_skips_empty_prompt_after_fallback(tmp_path):
    import json

    from core.prompts.asset_optimizer import AssetOptimizer

    raw = tmp_path / "raw"
    raw.mkdir()

    registry = {
        "generated_at": "now",
        "archetypes": {
            "builder": [
                {
                    "source": "",
                    "file": None,
                    "confidence": 100,
                }
            ]
        },
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
