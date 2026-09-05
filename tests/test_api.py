

"""Integration Tests for FastAPI Endpoints"""
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_range_endpoint():
    response = client.post("/api/primes/range", json={"start": 1, "end": 20, "algorithm": "segmented"})
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 8
    assert data["primes"] == [2, 3, 5, 7, 11, 13, 17, 19]


def test_api_check_prime_endpoint():
    response = client.post("/api/primes/check", json={"number": 17, "algorithm": "trial"})
    assert response.status_code == 200
    assert response.json()["is_prime"] is True

    response_comp = client.post("/api/primes/check", json={"number": 18, "algorithm": "trial"})
    assert response_comp.status_code == 200
    assert response_comp.json()["is_prime"] is False


def test_api_nth_prime_endpoint():
    response = client.post("/api/primes/nth", json={"n": 10})
    assert response.status_code == 200
    assert response.json()["nth_prime"] == 29
