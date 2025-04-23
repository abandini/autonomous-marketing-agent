from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import asyncio
import logging
import glob
import importlib
import yaml
import httpx
from main import MarketingAgentApp

app = FastAPI(title="A2A Resolver")
logger = logging.getLogger(__name__)

CONFIG_PATH = os.getenv("CONFIG_PATH", "config/default.yaml")
resolver = MarketingAgentApp(config_path=CONFIG_PATH)

@app.on_event("startup")
async def startup_event():
    # Initialize orchestrator and agents at startup
    await resolver.initialize()
    # Load MCP descriptors
    resolver.mcp_descriptors = []
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    mcp_dir = os.path.join(project_root, 'mcp', 'servers')
    for yaml_file in glob.glob(os.path.join(mcp_dir, '*.yaml')):
        try:
            with open(yaml_file) as f:
                resolver.mcp_descriptors.append(yaml.safe_load(f))
        except Exception as e:
            logger.error(f"Failed to load MCP descriptor {yaml_file}: {str(e)}")
    # Mount MCP stub applications
    for pyfile in glob.glob(os.path.join(mcp_dir, '*_server.py')):
        module_name = 'mcp.servers.' + os.path.basename(pyfile)[:-3]
        try:
            mod = importlib.import_module(module_name)
            stub_id = os.path.basename(pyfile).replace('_server.py', '')
            app.mount(f"/mcp/{stub_id}", mod.app)
            logger.info(f"Mounted MCP stub /mcp/{stub_id}")
        except Exception as e:
            logger.error(f"Failed to mount MCP stub {module_name}: {str(e)}")

class Invocation(BaseModel):
    agent: str
    capability: str
    params: dict = {}

@app.post("/invoke")
async def invoke(inv: Invocation):
    logger.info(f"Invoke request: agent={inv.agent}, capability={inv.capability}")
    # Application agents
    agent = resolver.agents.get(inv.agent)
    if agent:
        action = agent.actions.get(inv.capability)
        if not action:
            raise HTTPException(status_code=404, detail=f"Capability '{inv.capability}' not found for agent '{inv.agent}'")
        if asyncio.iscoroutinefunction(action):
            result = await action(inv.params)
        else:
            result = action(inv.params)
        return {"status": "success", "result": result}
    # MCP agents
    mcp_ids = [d.get('id') for d in getattr(resolver, 'mcp_descriptors', [])]
    if inv.agent in mcp_ids:
        stub_id = inv.agent.split('.')[-1]
        base_url = os.getenv("A2A_RESOLVER_BASE_URL", "http://localhost:8000")
        url = f"{base_url}/mcp/{stub_id}/{inv.capability}"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(url, json={"params": inv.params})
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"MCP '{inv.agent}' call failed: {str(e)}")
    # Unknown agent
    raise HTTPException(status_code=404, detail=f"Agent '{inv.agent}' not found")
