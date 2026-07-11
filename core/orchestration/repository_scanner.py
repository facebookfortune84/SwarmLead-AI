from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class RepositoryScanResult:
    root: str
    files: List[str] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)


class RepositoryScanner:
    def scan(
        self,
        root: str,
    ) -> RepositoryScanResult:

        root_path = Path(root)

        if not root_path.exists():
            return RepositoryScanResult(
                root=root,
            )

        files: List[str] = []
        directories: List[str] = []

        for item in root_path.rglob("*"):
            relative = item.relative_to(root_path).as_posix()

            if item.is_dir():
                directories.append(relative)

            elif item.is_file():
                files.append(relative)

        return RepositoryScanResult(
            root=root,
            files=sorted(files),
            directories=sorted(directories),
        )

    def file_count(
        self,
        result: RepositoryScanResult,
    ) -> int:
        return len(result.files)

    def directory_count(
        self,
        result: RepositoryScanResult,
    ) -> int:
        return len(result.directories)

    def summary(
        self,
        result: RepositoryScanResult,
    ) -> Dict:
        return {
            "root": result.root,
            "files": len(result.files),
            "directories": len(result.directories),
        }
