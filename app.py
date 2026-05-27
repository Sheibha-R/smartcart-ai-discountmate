
from flask import Flask, jsonify, request, render_template, session
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import random
import string

app = Flask(__name__)
app.secret_key = "smartcart-ai-discountmate-demo-secret"

REQUEST_COUNTER = Counter(
    "smartcart_requests_total",
    "Total number of requests made to SmartCart AI",
    ["endpoint"]
)

LOCATION_ON_VALUES = ["while_using", "always"]

USERS = {
    "maya.noplan@smartcart.demo": {
        "name": "Maya NoPlan",
        "email": "maya.noplan@smartcart.demo",
        "password": "DemoPass123",
        "membership": None,
        "location_access": "off",
        "usage_count": 0,
        "family_profile": []
    },
    "ben.basic@smartcart.demo": {
        "name": "Ben Basic",
        "email": "ben.basic@smartcart.demo",
        "password": "DemoPass123",
        "membership": {"plan_id": "basic", "plan_name": "Basic Saver", "discount": 5},
        "location_access": "while_using",
        "usage_count": 3,
        "family_profile": []
    },
    "priya.plus@smartcart.demo": {
        "name": "Priya Plus",
        "email": "priya.plus@smartcart.demo",
        "password": "DemoPass123",
        "membership": {"plan_id": "plus", "plan_name": "Smart Plus", "discount": 10},
        "location_access": "always",
        "usage_count": 14,
        "family_profile": []
    },
    "alex.premium@smartcart.demo": {
        "name": "Alex Premium",
        "email": "alex.premium@smartcart.demo",
        "password": "DemoPass123",
        "membership": {"plan_id": "premium", "plan_name": "AI Premium", "discount": 15},
        "location_access": "off",
        "usage_count": 21,
        "family_profile": [
            {"name": "Alex", "age": 34, "routine": "Work", "lifestyle": "Gym and fitness"},
            {"name": "Sam", "age": 32, "routine": "Business", "lifestyle": "Yoga"},
            {"name": "Mia", "age": 9, "routine": "School", "lifestyle": "Play time"},
            {"name": "George", "age": 70, "routine": "Retired", "lifestyle": "Meditation"}
        ]
    }
}

