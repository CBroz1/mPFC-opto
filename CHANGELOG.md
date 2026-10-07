# Change Log

This is a [changelog](https://keepachangelog.com/en/1.0.0/) designed to document
all notable changes to this project.

## [0.1.0] (Unreleased)

### Added

- Packaging: build backend, project metadata, and the full dependency list.
- `pytest` suite with a `--with-db` flag; database-backed tests are opt-in.
- `black` and `ruff` configuration, pre-commit hooks, and CI.
- `LICENSE`, `CHANGELOG.md`, `CONTRIBUTING.md`, and mkdocs sources.

### Changed

- `GLM`, `behavior`, and `sleep` are now subpackages of `mpfc_opto` rather than
  three top-level import names.
- Notebooks import the installed package instead of manipulating `sys.path`.

### Fixed

- `AS_EM_module` reached `FiltersEM` by a bare import that only resolved when
  the working directory happened to be `notebooks/`.
