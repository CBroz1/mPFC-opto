"""Check that the installed distribution agrees with `pyproject.toml`."""

import tomllib
from importlib.metadata import version
from pathlib import Path

import pytest

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


@pytest.fixture(scope="session")
def declared_version():
    """Version as written in `pyproject.toml`."""
    with PYPROJECT.open("rb") as f:
        return tomllib.load(f)["project"]["version"]


@pytest.mark.unit
def test_installed_version_matches_pyproject(declared_version):
    """A stale editable install is the usual cause of a mismatch here."""
    assert version("mPFC-opto") == declared_version


@pytest.mark.unit
def test_package_imports():
    """Smoke test: the package and its three subpackages are importable."""
    import importlib

    for name in (
        "mpfc_opto",
        "mpfc_opto.glm",
        "mpfc_opto.behavior",
        "mpfc_opto.sleep",
    ):
        assert importlib.import_module(name) is not None
