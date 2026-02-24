from pydantic import BaseModel
from typing import Optional

class TableData(BaseModel):
    headers: list[str]
    rows: list[list[str]]

class SlideContent(BaseModel):
    title: str
    bullets: list[str]
    notes: str = ""
    image_query: str = ""
    table: Optional[TableData] = None

class PresentationOutline(BaseModel):
    topic: str
    slides: list[SlideContent]
