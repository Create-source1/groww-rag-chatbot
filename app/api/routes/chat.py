"""Chat API endpoint."""
import uuid
from fastapi import APIRouter, Depends
from app.api.schemas.chat import ChatRequest, ChatResponse
from app.pipeline.query import QueryPipeline
from app.models.schemas import Message

router = APIRouter()

# In-memory session store
_sessions: dict = {}


def get_query_pipeline() -> QueryPipeline:
    """Dependency to get the query pipeline (set in main.py)."""
    from app.main import query_pipeline
    return query_pipeline


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, pipeline: QueryPipeline = Depends(get_query_pipeline)):
    """Process a user query and return a generated response."""
    # Get or create session
    session_id = request.session_id or str(uuid.uuid4())

    # Get conversation history
    history = _sessions.get(session_id, [])

    # Process query
    result = pipeline.process(request.query, history)

    # Update session history
    history.append(Message(role="user", content=request.query))
    history.append(Message(role="assistant", content=result["response"]))

    # Trim history to max length
    max_history = 10
    if len(history) > max_history * 2:
        history = history[-max_history * 2:]

    _sessions[session_id] = history

    return ChatResponse(
        response=result["response"],
        sources=result["sources"],
        session_id=session_id
    )
