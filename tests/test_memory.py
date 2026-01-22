import sys
from types import ModuleType
from datetime import datetime, timedelta


class FakeCursor:
    def __init__(self):
        self.jobs = {}
        self.user_rows = []
        self.last_sql = None
        self.last_params = None

    def cursor(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        self.last_sql = sql.strip() if isinstance(sql, str) else ''
        self.last_params = params
        # INSERT into curation_jobs
        if 'INSERT INTO curation_jobs' in self.last_sql:
            job_id = params[0]
            user_id = params[1]
            params_json = params[2]
            self.jobs[job_id] = {'user_id': user_id, 'params': params_json, 'status': 'pending'}
        # UPDATE curation_jobs
        if self.last_sql.startswith('UPDATE curation_jobs'):
            # simple parse: params (status, summary, candidate_ids, id)
            status = params[0]
            job_id = params[3]
            if job_id in self.jobs:
                self.jobs[job_id]['status'] = status
                self.jobs[job_id]['summary'] = params[1]
                self.jobs[job_id]['candidate_ids'] = params[2]

        # SELECT from user_memory
        if 'FROM user_memory' in self.last_sql and 'SELECT id, tipo, conteudo' in self.last_sql:
            # nothing to do; fetchall will return self.user_rows
            pass

        # DELETE FROM user_memory
        if self.last_sql.startswith('DELETE FROM user_memory'):
            # params is tuple with list of ids
            ids = params[0]
            self.user_rows = [r for r in self.user_rows if r[0] not in ids]

    def fetchone(self):
        # SELECT job
        if 'SELECT user_id, params FROM curation_jobs' in self.last_sql or 'SELECT user_id, params' in self.last_sql:
            # find job by id in last_params
            job_id = self.last_params[0]
            job = self.jobs.get(job_id)
            if job:
                return (job['user_id'], job['params'])
            return None
        return None

    def fetchall(self):
        if 'FROM user_memory' in self.last_sql:
            return self.user_rows
        return []

    def commit(self):
        pass


class FakeDB:
    def __init__(self):
        self._conn = FakeCursor()

    def get_connection(self):
        return self._conn


def test_curation_job_create_and_process(monkeypatch):
    # Prepare fake modules before importing memory
    fake_dbmod = ModuleType('database_models')
    fake_db = FakeDB()
    fake_dbmod.get_db = lambda: fake_db
    sys.modules['database_models'] = fake_dbmod

    fake_emb = ModuleType('embeddings')
    fake_emb.embed_text = lambda t: [0.1] * 3
    fake_emb.embed_texts = lambda texts: [[0.1, 0.1, 0.1] for _ in texts]
    fake_emb.similarity = lambda a, b: 0.95
    sys.modules['embeddings'] = fake_emb

    # Now import memory after fakes are in place
    from memory import UserMemory

    user_id = 'user-123'

    # Seed some old user_memory rows (two similar entries)
    now = datetime.utcnow()
    id1 = 'm1'
    id2 = 'm2'
    fake_db._conn.user_rows = [
        (id1, 'nota', 'Conteúdo antigo A', 1, now - timedelta(days=365)),
        (id2, 'nota', 'Conteúdo antigo B', 1, now - timedelta(days=360)),
    ]

    # Create a curation job
    params = {'older_than_days': 30, 'similarity_threshold': 0.8, 'keep_top': 1}
    job_id = UserMemory.create_curation_job(user_id, params)
    assert job_id in fake_db._conn.jobs
    assert fake_db._conn.jobs[job_id]['status'] == 'pending'

    # Process the job (worker would call this)
    result = UserMemory.process_curate_job(job_id)
    # result should indicate curated items (we had 2 similar -> one removed)
    assert 'curated' in result
    assert fake_db._conn.jobs[job_id]['status'] == 'ready'

    # Finalize (approve) the job
    res2 = UserMemory.finalize_curation_job(job_id, approve=True)
    assert res2.get('status') == 'approved'
