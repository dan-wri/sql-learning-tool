"""Deterministic Brightcart dataset for the training database.

Teaching-critical fixtures are written out explicitly. Background rows come from named random
streams, so changing one section does not reshuffle the others.
"""

import random
from datetime import date, timedelta

SEED = "brightcart-seed-2"
# The seeded history ends just before the story starts on Monday 2026-01-05.
HISTORY_END = date(2026, 1, 2)
QA_EMAIL = "qa.test@brightcart.example"


def _stream(name: str) -> random.Random:
    return random.Random(f"{SEED}:{name}")


COUNTRY_CITIES = {
    "UK": ["London", "Manchester", "Birmingham", "Leeds", "Glasgow", "Bristol"],
    "Ireland": ["Dublin", "Cork"],
    "France": ["Paris", "Lyon"],
    "Germany": ["Berlin", "Munich"],
    "Netherlands": ["Amsterdam"],
    "Spain": ["Madrid"],
}
COUNTRY_WEIGHTS = [34, 14, 14, 14, 12, 12]

# "Grace" is reserved for the explicit fixtures below.
FIRST_NAMES = [
    "Olivia", "Liam", "Amelia", "Noah", "Isla", "Oliver", "Ava", "George", "Mia", "Harry",
    "Sophia", "Jack", "Leo", "Freya", "Arthur", "Lily", "Oscar", "Emily", "Charlie",
    "Priya", "Mohammed", "Chloe", "Ethan", "Zara",
]
LAST_NAMES = [
    "Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Davies", "Patel", "Wright",
    "Walker", "Robinson", "Thompson", "Khan", "Evans", "Green", "Hall", "Wood", "Clarke", "Hughes",
]

# (first, last, email, phone, city, country, signup_date)
FIXTURE_CUSTOMERS = [
    ("QA", "Tester", QA_EMAIL, None, "Manchester", "UK", "2025-11-03"),
    # Several different people named Grace: names are not identifiers.
    ("Grace", "Taylor", "grace.taylor@example.com", "07411222333", "Leeds", "UK", "2023-02-14"),
    ("Grace", "Hall", "grace.hall@example.com", "07522333444", "Dublin", "Ireland", "2024-04-09"),
    ("Grace", "Evans", "grace.evans@example.com", None, "Berlin", "Germany", "2025-02-11"),
    # Three pairs of different customers who share a full name.
    ("Oliver", "Smith", "oliver.smith.london@example.com", "07833444555", "London", "UK", "2023-05-22"),
    ("Oliver", "Smith", "oliver.smith.cork@example.com", "07844555666", "Cork", "Ireland", "2024-08-30"),
    ("Priya", "Patel", "priya.patel.birmingham@example.com", None, "Birmingham", "UK", "2023-09-04"),
    ("Priya", "Patel", "priya.patel.lyon@example.com", "07955666777", "Lyon", "France", "2025-01-20"),
    ("Liam", "Jones", "liam.jones.glasgow@example.com", "07966777888", "Glasgow", "UK", "2024-01-15"),
    ("Liam", "Jones", "liam.jones.munich@example.com", "07977888999", "Munich", "Germany", "2025-06-12"),
    # Emails with deterministic case and whitespace defects for the data-quality chapter.
    ("Amelia", "Wood", " Amelia.Wood@Example.com ", "07100200300", "Bristol", "UK", "2024-02-07"),
    ("Noah", "Khan", "NOAH.KHAN@EXAMPLE.COM", "07200300400", "Paris", "France", "2024-06-25"),
    ("Zara", "Hughes", "Zara.Hughes@example.com ", None, "Madrid", "Spain", "2024-10-13"),
    ("Freya", "Clarke", "  freya.clarke@example.com", "07300400500", "Amsterdam", "Netherlands", "2025-03-28"),
    ("Arthur", "Robinson", "Arthur.Robinson@EXAMPLE.COM", "07400500600", "Berlin", "Germany", "2025-05-06"),
]
BACKGROUND_CUSTOMERS = 65
NO_ORDER_BACKGROUND_CUSTOMERS = 9
NULL_PHONE_UK_TARGET = 10
REFERRAL_COUNT = 10  # plus a two-step chain

