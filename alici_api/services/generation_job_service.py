"""Business service for durable generation jobs."""

from __future__ import annotations

from uuid import uuid4
from pathlib import Path

from alici_api.config import get_settings
from alici_api.jobs.queue import enqueue_generation_job, queue_for_plan
from alici_api.repositories.generation_job_repository import GenerationJobRepository
from alici_api.services.credit_service import CreditService, InsufficientCreditsError
from logger import get_logger


logger_jobs = get_logger("generation_jobs")


class GenerationJobService:
    def __init__(
        self,
        *,
        repository: GenerationJobRepository | None = None,
        credit_service: CreditService | None = None,
    ):
        self.repository = repository or GenerationJobRepository()
        self.credit_service = credit_service or CreditService()
        self.settings = get_settings()

    def new_job_id(self, job_type: str) -> str:
        return f"{job_type}_{uuid4().hex}"

    async def create_paid_job(
        self,
        *,
        user: dict,
        job_type: str,
        prompt: str,
        cost: int,
        model: str,
        reason: str,
        provider: str | None = None,
        input_path: str | None = None,
        metadata: dict | None = None,
        job_id: str | None = None,
        charge_on_success: bool = False,
    ) -> dict:
        plan = (user.get("plano") or "free").lower()
        queue_name, priority = queue_for_plan(plan)
        job_id = job_id or self.new_job_id(job_type)
        metadata_payload = {
            "plan": plan,
            "charge_on_success": bool(charge_on_success),
            "charge_reason": reason,
            **(metadata or {}),
        }

        self.repository.create_job(
            job_id=job_id,
            user_id=int(user["id"]),
            job_type=job_type,
            provider=provider,
            model=model,
            prompt=prompt,
            cost=cost,
            queue_name=queue_name,
            priority=priority,
            max_retries=self.settings.arq_max_retries,
            input_path=input_path,
            metadata=metadata_payload,
        )

        if charge_on_success:
            credit_balance = self.credit_service.get_balance(int(user["id"]))
            if cost > 0 and credit_balance < cost:
                self.repository.fail_job(job_id, error_message="Creditos insuficientes")
                self._cleanup_input(input_path, job_id)
                raise InsufficientCreditsError(balance=credit_balance, required=cost)
        else:
            try:
                credit_balance = self.credit_service.spend_credits(
                    user_id=int(user["id"]),
                    amount=cost,
                    reason=reason,
                    provider=provider,
                    model=model,
                    job_id=job_id,
                    metadata=metadata_payload,
                )
            except InsufficientCreditsError:
                self.repository.fail_job(job_id, error_message="Creditos insuficientes")
                self._cleanup_input(input_path, job_id)
                raise
            except Exception:
                self.repository.fail_job(job_id, error_message="Falha ao reservar creditos")
                self._cleanup_input(input_path, job_id)
                raise

        try:
            arq_job = await enqueue_generation_job(job_id, queue_name=queue_name)
            if arq_job is not None:
                self.repository.set_arq_job_id(job_id, arq_job.job_id)
        except Exception as exc:
            logger_jobs.exception("generation_enqueue_failed", extra={"job_id": job_id, "queue": queue_name})
            self.repository.fail_job(job_id, error_message=f"Falha ao enfileirar job: {exc}", dead_letter=True)
            self.refund_failed_job(job_id, error_message=str(exc))
            self._cleanup_input(input_path, job_id)
            raise

        job = self.repository.get_job(job_id) or {}
        return {
            "job": job,
            "credit_balance": credit_balance,
            "queue_name": queue_name,
            "priority": priority,
        }

    def get_job_for_user(self, job_id: str, user_id: int) -> dict | None:
        return self.repository.get_job(job_id, user_id=user_id)

    def list_jobs_for_user(self, user_id: int, limit: int = 50) -> list[dict]:
        return self.repository.list_user_jobs(user_id, limit=limit)

    def refund_failed_job(self, job_id: str, *, error_message: str | None = None) -> None:
        job = self.repository.get_job(job_id)
        if not job or job.get("refunded_at") or int(job.get("cost") or 0) <= 0:
            return

        metadata = job.get("metadata") or {}
        reason = str(metadata.get("charge_reason") or f"{job.get('job_type')}_generation")
        if not self.credit_service.transaction_exists(job_id=job_id, reason=reason, transaction_type="spend"):
            logger_jobs.info("generation_refund_skipped_no_spend", extra={"job_id": job_id, "reason": reason})
            return

        try:
            self.credit_service.refund_credits(
                user_id=int(job["user_id"]),
                amount=int(job["cost"]),
                reason="generation_failed_refund",
                provider=job.get("provider"),
                model=job.get("model"),
                job_id=job_id,
                metadata={
                    "job_type": job.get("job_type"),
                    "error_message": error_message or job.get("error_message"),
                },
            )
        except Exception as exc:
            if "uq_credit_refund_job_reason" not in str(exc):
                logger_jobs.exception("generation_refund_failed", extra={"job_id": job_id})
                raise

        self.repository.mark_refunded(job_id)
        logger_jobs.info(
            "generation_refunded",
            extra={"job_id": job_id, "user_id": job.get("user_id"), "cost": job.get("cost")},
        )

    def _cleanup_input(self, input_path: str | None, job_id: str) -> None:
        if not input_path:
            return
        if str(input_path).startswith(("http://", "https://")):
            return
        try:
            Path(input_path).unlink(missing_ok=True)
        except Exception:
            logger_jobs.warning("generation_input_cleanup_failed", extra={"job_id": job_id})
