"""
AI Orchestrator - Central hub for all AI operations
"""
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from app.core.config import settings
from app.models import Agent, Conversation, Message, UsageLog
from app.services.user_memory_service import UserMemoryService
from app.services.web_search_service import WebSearchService
from app.core.database import SessionLocal


class AIOrchestrator:
    """Central orchestrator for all AI operations"""

    def __init__(self):
        self.providers = {
            "openai": self._call_openai,
            "anthropic": self._call_anthropic,
            "huggingface": self._call_huggingface,
        }
        self.user_memory_service = UserMemoryService()
        self.web_search_service = WebSearchService()

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
                db=db,
                user_id=user_id,
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
            if conversation.title and conversation.title.startswith("Chat with"):
                conversation.title = message[:60]
            conversation.last_message_at = datetime.utcnow()
            conversation.updated_at = datetime.utcnow()

            # Track usage
            self._track_usage(
                db=db,
                organization_id=organization_id,
                user_id=user_id,
                agent_id=agent_id,
                tokens_used=response_data.get("tokens_used", 0),
                cost=response_data.get("cost", 0.0),
                endpoint="/api/chat/message",
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
        db=None,
        user_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate AI response using appropriate provider"""
        provider = self._get_provider_for_model(agent.model)
        if not provider:
            fallback = await self._web_search_fallback(message)
            if fallback:
                return fallback
            raise ValueError(f"No provider available for model {agent.model}")

        # Build messages for API
        system_prompt = agent.system_prompt
        if db is not None and user_id:
            memories = self.user_memory_service.list_memory(db, user_id=user_id, limit=20)
            memory_context = self.user_memory_service.build_memory_context(memories)
            if memory_context:
                system_prompt = f"{system_prompt}\n\n{memory_context}"

        messages = [{"role": "system", "content": system_prompt}]

        # Add history
        messages.extend(history[-10:])  # Last 10 messages for context

        # Add current message
        messages.append({"role": "user", "content": message})

        # Call provider; fallback to web search when unavailable or empty.
        try:
            response = await self.providers[provider](
                messages=messages,
                model=agent.model,
                temperature=agent.temperature / 100.0,  # Convert to 0-1 scale
                max_tokens=agent.max_tokens,
                **kwargs
            )
        except Exception:
            fallback = await self._web_search_fallback(message)
            if fallback:
                return fallback
            raise

        if not (response or {}).get("content"):
            fallback = await self._web_search_fallback(message)
            if fallback:
                return fallback

        return response

    async def _web_search_fallback(self, message: str) -> Optional[Dict[str, Any]]:
        """Fallback to web search when model/provider cannot answer."""
        if not settings.web_search_enabled:
            return None
        if not self._looks_like_web_query(message):
            return None

        try:
            result = await asyncio.to_thread(self.web_search_service.search, message)
        except Exception:
            return None

        if not result.get("found"):
            return None

        answer = result.get("answer") or ""
        source = result.get("source") or "DuckDuckGo"
        return {
            "content": f"{answer}\n\nFonte: {source}",
            "model": "web-search-fallback",
            "tokens_used": len(answer.split()),
            "finish_reason": "stop",
            "cost": 0.0,
        }

    def _looks_like_web_query(self, message: str) -> bool:
        text = (message or "").strip().lower()
        if not text:
            return False

        triggers = (
            "hoje",
            "atual",
            "noticia",
            "noticias",
            "preco",
            "cotacao",
            "quem",
            "quando",
            "onde",
            "qual",
            "o que",
        )
        return any(token in text for token in triggers)

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
        cost: float = 0.0,
        endpoint: str = "/api/chat",
    ):
        """Track API usage"""
        usage_log = UsageLog(
            id=str(uuid.uuid4()),
            organization_id=organization_id,
            user_id=user_id,
            agent_id=agent_id,
            endpoint=endpoint,
            method="POST",
            status_code=200,
            model="gpt-3.5-turbo",  # Default
            tokens_used=tokens_used,
            cost=cost
        )
        db.add(usage_log)