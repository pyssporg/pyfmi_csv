# pyfmi_csv

`pyfmi_csv` generates FMI 2.0 Co-Simulation FMU packages from CSV-described signals using a hybrid toolchain:

- Python handles CSV inspection, FMU metadata generation, and packaging.
- C++ provides the reusable runtime artifact that executes inside the FMU host.

The current product can:

- inspect a CSV header and assign FMI value references
- read header type annotations with `Real` fallback
- generate `modelDescription.xml` plus package metadata
- assemble a zipped `.fmu` artifact
- build a reusable FMI 2.0 Co-Simulation shared library
- expose the FMI 2.0 C API for initialization, stepping, and value access
- embed the compiled runtime into `binaries/<platform>/<modelIdentifier>`
- run the generated FMU through FMPy using the packaged CSV fallback or an explicit `csv_path` override
- optionally omit the source CSV from the packaged FMU and provide `csv_path` externally
- validate the generated artifact structurally with FMPy

The current chain works end to end after the native runtime has been built.

Supported output types today:

- `Real`
- `Integer`
- `Boolean`
- `String`

## Requirements

- Python 3.11 or newer.
- For a source build: Git with submodules, CMake 3.21 or newer, and a C++17
  compiler. The published wheel has no build toolchain requirement.

## Quick Install

This is the main usage path. Install the published wheel and use the bundled runtime
without cloning the repo or building the source tree.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install https://github.com/pyssporg/pyfmi_csv/releases/latest/download/pyfmi_csv-0-py3-none-linux_x86_64.whl
```

After installation, the CLI and bundled runtime are ready to use:

```bash
pyfmi-csv --help
pyfmi-csv generate-fmu \
  --input-csv samples/signals.csv \
  --output CsvSignals.fmu \
  --model-name CsvSignals
```

This published wheel path is currently for Linux and is tagged `py3-none-linux_x86_64`.

`samples/signals.csv` ships in the source checkout. When you install only the
wheel, point `--input-csv` at any CSV whose first column is `time`.

If the published wheel does not match your platform or Python version, use the
[Build From Source](docs/build-from-source.md) guide instead.

## Generate An FMU

Generate an FMU from a CSV file:

```bash
pyfmi-csv generate-fmu \
  --input-csv samples/signals.csv \
  --output CsvSignals.fmu \
  --model-name CsvSignals
```

Add `--no-copy-csv` if you want to omit the CSV from the FMU and set `csv_path` externally before initialization.

Inspect the CSV-to-VR mapping:

```bash
pyfmi-csv inspect-csv \
  --input-csv samples/signals.csv \
  --model-name CsvSignals
```

## Optional Shared FMI Emitter

The package installs with no third-party runtime dependency. Install the `fmi`
extra to emit `modelDescription.xml` through the shared `pyfmi_interfaces`
emitter:

```bash
python -m pip install "pyfmi_csv[fmi]"
```

Without the extra, packaging keeps working through the bundled writer and warns
with this same install command.

## Build From Source

Everything in the source workflow lives in the dedicated guide:

- [Build From Source](docs/build-from-source.md)
- [Testing](docs/testing.md)

## Development

```bash
git submodule update --init --recursive

# The editable install bundles the native runtime, so build it first.
cmake -S . -B build
cmake --build build

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt

python -m pytest          # the CI selection after the native build
ruff check src tests      # configured in pyproject.toml, not ruff.toml
```

Contributor rules, package layout, and native prerequisites are in
[AGENTS.md](AGENTS.md).

## Documentation

- [Overview](docs/overview.md)
- [Architecture](docs/architecture.md)
- [Build From Source](docs/build-from-source.md)
- [Usage](docs/usage.md)
- [Testing](docs/testing.md)
- [Limitations](docs/limitations.md)
- [Localization Notes](docs/localization.md)
- [Contributor rules](AGENTS.md)
