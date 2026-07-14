"""V1 API package initialization."""

# Intentionally do not import submodules here to avoid side effects on package import.
# Submodules like `health`, `ingest`, and `chat` should be imported explicitly
# by consumers (e.g., in routes.py) using `from app.api.v1 import health` or
# `from app.api.v1 import chat` which triggers proper submodule loading.

__all__: list[str] = []
