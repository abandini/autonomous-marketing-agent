# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands
- Install dependencies: `pip install -r requirements.txt`
- Run all tests: `python -m unittest discover tests`
- Run single test: `python -m unittest tests.test_name`
- Run the dashboard: `python examples/run_operator_dashboard.py`

## Code Style Guidelines
- **Imports**: Standard lib → Third-party → Local (absolute imports)
- **Naming**: Classes: PascalCase, Functions/variables: snake_case, Constants: UPPER_SNAKE_CASE
- **Types**: Use Python type annotations (Dict, List, Optional, Any)
- **Documentation**: Docstrings for modules/classes/functions with Args/Returns/Raises
- **Error handling**: Use try/except with proper logging and structured responses
- **Testing**: Use unittest framework with AAA pattern (Arrange, Act, Assert)

Always run tests after making changes: `python -m unittest discover tests`