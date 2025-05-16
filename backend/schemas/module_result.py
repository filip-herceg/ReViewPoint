from pydantic import BaseModel
from typing import List, Literal

class ModuleResult(BaseModel):
    module_name: str
    status: Literal["ok", "warning", "error"]
    score: int  # 0–100
    feedback: List[str]
    version: str
