from motor.motor_asyncio import AsyncIOMotorClientSession
from typing import Callable, Any, Awaitable
import logging

logger = logging.getLogger(__name__)

async def with_transaction(func: Callable[[AsyncIOMotorClientSession], Awaitable[Any]]):
    """
    Decorator/helper to run a function within a MongoDB transaction.
    Assumes `database.client` is available and connected.
    """
    from db.mongo import database # Import here to avoid circular dependency

    if not database.client:
        logger.error("MongoDB client not initialized for transaction.")
        raise Exception("Database client not available for transaction.")

    async with await database.client.start_session() as session:
        async with session.start_transaction():
            try:
                result = await func(session)
                await session.commit_transaction()
                return result
            except Exception as e:
                await session.abort_transaction()
                logger.error(f"Transaction aborted due to error: {e}")
                raise
