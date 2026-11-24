# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.12] - 2026-11-23

### Added

- `--no-copy-csv` on `create-fmu-skeleton` and `generate-fmu`: omit the source
  CSV from the package and set `csv_path` externally before initialization.
- Optional shared FMI emitter: the `fmi` extra installs
  `pyfmi-interfaces>=0.5.1` and emits `modelDescription.xml` through it;
  without the extra the bundled writer is used, with a warning.
- A `tests` CI workflow that builds the native runtime, runs the native tests,
  lints, and runs the Python suite on Python 3.11 and 3.12.
- `AGENTS.md` contributor rules and the `docs/breakdown/` product tree.

### Changed

- Adopted the `src/` layout: the Python package moved to `src/pyfmi_csv/` and
  the native runtime to `src/runtime/`.
- The version is dynamic from `pyfmi_csv.__version__`, the minimum Python is
  3.11, and the ruff and pytest configuration lives in `pyproject.toml`.
- Wheel builds always bundle the native runtime and fail when it is missing,
  instead of silently skipping it.
- `csv_path` accepts relative paths: checked as written first, then against the
  FMU `resources/` directory.

### Fixed

- `csv_path` is declared with `variability="fixed"` instead of `tunable`,
  matching a value read once during initialization.
- The runtime loads the CSV during `initialize()` instead of while reading the
  resource location, so an external `csv_path` override takes effect before the
  data is read.
- The `csv_path` parameter always emits its `String` type element, with `start`
  set only when a default exists.

