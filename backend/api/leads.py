from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import leads as svc

class LeadIn(BaseModel):
    email: str = Field(min_length=3)
    company: str = ""
    title: str = ""
    notes: str = ""

router = APIRouter()

@router.get("/leads")
async def leads(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_leads(db)
    return {"leads": [{"id": l.id, "email": l.email, "company": l.company, "title": l.title, "score": l.score, "band": l.band} for l in rows]}

@router.post("/leads")
async def create(payload: LeadIn, db: AsyncSession = Depends(get_db)):
    l = await svc.upsert_score(db, payload.email, payload.company, payload.title, payload.notes)
    return {"id": l.id, "score": l.score, "band": l.band}
