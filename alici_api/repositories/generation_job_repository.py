"""Repository for durable media generation jobs."""

from __future__ import annotations

import json
from typing import Any

from database import USE_POSTGRES, get_db_connection


class GenerationJobRepository:
    def _placeholder(self) -> str:
        return "%s" if USE_POSTGRES else "?"

    def _json_value(self, value: dict[str, Any] | None):
        payload = value or {}
        if USE_POSTGRES:
            from psycopg2.extras import Json

            return Json(payload)
        return json.dumps(payload, ensure_ascii=False)

    def _row_to_dict(self, cursor, row) -> dict[str, Any] | None:
        if row is None:
            return None
        if hasattr(row, "keys"):
            data = dict(row)
        else:
            columns = [desc[0] for desc in cursor.description]
            data = dict(zip(columns, row))
        for key in ("metadata", "result_payload"):
            if isinstance(data.get(key), str):
                try:
                    data[key] = json.loads(data[key])
                except json.JSONDecodeError:
                    data[key] = {}
        return data

    def create_job(
        self,
        *,
        job_id: str,
        user_id: int,
        job_type: str,
        prompt: str,
        cost: int,
        model: str,
        provider: str | None = None,
        queue_name: str | None = None,
        priority: int = 50,
        max_retries: int = 3,
        input_path: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        placeholder = self._placeholder()
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                INSERT INTO generation_jobs (
                    id, user_id, status, job_type, provider, model, prompt,
                    cost, progress, metadata, queue_name, priority, input_path,
                    max_retries, result_payload
                )
                VALUES (
                    {placeholder}, {placeholder}, 'queued', {placeholder}, {placeholder},
                    {placeholder}, {placeholder}, {placeholder}, 0, {placeholder},
                    {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}
                )
                """,
                (
                    job_id,
                    user_id,
                    job_type,
                    provider,
                    model,
                    prompt,
                    int(cost),
                    self._json_value(metadata),
                    queue_name,
                    int(priority),
                    input_path,
                    int(max_retries),
                    self._json_value({}),
                ),
            )
            cur.close()
        return self.get_job(job_id) or {}

    def set_arq_job_id(self, job_id: str, arq_job_id: str) -> None:
        placeholder = self._placeholder()
        timestamp_expr = "NOW()" if USE_POSTGRES else "CURRENT_TIMESTAMP"
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                UPDATE generation_jobs
                SET arq_job_id = {placeholder}, updated_at = {timestamp_expr}
                WHERE id = {placeholder}
                """,
                (arq_job_id, job_id),
            )
            cur.close()

    def get_job(self, job_id: str, *, user_id: int | None = None) -> dict[str, Any] | None:
        placeholder = self._placeholder()
        where = f"id = {placeholder}"
        params: list[Any] = [job_id]
        if user_id is not None:
            where += f" AND user_id = {placeholder}"
            params.append(user_id)

        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT id, user_id, status, job_type, provider, model, prompt,
                       result_url, cost, progress, error_message, metadata,
                       queue_name, priority, arq_job_id, input_path, result_payload,
                       attempts, max_retries, created_at, started_at, updated_at,
                       completed_at, refunded_at
                FROM generation_jobs
                WHERE {where}
                LIMIT 1
                """,
                tuple(params),
            )
            row = cur.fetchone()
            data = self._row_to_dict(cur, row)
            cur.close()
            return data

    def mark_processing(self, job_id: str) -> dict[str, Any] | None:
        placeholder = self._placeholder()
        timestamp_expr = "NOW()" if USE_POSTGRES else "CURRENT_TIMESTAMP"
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                UPDATE generation_jobs
                SET status = 'processing',
                    progress = CASE WHEN progress < 5 THEN 5 ELSE progress END,
                    attempts = attempts + 1,
                    started_at = COALESCE(started_at, {timestamp_expr}),
                    updated_at = {timestamp_expr}
                WHERE id = {placeholder}
                """,
                (job_id,),
            )
            cur.close()
        return self.get_job(job_id)

    def update_progress(self, job_id: str, progress: int, *, status: str | None = None) -> None:
        placeholder = self._placeholder()
        timestamp_expr = "NOW()" if USE_POSTGRES else "CURRENT_TIMESTAMP"
        progress = max(0, min(int(progress), 100))
        if status:
            sql = f"""
                UPDATE generation_jobs
                SET progress = {placeholder}, status = {placeholder}, updated_at = {timestamp_expr}
                WHERE id = {placeholder}
            """
            params = (progress, status, job_id)
        else:
            sql = f"""
                UPDATE generation_jobs
                SET progress = {placeholder}, updated_at = {timestamp_expr}
                WHERE id = {placeholder}
            """
            params = (progress, job_id)
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(sql, params)
            cur.close()

    def complete_job(
        self,
        job_id: str,
        *,
        result_url: str | None = None,
        result_payload: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        placeholder = self._placeholder()
        timestamp_expr = "NOW()" if USE_POSTGRES else "CURRENT_TIMESTAMP"
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                UPDATE generation_jobs
                SET status = 'completed',
                    progress = 100,
                    result_url = {placeholder},
                    result_payload = {placeholder},
                    error_message = NULL,
                    updated_at = {timestamp_expr},
                    completed_at = {timestamp_expr}
                WHERE id = {placeholder}
                """,
                (result_url, self._json_value(result_payload), job_id),
            )
            cur.close()
        return self.get_job(job_id)

    def fail_job(self, job_id: str, *, error_message: str, dead_letter: bool = False) -> dict[str, Any] | None:
        placeholder = self._placeholder()
        timestamp_expr = "NOW()" if USE_POSTGRES else "CURRENT_TIMESTAMP"
        status = "dead_letter" if dead_letter else "failed"
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                UPDATE generation_jobs
                SET status = {placeholder},
                    error_message = {placeholder},
                    updated_at = {timestamp_expr},
                    completed_at = {timestamp_expr}
                WHERE id = {placeholder}
                """,
                (status, str(error_message)[:2000], job_id),
            )
            cur.close()
        return self.get_job(job_id)

    def mark_refunded(self, job_id: str) -> None:
        placeholder = self._placeholder()
        timestamp_expr = "NOW()" if USE_POSTGRES else "CURRENT_TIMESTAMP"
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                UPDATE generation_jobs
                SET refunded_at = COALESCE(refunded_at, {timestamp_expr}),
                    updated_at = {timestamp_expr}
                WHERE id = {placeholder}
                """,
                (job_id,),
            )
            cur.close()

    def list_user_jobs(self, user_id: int, *, limit: int = 50) -> list[dict[str, Any]]:
        placeholder = self._placeholder()
        limit = max(1, min(int(limit or 50), 100))
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT id, user_id, status, job_type, provider, model, result_url,
                       cost, progress, error_message, metadata, result_payload,
                       queue_name, priority, arq_job_id, attempts, max_retries,
                       created_at, updated_at, completed_at,
                       refunded_at
                FROM generation_jobs
                WHERE user_id = {placeholder}
                ORDER BY created_at DESC
                LIMIT {limit}
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            result = [self._row_to_dict(cur, row) for row in rows]
            cur.close()
            return [item for item in result if item]
