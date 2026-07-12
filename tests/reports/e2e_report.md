# E2e Test Suite Report

Generated at: 2026-07-12 23:46:31
**Status**: PASSED
**Exit Code**: 0

## Test Execution Details
```text
C:\Users\ASUS\anaconda3\Lib\site-packages\pytest_asyncio\plugin.py:208: PytestDeprecationWarning: The configuration option "asyncio_default_fixture_loop_scope" is unset.
The event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: "function", "class", "module", "package", "session"

  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-8.3.3, pluggy-1.5.0 -- C:\Users\ASUS\anaconda3\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\ASUS\bit-mesra-ai-agent\tests
configfile: pytest.ini
plugins: anyio-4.13.0, langsmith-0.8.9, locust-2.44.4, asyncio-0.24.0, cov-7.1.0
asyncio: mode=Mode.AUTO, default_loop_scope=None
collecting ... collected 108 items / 106 deselected / 2 selected

tests\e2e\test_student_workflows.py::test_student_authentication_and_workspace_e2e[asyncio] PASSED [ 50%]
tests\e2e\test_student_workflows.py::test_student_chat_multi_turn_e2e[asyncio] PASSED [100%]

===================== 2 passed, 106 deselected in 41.74s ======================

```