GROCERY_DATA = [
    {"id": 1, "item": "milk", "brand": "DairyBest", "store": "Woolworths", "price": 3.20, "previous_price": 3.80, "category": "Dairy", "rating": 4.5, "image": "🥛", "calories": 120, "weight": "1L", "diet": "vegetarian"},
    {"id": 2, "item": "milk", "brand": "FarmFresh", "store": "Coles", "price": 3.50, "previous_price": 3.50, "category": "Dairy", "rating": 4.2, "image": "🥛", "calories": 125, "weight": "1L", "diet": "vegetarian"},
    {"id": 3, "item": "milk", "brand": "BudgetMilk", "store": "Aldi", "price": 2.95, "previous_price": 3.30, "category": "Dairy", "rating": 4.0, "image": "🥛", "calories": 115, "weight": "1L", "diet": "vegetarian"},
    {"id": 4, "item": "bread", "brand": "BakeHouse", "store": "Woolworths", "price": 2.40, "previous_price": 3.00, "category": "Bakery", "rating": 4.4, "image": "🍞", "calories": 80, "weight": "1 loaf", "diet": "vegetarian"},
    {"id": 5, "item": "bread", "brand": "DailyLoaf", "store": "Aldi", "price": 2.10, "previous_price": 2.60, "category": "Bakery", "rating": 4.1, "image": "🍞", "calories": 75, "weight": "1 loaf", "diet": "vegetarian"},
    {"id": 6, "item": "rice", "brand": "SunRice", "store": "Coles", "price": 8.50, "previous_price": 9.20, "category": "Pantry", "rating": 4.6, "image": "🍚", "calories": 210, "weight": "2kg", "diet": "vegetarian"},
    {"id": 7, "item": "rice", "brand": "BudgetGrain", "store": "Aldi", "price": 6.90, "previous_price": 7.50, "category": "Pantry", "rating": 4.0, "image": "🍚", "calories": 205, "weight": "2kg", "diet": "vegetarian"},
    {"id": 8, "item": "eggs", "brand": "FarmEggs", "store": "Woolworths", "price": 5.20, "previous_price": 6.00, "category": "Protein", "rating": 4.3, "image": "🥚", "calories": 70, "weight": "12 pack", "diet": "vegetarian"},
    {"id": 9, "item": "eggs", "brand": "ValueEggs", "store": "Aldi", "price": 4.60, "previous_price": 5.10, "category": "Protein", "rating": 4.0, "image": "🥚", "calories": 68, "weight": "12 pack", "diet": "vegetarian"},
    {"id": 10, "item": "pasta", "brand": "Italiano", "store": "Coles", "price": 2.80, "previous_price": 3.40, "category": "Pantry", "rating": 4.4, "image": "🍝", "calories": 180, "weight": "500g", "diet": "vegetarian"},
    {"id": 11, "item": "pasta", "brand": "BudgetPasta", "store": "Aldi", "price": 1.90, "previous_price": 2.30, "category": "Pantry", "rating": 3.9, "image": "🍝", "calories": 175, "weight": "500g", "diet": "vegetarian"},
    {"id": 12, "item": "chicken", "brand": "FreshFarm Chicken", "store": "Coles", "price": 10.90, "previous_price": 12.50, "category": "Protein", "rating": 4.5, "image": "🍗", "calories": 240, "weight": "1kg", "diet": "non-vegetarian"},
    {"id": 13, "item": "chicken", "brand": "Budget Chicken", "store": "Aldi", "price": 9.40, "previous_price": 10.20, "category": "Protein", "rating": 4.1, "image": "🍗", "calories": 235, "weight": "1kg", "diet": "non-vegetarian"},
    {"id": 14, "item": "apples", "brand": "Fresh Apples", "store": "Woolworths", "price": 4.20, "previous_price": 5.00, "category": "Fruit", "rating": 4.6, "image": "🍎", "calories": 95, "weight": "1kg", "diet": "vegetarian"},
    {"id": 15, "item": "apples", "brand": "Value Apples", "store": "Aldi", "price": 3.60, "previous_price": 4.20, "category": "Fruit", "rating": 4.2, "image": "🍎", "calories": 90, "weight": "1kg", "diet": "vegetarian"},
    {"id": 16, "item": "salmon", "brand": "OceanFresh Salmon", "store": "Woolworths", "price": 14.80, "previous_price": 17.00, "category": "Protein", "rating": 4.7, "image": "🐟", "calories": 280, "weight": "500g", "diet": "non-vegetarian"},
    {"id": 17, "item": "salmon", "brand": "Coles Tasmanian Salmon", "store": "Coles", "price": 15.30, "previous_price": 16.80, "category": "Protein", "rating": 4.5, "image": "🐟", "calories": 285, "weight": "500g", "diet": "non-vegetarian"},
    {"id": 19, "item": "beef", "brand": "Lean Beef Mince", "store": "Coles", "price": 12.50, "previous_price": 14.20, "category": "Protein", "rating": 4.4, "image": "🥩", "calories": 310, "weight": "500g", "diet": "non-vegetarian"},
    {"id": 20, "item": "beef", "brand": "Woolworths Beef Mince", "store": "Woolworths", "price": 13.10, "previous_price": 15.00, "category": "Protein", "rating": 4.5, "image": "🥩", "calories": 315, "weight": "500g", "diet": "non-vegetarian"},
    {"id": 21, "item": "beef", "brand": "Aldi Market Beef", "store": "Aldi", "price": 11.80, "previous_price": 13.40, "category": "Protein", "rating": 4.2, "image": "🥩", "calories": 305, "weight": "500g", "diet": "non-vegetarian"},
    {"id": 22, "item": "tuna", "brand": "SeaCan Tuna", "store": "Aldi", "price": 4.10, "previous_price": 4.90, "category": "Protein", "rating": 4.2, "image": "🐟", "calories": 130, "weight": "425g", "diet": "non-vegetarian"},
    {"id": 23, "item": "tuna", "brand": "John West Tuna", "store": "Woolworths", "price": 4.70, "previous_price": 5.50, "category": "Protein", "rating": 4.5, "image": "🐟", "calories": 135, "weight": "425g", "diet": "non-vegetarian"},
    {"id": 24, "item": "tuna", "brand": "Coles Tuna Chunks", "store": "Coles", "price": 4.40, "previous_price": 5.20, "category": "Protein", "rating": 4.3, "image": "🐟", "calories": 132, "weight": "425g", "diet": "non-vegetarian"},
    {"id": 25, "item": "prawns", "brand": "Coastal Prawns", "store": "Woolworths", "price": 11.90, "previous_price": 13.50, "category": "Protein", "rating": 4.3, "image": "🍤", "calories": 160, "weight": "500g", "diet": "non-vegetarian"},
    {"id": 26, "item": "prawns", "brand": "Coles Cooked Prawns", "store": "Coles", "price": 12.40, "previous_price": 14.20, "category": "Protein", "rating": 4.4, "image": "🍤", "calories": 165, "weight": "500g", "diet": "non-vegetarian"},
    {"id": 28, "item": "turkey", "brand": "Turkey Slices", "store": "Coles", "price": 6.70, "previous_price": 7.80, "category": "Protein", "rating": 4.1, "image": "🥪", "calories": 110, "weight": "250g", "diet": "non-vegetarian"},
    {"id": 29, "item": "turkey", "brand": "Woolworths Turkey Breast", "store": "Woolworths", "price": 7.20, "previous_price": 8.30, "category": "Protein", "rating": 4.3, "image": "🥪", "calories": 115, "weight": "250g", "diet": "non-vegetarian"},
    {"id": 31, "item": "lamb", "brand": "Aussie Lamb", "store": "Aldi", "price": 13.40, "previous_price": 15.00, "category": "Protein", "rating": 4.5, "image": "🥩", "calories": 330, "weight": "500g", "diet": "non-vegetarian"},
    {"id": 32, "item": "lamb", "brand": "Coles Lamb Cuts", "store": "Coles", "price": 14.20, "previous_price": 16.00, "category": "Protein", "rating": 4.4, "image": "🥩", "calories": 335, "weight": "500g", "diet": "non-vegetarian"},
    {"id": 33, "item": "lamb", "brand": "Woolworths Lamb", "store": "Woolworths", "price": 14.70, "previous_price": 16.50, "category": "Protein", "rating": 4.6, "image": "🥩", "calories": 340, "weight": "500g", "diet": "non-vegetarian"},
    {"id": 34, "item": "broccoli", "brand": "GreenFarm Broccoli", "store": "Woolworths", "price": 3.10, "previous_price": 3.80, "category": "Vegetable", "rating": 4.6, "image": "🥦", "calories": 55, "weight": "500g", "diet": "vegetarian"},
    {"id": 35, "item": "broccoli", "brand": "Coles Broccoli", "store": "Coles", "price": 3.30, "previous_price": 4.00, "category": "Vegetable", "rating": 4.4, "image": "🥦", "calories": 56, "weight": "500g", "diet": "vegetarian"},
    {"id": 36, "item": "broccoli", "brand": "Aldi Fresh Broccoli", "store": "Aldi", "price": 2.80, "previous_price": 3.50, "category": "Vegetable", "rating": 4.2, "image": "🥦", "calories": 54, "weight": "500g", "diet": "vegetarian"},
    {"id": 37, "item": "spinach", "brand": "Fresh Spinach", "store": "Coles", "price": 3.40, "previous_price": 4.00, "category": "Vegetable", "rating": 4.4, "image": "🥬", "calories": 45, "weight": "300g", "diet": "vegetarian"},
    {"id": 38, "item": "spinach", "brand": "Woolworths Baby Spinach", "store": "Woolworths", "price": 3.60, "previous_price": 4.30, "category": "Vegetable", "rating": 4.5, "image": "🥬", "calories": 46, "weight": "300g", "diet": "vegetarian"},
    {"id": 39, "item": "spinach", "brand": "Aldi Spinach Leaves", "store": "Aldi", "price": 3.00, "previous_price": 3.70, "category": "Vegetable", "rating": 4.1, "image": "🥬", "calories": 44, "weight": "300g", "diet": "vegetarian"},
    {"id": 40, "item": "carrots", "brand": "Value Carrots", "store": "Aldi", "price": 2.20, "previous_price": 2.80, "category": "Vegetable", "rating": 4.2, "image": "🥕", "calories": 50, "weight": "1kg", "diet": "vegetarian"},
    {"id": 41, "item": "carrots", "brand": "Coles Carrots", "store": "Coles", "price": 2.60, "previous_price": 3.10, "category": "Vegetable", "rating": 4.3, "image": "🥕", "calories": 52, "weight": "1kg", "diet": "vegetarian"},
    {"id": 43, "item": "lentils", "brand": "Protein Lentils", "store": "Coles", "price": 3.80, "previous_price": 4.50, "category": "Pantry", "rating": 4.5, "image": "🫘", "calories": 230, "weight": "500g", "diet": "vegetarian"},
    {"id": 44, "item": "lentils", "brand": "Aldi Lentils", "store": "Aldi", "price": 3.30, "previous_price": 4.00, "category": "Pantry", "rating": 4.2, "image": "🫘", "calories": 225, "weight": "500g", "diet": "vegetarian"},
    {"id": 45, "item": "lentils", "brand": "Woolworths Lentils", "store": "Woolworths", "price": 4.00, "previous_price": 4.60, "category": "Pantry", "rating": 4.4, "image": "🫘", "calories": 232, "weight": "500g", "diet": "vegetarian"},
    {"id": 46, "item": "tofu", "brand": "PlantPower Tofu", "store": "Woolworths", "price": 4.60, "previous_price": 5.30, "category": "Protein", "rating": 4.3, "image": "⬜", "calories": 180, "weight": "450g", "diet": "vegetarian"},
    {"id": 47, "item": "tofu", "brand": "Coles Firm Tofu", "store": "Coles", "price": 4.40, "previous_price": 5.10, "category": "Protein", "rating": 4.2, "image": "⬜", "calories": 178, "weight": "450g", "diet": "vegetarian"},
    {"id": 48, "item": "tofu", "brand": "Aldi Tofu Block", "store": "Aldi", "price": 3.90, "previous_price": 4.70, "category": "Protein", "rating": 4.0, "image": "⬜", "calories": 176, "weight": "450g", "diet": "vegetarian"},
    {"id": 49, "item": "oats", "brand": "Morning Oats", "store": "Aldi", "price": 3.30, "previous_price": 4.10, "category": "Breakfast", "rating": 4.6, "image": "🥣", "calories": 150, "weight": "1kg", "diet": "vegetarian"},
    {"id": 50, "item": "oats", "brand": "Uncle Tobys Oats", "store": "Woolworths", "price": 4.20, "previous_price": 5.10, "category": "Breakfast", "rating": 4.7, "image": "🥣", "calories": 155, "weight": "1kg", "diet": "vegetarian"},
    {"id": 51, "item": "oats", "brand": "Coles Rolled Oats", "store": "Coles", "price": 3.80, "previous_price": 4.50, "category": "Breakfast", "rating": 4.4, "image": "🥣", "calories": 152, "weight": "1kg", "diet": "vegetarian"},
    {"id": 52, "item": "yogurt", "brand": "Greek Yogurt", "store": "Coles", "price": 5.50, "previous_price": 6.40, "category": "Dairy", "rating": 4.7, "image": "🥛", "calories": 140, "weight": "1kg", "diet": "vegetarian"},
    {"id": 53, "item": "yogurt", "brand": "Woolworths Greek Yogurt", "store": "Woolworths", "price": 5.80, "previous_price": 6.70, "category": "Dairy", "rating": 4.6, "image": "🥛", "calories": 142, "weight": "1kg", "diet": "vegetarian"},
    {"id": 54, "item": "yogurt", "brand": "Aldi Natural Yogurt", "store": "Aldi", "price": 4.90, "previous_price": 5.80, "category": "Dairy", "rating": 4.3, "image": "🥛", "calories": 138, "weight": "1kg", "diet": "vegetarian"},
    {"id": 55, "item": "chickpeas", "brand": "Smart Chickpeas", "store": "Woolworths", "price": 2.40, "previous_price": 3.00, "category": "Pantry", "rating": 4.4, "image": "🫘", "calories": 210, "weight": "400g", "diet": "vegetarian"},
    {"id": 56, "item": "chickpeas", "brand": "Coles Chickpeas", "store": "Coles", "price": 2.20, "previous_price": 2.80, "category": "Pantry", "rating": 4.3, "image": "🫘", "calories": 208, "weight": "400g", "diet": "vegetarian"},
    {"id": 58, "item": "bananas", "brand": "Fresh Bananas", "store": "Aldi", "price": 3.20, "previous_price": 3.90, "category": "Fruit", "rating": 4.5, "image": "🍌", "calories": 105, "weight": "1kg", "diet": "vegetarian"},
    {"id": 59, "item": "bananas", "brand": "Coles Bananas", "store": "Coles", "price": 3.60, "previous_price": 4.20, "category": "Fruit", "rating": 4.4, "image": "🍌", "calories": 106, "weight": "1kg", "diet": "vegetarian"},
    {"id": 60, "item": "bananas", "brand": "Woolworths Bananas", "store": "Woolworths", "price": 3.80, "previous_price": 4.50, "category": "Fruit", "rating": 4.6, "image": "🍌", "calories": 108, "weight": "1kg", "diet": "vegetarian"}
]

