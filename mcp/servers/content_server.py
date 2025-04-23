from fastapi import FastAPI
from pydantic import BaseModel
import logging

app = FastAPI(title="Content MCP Server")
logger = logging.getLogger(__name__)

class RequestModel(BaseModel):
    params: dict

@app.post("/{capability}")
async def handle(capability: str, req: RequestModel):
    logger.info(f"Content Agent handling {capability} with params {req.params}")
    return {"status": "success", "agent": "content", "capability": capability, "data": req.params}
