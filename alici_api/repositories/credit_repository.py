"""Atomic credit repository.

Runtime database access stays on database.py (psycopg2 pool / sqlite3).
Postgres uses SELECT ... FOR UPDATE. SQLite uses BEGIN IMMEDIATE for a
single-writer transaction in local development.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Any

from database import USE_POSTGRES, USE_SQLITE, get_db_connection


class InsufficientCreditsError(Exception):
    def __init__(self, balance: int, required: int):
        self.balance = balance
        self.required = required
        super().__init__(f"Creditos insuficientes: saldo={balance}, necessario={required}")


class CreditRepository:
    max_retries = 2

    def _placeholder(self) -> str:
        return "%s" if USE_POSTGRES else "?"

    def _metadata_value(self, metadata: dict[str, Any] | None):
        payload = metadata or {}
        if USE_POSTGRES:
            from psycopg2.extras import Json

            return Json(payload)
        return json.dumps(payload, ensure_ascii=False)

    def _row_to_dict(self, cursor, row) -> dict[str, Any] | None:
        if row is None:
            return None
        if hasattr(row, "keys"):
            return dict(row)
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))

    def _begin_atomic(self, conn) -> None:
        if USE_SQLITE:
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("BEGIN IMMEDIATE")

    def _is_retryable_postgres_error(self, exc: Exception) -> bool:
        if not USE_POSTGRES:
            return False
        pgcode = getattr(exc, "pgcode", None)
        if pgcode in {"40P01", "40001"}:
            return True
        text = str(exc).lower()
        return "deadlock detected" in text or "could not serialize access" in text

    def _with_deadlock_retry(self, operation: Callable[[], int]) -> int:
        attempts = self.max_retries + 1 if USE_POSTGRES else 1
        last_exc: Exception | None = None
        for attempt in range(attempts):
            try:
                return operation()
            except Exception as exc:
                if not self._is_retryable_postgres_error(exc) or attempt >= attempts - 1:
                    raise
                last_exc = exc
                time.sleep(0.05 * (attempt + 1))
        raise last_exc or RuntimeError("Falha inesperada na operacao de creditos")

    def _ensure_balance_row(self, cursor, user_id: int) -> None:
        placeholder = self._placeholder()
        cursor.execute(
            f"""
            INSERT INTO credit_balances (user_id, balance)
            VALUES ({placeholder}, 0)
            ON CONFLICT(user_id) DO NOTHING
            """,
            (user_id,),
        )

    def get_balance(self, user_id: int) -> int:
        placeholder = self._placeholder()
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"SELECT balance FROM credit_balances WHERE user_id = {placeholder}",
                (user_id,),
            )
            row = cur.fetchone()
            cur.close()
            if not row:
                return 0
            return int(row["balance"] if hasattr(row, "keys") else row[0])

    def add_credits(
        self,
        user_id: int,
        amount: int,
        reason: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        job_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        if amount <= 0:
            raise ValueError("amount precisa ser positivo")

        def _operation() -> int:
            placeholder = self._placeholder()
            with get_db_connection() as conn:
                self._begin_atomic(conn)
                cur = conn.cursor()
                self._ensure_balance_row(cur, user_id)

                if USE_POSTGRES:
                    cur.execute(
                        f"""
                        UPDATE credit_balances
                        SET balance = balance + {placeholder}, updated_at = NOW()
                        WHERE user_id = {placeholder}
                        RETURNING balance
                        """,
                        (amount, user_id),
                    )
                else:
                    cur.execute(
                        f"""
                        UPDATE credit_balances
                        SET balance = balance + {placeholder}, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = {placeholder}
                        """,
                        (amount, user_id),
                    )
                    cur.execute(
                        f"SELECT balance FROM credit_balances WHERE user_id = {placeholder}",
                        (user_id,),
                    )

                new_balance = int(cur.fetchone()[0])
                cur.execute(
                    f"""
                    INSERT INTO credit_transactions (
                        user_id, amount, type, reason, provider, model, job_id, metadata
                    )
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                    """,
                    (
                        user_id,
                        amount,
                        "grant",
                        reason,
                        provider,
                        model,
                        job_id,
                        self._metadata_value(metadata),
                    ),
                )
                cur.close()
                return new_balance

        return self._with_deadlock_retry(_operation)

    def spend_credits(
        self,
        user_id: int,
        amount: int,
        reason: str,
        *,
        provider: str | None = None,
        model: str | None = None,
        job_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> int:
        if amount <= 0:
            raise ValueError("amount precisa ser positivo")

        def _operation() -> int:
            placeholder = self._placeholder()
            with get_db_connection() as conn:
                self._begin_atomic(conn)
                cur = conn.cursor()
                self._ensure_balance_row(cur, user_id)

                lock_clause = " FOR UPDATE" if USE_POSTGRES else ""
                cur.execute(
                    f"SELECT balance FROM credit_balances WHERE user_id = {placeholder}{lock_clause}",
                    (user_id,),
                )
                row = cur.fetchone()
                balance = int(row[0] if row else 0)
                if balance < amount:
                    cur.close()
                    raise InsufficientCreditsError(balance=balance, required=amount)

                if USE_POSTGRES:
                    cur.execute(
                        f"""
                        UPDATE credit_balances
                        SET balance = balance - {placeholder}, updated_at = NOW()
                        WHERE user_id = {placeholder}
                        RETURNING balance
                        """,
                        (amount, user_id),
                    )
                else:
                    cur.execute(
                        f"""
                        UPDATE credit_balances
                        SET balance = balance - {placeholder}, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = {placeholder}
                        """,
                        (amount, user_id),
                    )
                    cur.execute(
                        f"SELECT balance FROM credit_balances WHERE user_id = {placeholder}",
                        (user_id,),
                    )

                new_balance = int(cur.fetchone()[0])
                cur.execute(
                    f"""
                    INSERT INTO credit_transactions (
                        user_id, amount, type, reason, provider, model, job_id, metadata
                    )
                    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                    """,
                    (
                        user_id,
                        -amount,
                        "spend",
                        reason,
                        provider,
                        model,
                        job_id,
                        self._metadata_value(metadata),
                    ),
                )
                cur.close()
                return new_balance

        return self._with_deadlock_retry(_operation)

    def get_transaction_history(self, user_id: int, limit: int = 50) -> list[dict[str, Any]]:
        placeholder = self._placeholder()
        limit = max(1, min(int(limit or 50), 200))
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT id, user_id, amount, type, reason, provider, model, job_id, metadata, created_at
                FROM credit_transactions
                WHERE user_id = {placeholder}
                ORDER BY created_at DESC, id DESC
                LIMIT {limit}
                """,
                (user_id,),
            )
            rows = cur.fetchall()
            result = []
            for row in rows:
                item = self._row_to_dict(cur, row)
                if item and isinstance(item.get("metadata"), str):
                    try:
                        item["metadata"] = json.loads(item["metadata"])
                    except json.JSONDecodeError:
                        item["metadata"] = {}
                result.append(item)
            cur.close()
            return result

    def transaction_exists(self, *, job_id: str, reason: str, transaction_type: str = "grant") -> bool:
        if not job_id:
            return False

        placeholder = self._placeholder()
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT 1
                FROM credit_transactions
                WHERE job_id = {placeholder}
                  AND reason = {placeholder}
                  AND type = {placeholder}
                LIMIT 1
                """,
                (job_id, reason, transaction_type),
            )
            exists = cur.fetchone() is not None
            cur.close()
            return exists

    def get_price(
        self,
        *,
        job_type: str,
        model: str,
        provider: str | None = None,
        resolution: str | None = None,
        duration_seconds: int | None = None,
    ) -> int | None:
        placeholder = self._placeholder()
        active_value = True if USE_POSTGRES else 1
        with get_db_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                f"""
                SELECT cost_credits
                FROM credit_pricing
                WHERE active = {placeholder}
                  AND job_type = {placeholder}
                  AND model = {placeholder}
                  AND (provider = {placeholder} OR (provider IS NULL AND {placeholder} IS NULL))
                  AND (resolution = {placeholder} OR (resolution IS NULL AND {placeholder} IS NULL))
                  AND (duration_seconds = {placeholder} OR (duration_seconds IS NULL AND {placeholder} IS NULL))
                ORDER BY id DESC
                LIMIT 1
                """,
                (
                    active_value,
                    job_type,
                    model,
                    provider,
                    provider,
                    resolution,
                    resolution,
                    duration_seconds,
                    duration_seconds,
                ),
            )
            row = cur.fetchone()
            cur.close()
            if not row:
                return None
            return int(row[0])