CATEGORIES = ["Electronics", "Books", "Home & Kitchen",
              "Clothing", "Sports & Outdoors", "Toys & Games"]

# (name, category_id, price)
PRODUCTS = [
    ("Wireless Earbuds", 1, 59.99), ("Bluetooth Speaker", 1, 39.99), ("USB-C Charger", 1, 19.99),
    ("Mechanical Keyboard", 1, 89.00), ("27-inch Monitor", 1, 229.00), ("Webcam HD", 1, 49.50),
    ("SQL for Beginners", 2, 24.99), ("The Data Warehouse Toolkit", 2, 42.00), ("Mystery at Midnight", 2, 8.99),
    ("Cooking Made Simple", 2, 15.50), ("Space Atlas", 2, 29.95),
    ("Chef's Knife", 3, 34.00), ("Non-stick Frying Pan", 3, 27.49), ("French Press", 3, 22.00),
    ("Bamboo Cutting Board", 3, 14.99), ("Electric Kettle", 3, 31.99),
    ("Cotton T-Shirt", 4, 12.00), ("Denim Jacket", 4, 64.99), ("Running Socks (3 pack)", 4, 9.99),
    ("Wool Scarf", 4, 19.00), ("Rain Jacket", 4, 79.00),
    ("Yoga Mat", 5, 25.00), ("Water Bottle", 5, 11.50), ("Camping Tent", 5, 149.00),
    ("Resistance Bands", 5, 17.99), ("Cycling Helmet", 5, 59.99),
    ("Building Blocks Set", 6, 44.99), ("Jigsaw Puzzle 1000pc", 6, 16.99), ("Board Game Classic", 6, 29.99),
    ("Remote Control Car", 6, 39.99),
]
# Deliberate ties (59.99, 39.99 and 152 units at the top-five boundary) make ORDER BY tie-breakers matter.
STOCK_FIXTURES = {11: 152, 22: 152}
USB_C_CHARGER_ID = 3
INACTIVE_PRODUCT_IDS = {6, 21}
OUT_OF_STOCK_PRODUCT_IDS = {5, 18, 24}
# product_id -> (price changed on, price before that date); order_items keep the price at sale.
PRICE_HISTORY = {
    1: (date(2025, 3, 1), 64.99),
    4: (date(2024, 9, 1), 94.00),
    11: (date(2024, 6, 1), 27.95),
    22: (date(2025, 6, 1), 22.00),
    24: (date(2025, 1, 1), 159.00),
}

HOLIDAY_SLOW_START = date(2025, 11, 15)
HOLIDAY_SLOW_END = date(2025, 12, 22)
BALANCED_COUNTRY_MONTHS = {(2025, 11), (2025, 12)}

RETURN_REASONS = ["Damaged on arrival", "Not as described", "Changed my mind", "Wrong size or fit",
                  "Stopped working", "Arrived late"]
REVIEW_TEXT = {
    1: ["Broke within a week.", "Very disappointed with the quality."],
    2: ["Not what I expected.", "Worked at first, then gave up."],
    3: ["Does the job, nothing special.", "Average for the price."],
    4: ["Good value and arrived quickly.", "Happy with this purchase."],
    5: ["Excellent, would buy again.", "Exactly what I needed."],
}
RATING_WEIGHTS = [4, 6, 15, 35, 40]
BOT_REVIEWS = ["BOT: Amazing deal, visit cheap-offers.example now",
               "BOT: Best price guaranteed, click the link in my profile",
               "BOT: Five stars! Earn money from home today",
               "BOT: Limited offer, message me for a discount code"]
VERIFIED_REVIEWS = 62
UNVERIFIED_REVIEWS = 12


def _month_order_count(year: int, month: int) -> int:
    if year == 2023:
        return 3
    if (year, month) == (2025, 11):
        return 40
    if (year, month) == (2025, 12):
        return 54
    return 12 + month % 2


