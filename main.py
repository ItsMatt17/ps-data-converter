import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, List, Optional

from rich import print

from models import *

FILE: Path = Path("xml") / "Kruijer_et_al_2022.xml"

# Constants
UNITS = ["mu", "epsilon"]


data = []
samples = []


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

        # Assuming that there's only one CRE data point.
        cre_data = list(
            filter(
                lambda k: k[0] == "CRE",
                sample.keys(),
            )
        )

        if not cre_data:
            cre = CRE()
        else:
            # This will give me tag1="..."
            correction_type = cre_data[0][1]
            cre = CRE(
                correction=correction_type, value=g(sample, "CRE", correction_type)
            )

        s = Sample(
            name=g(sample, "sample name"),
            type=g(sample, "Type"),
            warren_class=g(sample, "Warren class"),
            parent_body=g(sample, "Parent body"),
            classification=g(sample, "Classification"),
            original_table=g(sample, "Original Table"),
            cre=cre,
        )

        measurements = filter(
            lambda k: k[0] in UNITS and k[2] in ["value", "error"],
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
        title=g(data[0], "note", "W", "Title"),
        citation=g(data[0], "note", "W", "Citation"),
        doi=g(data[0], "note", "W", "DOI"),
        standard=g(data[0], "note", "W", "Standard"),
        error_type=g(data[0], "note", "W", "Error type"),
        samples=samples,
    )

    json_pub = pub.model_dump_json(indent=None)

    with open(f"output/{FILE.with_suffix('.json').name}", "w+") as f:
        f.write(json_pub)

    print(json_pub)


if __name__ == "__main__":
    main()
