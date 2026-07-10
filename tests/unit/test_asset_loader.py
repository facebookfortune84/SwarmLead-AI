import json

from core.prompts.asset_loader import AssetLoader


def test_asset_loader_load(tmp_path):
    file = tmp_path / "optimized.json"

    data = {"archetypes": {"builder": [{"source": "test", "score": 10}]}}

    file.write_text(json.dumps(data))

    loader = AssetLoader(path=str(file))

    assert loader.get("builder")[0]["source"] == "test"


def test_asset_loader_missing_file():
    loader = AssetLoader(path="non_existent.json")

    assert loader.get("builder") == []


def test_asset_loader_build_context(tmp_path):
    file = tmp_path / "optimized.json"

    data = {"archetypes": {"builder": [{"source": "test", "score": 10}]}}

    file.write_text(json.dumps(data))

    loader = AssetLoader(path=str(file))

    context = loader.build_context({"builder": 0.8})

    assert "builder" in context
    assert "test" in context


def test_asset_loader_invalid_json(tmp_path):
    from core.prompts.asset_loader import AssetLoader

    file = tmp_path / "bad.json"
    file.write_text("INVALID JSON")

    loader = AssetLoader(path=str(file))

    assert loader.get("anything") == []


def test_asset_loader_supports_text_field(tmp_path):
    from core.prompts.asset_loader import AssetLoader

    file = tmp_path / "optimized.json"

    data = {"archetypes": {"builder": [{"text": "hello world", "score": 1}]}}

    file.write_text(json.dumps(data))

    loader = AssetLoader(path=str(file))

    context = loader.build_context({"builder": 1.0})

    assert "hello world" in context


def test_asset_loader_fallback_to_source(tmp_path):
    from core.prompts.asset_loader import AssetLoader

    file = tmp_path / "optimized.json"

    data = {"archetypes": {"builder": [{"source": "fallback text", "score": 1}]}}

    file.write_text(json.dumps(data))

    loader = AssetLoader(path=str(file))

    context = loader.build_context({"builder": 1.0})

    assert "fallback text" in context


def test_asset_loader_skips_empty_entries(tmp_path):
    from core.prompts.asset_loader import AssetLoader

    file = tmp_path / "optimized.json"

    data = {
        "archetypes": {
            "builder": [{"score": 1}]  # no text or source
        }
    }

    file.write_text(json.dumps(data))

    loader = AssetLoader(path=str(file))

    context = loader.build_context({"builder": 1.0})

    assert context == ""


def test_loader_handles_text(tmp_path):
    from core.prompts.asset_loader import AssetLoader

    f = tmp_path / "opt.json"
    f.write_text(json.dumps({"archetypes": {"builder": [{"text": "hello", "score": 1}]}}))

    loader = AssetLoader(path=str(f))
    ctx = loader.build_context({"builder": 1.0})

    assert "hello" in ctx


def test_loader_handles_source_fallback(tmp_path):
    from core.prompts.asset_loader import AssetLoader

    f = tmp_path / "opt.json"
    f.write_text(json.dumps({"archetypes": {"builder": [{"source": "fallback", "score": 1}]}}))

    loader = AssetLoader(path=str(f))
    ctx = loader.build_context({"builder": 1.0})

    assert "fallback" in ctx


def test_loader_skips_invalid_entry(tmp_path):
    from core.prompts.asset_loader import AssetLoader

    f = tmp_path / "opt.json"
    f.write_text(json.dumps({"archetypes": {"builder": [{"score": 1}]}}))

    loader = AssetLoader(path=str(f))
    ctx = loader.build_context({"builder": 1.0})

    assert ctx == ""