def _month_end(year: int, month: int) -> date:
    first_of_next = date(year + month // 12, month % 12 + 1, 1)
    return first_of_next - timedelta(days=1)


def _customers() -> tuple[list[tuple], set[int], dict[int, date], dict[int, str]]:
    rng = _stream("customers")
    used_names = {(f[0], f[1]) for f in FIXTURE_CUSTOMERS}
    background = []
    while len(background) < BACKGROUND_CUSTOMERS:
        first, last = rng.choice(FIRST_NAMES), rng.choice(LAST_NAMES)
        if (first, last) in used_names:
            continue
        used_names.add((first, last))
        country = rng.choices(list(COUNTRY_CITIES), weights=COUNTRY_WEIGHTS)[0]
        city = rng.choice(COUNTRY_CITIES[country])
        phone = None if rng.random() < 0.2 else f"07{rng.randint(100_000_000, 999_999_999)}"
        index = len(background)
        if index < 3:
            signup = date(2023, 1, 2) + timedelta(days=rng.randint(0, 25))
        elif index < 11:
            signup = date(2025, 10, 1) + timedelta(days=rng.randint(0, 84))
        else:
            signup = date(2023, 1, 1) + timedelta(days=rng.randint(0, 1002))
        background.append((first, last, None, phone, city, country, signup.isoformat()))

    tagged = [(row, True) for row in FIXTURE_CUSTOMERS] + [(row, False) for row in background]
    tagged.sort(key=lambda item: (item[0][6], item[0][1], item[0][0], not item[1]))

    rows, background_ids, fixture_ids = [], [], {}
    for customer_id, (row, is_fixture) in enumerate(tagged, start=1):
        first, last, email, phone, city, country, signup = row
        if is_fixture:
            fixture_ids[email] = customer_id
        else:
            email = f"{first}.{last}{customer_id}@example.com".lower()
            background_ids.append(customer_id)
        rows.append([customer_id, first, last, email, phone, city, country, signup, None])

    uk_null = sum(1 for r in rows if r[6] == "UK" and r[4] is None and r[3] != QA_EMAIL)
    for row in rows:
        if uk_null >= NULL_PHONE_UK_TARGET:
            break
        if row[6] == "UK" and row[4] is not None and row[0] in background_ids:
            row[4] = None
            uk_null += 1

    referral_rng = _stream("referrals")
    chain_start = background_ids[12:]
    a, b, c = chain_start[0], chain_start[10], chain_start[20]
    by_id = {r[0]: r for r in rows}
    by_id[b][8], by_id[c][8] = a, b
    pool = [i for i in background_ids[15:] if i not in (b, c)]
    for referee in sorted(referral_rng.sample(pool, REFERRAL_COUNT)):
        by_id[referee][8] = referral_rng.choice([i for i in background_ids if i < referee])

    no_order_rng = _stream("no_orders")
    no_orders = {fixture_ids[QA_EMAIL], *no_order_rng.sample(background_ids, NO_ORDER_BACKGROUND_CUSTOMERS)}
    signup_by_id = {r[0]: date.fromisoformat(r[7]) for r in rows}
    country_by_id = {r[0]: r[6] for r in rows}
    return [tuple(r) for r in rows], no_orders, signup_by_id, country_by_id


def _products() -> list[tuple]:
    rng = _stream("products")
    products = []
    for product_id, (name, category_id, price) in enumerate(PRODUCTS, start=1):
        stock = 0 if product_id in OUT_OF_STOCK_PRODUCT_IDS else rng.randint(5, 250)
        stock = STOCK_FIXTURES.get(product_id, stock)
        is_active = 0 if product_id in INACTIVE_PRODUCT_IDS else 1
        products.append((product_id, name, category_id, price, stock, is_active))
    return products


def _price_at_sale(product_id: int, current_price: float, order_date: date) -> float:
    change = PRICE_HISTORY.get(product_id)
    return change[1] if change and order_date < change[0] else current_price


def _draft_orders(customers, no_orders, signup_by_id, country_by_id, products) -> list[dict]:
    price_by_product = {p[0]: p[3] for p in products}
    ordering = [c[0] for c in customers if c[0] not in no_orders]
    countries = list(COUNTRY_CITIES)
    drafts = []
    for year in (2023, 2024, 2025):
        for month in range(1, 13):
            rng = _stream(f"orders:{year}-{month:02d}")
            start, end = date(year, month, 1), _month_end(year, month)
            eligible = [i for i in ordering if signup_by_id[i] <= end]
            for n in range(_month_order_count(year, month)):
                pool = eligible
                if (year, month) in BALANCED_COUNTRY_MONTHS:
                    in_country = [i for i in eligible if country_by_id[i] == countries[n % len(countries)]]
                    pool = in_country or eligible
                customer_id = rng.choice(pool)
                earliest = max(start, signup_by_id[customer_id])
                order_date = earliest + timedelta(days=rng.randint(0, (end - earliest).days))

                cancelled = rng.random() < 0.07
                ship_lag, transit = rng.randint(1, 3), rng.randint(2, 5)
                if HOLIDAY_SLOW_START <= order_date <= HOLIDAY_SLOW_END and rng.random() < 0.4:
                    ship_lag, transit = rng.randint(3, 5), rng.randint(8, 13)
                held_back = order_date >= date(2025, 12, 30) and rng.random() < 0.6

                product_ids = rng.sample(range(1, len(PRODUCTS) + 1), rng.choices([1, 2, 3, 4], [40, 30, 20, 10])[0])
                if USB_C_CHARGER_ID not in product_ids and rng.random() < 0.12:
                    product_ids[0] = USB_C_CHARGER_ID
                items = [(pid, rng.choices([1, 2, 3, 5], [60, 25, 10, 5])[0],
                          _price_at_sale(pid, price_by_product[pid], order_date)) for pid in product_ids]

                shipped = order_date + timedelta(days=ship_lag)
                delivered = shipped + timedelta(days=transit)
                if cancelled:
                    status, shipped, delivered = "cancelled", None, None
                elif held_back or shipped > HISTORY_END:
                    status, shipped, delivered = "pending", None, None
                elif delivered > HISTORY_END:
                    status, delivered = "shipped", None
                else:
                    status = "delivered"
                drafts.append({"customer_id": customer_id, "date": order_date, "status": status,
                               "shipped": shipped, "delivered": delivered, "items": items})
    drafts.sort(key=lambda d: (d["date"], d["customer_id"]))
    return drafts


def _payments(orders: list[dict]) -> list[tuple]:
    totals = {o["id"]: round(sum(q * p for _, q, p in o["items"]), 2) for o in orders}
    delivered_2025 = [o["id"] for o in orders
                      if o["status"] == "delivered" and date(2025, 2, 1) <= o["date"] <= date(2025, 10, 31)]
    picks = _stream("finance").sample(delivered_2025, 8)
    unpaid, underpaid, split = set(picks[:3]), set(picks[3:5]), set(picks[5:])

    rng = _stream("payments")
    rows = []
    for o in orders:
        if o["status"] not in ("delivered", "shipped") or o["id"] in unpaid:
            continue
        paid_at = o["date"].isoformat()
        total = totals[o["id"]]
        method = rng.choices(["card", "paypal", "bank_transfer"], [65, 25, 10])[0]
        if o["id"] in split:
            first_part = round(total / 2, 2)
            rows.append((len(rows) + 1, o["id"], first_part, "card", paid_at))
            rows.append((len(rows) + 1, o["id"], round(total - first_part, 2), "paypal", paid_at))
        else:
            amount = round(total * 0.75, 2) if o["id"] in underpaid else total
            rows.append((len(rows) + 1, o["id"], amount, method, paid_at))
    return rows


def _returns(orders: list[dict], items: list[tuple]) -> list[tuple]:
    delivered = {o["id"]: o["delivered"] for o in orders if o["status"] == "delivered"}
    returnable = [i for i in items if i[1] in delivered and delivered[i[1]] <= HISTORY_END - timedelta(days=20)]
    rng = _stream("returns")
    usb_c = [i for i in returnable if i[2] == USB_C_CHARGER_ID]
    others = [i for i in returnable if i[2] != USB_C_CHARGER_ID]
    picks = rng.sample(usb_c, 2) + rng.sample(others, 22)
    drafts = []
    for position, (item_id, order_id, _, item_qty, unit_price) in enumerate(picks):
        quantity = rng.randint(1, item_qty)
        refund = round(quantity * unit_price, 2)
        # Three deliberately wrong refunds for the finance audit.
        refund = {4: round(refund * 2, 2), 12: round(refund + 15, 2), 19: round(refund * 0.5, 2)}.get(position, refund)
        return_date = delivered[order_id] + timedelta(days=rng.randint(2, 18))
        drafts.append((return_date.isoformat(), item_id, quantity, rng.choice(RETURN_REASONS), refund))
    drafts.sort()
    return [(n, item_id, d, q, reason, refund) for n, (d, item_id, q, reason, refund) in enumerate(drafts, start=1)]


def _reviews(orders: list[dict], items: list[tuple], customers: list[tuple], no_orders: set[int]) -> list[tuple]:
    qa_id = next(c[0] for c in customers if c[3] == QA_EMAIL)
    order_by_id = {o["id"]: o for o in orders}
    purchased = {(order_by_id[i[1]]["customer_id"], i[2]) for i in items}
    verified = {}
    for _, order_id, product_id, _, _ in items:
        order = order_by_id[order_id]
        if order["status"] == "delivered":
            verified.setdefault((order["customer_id"], product_id), order["delivered"])

    rng = _stream("reviews")
    drafts = []
    for (customer_id, product_id), delivered in rng.sample(sorted(verified.items()), VERIFIED_REVIEWS):
        drafts.append((min(delivered + timedelta(days=rng.randint(3, 30)), HISTORY_END),
                       product_id, customer_id, rng.choices([1, 2, 3, 4, 5], RATING_WEIGHTS)[0], None))

    taken = {(d[2], d[1]) for d in drafts}
    reviewers = [c[0] for c in customers if c[0] != qa_id]
    while len(drafts) < VERIFIED_REVIEWS + UNVERIFIED_REVIEWS:
        customer_id, product_id = rng.choice(reviewers), rng.randint(1, len(PRODUCTS))
        if (customer_id, product_id) in purchased or (customer_id, product_id) in taken:
            continue
        taken.add((customer_id, product_id))
        review_date = date(2024, 1, 1) + timedelta(days=rng.randint(0, (HISTORY_END - date(2024, 1, 1)).days))
        drafts.append((review_date, product_id, customer_id, rng.choices([1, 2, 3, 4, 5], RATING_WEIGHTS)[0], None))

    bots = sorted(no_orders - {qa_id})
    for text in BOT_REVIEWS:
        review_date = date(2025, 9, 1) + timedelta(days=rng.randint(0, 100))
        drafts.append((review_date, rng.randint(1, len(PRODUCTS)), rng.choice(bots), 5, text))

    drafts.sort(key=lambda d: (d[0], d[1], d[2]))
    return [(n, product_id, customer_id, rating, review_date.isoformat(),
             text or rng.choice(REVIEW_TEXT[rating]))
            for n, (review_date, product_id, customer_id, rating, text) in enumerate(drafts, start=1)]


def generate() -> dict[str, list[tuple]]:
    """Return rows per table, in foreign-key-safe insertion order."""
    customers, no_orders, signup_by_id, country_by_id = _customers()
    products = _products()
    orders = _draft_orders(customers, no_orders, signup_by_id, country_by_id, products)

    order_rows, items = [], []
    for order_id, order in enumerate(orders, start=1):
        order["id"] = order_id
        order_rows.append((order_id, order["customer_id"], order["date"].isoformat(), order["status"],
                           order["shipped"].isoformat() if order["shipped"] else None,
                           order["delivered"].isoformat() if order["delivered"] else None))
        for product_id, quantity, unit_price in order["items"]:
            items.append((len(items) + 1, order_id, product_id, quantity, unit_price))

    return {
        "customers": customers,
        "categories": [(i, name) for i, name in enumerate(CATEGORIES, start=1)],
        "products": products,
        "orders": order_rows,
        "order_items": items,
        "payments": _payments(orders),
        "returns": _returns(orders, items),
        "product_reviews": _reviews(orders, items, customers, no_orders),
    }
