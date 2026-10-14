# Dev server for lead-scoring-app
$env:LLM_MODE = "mock"
uvicorn backend.main:app --reload --port 8000
