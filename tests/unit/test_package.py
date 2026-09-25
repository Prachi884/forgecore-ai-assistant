"""Smoke tests for the top-level forgecore package."""

from __future__ import annotations

import forgecore


class TestPackageMetadata:
    def test_version_is_string(self) -> None:
        assert isinstance(forgecore.__version__, str)
        assert len(forgecore.__version__.split(".")) == 3  # major.minor.patch

    def test_stage_is_positive_integer(self) -> None:
        assert isinstance(forgecore.__stage__, int)
        assert forgecore.__stage__ >= 1

    def test_stage_name_is_nonempty(self) -> None:
        assert isinstance(forgecore.__stage_name__, str)
        assert len(forgecore.__stage_name__) > 0

    def test_author_is_set(self) -> None:
        assert isinstance(forgecore.__author__, str)
        assert forgecore.__author__
