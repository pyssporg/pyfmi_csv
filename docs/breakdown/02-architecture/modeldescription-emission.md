---
id: INFO-004
type: info
title: modelDescription emission
summary: model_description.py emits through the optional pyfmi_interfaces [fmi] extra and falls back to the bundled zero-dependency writer.
date: 2026-11-22
status: current
---

# modelDescription emission

`src/pyfmi_csv/model_description.py` emits `modelDescription.xml` through
`pyfmi_interfaces` when its optional `[fmi]` extra is installed and falls back
to the bundled writer when it is not.

- **Ownership:** `CsvModelDescription` is the only input. The writer maps its
  parameter and outputs to `pyfmi_interfaces.Component`/`Variable` and calls
  `generate_model_description`, so variable order, names, value references,
  causality, variability, and `modelIdentifier` match the bundled writer.
- **Zero-dependency fallback:** a missing `pyfmi_interfaces` import warns with
  `pip install pyfmi-csv[fmi]` and uses the bundled writer, so packaging never
  requires the extra.
- **Known shared-emitter gaps:** `pyfmi_interfaces` fixes `modelName` to the
  component name (the sanitized `modelIdentifier`), derives its own uuid5 GUID,
  stamps `generationTool`/`generationDateAndTime`, emits `InitialUnknowns`, and
  omits `canHandleVariableCommunicationStepSize`. Those authoring attributes
  differ only on the shared path; the interface contract does not.
- **Evidence:** `tests/unit/test_model_description.py` checks the fallback and
  compares the shared and bundled interface contracts; the FMPy end-to-end
  tests pass on either path.
