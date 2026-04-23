from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime


class ToolExecutionBase(BaseModel):
    tool_name: str
    tool_args: str  # JSON string
    success: bool = True
    result: Optional[str] = None  # JSON string
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None
    agent_id: Optional[int] = None
    user_id: Optional[int] = None
    conversation_id: Optional[int] = None


class ToolExecutionCreate(ToolExecutionBase):
    pass


class ToolExecutionRead(ToolExecutionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ToolExecutionUpdate(BaseModel):
    success: Optional[bool] = None
    result: Optional[str] = None
    error: Optional[str] = None
    execution_time_ms: Optional[int] = None