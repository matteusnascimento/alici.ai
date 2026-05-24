import json
import time
from typing import Any, Optional
from sqlalchemy.orm import Session

from app.models.tool_execution import ToolExecution
from app.schemas.tool_execution import ToolExecutionCreate, ToolExecutionRead


class ToolExecutionService:
    def __init__(self, db: Session):
        self.db = db

    def log_execution(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        success: bool = True,
        result: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        execution_time_ms: Optional[int] = None,
        agent_id: Optional[int] = None,
        user_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
    ) -> ToolExecutionRead:
        """Registra execução de tool no banco."""
        execution_data = ToolExecutionCreate(
            tool_name=tool_name,
            tool_args=json.dumps(tool_args, default=str),
            success=success,
            result=json.dumps(result, default=str) if result else None,
            error=error,
            execution_time_ms=execution_time_ms,
            agent_id=agent_id,
            user_id=user_id,
            conversation_id=conversation_id,
        )

        execution = ToolExecution(**execution_data.model_dump())
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return ToolExecutionRead.model_validate(execution)

    def get_execution(self, execution_id: int) -> ToolExecutionRead:
        """Busca execução por ID."""
        execution = self.db.query(ToolExecution).filter(ToolExecution.id == execution_id).first()
        if not execution:
            from fastapi import HTTPException, status
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execução não encontrada",
            )
        return ToolExecutionRead.model_validate(execution)

    def list_executions(
        self,
        tool_name: Optional[str] = None,
        agent_id: Optional[int] = None,
        user_id: Optional[int] = None,
        conversation_id: Optional[int] = None,
        success: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[ToolExecutionRead]:
        """Lista execuções com filtros."""
        query = self.db.query(ToolExecution)

        if tool_name:
            query = query.filter(ToolExecution.tool_name == tool_name)
        if agent_id:
            query = query.filter(ToolExecution.agent_id == agent_id)
        if user_id:
            query = query.filter(ToolExecution.user_id == user_id)
        if conversation_id:
            query = query.filter(ToolExecution.conversation_id == conversation_id)
        if success is not None:
            query = query.filter(ToolExecution.success == success)

        executions = query.offset(skip).limit(limit).all()
        return [ToolExecutionRead.model_validate(execution) for execution in executions]

    def get_execution_stats(self) -> dict[str, Any]:
        """Retorna estatísticas de execução de tools."""
        total = self.db.query(ToolExecution).count()
        successful = self.db.query(ToolExecution).filter(ToolExecution.success == True).count()
        failed = total - successful

        # Tools mais executadas
        from sqlalchemy import func
        tool_counts = (
            self.db.query(ToolExecution.tool_name, func.count(ToolExecution.id))
            .group_by(ToolExecution.tool_name)
            .all()
        )

        return {
            "total_executions": total,
            "successful_executions": successful,
            "failed_executions": failed,
            "success_rate": successful / total if total > 0 else 0,
            "tools_usage": dict(tool_counts),
        }