"""Deterministic e-commerce dataset for the training database."""

import random
from datetime import date, timedelta

RANDOM_SEED = 20240101

FIRST_NAMES = [
    "Olivia", "Liam", "Amelia", "Noah", "Isla", "Oliver", "Ava", "George", "Mia", "Harry",
    "Sophia", "Jack", "Grace", "Leo", "Freya", "Arthur", "Lily", "Oscar", "Emily", "Charlie",
    "Priya", "Mohammed", "Chloe", "Ethan", "Zara",
]
LAST_NAMES = [
    "Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Davies", "Patel", "Wright",
    "Walker", "Robinson", "Thompson", "Khan", "Evans", "Green", "Hall", "Wood", "Clarke", "Hughes",
]
CITIES = [
    ("London", "UK"), ("Manchester", "UK"), ("Birmingham",
                                             "UK"), ("Leeds", "UK"), ("Glasgow", "UK"),
    ("Bristol", "UK"), ("Dublin", "Ireland"), ("Cork",
                                               "Ireland"), ("Paris", "France"), ("Lyon", "France"),
    ("Berlin", "Germany"), ("Munich", "Germany"), ("Amsterdam",
                                                   "Netherlands"), ("Madrid", "Spain"),
]
CATEGORIES = ["Electronics", "Books", "Home & Kitchen",
              "Clothing", "Sports & Outdoors", "Toys & Games"]

# (name, category_id, price)
PRODUCTS = [
    ("Wireless Earbuds", 1, 59.99), ("Bluetooth Speaker",
                                     1, 39.99), ("USB-C Charger", 1, 19.99),
    ("Mechanical Keyboard", 1, 89.00), ("27-inch Monitor",
                                        1, 229.00), ("Webcam HD", 1, 49.50),
    ("SQL for Beginners", 2, 24.99), ("The Data Warehouse Toolkit",
                                      2, 42.00), ("Mystery at Midnight", 2, 8.99),
    ("Cooking Made Simple", 2, 15.50), ("Space Atlas", 2, 29.95),
    ("Chef's Knife", 3, 34.00), ("Non-stick Frying Pan",
                                 3, 27.49), ("French Press", 3, 22.00),
    ("Bamboo Cutting Board", 3, 14.99), ("Electric Kettle", 3, 31.99),
    ("Cotton T-Shirt", 4, 12.00), ("Denim Jacket",
                                   4, 64.99), ("Running Socks (3 pack)", 4, 9.99),
    ("Wool Scarf", 4, 19.00), ("Rain Jacket", 4, 79.00),
    ("Yoga Mat", 5, 25.00), ("Water Bottle",
                             5, 11.50), ("Camping Tent", 5, 149.00),
    ("Resistance Bands", 5, 17.99), ("Cycling Helmet", 5, 54.00),
    ("Building Blocks Set", 6, 44.99), ("Jigsaw Puzzle 1000pc",
                                        6, 16.99), ("Board Game Classic", 6, 29.99),
    ("Remote Control Car", 6, 39.00),
]
INACTIVE_PRODUCT_IDS = {6, 21}
OUT_OF_STOCK_PRODUCT_IDS = {5, 18, 24}

NUM_CUSTOMERS = 60
# Customers above this id never place an order, so "customers with no orders" questions have answers.
LAST_ORDERING_CUSTOMER_ID = 54
NUM_ORDERS = 150
SIGNUP_START = date(2023, 1, 1)
ORDERS_END = date(2025, 6, 30)


def generate(seed: int = RANDOM_SEED) -> dict[str, list[tuple]]:
    """Return rows per table, in foreign-key-safe insertion order."""
    rng = random.Random(seed)

    customers = []
    signup_by_customer = {}
    for customer_id in range(1, NUM_CUSTOMERS + 1):
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        city, country = rng.choice(CITIES)
        phone = None if rng.random(
        ) < 0.2 else f"07{rng.randint(100_000_000, 999_999_999)}"
        signup = SIGNUP_START + timedelta(days=rng.randint(0, 729))
        signup_by_customer[customer_id] = signup
        email = f"{first}.{last}{customer_id}@example.com".lower()
        customers.append((customer_id, first, last, email,
                         phone, city, country, signup.isoformat()))

    categories = [(i, name) for i, name in enumerate(CATEGORIES, start=1)]

    products = []
    for product_id, (name, category_id, price) in enumerate(PRODUCTS, start=1):
        stock = 0 if product_id in OUT_OF_STOCK_PRODUCT_IDS else rng.randint(
            5, 250)
        is_active = 0 if product_id in INACTIVE_PRODUCT_IDS else 1
        products.append(
            (product_id, name, category_id, price, stock, is_active))
    price_by_product = {p[0]: p[3] for p in products}

    order_specs = []
    for _ in range(NUM_ORDERS):
        customer_id = rng.randint(1, LAST_ORDERING_CUSTOMER_ID)
        signup = signup_by_customer[customer_id]
        order_date = signup + \
            timedelta(days=rng.randint(0, (ORDERS_END - signup).days))
        status = rng.choices(
            ["delivered", "shipped", "pending", "cancelled"], weights=[70, 12, 8, 10])[0]
        order_specs.append((order_date, customer_id, status))
    order_specs.sort(key=lambda spec: (spec[0], spec[1]))

    orders, order_items, payments = [], [], []
    for order_id, (order_date, customer_id, status) in enumerate(order_specs, start=1):
        orders.append((order_id, customer_id, order_date.isoformat(), status))

        item_count = rng.choices([1, 2, 3, 4], weights=[40, 30, 20, 10])[0]
        total = 0.0
        for product_id in rng.sample(range(1, len(PRODUCTS) + 1), item_count):
            quantity = rng.choices([1, 2, 3, 5], weights=[60, 25, 10, 5])[0]
            unit_price = price_by_product[product_id]
            order_items.append(
                (len(order_items) + 1, order_id, product_id, quantity, unit_price))
            total += quantity * unit_price

        if status in ("delivered", "shipped"):
            method = rng.choices(
                ["card", "paypal", "bank_transfer"], weights=[65, 25, 10])[0]
            payments.append((len(payments) + 1, order_id,
                            round(total, 2), method, order_date.isoformat()))

    return {
        "customers": customers,
        "categories": categories,
        "products": products,
        "orders": orders,
        "order_items": order_items,
        "payments": payments,
    }
