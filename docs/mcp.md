# MCP Suite Integration

This documentation covers the new MCP (Marketing Control Protocol) suite integrated into the GAMS framework.

## Architecture

- Each MCP server has:
  - A YAML descriptor in `mcp/servers/{id}.yaml` defining `id`, `title`, `auth`, `api.base_url`, and `max_calls_per_minute`.
  - A FastAPI stub in `mcp/servers/{id}_server.py` under `/mcp/{id}` path when running the resolver.

## Environment Variables

- `A2A_RESOLVER_URL`: URL for the A2A resolver (default: `http://localhost:8000/invoke`).
- `A2A_RESOLVER_BASE_URL`: Base URL for mounting MCP stubs (default: `http://localhost:8000`).
- API credentials for each MCP service:
  - `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`
  - `GA4_CLIENT_ID`, `GA4_CLIENT_SECRET`
  - `GSC_CLIENT_ID`, `GSC_CLIENT_SECRET`
  - `SEMRUSH_API_KEY`
  - `OPENAI_API_KEY`
  - ...

## Usage

1. **Scaffold descriptors & stubs**:
   ```bash
   python3 scripts/scaffold_mcp.py
   ```
2. **Start resolver**:
   ```bash
   uvicorn core.orchestrator.resolver:app --reload
   ```
3. **Invoke through BaseAgent**:
   ```python
   await agent.call_mcp("mcp.semrush", "search_products", {"keyword": "example"})
   ```
4. **Run tests**:
   ```bash
   pytest tests/test_integration_mcp.py
   ```

## CI

A GitHub Actions workflow `ci.yml` runs on `main` pushes/PRs:
- Python versions 3.8-3.10
- Installs deps + pytest
- Executes all tests

## Next Steps

- Implement real API integrations in stubs.
- Add more integration tests for other MCP services.
