from __future__ import annotations
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.llm import get_llm
from backend.models import Lead

HOT_TITLES = {"ceo", "cto", "vp", "director", "head", "founder"}

def rule_score(title: str, company: str, notes: str) -> float:
    s = 0.2
    tl = title.lower()
    if any(t in tl for t in HOT_TITLES): s += 0.35
    if company: s += 0.15
    if "budget" in notes.lower() or "timeline" in notes.lower(): s += 0.2
    return min(1.0, s)

def band_for(score: float) -> str:
    if score >= 0.75: return "hot"
    if score >= 0.45: return "warm"
    return "cold"

async def upsert_score(session: AsyncSession, email: str, company: str = "", title: str = "", notes: str = "") -> Lead:
    base = rule_score(title, company, notes)
    llm = get_llm()
    hint = await llm.complete(f"Rate lead 0-1 for B2B SaaS: {title} @ {company}. Notes: {notes}", system="Return a short rationale.")
    boost = 0.1 if "high" in hint.lower() or "strong" in hint.lower() else 0.0
    score = min(1.0, round(base + boost, 3))
    lead = Lead(id=uuid.uuid4().hex[:10], email=email.strip().lower()[:200], company=company[:160],
                title=title[:160], notes=notes, score=score, band=band_for(score))
    session.add(lead); await session.commit(); await session.refresh(lead); return lead

async def list_leads(session: AsyncSession) -> list[Lead]:
    return list((await session.execute(select(Lead).order_by(Lead.score.desc()))).scalars())
