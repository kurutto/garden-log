from pydantic import BaseModel


class SVGDataSchema(BaseModel):
    viewBox: str
    elements: list[dict]


class FarmSchema(BaseModel):
    farmName: str
    svgData: SVGDataSchema
