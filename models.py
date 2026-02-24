from pydantic import BaseModel
from typing import List, Optional

class Slide(BaseModel):
    title: str
    bullets: List[str]
    notes: Optional[str] = None
    image_query: Optional[str] = None  # ← NEW

class PresentationOutline(BaseModel):
    topic: str
    slides: List[Slide]
