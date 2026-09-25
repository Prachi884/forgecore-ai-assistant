"""Unit tests for forgecore.utils.paths."""

from __future__ import annotations

from pathlib import Path

import pytest

from forgecore.utils.paths import (
    DATA_DIR,
    ENV_FILE,
    PROJECT_ROOT,
    RAW_DOCS_DIR,
    SETTINGS_FILE,
    ensure_directory,
    find_project_root,
)


class TestFindProjectRoot:
    def test_returns_path_with_pyproject_toml(self) -> None:
        """The resolved root must be a directory that contains pyproject.toml."""
        root = find_project_root()
        assert isinstance(root, Path)
        assert (root / "pyproject.toml").is_file()

    def test_finds_root_when_started_deep(self) -> None:
        """Searching from a nested path still resolves to the same root."""
        deep_start = PROJECT_ROOT / "src" / "forgecore" / "utils"
        assert find_project_root(deep_start) == PROJECT_ROOT


class TestProjectPaths:
    def test_project_root_exists(self) -> None:
        assert PROJECT_ROOT.is_dir()

    def test_data_dir_points_inside_project(self) -> None:
        assert DATA_DIR.parent == PROJECT_ROOT

    def test_raw_docs_dir_inside_data_dir(self) -> None:
        assert RAW_DOCS_DIR.parent == DATA_DIR

    @pytest.mark.parametrize(
        "path_attr,expected_name",
        [
            (DATA_DIR, "data"),
            (RAW_DOCS_DIR, "raw"),
            (SETTINGS_FILE, "settings.yaml"),
            (ENV_FILE, ".env"),
        ],
    )
    def test_path_naming(self, path_attr: Path, expected_name: str) -> None:
        assert path_attr.name == expected_name


class TestEnsureDirectory:
    def test_creates_missing_directory(self, tmp_path: Path) -> None:
        target = tmp_path / "a" / "b" / "c"
        assert not target.exists()
        result = ensure_directory(target)
        assert result == target
        assert target.is_dir()

    def test_is_idempotent_on_existing_directory(self, tmp_path: Path) -> None:
        existing = tmp_path / "already_here"
        existing.mkdir()
        # Should not raise.
        result = ensure_directory(existing)
        assert result == existing
        assert existing.is_dir()
