from app.main import app


def test_home_page_loads():
    client = app.test_client()
    assert client.get("/").status_code == 200


def test_health():
    client = app.test_client()
    assert client.get("/health").status_code == 200


def test_quote_young_driver_costs_more():
    client = app.test_client()
    young = client.post("/api/quote", json={"vehicle_age": 3, "driver_age": 20, "vehicle_value": 10000})
    older = client.post("/api/quote", json={"vehicle_age": 3, "driver_age": 40, "vehicle_value": 10000})
    assert young.get_json()["premium"] > older.get_json()["premium"]