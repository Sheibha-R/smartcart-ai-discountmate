
from app import app, calculate_discount_percentage, find_items_by_name, recommend_best_value, enrich_product


def test_health():
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_no_plan_user_can_login():
    client = app.test_client()
    response = client.post("/login", json={
        "email": "maya.noplan@smartcart.demo",
        "password": "DemoPass123"
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["user"]["membership"] is None


def test_items_include_added_products():
    client = app.test_client()
    response = client.get("/api/items")
    items = response.get_json()["items"]
    assert "salmon" in items
    assert "beef" in items
    assert "broccoli" in items
    assert "tofu" in items
    assert "bananas" in items


def test_forgot_password():
    client = app.test_client()
    response = client.post("/forgot-password", json={
        "email": "maya.noplan@smartcart.demo"
    })
    assert response.status_code == 200
    assert "link has been sent" in response.get_json()["message"]


def test_payment_validation_rejects_low_balance():
    client = app.test_client()
    response = client.post("/validate-payment-step", json={
        "plan_id": "premium",
        "email": "test@smartcart.demo",
        "password": "Password123",
        "card_name": "Test User",
        "card_number": "12345678",
        "payment_method": "Card",
        "demo_balance": 1
    })
    assert response.status_code == 400


def test_payment_validation_rejects_card_ending_0000():
    client = app.test_client()
    response = client.post("/validate-payment-step", json={
        "plan_id": "basic",
        "email": "test@smartcart.demo",
        "password": "Password123",
        "card_name": "Test User",
        "card_number": "12340000",
        "payment_method": "Card",
        "demo_balance": 100
    })
    assert response.status_code == 400


def test_premium_guidance_for_premium_user():
    client = app.test_client()
    client.post("/login", json={
        "email": "alex.premium@smartcart.demo",
        "password": "DemoPass123"
    })
    response = client.get("/premium-guidance")
    assert response.status_code == 200
    data = response.get_json()
    assert data["enabled"] is True
    assert len(data["recommendations"]) > 0


def test_discount_calculation():
    assert calculate_discount_percentage(80, 100) == 20.0


def test_find_items():
    assert len(find_items_by_name("milk")) > 0


def test_best_value():
    result = recommend_best_value([{"price": 4}, {"price": 2}])
    assert result["price"] == 2


def test_enrich_product():
    product = {"price": 8, "previous_price": 10}
    enriched = enrich_product(product)
    assert enriched["discount_percentage"] == 20
