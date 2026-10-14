import pytest
@pytest.mark.asyncio
async def test_score(client):
    r = await client.post("/api/leads", json={"email": "c@x.com", "title": "VP Sales", "company": "Acme", "notes": "Has budget"})
    assert r.status_code == 200
    assert r.json()["band"] in {"hot", "warm", "cold"}
