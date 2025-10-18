@echo off
set PYTHONPATH=%CD%\src
uv run python -m lockr.main %*
