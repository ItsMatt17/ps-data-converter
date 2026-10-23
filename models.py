from typing import List, Optional

from pydantic import BaseModel


class Measurement(BaseModel):
    type: str = "isotopic_ratio"
    value: float
    error: float
    isotopic_ratio: str


class CRE(BaseModel):
    correction: str = "Not Corrected"
    value: Optional[str] = None


class Sample(BaseModel):
    name: str
    type: str
    classification: str
    warren_class: Optional[str] = None
    parent_body: str
    original_table: str
    cre: CRE
    measurements: List[Measurement] = []


class Publication(BaseModel):
    title: str
    doi: str
    citation: str
    standard: str
    error_type: str
    samples: List[Sample] = []
