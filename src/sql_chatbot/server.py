import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from sql_chatbot.metadata.loader import build
from sql_chatbot.retrieval.engine import Retriever
from sql_chatbot.generation.pipeline import run_sql_with_answer

app = FastAPI(title="SQL Chatbot API", version="1.0.0")

print("Loading knowledge base ...")
_data = build()
_retriever = Retriever(_data)

print(f"  {len(_data['tables'])} tables, {len(_data['domains'])} domains, {len(_data['joins'])} joins")
print("Server ready on /health and /search")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural-language search query")


class SearchResponse(BaseModel):
    query: str
    relevant: bool
    message: str | None = None
    results: list[dict] = []
    joins: list[dict] = []
    tables_count: int = 0
    latency_ms: float = 0.0
    confidence: float = 0.0
    sql: str | None = None
    row_count: int = 0
    answer: str | None = None


class HealthResponse(BaseModel):
    status: str = "ok"
    tables: int = 0
    columns: int = 0
    domains: int = 0
    joins: int = 0
    db_connected: bool = False
    version: str = "1.0.0"


@app.get("/health", response_model=HealthResponse)
async def health():
    col_count = sum(len(t.get("columns", [])) for t in _retriever.tables.values())
    return HealthResponse(
        status="ok",
        tables=len(_retriever.tables),
        columns=col_count,
        domains=len(_retriever.domains),
        joins=len(_retriever.joins),
        db_connected=_retriever.db_connected,
    )


@app.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest):
    t0 = time.perf_counter()
    try:
        result = _retriever.search(req.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    sql = None
    row_count = 0
    answer = None
    if result.get("relevant") and _retriever.db_connected:
        sql_result = run_sql_with_answer(result["query"], result)
        sql = sql_result.get("sql")
        row_count = sql_result.get("row_count", 0)
        answer = sql_result.get("answer")

    latency = round((time.perf_counter() - t0) * 1000, 1)
    return SearchResponse(
        query=result.get("query", req.query),
        relevant=result.get("relevant", False),
        message=result.get("message"),
        results=result.get("results", []),
        joins=result.get("joins", []),
        tables_count=result.get("table_count", 0),
        latency_ms=result.get("latency_ms", latency),
        confidence=result.get("confidence", 0.0),
        sql=sql,
        row_count=row_count,
        answer=answer,
    )
