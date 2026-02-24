from pydantic import BaseModel
from typing import List, Optional

class Slide(BaseModel):
    title: str
    bullets: List[str]
    notes: Optional[str] = None

class PresentationOutline(BaseModel):
    topic: str
    slides: List[Slide]
