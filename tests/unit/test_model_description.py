from __future__ import annotations

import pytest

from pyfmi_csv.csv_model import load_csv_model
from pyfmi_csv.model_description import build_model_description_xml


def test_model_description_declares_csv_path_parameter_and_outputs(tmp_path) -> None:
    csv_path = tmp_path / "signals.csv"
    csv_path.write_text("time,temperature,pressure\n0,1,2\n", encoding="utf-8")

    model = load_csv_model(csv_path, "DemoModel")
    xml = build_model_description_xml(model)

    assert 'modelName="DemoModel"' in xml
    assert 'name="csv_path"' in xml
    assert 'start="data/signals.csv"' in xml
    # Initialization configuration: read once in initialize(), never retuned.
    assert 'variability="fixed"' in xml
    assert 'causality="parameter"' in xml
    assert 'name="temperature"' in xml
    assert 'valueReference="1"' in xml
    assert "<Outputs>" in xml


def test_model_description_can_omit_packaged_csv_start_value(tmp_path) -> None:
    csv_path = tmp_path / "signals.csv"
    csv_path.write_text("time,temperature,pressure\n0,1,2\n", encoding="utf-8")

    model = load_csv_model(csv_path, "DemoModel")
    xml = build_model_description_xml(model, csv_path_start=None)

    assert 'name="csv_path"' in xml
    assert "<String" in xml
    assert 'start="data/signals.csv"' not in xml


def test_model_description_emits_supported_scalar_types(tmp_path) -> None:
    csv_path = tmp_path / "signals.csv"
    csv_path.write_text(
        "time,temperature,count:Integer,enabled:Boolean,mode:String\n0,1.0,2,true,auto\n",
        encoding="utf-8",
    )

    model = load_csv_model(csv_path, "TypedModel")
    xml = build_model_description_xml(model)

    assert '<Real />' in xml or "<Real/>" in xml
    assert '<Integer />' in xml or "<Integer/>" in xml
    assert '<Boolean />' in xml or "<Boolean/>" in xml
    assert '<String />' in xml or "<String/>" in xml


def _interface_contract(xml_text: str) -> tuple[object, ...]:
    from xml.etree import ElementTree as ET

    root = ET.fromstring(xml_text)
    interface = root.find("CoSimulation")
    variables = []
    for variable in root.findall("./ModelVariables/ScalarVariable"):
        type_element = next(iter(variable))
        variables.append(
            (
                variable.get("name"),
                variable.get("valueReference"),
                variable.get("causality"),
                variable.get("variability"),
                type_element.tag,
                type_element.get("start"),
            )
        )
    output_indexes = [
        unknown.get("index")
        for unknown in root.findall("./ModelStructure/Outputs/Unknown")
    ]
    return (
        interface.get("modelIdentifier") if interface is not None else None,
        tuple(variables),
        tuple(output_indexes),
    )


def test_build_falls_back_to_bundled_writer_without_the_extra(tmp_path, monkeypatch) -> None:
    from pyfmi_csv import model_description

    csv_path = tmp_path / "signals.csv"
    csv_path.write_text("time,temperature,count:Integer\n0,1,2\n", encoding="utf-8")
    model = load_csv_model(csv_path, "DemoModel")

    monkeypatch.setattr(model_description, "_shared_emitter", lambda: None)
    with pytest.warns(RuntimeWarning, match=r"pyfmi-csv\[fmi\]"):
        xml = model_description.build_model_description_xml(model)

    assert xml == model_description._build_bundled_model_description_xml(
        model, model.packaged_csv_path
    )


def test_shared_emitter_matches_the_bundled_interface_contract(tmp_path) -> None:
    from pyfmi_csv import model_description

    pytest.importorskip("pyfmi_interfaces")
    csv_path = tmp_path / "signals.csv"
    csv_path.write_text(
        "time,temperature,count:Integer,enabled:Boolean,mode:String\n0,1.0,2,true,auto\n",
        encoding="utf-8",
    )
    model = load_csv_model(csv_path, "Demo Model")

    shared = model_description.build_model_description_xml(model)
    bundled = model_description._build_bundled_model_description_xml(
        model, model.packaged_csv_path
    )

    assert _interface_contract(shared) == _interface_contract(bundled)
    assert model.model_identifier == "Demo_Model"
