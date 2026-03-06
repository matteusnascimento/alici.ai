"""
AI Orchestrator - Central hub for all AI operations
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from app.core.config import settings
from app.models import Agent, Conversation, Message, UsageLog
from app.core.database import SessionLocal


class AIOrchestrator:
    """Central orchestrator for all AI operations"""

    def __init__(self):
        self.providers = {
            "openai": self._call_openai,
            "anthropic": self._call_anthropic,
            "huggingface": self._call_huggingface,
        }

    async def process_chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process a chat message through the AI pipeline

        Args:
            message: User message
            conversation_id: Existing conversation ID
            agent_id: Agent to use
            user_id: User ID for tracking
            organization_id: Organization ID for multi-tenant

        Returns:
            Dict with response and metadata
        """
        db = SessionLocal()

        try:
            # Get or create conversation
            if conversation_id:
                conversation = db.query(Conversation).filter(
                    Conversation.id == conversation_id,
                    Conversation.organization_id == organization_id
                ).first()
                if not conversation:
                    raise ValueError("Conversation not found")
            else:
                conversation = self._create_conversation(db, user_id, agent_id, organization_id)

            # Get agent configuration
            agent = db.query(Agent).filter(
                Agent.id == agent_id,
                Agent.organization_id == organization_id,
                Agent.is_active == True
            ).first()
            if not agent:
                raise ValueError("Agent not found or inactive")

            # Get conversation history
            history = self._get_conversation_history(db, conversation.id)

            # Generate response
            response_data = await self._generate_response(
                message=message,
                agent=agent,
                history=history,
                **kwargs
            )

            # Save messages
            user_message = self._save_message(
                db, conversation.id, "user", message
            )
            ai_message = self._save_message(
                db, conversation.id, "assistant", response_data["content"],
                model=response_data.get("model"),
                tokens_used=response_data.get("tokens_used")
            )

            # Update conversation
            conversation.last_message_at = datetime.utcnow()
            conversation.updated_at = datetime.utcnow()

            # Track usage
            self._track_usage(
                db=db,
                organization_id=organization_id,
                user_id=user_id,
                agent_id=agent_id,
                tokens_used=response_data.get("tokens_used", 0),
                cost=response_data.get("cost", 0.0)
            )

            db.commit()

            return {
                "conversation_id": conversation.id,
                "message_id": ai_message.id,
                "content": response_data["content"],
                "model": response_data.get("model"),
                "tokens_used": response_data.get("tokens_used"),
                "finish_reason": response_data.get("finish_reason")
            }

        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

    def _create_conversation(self, db, user_id: str, agent_id: str, organization_id: str) -> Conversation:
        """Create a new conversation"""
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            agent_id=agent_id,
            organization_id=organization_id,
            title=f"Chat with {agent_id}"  # Will be updated with first message
        )
        db.add(conversation)
        return conversation

    def _get_conversation_history(self, db, conversation_id: str, limit: int = 50) -> List[Dict]:
        """Get recent conversation history"""
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(limit).all()

        # Reverse to get chronological order
        messages.reverse()

        return [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]

    async def _generate_response(
        self,
        message: str,
        agent: Agent,
        history: List[Dict],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate AI response using appropriate provider"""
        provider = self._get_provider_for_model(agent.model)
        if not provider:
            raise ValueError(f"No provider available for model {agent.model}")

        # Build messages for API
        messages = [{"role": "system", "content": agent.system_prompt}]

        # Add history
        messages.extend(history[-10:])  # Last 10 messages for context

        # Add current message
        messages.append({"role": "user", "content": message})

        # Call provider
        return await self.providers[provider](
            messages=messages,
            model=agent.model,
            temperature=agent.temperature / 100.0,  # Convert to 0-1 scale
            max_tokens=agent.max_tokens,
            **kwargs
        )

    def _get_provider_for_model(self, model: str) -> Optional[str]:
        """Determine which provider to use for a model"""
        if model.startswith("gpt"):
            return "openai"
        elif model.startswith("claude"):
            return "anthropic"
        elif model.startswith("hf:"):
            return "huggingface"
        return None

    async def _call_openai(self, messages: List[Dict], model: str, **kwargs) -> Dict[str, Any]:
        """Call OpenAI API"""
        if not settings.openai_api_key:
            raise ValueError("OpenAI API key not configured")

        # Placeholder - implement actual OpenAI call
        await asyncio.sleep(0.1)  # Simulate API call

        return {
            "content": f"ALICI response via {model}: {messages[-1]['content'][:50]}...",
            "model": model,
            "tokens_used": len(messages[-1]['content'].split()) * 2,
            "finish_reason": "stop",
            "cost": 0.002
        }

    async def _call_anthropic(self, messages: List[Dict], model: str, **kwargs) -> Dict[str, Any]:
        """Call Anthropic API"""
        if not settings.anthropic_api_key:
            raise ValueError("Anthropic API key not configured")

        # Placeholder - implement actual Anthropic call
        await asyncio.sleep(0.1)

        return {
            "content": f"Claude response: {messages[-1]['content'][:50]}...",
            "model": model,
            "tokens_used": len(messages[-1]['content'].split()) * 2,
            "finish_reason": "stop",
            "cost": 0.003
        }

    async def _call_huggingface(self, messages: List[Dict], model: str, **kwargs) -> Dict[str, Any]:
        """Call HuggingFace API"""
        if not settings.huggingface_api_key:
            raise ValueError("HuggingFace API key not configured")

        # Placeholder - implement actual HuggingFace call
        await asyncio.sleep(0.1)

        return {
            "content": f"HuggingFace response: {messages[-1]['content'][:50]}...",
            "model": model,
            "tokens_used": len(messages[-1]['content'].split()) * 2,
            "finish_reason": "stop",
            "cost": 0.001
        }

    def _save_message(
        self,
        db,
        conversation_id: str,
        role: str,
        content: str,
        model: Optional[str] = None,
        tokens_used: Optional[int] = None,
        finish_reason: Optional[str] = None
    ) -> Message:
        """Save a message to database"""
        message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=role,
            content=content,
            model=model,
            tokens_used=tokens_used,
            finish_reason=finish_reason
        )
        db.add(message)
        return message

    def _track_usage(
        self,
        db,
        organization_id: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        tokens_used: int = 0,
        cost: float = 0.0
    ):
        """Track API usage"""
        usage_log = UsageLog(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            user_id=user_id,
            agent_id=agent_id,
            endpoint="/api/chat",
            method="POST",
            status_code=200,
            model="gpt-3.5-turbo",  # Default
            tokens_used=tokens_used,
            cost=cost
        )
        db.add(usage_log)