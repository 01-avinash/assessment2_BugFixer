"""
Minimal Reproduction Script — BUG-2024-0042
"""
import asyncio
import uuid
import time
import sys

class UserSession:
    def __init__(self, token: str):
        self.token = token
        self.created_at = time.time()

    async def _async_init(self, user_id: str):
        await asyncio.sleep(0.05)
        self._user_id = user_id

    @property
    def user_id(self):
        return self._user_id

class BuggySessionManager:
    def __init__(self):
        self._sessions = {}

    async def create_session(self, user_id: str) -> UserSession:
        token = str(uuid.uuid4())[:8]
        session = UserSession(token)
        asyncio.ensure_future(session._async_init(user_id))
        self._sessions[token] = session
        return session

async def simulate_login(manager, user_id: str, results: list):
    try:
        session = await manager.create_session(user_id)
        uid = session.user_id
        results.append({"user": user_id, "status": "OK", "user_id": uid})
    except AttributeError as e:
        results.append({"user": user_id, "status": "FAILED", "error": str(e)})

async def run_concurrent_logins(num_users: int = 20) -> list:
    manager = BuggySessionManager()
    results = []
    tasks = [simulate_login(manager, f"user_{i:04d}", results) for i in range(num_users)]
    await asyncio.gather(*tasks)
    return results

async def main():
    results = await run_concurrent_logins(20)
    failed = [r for r in results if r["status"] == "FAILED"]
    return len(failed) > 0

if __name__ == "__main__":
    bug_found = asyncio.run(main())
    sys.exit(1 if bug_found else 0)
