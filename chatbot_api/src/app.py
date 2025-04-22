import logging
from typing import Dict, Optional
from fastapi import FastAPI, HTTPException

from agent import get_agent_response
from utils import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Chatbot API",
    description="This API allows interaction with a chatbot.",
    version="1.0.0",
    contact={
        "name": "Thach Le",
        "email": "thach.le.tech@gmail.com",
    }
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/chat/complete")
async def complete(data: Dict):
    user_message = data['message']
    response = get_agent_response(user_message)
    logger.info(f"Complete message: {user_message} --> {response}")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, workers=1, log_level="info")
