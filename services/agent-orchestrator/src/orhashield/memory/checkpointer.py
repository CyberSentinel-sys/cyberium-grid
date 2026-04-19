"""Postgres-backed LangGraph checkpointer for durable agent sessions."""
from __future__ import annotations

import asyncpg
import structlog

log = structlog.get_logger(__name__)


async def create_checkpointer(database_url: str) -> object:
    """Create and return a Postgres-backed LangGraph AsyncPostgresSaver.

    Handles the LangGraph version-dependent import path gracefully.
    """
    pool = await asyncpg.create_pool(database_url, min_size=2, max_size=10)

    try:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver  # type: ignore[import-not-found]

        checkpointer = AsyncPostgresSaver(pool)
        await checkpointer.setup()
        log.info("checkpointer_ready", backend="postgres")
        return checkpointer
    except ImportError:
        log.warning(
            "langgraph_postgres_checkpointer_unavailable",
            fallback="in_memory",
            hint="Install langgraph-checkpoint-postgres",
        )
        from langgraph.checkpoint.memory import MemorySaver  # type: ignore[import-not-found]

        return MemorySaver()