OFFERS = [
    {"title": "Weekend Grocery Saver", "description": "Up to 18% off selected pantry and dairy products.", "valid_until": "Sunday"},
    {"title": "Student Budget Basket", "description": "Extra savings on bread, pasta, rice, and milk.", "valid_until": "Friday"},
    {"title": "Family Essentials Deal", "description": "Bundle discounts for chicken, eggs, rice, and apples.", "valid_until": "Next week"}
]

COUPONS = {
    "SAVE10": {"type": "percentage", "value": 10, "description": "10% off your cart"},
    "STUDENT15": {"type": "percentage", "value": 15, "description": "15% student discount"},
    "SMART5": {"type": "fixed", "value": 5, "description": "$5 off your cart"}
}

MEMBERSHIP_PLANS = [
    {
        "id": "basic",
        "name": "Basic Saver",
        "price": 4.99,
        "discount": 5,
        "requires_location": True,
        "requires_family": False,
        "features": [
            "5% member discount",
            "Basic price alerts",
            "Monthly savings report",
            "Nearby store search when location is enabled"
        ]
    },
    {
        "id": "plus",
        "name": "Smart Plus",
        "price": 9.99,
        "discount": 10,
        "requires_location": True,
        "requires_family": False,
        "features": [
            "10% member discount",
            "Priority offers",
            "Smart substitute alerts",
            "Weekly savings report",
            "Nearby store search when location is enabled",
            "Extra usage-based app discounts"
        ]
    },
    {
        "id": "premium",
        "name": "AI Premium",
        "price": 14.99,
        "discount": 15,
        "requires_location": False,
        "requires_family": True,
        "features": [
            "15% member discount",
            "Advanced AI recommendations",
            "Early offer access",
            "Premium dashboard insights",
            "Customised meal planning for budget, fitness, families, kids and seniors"
        ]
    }
]


