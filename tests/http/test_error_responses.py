"""Small HTTP contract tests to ensure domain exceptions are translated.

We exercise the endpoints that raise those exceptions via dependency overrides so
we hit the global exception handlers implemented on the FastAPI app.
"""

from fastapi.testclient import TestClient
from app.adapters.http.api import create_app
from app.domain.exceptions import UserNotFoundError, EmailAlreadyRegisteredError


def test_user_not_found_is_translated_to_404():
    app = create_app()

    # Inject a dependency that will raise UserNotFoundError when called.
    class _RaiseUseCase:
        def execute(self, *_, **__):
            raise UserNotFoundError("x@example.com")

    app.dependency_overrides.clear()
    # The users router wires use cases to dependencies; we override the
    # use case provider used by the GET /users/{email} endpoint.
    from app.adapters.http.dependencies import get_user_by_email_use_case

    app.dependency_overrides[get_user_by_email_use_case] = lambda: _RaiseUseCase()

    client = TestClient(app)
    resp = client.get("/users/x@example.com")

    assert resp.status_code == 404
    body = resp.json()
    assert body["detail"] == "User not found: x@example.com"
    assert body["code"] == "user_not_found"
    assert "trace_id" in body
    # trace id is also set as a response header and should match
    assert resp.headers.get("X-Trace-Id") == body["trace_id"]


def test_email_already_registered_translated_to_400():
    app = create_app()

    class _RaiseCreateUseCase:
        def execute(self, *_, **__):
            raise EmailAlreadyRegisteredError("dupe@example.com")

    from app.adapters.http.dependencies import get_create_user_use_case

    app.dependency_overrides.clear()
    app.dependency_overrides[get_create_user_use_case] = lambda: _RaiseCreateUseCase()

    client = TestClient(app)
    resp = client.post("/users", json={"name": "X", "email": "dupe@example.com", "password": "p"})

    assert resp.status_code == 400
    body = resp.json()
    assert body["detail"] == "Email already registered: dupe@example.com"
    assert body["code"] == "email_already_registered"
    assert "trace_id" in body
    assert resp.headers.get("X-Trace-Id") == body["trace_id"]
