from celery import Celery

app = Celery("orchestrator")


@app.task
def process_job(job_id: str) -> None:
    """Split scenario into chapters and create sub-tasks.

    TODO: implement orchestration logic and track segment readiness.
    """
    pass