def get_current_user():
    email = session.get("user_email")
    return USERS.get(email) if email else None


def public_user(user):
    if not user:
        return None
    return {
        "name": user["name"],
        "email": user["email"],
        "membership": user["membership"],
        "location_access": user["location_access"],
        "usage_count": user["usage_count"],
        "family_profile": user.get("family_profile", [])
    }


def generate_captcha():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=5))


def calculate_discount_percentage(current_price, previous_price):
    if previous_price <= 0:
        return 0
    return round(((previous_price - current_price) / previous_price) * 100, 2)


def enrich_product(product):
    enriched = product.copy()
    enriched["discount_percentage"] = calculate_discount_percentage(product["price"], product["previous_price"])
    enriched["saving"] = round(product["previous_price"] - product["price"], 2)

    if enriched["discount_percentage"] >= 15:
        enriched["recommendation"] = "Buy now"
        enriched["confidence"] = "High"
    elif enriched["discount_percentage"] >= 8:
        enriched["recommendation"] = "Good deal"
        enriched["confidence"] = "Medium"
    else:
        enriched["recommendation"] = "Wait"
        enriched["confidence"] = "Low"

    return enriched


def find_items_by_name(item_name):
    return [product for product in GROCERY_DATA if product["item"].lower() == item_name.lower()]


def recommend_best_value(products):
    if not products:
        return None
    return min(products, key=lambda product: product["price"])


