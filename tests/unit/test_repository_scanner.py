from core.orchestration.repository_scanner import (
    RepositoryScanner,
    RepositoryScanResult,
)


def test_scan_missing_directory():
    scanner = RepositoryScanner()

    result = scanner.scan("__definitely_missing__")

    assert result.files == []
    assert result.directories == []


def test_scan_empty_directory(tmp_path):
    scanner = RepositoryScanner()

    result = scanner.scan(str(tmp_path))

    assert result.files == []
    assert result.directories == []


def test_scan_single_file(tmp_path):
    scanner = RepositoryScanner()

    (tmp_path / "test.py").write_text("x")

    result = scanner.scan(str(tmp_path))

    assert result.files == ["test.py"]


def test_scan_directory(tmp_path):
    scanner = RepositoryScanner()

    (tmp_path / "subdir").mkdir()

    result = scanner.scan(str(tmp_path))

    assert result.directories == ["subdir"]


def test_scan_nested_structure(tmp_path):
    scanner = RepositoryScanner()

    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)

    (nested / "demo.py").write_text("x")

    result = scanner.scan(str(tmp_path))

    assert "a" in result.directories
    assert "a/b" in result.directories
    assert "a/b/demo.py" in result.files


def test_file_count(tmp_path):
    scanner = RepositoryScanner()

    (tmp_path / "one.py").write_text("1")
    (tmp_path / "two.py").write_text("2")

    result = scanner.scan(str(tmp_path))

    assert scanner.file_count(result) == 2


def test_directory_count(tmp_path):
    scanner = RepositoryScanner()

    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()

    result = scanner.scan(str(tmp_path))

    assert scanner.directory_count(result) == 2


def test_summary(tmp_path):
    scanner = RepositoryScanner()

    (tmp_path / "x.py").write_text("x")
    (tmp_path / "folder").mkdir()

    result = scanner.scan(str(tmp_path))

    summary = scanner.summary(result)

    assert summary["files"] == 1
    assert summary["directories"] == 1


def test_repository_scan_result_dataclass():
    result = RepositoryScanResult(root="repo")

    assert result.root == "repo"
    assert result.files == []
    assert result.directories == []
