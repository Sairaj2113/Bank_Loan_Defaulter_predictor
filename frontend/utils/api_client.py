from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def _request_json(method: str, path: str, payload: dict | None = None, params: dict | None = None) -> dict:
    url = f"{BACKEND_URL.rstrip('/')}{path}"
    if params:
        query = urlencode({key: value for key, value in params.items() if value is not None})
        if query:
            url = f"{url}?{query}"

    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    request = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method=method,
    )

    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def get_health() -> dict:
    return _request_json("GET", "/health")


def get_db_health() -> dict:
    return _request_json("GET", "/db-health")


def get_customers(query: str | None = None, limit: int = 20, offset: int = 0) -> dict:
    return _request_json("GET", "/customers", params={"q": query, "limit": limit, "offset": offset})


def get_customer(customer_id: str) -> dict:
    return _request_json("GET", f"/customer/{customer_id}")


def get_predictions(limit: int = 20, offset: int = 0) -> dict:
    return _request_json("GET", "/predictions", params={"limit": limit, "offset": offset})


def predict_customer(customer_id: str, application_payload: dict) -> dict:
    return _request_json("POST", f"/predict/{customer_id}", payload=application_payload)