def get_usage_bonus(user):
    if not user or not user.get("membership") or user["membership"]["plan_id"] != "plus":
        return 0

    usage_count = user.get("usage_count", 0)

    if usage_count >= 20:
        return 5
    if usage_count >= 10:
        return 3
    if usage_count >= 5:
        return 1

    return 0


def build_nearby_store_result(user, item_name):
    if not user or not user.get("membership"):
        return {
            "enabled": False,
            "visible": False,
            "message": "Nearby store search is available for Basic Saver and Smart Plus members.",
            "stores": []
        }

    plan_id = user["membership"]["plan_id"]

    if plan_id not in ["basic", "plus"]:
        return {
            "enabled": False,
            "visible": False,
            "message": "Nearby store search is not included in this plan.",
            "stores": []
        }

    if user.get("location_access") not in LOCATION_ON_VALUES:
        return {
            "enabled": False,
            "visible": True,
            "message": "Benefits can be well used only while location is accessed.",
            "stores": []
        }

    products = [enrich_product(product) for product in find_items_by_name(item_name)]
    stores = []

    for product in products:
        stores.append({
            "store": product["store"],
            "brand": product["brand"],
            "price": product["price"],
            "discount_percentage": product["discount_percentage"],
            "distance": round(random.uniform(0.4, 4.8), 1),
            "eta": random.choice(["5 min", "8 min", "12 min", "15 min"])
        })

    return {
        "enabled": True,
        "visible": True,
        "message": "Location-enabled nearby store search is active.",
        "stores": sorted(stores, key=lambda item: item["price"])
    }


def choose_meal_product_for_person(person, index):
    age = int(person.get("age", 0))
    routine = person.get("routine", "Not regular")
    lifestyle = person.get("lifestyle", "Not so active")

    if age <= 12 or routine == "School":
        item_names = ["milk", "eggs", "bananas", "apples", "yogurt", "oats", "bread"]
    elif age >= 65 or routine == "Retired":
        item_names = ["spinach", "broccoli", "lentils", "tofu", "salmon", "yogurt", "rice"]
    elif lifestyle == "Gym and fitness":
        item_names = ["chicken", "eggs", "tofu", "lentils", "salmon", "beef", "yogurt"]
    elif lifestyle in ["Yoga", "Meditation"]:
        item_names = ["spinach", "broccoli", "tofu", "chickpeas", "oats", "bananas", "rice"]
    elif lifestyle == "Play time":
        item_names = ["bananas", "apples", "milk", "bread", "eggs", "pasta", "yogurt"]
    else:
        item_names = ["rice", "pasta", "broccoli", "carrots", "lentils", "tofu", "chickpeas"]

    pool = [item for item in GROCERY_DATA if item["item"] in item_names]
    seed_value = sum(ord(char) for char in person.get("name", "")) + age + index * 11 + len(routine) + len(lifestyle)
    return enrich_product(pool[seed_value % len(pool)])


def build_premium_meal_guidance(user):
    if not user or not user.get("membership") or user["membership"]["plan_id"] != "premium":
        return {
            "enabled": False,
            "visible": False,
            "message": "Login with AI Premium to unlock meal and wellness guidance.",
            "recommendations": []
        }

    family = user.get("family_profile", [])

    if not family:
        return {
            "enabled": True,
            "visible": True,
            "message": "AI Premium is active. Add family details for personalised guidance.",
            "recommendations": []
        }

    recommendations = []

    for index, person in enumerate(family):
        age = int(person.get("age", 0))
        lifestyle = person.get("lifestyle", "Not so active")
        routine = person.get("routine", "Not regular")
        product = choose_meal_product_for_person(person, index)

        if age <= 12:
            portion = "small kid-friendly portion"
            sleep = "9–10 hours sleep"
            activity = "30–45 minutes play time"
        elif age >= 65:
            portion = "light and balanced senior-friendly portion"
            sleep = "7–8 hours sleep"
            activity = "15–25 minutes gentle walk or stretching"
        elif lifestyle in ["Gym and fitness", "Play time"]:
            portion = "higher energy and protein-supporting portion"
            sleep = "7–9 hours sleep"
            activity = "30–45 minutes training or active movement"
        elif lifestyle in ["Yoga", "Meditation"]:
            portion = "balanced wellness-focused portion"
            sleep = "7–8 hours sleep"
            activity = "20–30 minutes yoga, breathing, or mobility"
        else:
            portion = "regular balanced portion"
            sleep = "7–8 hours sleep"
            activity = "20 minutes light movement"

        recommendations.append({
            "person": person["name"],
            "age": age,
            "routine": routine,
            "lifestyle": lifestyle,
            "product": product["brand"],
            "item": product["item"],
            "image": product["image"],
            "diet": product["diet"],
            "weight": product["weight"],
            "calories": product["calories"],
            "meal_fit": f"{product['item'].title()} suits {person['name']} as a {portion} based on their {routine.lower()} routine and {lifestyle.lower()} lifestyle.",
            "wellness_tip": f"Suggested routine: {activity}, hydration, and {sleep}."
        })

    return {
        "enabled": True,
        "visible": True,
        "message": "AI Premium personalised meal, fitness and sleep guidance generated.",
        "recommendations": recommendations
    }


@app.route("/")
def dashboard():
    REQUEST_COUNTER.labels(endpoint="/").inc()
    return render_template("index.html")


