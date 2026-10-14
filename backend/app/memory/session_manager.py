import time
import uuid
from typing import List, Dict, Any, Optional

class SessionState:
    def __init__(self, session_id: str):
        self.session_id: str = session_id
        self.session_state: str = "dormant"  # "dormant" | "listening" | "processing" | "speaking"
        self.has_introduced: bool = False
        self.last_intent: Optional[str] = None
        self.last_user_text: str = ""
        self.last_assistant_text: str = ""
        self.last_response_time: float = 0.0
        self.active_cow_id: Optional[str] = None
        self.active_topic: Optional[str] = None

    def update(
        self,
        intent: Optional[str] = None,
        user_text: Optional[str] = None,
        assistant_text: Optional[str] = None,
        cow_id: Optional[str] = None,
        topic: Optional[str] = None,
        state: Optional[str] = None
    ):
        if intent is not None:
            self.last_intent = intent
        if user_text is not None:
            self.last_user_text = user_text
        if assistant_text is not None:
            self.last_assistant_text = assistant_text
            self.last_response_time = time.time()
        if cow_id is not None:
            self.active_cow_id = cow_id
        if topic is not None:
            self.active_topic = topic
        if state is not None:
            self.session_state = state

class SessionManager:
    def __init__(self):
        self._states: Dict[str, SessionState] = {}
        self._history: Dict[str, List[Dict[str, str]]] = {}

    def get_state(self, session_id: str) -> SessionState:
        if session_id not in self._states:
            self._states[session_id] = SessionState(session_id)
        return self._states[session_id]

    async def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        if not session_id:
            session_id = str(uuid.uuid4())
        if session_id not in self._history:
            self._history[session_id] = []
        self.get_state(session_id)
        return session_id

    async def get_recent_history(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        messages = self._history.get(session_id, [])
        return messages[-limit:]

    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_calls: Optional[dict] = None,
        tool_results: Optional[dict] = None,
        detected_language: str = "tanglish"
    ):
        if session_id not in self._history:
            self._history[session_id] = []
        self._history[session_id].append({
            "role": role,
            "content": content
        })
        # Keep last 50 messages max
        if len(self._history[session_id]) > 50:
            self._history[session_id] = self._history[session_id][-50:]

session_manager = SessionManager()
