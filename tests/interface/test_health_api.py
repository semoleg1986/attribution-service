from tests.interface._auth_helpers import build_client


def test_healthz() -> None:
    response = build_client().get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
