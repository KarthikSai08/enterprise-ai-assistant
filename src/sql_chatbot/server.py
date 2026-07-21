import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from sql_chatbot.metadata.loader import build
from sql_chatbot.retrieval.engine import Retriever
from sql_chatbot.generation.pipeline import run_sql_with_answer

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading knowledge base ...")
    app.state.data = build()
    app.state.retriever = Retriever(app.state.data)
    d = app.state.data
    logger.info("%d tables, %d domains, %d joins", len(d['tables']), len(d['domains']), len(d['joins']))
    logger.info("Server ready on /health and /search")
    yield


app = FastAPI(title="SQL Chatbot API", version="1.0.0", lifespan=lifespan)


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
    ret = app.state.retriever
    col_count = sum(len(t.get("columns", [])) for t in ret.tables.values())
    return HealthResponse(
        status="ok",
        tables=len(ret.tables),
        columns=col_count,
        domains=len(ret.domains),
        joins=len(ret.joins),
        db_connected=ret.db_connected,
    )


@app.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest):
    retriever = app.state.retriever
    t0 = time.perf_counter()

    try:
        result = await asyncio.to_thread(retriever.search, req.query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    sql = None
    row_count = 0
    answer = None
    if result.get("relevant") and retriever.db_connected:
        corrected_query = result.get("normalized", result["query"])
        sql_result = await asyncio.to_thread(
            run_sql_with_answer, corrected_query, result
        )
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
