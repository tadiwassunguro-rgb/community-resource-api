def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_create_and_fetch_resource(client):
    created = client.post(
        "/api/resources",
        json={
            "name": "School laptops",
            "category": "education",
            "quantity": 10,
        },
    )

    assert created.status_code == 201
    resource_id = created.get_json()["id"]

    fetched = client.get(f"/api/resources/{resource_id}")

    assert fetched.status_code == 200
    assert fetched.get_json()["name"] == "School laptops"
    assert fetched.get_json()["quantity"] == 10


def test_invalid_resource_is_rejected(client):
    response = client.post(
        "/api/resources",
        json={
            "name": "",
            "category": "education",
            "quantity": -1,
        },
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_request_reduces_available_quantity(client):
    resource = client.post(
        "/api/resources",
        json={
            "name": "Internet vouchers",
            "category": "connectivity",
            "quantity": 8,
        },
    ).get_json()

    response = client.post(
        "/api/requests",
        json={
            "resource_id": resource["id"],
            "requester": "Youth Centre",
            "quantity": 3,
        },
    )

    assert response.status_code == 201

    updated = client.get(
        f"/api/resources/{resource['id']}"
    ).get_json()

    assert updated["quantity"] == 5


def test_request_cannot_exceed_inventory(client):
    resource = client.post(
        "/api/resources",
        json={
            "name": "Tablets",
            "category": "education",
            "quantity": 2,
        },
    ).get_json()

    response = client.post(
        "/api/requests",
        json={
            "resource_id": resource["id"],
            "requester": "Community Centre",
            "quantity": 5,
        },
    )

    assert response.status_code == 409
    assert response.get_json()["error"] == "insufficient resource quantity"


def test_metrics(client):
    client.post(
        "/api/resources",
        json={
            "name": "Books",
            "category": "education",
            "quantity": 20,
        },
    )

    response = client.get("/metrics")

    assert response.status_code == 200
    data = response.get_json()
    assert data["resources_total"] == 1
    assert "http_requests_total" in data
