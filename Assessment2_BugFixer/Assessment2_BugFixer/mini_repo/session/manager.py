"""
session/manager.py — UserSession and SessionManager
BUG: In v2.3.1, create_session() was refactored to be async.
The _user_id assignment happens in an awaited coroutine, but the
caller doesn't always await it before returning the session object.
Under concurrent load, the session object is returned before
_user_id is set, causing AttributeError on access.
"""

import asyncio
import uuid
import time


class UserSession:
    """Represents an authenticated user session."""

    def __init__(self, token: str):
        self.token = token
        self.created_at = time.time()
        # BUG: _user_id is not set in __init__ — set later in async method
        # Under concurrency, session can be accessed before _user_id is set

    async def _async_init(self, user_id: str):
        """Async initialisation — simulates DB write latency."""
        await asyncio.sleep(0.05)  # simulate DB write
        self._user_id = user_id   # BUG: This may not complete before session is returned

    @property
    def user_id(self):
        return self._user_id  # AttributeError if _async_init not awaited first


class SessionManager:
    """Manages user sessions."""

    def __init__(self):
        self._sessions: dict[str, UserSession] = {}

    async def create_session(self, user_id: str) -> UserSession:
        """
        BUG INTRODUCED IN v2.3.1:
        Previously (v2.3.0): session._user_id was set synchronously.
        Now: _async_init is called but not properly awaited before returning
        under high concurrency due to a missing await in the task scheduling.
        """
        token = str(uuid.uuid4())
        session = UserSession(token)

        # BUG: asyncio.ensure_future schedules the coroutine but does NOT
        # guarantee it completes before this function returns.
        # The caller gets a session without _user_id set.
        asyncio.ensure_future(session._async_init(user_id))  # ← THE BUG

        # CORRECT FIX would be:
        # await session._async_init(user_id)

        self._sessions[token] = session
        return session   # returned before _user_id is set!

    def get_session(self, token: str) -> UserSession | None:
        return self._sessions.get(token)
