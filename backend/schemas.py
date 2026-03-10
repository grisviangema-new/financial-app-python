from typing import List, Optional
from pydantic import BaseModel

# --- SCHEMA DATA (Validasi Input) ---
class BreakdownSchema(BaseModel):
    type: str
    label: str
    amount: int

class ReportSchema(BaseModel):
    ticker: str
    year: int
    period: str
    revenue: int
    breakdowns: List[BreakdownSchema]
    currency: str