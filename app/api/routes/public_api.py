"""
Public API routes (OpenAI-compatible)
"""
from typing import Optional
from fastapi import APIRouter, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.ai_orchestrator import AIOrchestrator
from app.services.auth_service import AuthService
from app.models import Organization, Agent

router = APIRouter()
orchestrator = AIOrchestrator()


class ChatCompletionRequest(BaseModel):
    model: str
    messages: list
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000
    user: Optional[str] = None


def get_organization_from_api_key(api_key: str = Header(None), db: Session = Depends(get_db)):
    """Get organization from API key"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    # Remove Bearer prefix if present
    if api_key.startswith("Bearer "):
        api_key = api_key[7:]

    organization = AuthService.verify_api_key(db, api_key)
    if not organization:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return organization


@router.post("/chat/completions")
async def create_chat_completion(
    request: ChatCompletionRequest,
    organization: Organization = Depends(get_organization_from_api_key),
    db: Session = Depends(get_db)
):
    """OpenAI-compatible chat completions endpoint"""
    # Find agent by model name (for now, use first available agent)
    # In production, you'd map model names to specific agents
    agent = db.query(Agent).filter(
        Agent.organization_id == organization.id,
        Agent.is_active == True,
        Agent.is_public == True
    ).first()

    if not agent:
        raise HTTPException(status_code=400, detail="No available agents")

    # Extract user message
    user_message = ""
    for msg in request.messages:
        if msg["role"] == "user":
            user_message = msg["content"]
            break

    if not user_message:
        raise HTTPException(status_code=400, detail="No user message found")

    try:
        # Process through orchestrator
        result = await orchestrator.process_chat(
            message=user_message,
            agent_id=agent.id,
            organization_id=organization.id,
            user_id=request.user
        )

        # Format response like OpenAI
        return {
            "id": f"chatcmpl-{result['message_id']}",
            "object": "chat.completion",
            "created": int(result.get('created_at', 0)),
            "model": result.get("model", request.model),
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result["content"]
                },
                "finish_reason": result.get("finish_reason", "stop")
            }],
            "usage": {
                "prompt_tokens": result.get("tokens_used", 0) // 2,  # Estimate
                "completion_tokens": result.get("tokens_used", 0) // 2,
                "total_tokens": result.get("tokens_used", 0)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
def list_models(organization: Organization = Depends(get_organization_from_api_key)):
    """List available models"""
    # Return available agents as models
    return {
        "object": "list",
        "data": [
            {
                "id": "alici-gpt-3.5-turbo",
                "object": "model",
                "created": 1677610602,
                "owned_by": "alici"
            },
            {
                "id": "alici-gpt-4",
                "object": "model",
                "created": 1687882411,
                "owned_by": "alici"
            }
        ]
    }


@router.get("/models/{model}")
def get_model(model: str, organization: Organization = Depends(get_organization_from_api_key)):
    """Get model information"""
    return {
        "id": model,
        "object": "model",
        "created": 1677610602,
        "owned_by": "alici",
        "permission": [],
        "root": model,
        "parent": None
    }