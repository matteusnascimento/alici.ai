from __future__ import annotations

import pytest

import alici_api.jobs.generation_jobs as generation_jobs


class FakeGenerationRepo:
    def __init__(self):
        self.job = {
            "id": "job-1",
            "user_id": 7,
            "status": "queued",
            "job_type": "image",
            "provider": "replicate",
            "model": "flux",
            "prompt": "imagem",
            "cost": 10,
            "metadata": {"charge_on_success": True, "charge_reason": "image_generation"},
            "max_retries": 1,
            "progress": 0,
            "refunded_at": None,
        }

    def mark_processing(self, job_id):
        self.job["status"] = "processing"
        self.job["attempts"] = self.job.get("attempts", 0) + 1
        return dict(self.job)

    def update_progress(self, job_id, progress, *, status=None):
        self.job["progress"] = progress
        if status:
            self.job["status"] = status

    def complete_job(self, job_id, *, result_url=None, result_payload=None):
        self.job.update(status="completed", progress=100, result_url=result_url, result_payload=result_payload or {})
        return dict(self.job)

    def fail_job(self, job_id, *, error_message, dead_letter=False):
        self.job.update(status="dead_letter" if dead_letter else "failed", error_message=error_message)
        return dict(self.job)

    def mark_refunded(self, job_id):
        self.job["refunded_at"] = "now"

    def get_job(self, job_id):
        return dict(self.job)


class FakeCreditService:
    refunds = []
    spends = []
    existing_spend = False

    def transaction_exists(self, *, job_id, reason, transaction_type="grant"):
        return self.existing_spend and transaction_type == "spend" and job_id == "job-1" and reason == "image_generation"

    def refund_credits(self, **kwargs):
        self.refunds.append(kwargs)
        return 100

    def spend_credits(self, **kwargs):
        self.spends.append(kwargs)
        return 90


@pytest.mark.asyncio
async def test_arq_generation_job_refunds_on_dead_letter(monkeypatch):
    repo = FakeGenerationRepo()
    FakeCreditService.refunds = []
    FakeCreditService.existing_spend = True
    monkeypatch.setattr(generation_jobs, "GenerationJobRepository", lambda: repo)
    monkeypatch.setattr(generation_jobs, "CreditService", FakeCreditService)
    monkeypatch.setattr(generation_jobs, "generate_image", lambda prompt: (_ for _ in ()).throw(RuntimeError("upstream failed")))
    monkeypatch.setattr(generation_jobs, "capture_critical_event", lambda *args, **kwargs: None)

    with pytest.raises(RuntimeError):
        await generation_jobs.run_generation_job({"job_try": 1, "redis": None}, "job-1")

    assert repo.job["status"] == "dead_letter"
    assert repo.job["refunded_at"] == "now"
    assert FakeCreditService.refunds[0]["amount"] == 10
    assert FakeCreditService.refunds[0]["reason"] == "generation_failed_refund"


@pytest.mark.asyncio
async def test_arq_generation_job_charges_only_after_success(monkeypatch):
    repo = FakeGenerationRepo()
    FakeCreditService.spends = []
    FakeCreditService.existing_spend = False
    monkeypatch.setattr(generation_jobs, "GenerationJobRepository", lambda: repo)
    monkeypatch.setattr(generation_jobs, "CreditService", FakeCreditService)
    monkeypatch.setattr(generation_jobs, "generate_image", lambda prompt: "https://cdn.example.com/result.png")
    async def fake_set_payload(*args, **kwargs):
        return None

    monkeypatch.setattr(generation_jobs.AICache, "set_payload", fake_set_payload)

    result = await generation_jobs.run_generation_job({"job_try": 1, "redis": None}, "job-1")

    assert result["status"] == "completed"
    assert repo.job["status"] == "completed"
    assert FakeCreditService.spends[0]["amount"] == 10
    assert FakeCreditService.spends[0]["reason"] == "image_generation"
