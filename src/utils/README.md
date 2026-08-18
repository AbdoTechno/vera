# Shared Utilities (`src/utils/`)

This module provides logging, environment helpers, and text sanitization functions used across the platform.

---

## Core Utilities

1. **Structured Logging (`logger.py`)**:
   - Configures formatted standard-output stream logging (`sys.stdout`) compatible with cloud container runners (Railway, Docker, Hugging Face Spaces).
   - Safe non-blocking file-logging fallbacks for local development environments.

2. **Helper Functions**:
   - UTF-8 JSON serialization and deserialization.
   - Text sanitization, regex cleanup, and citation parsing helpers.