@app.route("/health")
def health():
    REQUEST_COUNTER.labels(endpoint="/health").inc()
    return jsonify({"status": "healthy", "service": "SmartCart AI - DiscountMate", "version": "5.2.0"})


@app.route("/metrics")
def metrics():
    REQUEST_COUNTER.labels(endpoint="/metrics").inc()
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


@app.route("/captcha")
def captcha():
    REQUEST_COUNTER.labels(endpoint="/captcha").inc()
    captcha_code = generate_captcha()
    session["captcha"] = captcha_code
    return jsonify({"captcha": captcha_code})


@app.route("/session-user")
def session_user():
    REQUEST_COUNTER.labels(endpoint="/session-user").inc()
    return jsonify({"user": public_user(get_current_user())})


@app.route("/logout", methods=["POST"])
def logout():
    REQUEST_COUNTER.labels(endpoint="/logout").inc()
    session.pop("user_email", None)
    return jsonify({"success": True, "message": "Logged out successfully."})


@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    REQUEST_COUNTER.labels(endpoint="/forgot-password").inc()
    data = request.get_json() or {}
    email = data.get("email", "").lower().strip()

    if not email:
        return jsonify({"success": False, "message": "Please enter your recovery email address."}), 400

    return jsonify({"success": True, "message": "A link has been sent to create a new password to your email."})


@app.route("/api/products")
def products():
    REQUEST_COUNTER.labels(endpoint="/api/products").inc()
    return jsonify({"products": [enrich_product(product) for product in GROCERY_DATA]})


@app.route("/api/items")
def items():
    REQUEST_COUNTER.labels(endpoint="/api/items").inc()
    return jsonify({"items": sorted(set(product["item"] for product in GROCERY_DATA))})


@app.route("/compare")
def compare_prices():
    REQUEST_COUNTER.labels(endpoint="/compare").inc()
    item_name = request.args.get("item", "").strip()
    user = get_current_user()

    if user:
        user["usage_count"] += 1

    if not item_name:
        return jsonify({"error": "Please select or enter a grocery item."}), 400

    products_found = find_items_by_name(item_name)

    if not products_found:
        return jsonify({"error": f"No products found for item: {item_name}"}), 404

    enriched_products = [enrich_product(product) for product in products_found]
    best_value = recommend_best_value(enriched_products)
    highest_price = max(product["previous_price"] for product in enriched_products)

    return jsonify({
        "item": item_name,
        "results": enriched_products,
        "best_value": best_value,
        "estimated_saving": round(highest_price - best_value["price"], 2),
        "stores_checked": len(set(product["store"] for product in enriched_products)),
        "nearby_store_search": build_nearby_store_result(user, item_name),
        "usage_bonus": get_usage_bonus(user),
        "user": public_user(user)
    })


@app.route("/predict-discount")
def predict_discount():
    REQUEST_COUNTER.labels(endpoint="/predict-discount").inc()
    item_name = request.args.get("item", "").strip()

    if not item_name:
        return jsonify({"error": "Please select or enter a grocery item."}), 400

    products_found = find_items_by_name(item_name)

    if not products_found:
        return jsonify({"error": f"No products found for item: {item_name}"}), 404

    return jsonify({"item": item_name, "discount_predictions": [enrich_product(product) for product in products_found]})


@app.route("/substitute")
def substitute():
    REQUEST_COUNTER.labels(endpoint="/substitute").inc()
    item_name = request.args.get("item", "").strip()

    if not item_name:
        return jsonify({"error": "Please select or enter a grocery item."}), 400

    products_found = find_items_by_name(item_name)

    if not products_found:
        return jsonify({"error": f"No substitute found for item: {item_name}"}), 404

    enriched_products = [enrich_product(product) for product in products_found]
    return jsonify({
        "requested_item": item_name,
        "recommended_substitute": recommend_best_value(enriched_products),
        "reason": "Lowest price option across available stores."
    })


@app.route("/meal-plan")
def meal_plan():
    REQUEST_COUNTER.labels(endpoint="/meal-plan").inc()

    try:
        budget = float(request.args.get("budget", "20"))
    except ValueError:
        return jsonify({"error": "Budget must be a valid number."}), 400

    cheapest_by_item = {}

    for product in GROCERY_DATA:
        item = product["item"]
        if item not in cheapest_by_item or product["price"] < cheapest_by_item[item]["price"]:
            cheapest_by_item[item] = product

    selected_items = []
    total_cost = 0

    for product in sorted(cheapest_by_item.values(), key=lambda grocery: grocery["price"]):
        if total_cost + product["price"] <= budget:
            selected_items.append(enrich_product(product))
            total_cost += product["price"]

    return jsonify({
        "budget": round(budget, 2),
        "recommended_items": selected_items,
        "estimated_total": round(total_cost, 2),
        "remaining_budget": round(budget - total_cost, 2),
        "items_count": len(selected_items)
    })


@app.route("/api/offers")
def offers():
    REQUEST_COUNTER.labels(endpoint="/api/offers").inc()
    user = get_current_user()
    bonus = get_usage_bonus(user)
    return jsonify({
        "offers": OFFERS,
        "usage_bonus": bonus,
        "message": f"Smart Plus usage bonus: {bonus}% extra discount." if bonus else "No usage bonus currently active."
    })


