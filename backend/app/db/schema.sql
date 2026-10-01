-- Learner-visible training schema (e-commerce).
-- No ON DELETE CASCADE on purpose: learners should meet foreign key errors.

CREATE TABLE customers (
    customer_id  INTEGER PRIMARY KEY,
    first_name   TEXT NOT NULL,
    last_name    TEXT NOT NULL,
    email        TEXT NOT NULL UNIQUE,
    phone        TEXT,
    city         TEXT NOT NULL,
    country      TEXT NOT NULL,
    signup_date  TEXT NOT NULL
);

CREATE TABLE categories (
    category_id  INTEGER PRIMARY KEY,
    name         TEXT NOT NULL UNIQUE
);

CREATE TABLE products (
    product_id      INTEGER PRIMARY KEY,
    name            TEXT NOT NULL,
    category_id     INTEGER NOT NULL REFERENCES categories (category_id),
    price           REAL NOT NULL CHECK (price >= 0),
    stock_quantity  INTEGER NOT NULL CHECK (stock_quantity >= 0),
    is_active       INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

CREATE TABLE orders (
    order_id     INTEGER PRIMARY KEY,
    customer_id  INTEGER NOT NULL REFERENCES customers (customer_id),
    order_date   TEXT NOT NULL,
    status       TEXT NOT NULL CHECK (status IN ('pending', 'shipped', 'delivered', 'cancelled'))
);

CREATE TABLE order_items (
    order_item_id  INTEGER PRIMARY KEY,
    order_id       INTEGER NOT NULL REFERENCES orders (order_id),
    product_id     INTEGER NOT NULL REFERENCES products (product_id),
    quantity       INTEGER NOT NULL CHECK (quantity > 0),
    unit_price     REAL NOT NULL CHECK (unit_price >= 0)
);

CREATE TABLE payments (
    payment_id  INTEGER PRIMARY KEY,
    order_id    INTEGER NOT NULL REFERENCES orders (order_id),
    amount      REAL NOT NULL,
    method      TEXT NOT NULL CHECK (method IN ('card', 'paypal', 'bank_transfer')),
    paid_at     TEXT NOT NULL
);
