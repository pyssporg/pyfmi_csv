"""Emit the FMI 2.0 ``modelDescription.xml`` for a CSV model.

The shared FMI emitter in ``pyfmi_interfaces`` owns the document when its
optional extra is installed. The package keeps a bundled writer for the
zero-dependency path: a user without the extra still gets a working FMU, and
the warning names the extra to install.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, cast
from xml.etree.ElementTree import Element, SubElement, tostring

from .model import CsvModelDescription

_DEFAULT_CSV_PATH_START = object()

_EXTRA_MISSING_MESSAGE = (
    "pyfmi_interfaces is not installed; pyfmu_csv is using its bundled "
    "modelDescription writer. Install the shared FMI emitter with "
    "`pip install pyfmu-csv[fmi]` to emit through pyfmi_interfaces."
)


def _shared_emitter() -> Any | None:
    """The optional emitter module, or ``None`` when the extra is absent."""
    try:
        import pyfmi_interfaces
    except ModuleNotFoundError as exc:
        if exc.name != "pyfmi_interfaces":
            raise
        return None
    return pyfmi_interfaces


def build_model_description_xml(
    model: CsvModelDescription,
    csv_path_start: object = _DEFAULT_CSV_PATH_START,
) -> str:
    if csv_path_start is _DEFAULT_CSV_PATH_START:
        csv_path_start = model.packaged_csv_path

    emitter = _shared_emitter()
    if emitter is None:
        warnings.warn(_EXTRA_MISSING_MESSAGE, RuntimeWarning, stacklevel=2)
        return _build_bundled_model_description_xml(model, csv_path_start)
    return _build_shared_model_description_xml(emitter, model, csv_path_start)


def _build_shared_model_description_xml(
    emitter: Any,
    model: CsvModelDescription,
    csv_path_start: object,
) -> str:
    """Render the document through the shared ``pyfmi_interfaces`` emitter.

    The shared API fixes ``modelName`` and ``modelIdentifier`` to the component
    name, so the component is named after the CSV model's sanitized identifier.
    """

    variables = [
        emitter.Variable(
            name=model.csv_path_parameter,
            type_name="String",
            causality="parameter",
            variability="tunable",
            value_reference=0,
            index=1,
            description=None,
            member=model.csv_path_parameter,
            start=None if csv_path_start is None else str(csv_path_start),
            start_text=None if csv_path_start is None else str(csv_path_start),
        )
    ]
    for signal in model.outputs:
        variables.append(
            emitter.Variable(
                name=signal.name,
                type_name=signal.signal_type.value,
                causality="output",
                variability=(
                    "continuous" if signal.signal_type.value == "Real" else "discrete"
                ),
                value_reference=signal.value_reference,
                index=signal.value_reference + 1,
                description=None,
                member=signal.name,
            )
        )

    component = emitter.Component(
        name=model.model_identifier,
        doc=None,
        parameters=(),
        ports=(),
        variables=tuple(variables),
        attributes=(),
    )
    reduction = emitter.Reduction(
        components=(component,),
        identity=emitter.ExportIdentity(system=model.model_name, direct=True),
        package="",
        experiment=None,
        root=None,
        attributes=(),
    )

    with TemporaryDirectory(prefix="pyfmu_csv_fmi_") as temporary_root:
        written = emitter.generate_model_description(reduction, Path(temporary_root))
        return written[0].read_text(encoding="utf-8")


def _build_bundled_model_description_xml(
    model: CsvModelDescription,
    csv_path_start: object,
) -> str:
    """The zero-dependency writer, kept for installations without the extra."""

    root = Element(
        "fmiModelDescription",
        {
            "fmiVersion": "2.0",
            "modelName": model.model_name,
            "guid": model.guid,
            "generationTool": "pyfmu-csv",
            "variableNamingConvention": "structured",
        },
    )
    SubElement(
        root,
        "CoSimulation",
        {
            "modelIdentifier": model.model_identifier,
            "canHandleVariableCommunicationStepSize": "true",
        },
    )

    model_variables = SubElement(root, "ModelVariables")
    csv_parameter = SubElement(
        model_variables,
        "ScalarVariable",
        {
            "name": model.csv_path_parameter,
            "valueReference": "0",
            "variability": "tunable",
            "causality": "parameter",
        },
    )
    csv_parameter_type = SubElement(csv_parameter, "String")
    if csv_path_start is not None:
        csv_parameter_type.set("start", cast(str, csv_path_start))

    for signal in model.outputs:
        variability = "continuous" if signal.signal_type.value == "Real" else "discrete"
        variable = SubElement(
            model_variables,
            "ScalarVariable",
            {
                "name": signal.name,
                "valueReference": str(signal.value_reference),
                "variability": variability,
                "causality": "output",
            },
        )
        SubElement(variable, signal.signal_type.value)

    model_structure = SubElement(root, "ModelStructure")
    outputs = SubElement(model_structure, "Outputs")
    for output_index, _signal in enumerate(model.outputs, start=2):
        SubElement(outputs, "Unknown", {"index": str(output_index)})

    xml_text = tostring(root, encoding="unicode")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_text