@app.route("/apply-coupon", methods=["POST"])
def apply_coupon():
    REQUEST_COUNTER.labels(endpoint="/apply-coupon").inc()
    data = request.get_json() or {}
    code = data.get("code", "").upper().strip()
    total = float(data.get("total", 0))

    if code not in COUPONS:
        return jsonify({"accepted": False, "message": "Coupon code is invalid."}), 400

    coupon = COUPONS[code]

    if coupon["type"] == "percentage":
        discount = round(total * coupon["value"] / 100, 2)
    else:
        discount = min(coupon["value"], total)

    return jsonify({
        "accepted": True,
        "code": code,
        "description": coupon["description"],
        "discount": round(discount, 2),
        "new_total": round(max(total - discount, 0), 2)
    })


@app.route("/api/membership-plans")
def membership_plans():
    REQUEST_COUNTER.labels(endpoint="/api/membership-plans").inc()
    return jsonify({"plans": MEMBERSHIP_PLANS})


@app.route("/signup", methods=["POST"])
def signup():
    REQUEST_COUNTER.labels(endpoint="/signup").inc()
    data = request.get_json() or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").lower().strip()
    password = data.get("password", "").strip()
    confirm_password = data.get("confirm_password", "").strip()
    captcha_answer = data.get("captcha", "").upper().strip()
    expected_captcha = session.get("captcha")

    if not name or not email or not password or not confirm_password:
        return jsonify({"success": False, "message": "Name, email, password and confirm password are required."}), 400

    if password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match."}), 400

    if not expected_captcha or captcha_answer != expected_captcha:
        return jsonify({"success": False, "message": "Captcha verification failed. Please try again."}), 400

    if email in USERS:
        return jsonify({"success": False, "message": "Account already exists."}), 400

    USERS[email] = {
        "name": name,
        "email": email,
        "password": password,
        "membership": None,
        "location_access": "off",
        "usage_count": 0,
        "family_profile": []
    }

    session["user_email"] = email
    session.pop("captcha", None)

    return jsonify({
        "success": True,
        "message": "Account created successfully. You can use SmartCart without plan benefits or activate a membership anytime.",
        "user": public_user(USERS[email])
    })


@app.route("/login", methods=["POST"])
def login():
    REQUEST_COUNTER.labels(endpoint="/login").inc()
    data = request.get_json() or {}

    email = data.get("email", "").lower().strip()
    password = data.get("password", "").strip()

    user = USERS.get(email)

    if not user or user["password"] != password:
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    session["user_email"] = email

    plan_message = (
        "No membership plan is active, so plan benefits are disabled."
        if not user.get("membership")
        else f"{user['membership']['plan_name']} benefits are active."
    )

    return jsonify({
        "success": True,
        "message": f"Welcome back, {user['name']}! {plan_message}",
        "user": public_user(user)
    })


@app.route("/validate-payment-step", methods=["POST"])
def validate_payment_step():
    REQUEST_COUNTER.labels(endpoint="/validate-payment-step").inc()
    data = request.get_json() or {}

    plan_id = data.get("plan_id", "").strip()
    card_number = data.get("card_number", "").replace(" ", "")
    payment_method = data.get("payment_method", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "").strip()
    card_name = data.get("card_name", "").strip()

    try:
        demo_balance = float(data.get("demo_balance", 0))
    except ValueError:
        return jsonify({"success": False, "message": "Available balance must be a valid number."}), 400

    selected_plan = next((plan for plan in MEMBERSHIP_PLANS if plan["id"] == plan_id), None)

    if not selected_plan:
        return jsonify({"success": False, "message": "Please select a valid plan."}), 400

    if not email or not password or not card_name or not card_number or not payment_method:
        return jsonify({"success": False, "message": "Please complete all mandatory payment and account fields before continuing."}), 400

    if len(card_number) < 8:
        return jsonify({"success": False, "message": "Card/account number must contain at least 8 digits."}), 400

    if card_number.endswith("0000"):
        return jsonify({"success": False, "message": "Payment rejected because the card/account number cannot end with 0000."}), 400

    if demo_balance < selected_plan["price"]:
        return jsonify({
            "success": False,
            "message": f"Payment rejected. Available balance must be more than the {selected_plan['name']} plan price of ${selected_plan['price']:.2f}."
        }), 400

    return jsonify({"success": True, "message": "Payment details validated. You can continue."})


