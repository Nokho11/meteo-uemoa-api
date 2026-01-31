# app/models/schemas.py
from pydantic import BaseModel
from datetime import date
from typing import Optional, List


class MessageResponse(BaseModel):
    status: str
    message: str


class CollectResponse(MessageResponse):
    rows_collected: Optional[int] = None


class StatsSummary(BaseModel):
    ville: str
    pays: str
    temp_moyenne: float
    precip_total: float
    date_debut: date
    date_fin: date


class StatsResponse(BaseModel):
    summary: List[StatsSummary]