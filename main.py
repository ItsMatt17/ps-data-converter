import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, List, Optional

from pydantic import BaseModel
from rich import print

FILE: Path = Path("xml") / "Spitzer_et_al_2025.xml"

data = []
samples = []


class Measurement(BaseModel):
    type: str = "isotopic_ratio"
    value: float
    error: float
    isotopic_ratio: str


class Sample(BaseModel):
    name: str
    type: str
    classification: str
    warren_class: Optional[str] = None
    parent_body: str
    measurements: List[Measurement] = []


class Publication(BaseModel):
    name: str
    doi: str
    citation: str
    standard: str
    error_type: str
    samples: List[Sample] = []


def g(sample, name, tag1=None, tag2=None):
    return sample.get((name, tag1, tag2), None)


def main():
    print("--- Starting Parsing ---")
    tree = ET.parse(FILE)
    root = tree.getroot()

    for item in root.iterfind(".//item"):
        sample = {}

        for p in item.iterfind(".//property"):
            key = (p.get("name"), p.get("tag1"), p.get("tag2"))
            if key in sample:
                raise Exception(f"Overwriting key value in sample: {key}")
            sample[key] = p.text or ""

        data.append(sample)

    for sample in data:

        s = Sample(
            name=g(sample, "sample name"),
            type=g(sample, "Type"),
            warren_class=g(sample, "Warren class"),
            parent_body=g(sample, "Parent body"),
            classification=g(sample, "Classification"),
        )

        measurements = filter(
            lambda k: k[0] in ["mu", "epsilon"] and k[2] in ["value", "error"],
            sample.keys(),
        )

        unique_isotopes = set([m[1] for m in measurements])

        for iso in unique_isotopes:
            s.measurements.append(
                Measurement(
                    isotopic_ratio=iso,
                    value=g(sample, "mu", iso, "value"),
                    error=g(sample, "mu", iso, "error"),
                )
            )

        samples.append(s)

    pub = Publication(
        name=g(data[0], "note", "W", "Title"),
        citation=g(data[0], "note", "W", "Citation"),
        doi=g(data[0], "note", "W", "DOI"),
        standard=g(data[0], "note", "W", "Standard"),
        error_type=g(data[0], "note", "W", "Error type"),
        samples=samples,
    )

    print(pub.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