@app.route("/activate-membership", methods=["POST"])
def activate_membership():
    REQUEST_COUNTER.labels(endpoint="/activate-membership").inc()
    data = request.get_json() or {}

    email = data.get("email", "").lower().strip()
    password = data.get("password", "").strip()
    plan_id = data.get("plan_id", "").strip()
    location_access = data.get("location_access", "off").strip()
    family_profile = data.get("family_profile", [])
    card_name = data.get("card_name", "").strip()
    card_number = data.get("card_number", "").replace(" ", "")
    payment_method = data.get("payment_method", "").strip()
    captcha_answer = data.get("captcha", "").upper().strip()

    try:
        demo_balance = float(data.get("demo_balance", 0))
    except ValueError:
        return jsonify({"success": False, "message": "Available balance must be a valid number."}), 400

    selected_plan = next((plan for plan in MEMBERSHIP_PLANS if plan["id"] == plan_id), None)

    if not selected_plan:
        return jsonify({"success": False, "message": "Invalid membership plan selected."}), 400

    if not email or not password or not card_name or not payment_method or len(card_number) < 8:
        return jsonify({"success": False, "message": "Please enter all mandatory payment and account details."}), 400

    if card_number.endswith("0000"):
        return jsonify({"success": False, "message": "Payment rejected because the card/account number cannot end with 0000."}), 402

    if demo_balance < selected_plan["price"]:
        return jsonify({"success": False, "message": f"Payment rejected. Available balance must be more than the {selected_plan['name']} plan price."}), 402

    expected_captcha = session.get("captcha")

    if not expected_captcha or captcha_answer != expected_captcha:
        return jsonify({"success": False, "message": "Captcha verification failed. Please try again."}), 400

    if email not in USERS:
        USERS[email] = {
            "name": card_name,
            "email": email,
            "password": password,
            "membership": None,
            "location_access": "off",
            "usage_count": 0,
            "family_profile": []
        }
    else:
        USERS[email]["password"] = password
        if card_name:
            USERS[email]["name"] = card_name

    USERS[email]["membership"] = {
        "plan_id": selected_plan["id"],
        "plan_name": selected_plan["name"],
        "discount": selected_plan["discount"]
    }

    USERS[email]["location_access"] = location_access if selected_plan["requires_location"] else "off"

    if selected_plan["id"] == "premium":
        existing = USERS[email].get("family_profile", [])

        for person in family_profile:
            name = person.get("name", "").strip()

            if not name:
                continue

            existing.append({
                "name": name,
                "age": int(person.get("age", 0)),
                "routine": person.get("routine", "Not regular"),
                "lifestyle": person.get("lifestyle", "Not so active")
            })

        USERS[email]["family_profile"] = existing

    session["user_email"] = email
    session.pop("captcha", None)

    return jsonify({
        "success": True,
        "message": f"Payment successful. {selected_plan['name']} membership activated.",
        "user": public_user(USERS[email])
    })


@app.route("/update-location", methods=["POST"])
def update_location():
    REQUEST_COUNTER.labels(endpoint="/update-location").inc()
    user = get_current_user()

    if not user:
        return jsonify({"success": False, "message": "Please login first."}), 401

    if not user.get("membership") or user["membership"]["plan_id"] not in ["basic", "plus"]:
        return jsonify({"success": False, "message": "Location benefits are available only for Basic Saver and Smart Plus."}), 403

    data = request.get_json() or {}
    user["location_access"] = data.get("location_access", "off")

    return jsonify({"success": True, "message": "Location preference updated.", "user": public_user(user)})


@app.route("/save-family-profile", methods=["POST"])
def save_family_profile():
    REQUEST_COUNTER.labels(endpoint="/save-family-profile").inc()
    user = get_current_user()

    if not user:
        return jsonify({"success": False, "message": "Please login first."}), 401

    if not user.get("membership") or user["membership"]["plan_id"] != "premium":
        return jsonify({"success": False, "message": "Family profile is available for AI Premium members only."}), 403

    data = request.get_json() or {}
    family_profile = data.get("family_profile", [])
    existing = user.get("family_profile", [])

    for person in family_profile:
        name = person.get("name", "").strip()

        if not name:
            continue

        existing.append({
            "name": name,
            "age": int(person.get("age", 0)),
            "routine": person.get("routine", "Not regular"),
            "lifestyle": person.get("lifestyle", "Not so active")
        })

    user["family_profile"] = existing

    return jsonify({"success": True, "message": "Family member details added.", "user": public_user(user)})


@app.route("/remove-family-member", methods=["POST"])
def remove_family_member():
    REQUEST_COUNTER.labels(endpoint="/remove-family-member").inc()
    user = get_current_user()

    if not user:
        return jsonify({"success": False, "message": "Please login first."}), 401

    if not user.get("membership") or user["membership"]["plan_id"] != "premium":
        return jsonify({"success": False, "message": "Family profile is available for AI Premium members only."}), 403

    data = request.get_json() or {}
    index = int(data.get("index", -1))
    family = user.get("family_profile", [])

    if index < 0 or index >= len(family):
        return jsonify({"success": False, "message": "Invalid family member selected."}), 400

    removed = family.pop(index)
    user["family_profile"] = family

    return jsonify({"success": True, "message": f"{removed['name']} removed from family profile.", "user": public_user(user)})


@app.route("/premium-guidance")
def premium_guidance():
    REQUEST_COUNTER.labels(endpoint="/premium-guidance").inc()
    return jsonify(build_premium_meal_guidance(get_current_user()))


@app.route("/pipeline-status")
def pipeline_status():
    REQUEST_COUNTER.labels(endpoint="/pipeline-status").inc()
    return jsonify({
        "project": "SmartCart AI - DiscountMate",
        "stages": [
            {"stage": "Build", "status": "Supported", "tool": "Docker"},
            {"stage": "Test", "status": "Supported", "tool": "Pytest"},
            {"stage": "Code Quality", "status": "Supported", "tool": "Flake8, Pylint, SonarQube"},
            {"stage": "Security", "status": "Supported", "tool": "Bandit"},
            {"stage": "Deploy", "status": "Supported", "tool": "Docker Compose Staging"},
            {"stage": "Release", "status": "Supported", "tool": "Docker Tagging Production"},
            {"stage": "Monitoring", "status": "Supported", "tool": "Health Check, Prometheus Metrics"}
        ]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
