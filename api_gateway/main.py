from fastapi import FastAPI

app = FastAPI()


@app.post("/create_job")
async def create_job() -> dict:
    """Accept a new video generation job.

    TODO: validate input and enqueue job in the message broker.
    """
    return {"status": "accepted"}
