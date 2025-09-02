from fastapi import FastAPI

app = FastAPI()


@app.post("/jobs")
async def create_job() -> dict:
    """Accept a new video generation job.

    TODO: validate input and enqueue job in the message broker.
    """
    return {"status": "accepted"}
