# AGENTS

## Vision first (required)

Before you read code, edit files, or plan a change, read the project vision:

**`docs/breakdown/00-intent/intent.md`**

It states why this repository exists, what it commits to, and what it refuses to
become. It is the first document to read, not a reference of last resort.

- Read it in full before making any change to code, tests, docs, or artifacts.
- Judge every proposed change against it. If a change conflicts with the vision,
  its commitments, goals, or non-goals, stop and surface the conflict; do not
  implement it silently.
- If the work shows the long-term direction is wrong, change the vision
  deliberately first, then the code. Never let the repository drift away from
  its stated intent.

## Rules

1. **Don't assume. Surface tradeoffs.** If a contract is ambiguous, stop and say
   so rather than picking a behaviour silently.
2. **Minimum code that solves the problem.** Nothing speculative.
3. **Touch only what you must.** Clean up only your own mess.
4. **Define success criteria and verify.**

## Repository Focus

`pyfmu_csv` turns a CSV-described signal set into a packaged FMI 2.0
Co-Simulation FMU. It reads the CSV header to build a parser-free
`CsvModelDescription`, emits `modelDescription.xml`, stages the package layout,
and zips the `.fmu`. It does not parse SysML and emits no SysML artifacts.

- Input: a CSV file whose first column is `time` and whose remaining header
  names carry optional `:Real`, `:Integer`, `:Boolean`, or `:String` types.
- Outputs: `modelDescription.xml`, `resources/model.json`, an optional copy of
  the source CSV under `resources/data/`, and the native runtime binary under
  `binaries/<platform>/`.
- Current state lives in `docs/breakdown/`; the code is the source of truth
  when the two disagree.

## Hard constraints

- **Zero-dependency core.** The Python package installs and packages FMUs with
  no third-party runtime dependency. `pyfmi_interfaces` is an optional `[fmi]`
  extra, imported lazily; without it the bundled XML writer keeps working.
- **One model description per build.** `CsvModelDescription` is the only input
  of the XML writer, and variable order, names, value references, causality,
  variability, and `modelIdentifier` are preserved whichever writer is used.
- **The generated artifact is the unit under test.** Assertions run against
  the emitted XML or the packed `.fmu`, not an intermediate string.
- **Deterministic output.** The GUID is the stable uuid5 of the model name, and
  archive order is sorted.
- **Do not edit generated files by hand.** Change the CSV model, the writer, or
  the template, then regenerate.
- **One runtime per package.** The C++ runtime in `runtime/` is built once and
  copied into each FMU; the package does not generate model C++ sources.

## Code guidelines

- Keep changes direct and explicit. Minimize duplication without hiding the
  data flow behind abstractions.
- Keep error messages naming the input, its owner, and the path involved.
- Preserve the zero-dependency path whenever an optional integration is added.
- Treat interfaces as pre-1.0: clarity outranks compatibility shims.

## Conventions

- `README.md` is the landing page; `docs/breakdown/` holds current state.
- `docs/breakdown/` follows the product-breakdown skill. Set
  `PB=<skills-dir>/product-breakdown/scripts/pb` and pass
  `--root docs/breakdown` to every command:
  - current state lives in layer leaves, in the present tense;
  - regenerate the generated registers with `python3 $PB registers --root
    docs/breakdown`; never edit them by hand;
  - run `python3 $PB check --strict --root docs/breakdown` and
    `python3 $PB node-size --strict --root docs/breakdown` after edits.
- Version lives in `python/pyfmu_csv/__init__.py` only; `pyproject.toml` is
  dynamic and has no `[project].version`.

## Environment

- Python >= 3.11; a C++17 compiler, `cmake`, and `ninja` build the native
  runtime.
- `python3 -m venv .venv`, `source .venv/bin/activate`,
  `pip install -e ".[dev]"`.
- Native build: `cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release` then
  `cmake --build build`; native tests: `ctest --test-dir build --output-on-failure`.
- Tests: `python -m pytest`; the full suite includes the FMPy end-to-end checks
  when the native runtime has been built.
- Lint: `ruff check python tests`.
- Build: `python -m build --wheel --sdist`.
