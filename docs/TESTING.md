# MDex Omni-v5: Testing Strategy (Total Singularity)

The **Singularity Absoluta** milestone ensures that 100% of the core logic (`src/`) is covered by automated tests.

## 🧪 Testing Pillars

### 1. 100% Code Coverage
We utilize `pytest` and `pytest-cov` to monitor coverage. Every branch, error path, and edge case is targeted.
- **Pragma Policy**: Only environment-specific exits (sys.exit) or manual interrupts (KeyboardInterrupt) are excluded via `# pragma: no cover`.

### 2. Singularity Test Suite (`tests/test_singularity_100.py`)
A specialized suite designed to reach the unreachable lines:
- **API Down Simulation**: Verifies system resilience when MangaDex is offline.
- **Empty Title Handling**: Ensures CLI input validation.
- **Pagination Edge Cases**: Verifies that the provider correctly handles manga with hundreds of chapters.
- **AI Fault Injection**: Simulates Argos Translate model failures and verification of fallback mechanisms.

### 3. Asynchronous Mocking
Extensive use of `unittest.mock.AsyncMock` to simulate network latency and API responses without external dependency reliance.

## 🚀 Running the Audit

To verify the state of Total Singularity:

```powershell
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH="."
pytest --cov=src --cov-report=term-missing
```

---
**Status: 100% Coverage Reached | 68 Tests Passed.**
**Authority: L0g0rhythm Secure SDLC.**
