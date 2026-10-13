# SQL Curriculum — Brightcart

**Status:** curriculum design complete; implementation has **not** started beyond the existing three prototype challenges.

This document is the source of truth for the planned 100-level course. It is grounded in the current repository: FastAPI + SQLite, a persistent per-learner database, result-based query validation, state-diff mutation validation, transactional commit/rollback, linear unlocking, and mutation Review mode rebuilt from the canonical pre-challenge state.

The design deliberately separates **curriculum design** from **challenge implementation**. The current three YAML challenges are prototypes; their proven engine behaviours are retained, but their final positions and story framing change.

---

## 1. Course promise

Brightcart should feel like a small company the learner actually joins, not a themed worksheet.

Across 100 levels, four things progress together:

| Dimension | Level 1 | Level 100 |
|---|---|---|
| SQL ability | Read one small table | Solve a multi-stage analytical problem with CTEs, joins, conditional aggregation and window functions |
| Guidance | Clause-level instructions | A business question with exact output requirements but no prescribed technique |
| Responsibility | New junior analyst completing safe support tasks | Trusted analyst preparing evidence for the leadership team |
| Database/story | Seeded company snapshot | A database whose customers, orders, prices, reviews, returns and corrections partly exist because of the learner's earlier SQL |

Every level must answer two questions:

1. **Learning purpose:** what SQL skill is being developed or revisited?
2. **Business purpose:** why does Brightcart need this result or change now?

The intended learning loop is:

> **introduce → practise → combine → revisit later → apply independently**

The course is linear, but earlier completed challenges remain replayable. The persistent database only changes when a first-time mutation challenge passes.

---

## 2. Story setting

### Brightcart Ltd

Brightcart is a Manchester-based online retailer selling everyday goods across six departments: Electronics, Books, Home & Kitchen, Clothing, Sports & Outdoors, and Toys & Games. It serves the UK, Ireland and several European markets.

The learner joins on **Monday 5 January 2026** as a **Junior Data Analyst attached to Operations**. Their job title does not unrealistically jump every 20 levels; what grows is the scope and ambiguity of the work they are trusted with.

### Story timeline

| Chapter | Approx. story period | Business context | Learner's scope |
|---|---|---|---|
| 1 — Foundations | 5–16 Jan 2026 | Onboarding and support desk | Safe lookups, simple filters, first controlled edits |
| 2 — Relational SQL | 19 Jan–6 Feb 2026 | Orders, stock and January trading | Connect tables, maintain a real order, basic operational reporting |
| 3 — Intermediate SQL | 9–27 Feb 2026 | Service recovery, data quality and a product launch | Investigate patterns, clean data, use subqueries and set logic |
| 4 — Advanced Query Construction | 2–20 Mar 2026 | Finance audit, referral review and product recall | Break complex work into stages and perform carefully scoped advanced mutations |
| 5 — Advanced Analytics | 23 Mar–3 Apr 2026 | Leadership/board preparation | Trends, rankings, cohorts, retention and multi-metric decision support |

### Recurring people and events

**Story-only staff:** Nadia Brooks (Support Lead), Kwame Mensah (Fulfilment), Lena Fischer (Merchandising), Isabel Torres (Marketing), Femi Adeyemi (Finance Director), Margaret Lowe (CEO).

**Recurring learner-created entities:**

- **Grace Hopper** — signs up in Chapter 1, adds contact details, places and receives an order, leaves a review, later makes a return, and appears in later customer/referral analysis.
- **Linnea Berg** — becomes Brightcart's first Swedish customer through Grace's referral, then places an order for the newly launched Smart Kettle Pro. Her referral is revisited in Chapters 4 and 5.
- **Smart Kettle Pro** — launched by the learner in Chapter 3 and used as a callback in later product-health analysis.

**Recurring business events:**

- January Toys & Games clearance — changes current product prices, while historical `order_items.unit_price` preserves price-at-sale.
- Holiday delivery delays — seeded historical incident investigated in Chapters 3 and 5.
- Finance refund anomalies — discovered, corrected and later reflected in net-revenue reports.
- USB-C Charger recall — a real multi-row database event in Chapter 4 whose returns affect later product and country metrics.

The story should use callbacks frequently, but never at the cost of learning clarity. A named character or event should recur because it creates useful data or context, not because the course needs lore.

---

## 3. Repo-grounded decisions before scaling to 100 levels

The existing engine is strong enough for the course, but four decisions should be treated as prerequisites before large-scale challenge implementation.

### D1 — Completed query challenges should also have historical Review mode

**Decision: implement this.**

Today, completed mutation challenges replay in a reconstructed pre-challenge sandbox, but completed query challenges run against the learner's *current* database. In a story where state changes over time, an old query can become false later.

For example, a challenge that asks for customers with no phone number may produce a different result after later contact details are updated.

**Required behaviour:** when replaying any completed challenge, validate it against the canonical database state immediately before that challenge. For queries this can reuse the existing sandbox reconstruction machinery. First-time attempts still run against the learner's live current state.

This allows story-specific query wording without forcing every early query to remain true forever.

### D2 — Optional column-name validation

**Decision: add `match_column_names: true|false`, default false.**

The current result validator deliberately ignores aliases. That is correct for most challenges, but one or two explicit alias lessons should be capable of validating the requested output names. Do not make alias matching the default.

### D3 — Separate story text from the task in challenge content

**Recommendation:** extend challenge content with a required short `story` field while keeping `instructions` as the exact deliverable. This is not required for validation, but it is worth doing before 100 levels because it lets the frontend render narrative context separately from the SQL task.

A lightweight optional metadata set is also useful for maintainability:

- `level`
- `chapter`
- `concepts`

Do **not** make runtime progression depend on this metadata; file order remains the canonical linear order.

### D4 — Schema/seed expansion is approved in principle before rewriting Levels 1–10

The current six-table schema is excellent for the prototype, but not varied enough for 100 levels. The minimum additions below materially expand the SQL that can be taught without turning the schema into a toy warehouse.

### D5 — Optional structural feature checks for concept-introduction levels

**Decision: add this narrowly, not as the default validator.** Result/state validation remains the primary definition of correctness. However, a few introduction levels exist specifically to teach a construct whose use cannot be inferred from the final rows (for example L61 CTEs and the first window-function levels). For those levels only, allow metadata such as `required_features: [cte]` or `required_features: [window]`, implemented with a real SQL parser rather than brittle string matching.

Rules:

- only require broad feature presence, never one exact AST/query shape;
- use it mainly on the first one or two levels that introduce a construct;
- later practice/independent levels return to pure outcome validation;
- equivalent implementations remain valid whenever the construct itself is not the lesson;
- do not use structural checks to force stylistic preferences.

---

## 4. Required schema and seed evolution

These changes should be implemented **before the final 100 challenge files are created**, followed by a `SEED_VERSION` bump and a full replay/content test run.

### S1 — Order lifecycle dates

Add nullable `TEXT` columns to `orders`:

- `shipped_date`
- `delivered_date`

Seed rules:

- `pending`: both NULL
- `shipped`: `shipped_date` populated, `delivered_date` NULL
- `delivered`: both populated in chronological order
- `cancelled`: both NULL

Why: enables date arithmetic, NULL lifecycle logic, delivery performance, delay cohorts and later retention analysis.

### S2 — Returns

Add:

```text
returns(
    return_id INTEGER PRIMARY KEY,
    order_item_id INTEGER NOT NULL REFERENCES order_items(order_item_id),
    return_date TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK(quantity > 0),
    reason TEXT NOT NULL,
    refund_amount REAL NOT NULL CHECK(refund_amount >= 0)
)
```

Why: enables net revenue, refund reconciliation, `EXISTS`, anti-joins, recall logic, return rates and meaningful finance work.

### S3 — Product reviews

Add:

```text
product_reviews(
    review_id INTEGER PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(product_id),
    customer_id INTEGER NOT NULL REFERENCES customers(customer_id),
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    review_date TEXT NOT NULL,
    review_text TEXT NOT NULL
)
```

Why: creates a second customer↔product relationship, supports verified-purchase questions, text work, rating aggregates and product-health analysis.

### S4 — Referrals

Add nullable `customers.referred_by_customer_id` referencing `customers(customer_id)`.

Why: gives a natural self-join and a story reason to compare referred and non-referred customers. Linnea's referral to Grace becomes a long-running callback.

### S5 — Strengthen the deterministic seed

The current fixed random seed is useful, but narrative and teaching-critical facts should be **explicit fixtures**, not accidental consequences of random generation.

Recommended final template characteristics:

- roughly **75–90 background customers** spanning signups from 2023 through Dec 2025;
- roughly **350–420 orders**, with at least 12 orders in every month of 2024–2025 so window/monthly tasks are stable;
- background orders still remain under the 500-row query cap;
- enough order items for meaningful product/category analysis, while level queries are always constrained below 500 returned rows;
- `categories` keep stable IDs 1–6 (reference data IDs may be taught/quoted; mutable story entities should still be found by natural keys);
- at least 8 customers with no order history;
- at least 8 UK customers with NULL phone numbers after the initial seed so Level 20 remains non-empty;
- one explicit QA customer `qa.test@brightcart.example` with no child rows;
- no customer in Sweden before Linnea joins;
- a cluster of slow delivered orders in Nov–Dec 2025, alongside normal deliveries;
- 2–3 delivered orders with no payment, 1–2 underpaid orders, and at least one correctly split payment across two payment rows;
- 18–30 historical returns, with 2–3 deliberately incorrect refund amounts for the Chapter 4 audit;
- 70–100 product reviews, including both verified and non-verified reviewers, plus 3–4 obvious moderation fixtures whose review text begins with `BOT:`;
- 10–15 existing referral relationships, including at least one two-step chain;
- 4–6 emails containing deterministic upper-case/whitespace defects for the Chapter 3 clean-up, with no normalization collision against another customer's canonical email;
- historical `order_items.unit_price` differs from current `products.price` for a handful of products, proving why historical revenue must use unit price at sale;
- enough historical USB-C Charger purchases for the recall to affect several rows;
- at least five countries satisfy the Level 99/100 eligibility thresholds so the final top-3 ranking is always meaningful;
- existing out-of-stock and inactive products remain useful fixtures;
- the three duplicate customer names and three seeded people named Grace are retained to teach that names are not identifiers.

**Important seed engineering rule:** keep narrative fixtures separate from background random generation where practical. Adding one random call later should not silently rename or move every teaching-critical row.

---

## 5. Curriculum design rules

### 5.1 Difficulty

Each 20-level chapter is a real step up, but there are no cliffs at 21/41/61/81.

Within each chapter, use four five-level arcs:

1. introduce/re-anchor;
2. practise;
3. combine;
4. apply with less guidance;
5. consolidate/callback.

A level should normally introduce **one new idea** or combine at most **two familiar ideas in a new way**.

### 5.2 Concept recurrence

Foundational query concepts introduced before Chapter 5 should recur repeatedly, normally at least three times later and at least once in a later chapter. Specialist constructs and destructive DML verbs should recur when the story gives them an authentic reason; do not invent pointless DELETEs or exotic syntax merely to satisfy a frequency quota.

Do not teach `JOIN`, `GROUP BY`, `CASE`, CTEs or windows as one-off syntax demonstrations. Learners should repeatedly need them for different business reasons.

### 5.3 Story continuity

- Every level has a 1–3 sentence story beat.
- At least one level in every five should directly call back to an earlier person, order, product, mutation or incident.
- Mutations are story events, not syntax demonstrations.
- Avoid more than two consecutive levels triggered by “X asks you to…”.
- The database should visibly remember successful actions.

### 5.4 Validation philosophy

- Validate **results/state**, not one canonical SQL string.
- Equivalent SQL is correct SQL.
- Require a particular construct only when it is genuinely the learning objective and D5's narrow parser-based feature check is enabled; otherwise teach through task framing and hints.
- Query tasks state exact output columns, column order, ordering/tie-breakers, rounding and date format where relevant.
- Ordered challenges must have deterministic tie-breakers.
- Mutation tasks state explicit values and an unambiguous target set.
- No mutation uses `CURRENT_TIMESTAMP`, `date('now')`, randomness or any value that cannot be reconstructed.
- No challenge depends on a column listed in `ignore_columns`.

### 5.5 Replay and determinism

- One statement per submission remains a deliberate constraint.
- Multi-table business actions are split into sequential levels.
- Story-created rows are referenced by natural keys (email, product name, date) or by IDs the learner deliberately retrieved in the immediately preceding task.
- Bulk updates use exact predicates that cannot accidentally match later learner-created rows.
- Review-mode reconstruction must remain deterministic from template + prior reference mutations.
- The canonical replay test must pass from Level 1 through Level 100 whenever challenge content changes.

### 5.6 SQLite portability

Teach broadly transferable SQL first. When SQLite differs, explain the difference rather than pretending all databases behave identically.

Important course-specific notes:

- dates are ISO text and use `date()`, `strftime()` and `julianday()`;
- `LIKE` is ASCII case-insensitive by default;
- booleans are represented by 0/1;
- money is stored as `REAL`, so displayed calculations specify `ROUND(..., 2)`;
- no `QUALIFY`; filter window results in an outer query/CTE;
- `UPDATE ... FROM`, window functions and modern joins are available in the project's SQLite version, but the course should still favour widely recognisable patterns.

---

## 6. Chapter map

| Levels | Chapter | Primary new skills | Story outcome |
|---|---|---|---|
| 1–20 | Foundations | SELECT, filtering, sorting, NULLs, search predicates, DISTINCT, basic aggregates, INSERT/UPDATE/DELETE | Learner understands the core tables; Grace is created and updated; QA data is removed |
| 21–40 | Relational SQL | GROUP BY, HAVING, INNER/LEFT JOIN, 3-table joins, multi-row DML, operational totals | Grace gets a real order/payment; stock and prices change; Linnea joins via referral |
| 41–60 | Intermediate SQL | CASE, COALESCE, strings, dates, scalar/IN/EXISTS subqueries, UNION, conditional aggregation | Data is cleaned, delivery delays analysed, Grace reviews a product, Smart Kettle launches, Linnea orders it |
| 61–80 | Advanced Query Construction | CTEs, chained CTEs, correlated logic, self joins, set differences, advanced mutation-by-query | Finance anomalies are corrected, Grace returns an item, USB-C Charger recall is processed |
| 81–100 | Advanced Analytics | Window functions, partitions, ranking, LAG/LEAD, frames, cohorts, scorecards | Learner converts the full database history into leadership-level evidence and a final priority ranking |

---

## 7. Full 100-level curriculum

### Chapter 1: Foundations — First fortnight (5–16 Jan 2026)

#### Level 1 — Meet the catalogue

- **Difficulty within chapter:** 1/5
- **Story:** Nadia starts onboarding by showing the learner the small reference table that defines what Brightcart sells. Before touching customer data, they simply need to see the six departments.
- **Task:** Return every column and every row from `categories`.
- **Kind:** `query`
- **New concept(s):** SELECT *, FROM
- **Reuses:** —
- **Tables:** categories
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Unordered result. This is the gentlest possible first success.

#### Level 2 — First contact sheet

- **Difficulty within chapter:** 1/5
- **Story:** Support needs a basic contact sheet for a routine campaign. This becomes the learner's first exercise in choosing only the fields the business actually needs.
- **Task:** Return `first_name`, `last_name`, `email` from every customer, in that column order.
- **Kind:** `query`
- **New concept(s):** Selecting specific columns
- **Reuses:** SELECT/FROM
- **Tables:** customers
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Unordered. This is the final home of the current `customer-contact-list` prototype.

#### Level 3 — UK customers

- **Difficulty within chapter:** 1/5
- **Story:** A UK-only service notice is going out. Nadia asks the learner to isolate the relevant customer records.
- **Task:** Return first name, last name, email and city for customers whose `country` is `UK`.
- **Kind:** `query`
- **New concept(s):** WHERE with equality
- **Reuses:** Specific columns
- **Tables:** customers
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 4 — Budget finds

- **Difficulty within chapter:** 1/5
- **Story:** Lena from Merchandising wants a quick list of genuinely low-cost items for a small promotion.
- **Task:** Return product name and price for products priced below £20.
- **Kind:** `query`
- **New concept(s):** Comparison operators
- **Reuses:** WHERE
- **Tables:** products
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 5 — Ready to sell

- **Difficulty within chapter:** 2/5
- **Story:** The storefront team only wants products that are both active and physically in stock. The learner now has to satisfy two conditions at once.
- **Task:** Return product name, price and stock quantity where `is_active = 1` AND `stock_quantity > 0`.
- **Kind:** `query`
- **New concept(s):** AND
- **Reuses:** WHERE/comparisons
- **Tables:** products
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 6 — Products needing attention

- **Difficulty within chapter:** 2/5
- **Story:** Lena is preparing a clean-up list: either an out-of-stock product or an inactive product needs attention.
- **Task:** Return product name, stock quantity and active flag where stock is zero OR the product is inactive.
- **Kind:** `query`
- **New concept(s):** OR
- **Reuses:** WHERE/comparisons
- **Tables:** products
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 7 — Price list

- **Difficulty within chapter:** 2/5
- **Story:** A supplier call starts in ten minutes and Lena wants the expensive items at the top of the sheet.
- **Task:** Return product name and price for all products, sorted by price descending and then product name ascending as a tie-breaker.
- **Kind:** `query`
- **New concept(s):** ORDER BY, ASC/DESC, tie-breakers
- **Reuses:** SELECT
- **Tables:** products
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered: `price DESC, name ASC`.

#### Level 8 — Premium range

- **Difficulty within chapter:** 2/5
- **Story:** With sorting understood, Lena narrows the same list to products above £50.
- **Task:** Return product name and price for products priced above £50, most expensive first and then name ascending.
- **Kind:** `query`
- **New concept(s):** Combine filter + sort
- **Reuses:** WHERE, ORDER BY
- **Tables:** products
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered. This is the final home of the current `premium-products` prototype.

#### Level 9 — Top five by stock

- **Difficulty within chapter:** 2/5
- **Story:** Kwame wants to know which active products occupy the most warehouse space before a shelf move.
- **Task:** Return product name and stock quantity for the five active products with the highest stock, ordered by stock descending then name ascending.
- **Kind:** `query`
- **New concept(s):** LIMIT
- **Reuses:** WHERE, ORDER BY
- **Tables:** products
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered and exactly five rows.

#### Level 10 — Missing phone numbers

- **Difficulty within chapter:** 2/5
- **Story:** Support notices that some customer records cannot be reached by phone.
- **Task:** Return customer id, first name, last name and email for customers whose phone is NULL.
- **Kind:** `query`
- **New concept(s):** IS NULL
- **Reuses:** WHERE
- **Tables:** customers
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 11 — Search from a fragment

- **Difficulty within chapter:** 2/5
- **Story:** A caller remembers only that the customer's surname begins with `W`. Nadia shows how support-style searches work.
- **Task:** Return first name, last name and email for customers whose last name begins with `W`, ordered by last name then first name.
- **Kind:** `query`
- **New concept(s):** LIKE
- **Reuses:** WHERE, ORDER BY
- **Tables:** customers
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by `last_name, first_name, email` so duplicate names remain deterministic.

#### Level 12 — Priority markets

- **Difficulty within chapter:** 2/5
- **Story:** A translated help article is ready for three markets first.
- **Task:** Return first name, last name, country and email for customers in the UK, Ireland or Germany.
- **Kind:** `query`
- **New concept(s):** IN
- **Reuses:** WHERE
- **Tables:** customers
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 13 — Recent sign-ups

- **Difficulty within chapter:** 3/5
- **Story:** Nadia wants to check people who joined during the final quarter of 2025 before the new-year campaign starts.
- **Task:** Return first name, last name, email and signup date for customers who signed up between `2025-10-01` and `2025-12-31`, inclusive, ordered by signup date then email.
- **Kind:** `query`
- **New concept(s):** BETWEEN
- **Reuses:** WHERE, ORDER BY
- **Tables:** customers
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered; seed must guarantee non-empty Q4 2025 signups.

#### Level 14 — Grace joins Brightcart

- **Difficulty within chapter:** 3/5
- **Story:** A new customer, Grace Hopper, signs up by phone but does not provide a phone number yet. For the first time the learner is trusted to add real data.
- **Task:** Insert Grace Hopper with email `grace.hopper@example.com`, city London, country UK, signup date `2026-01-12`, phone NULL, and let SQLite assign the customer id.
- **Kind:** `mutation`
- **New concept(s):** INSERT
- **Reuses:** Column selection, NULL
- **Tables:** customers
- **Depends on state from:** —
- **Canonical state change:** INSERT exactly one Grace Hopper row; phone NULL; deterministic date 2026-01-12.
- **Enables later:** L15–16, L28–35, L55, L68–69, L74, L96 and later customer metrics.
- **Validation notes:** State diff must show exactly one inserted customer and no other table changes.

#### Level 15 — The right Grace

- **Difficulty within chapter:** 3/5
- **Story:** A support ticket arrives for `grace.hopper@example.com`. The learner sees several other customers named Grace and learns why names are not safe identifiers.
- **Task:** Return customer id, first name, last name, email and phone for the customer with email `grace.hopper@example.com`.
- **Kind:** `query`
- **New concept(s):** Natural-key lookup
- **Reuses:** WHERE
- **Tables:** customers
- **Depends on state from:** L14 created Grace
- **Enables later:** L16 and later Grace tasks
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 16 — Grace adds a phone number

- **Difficulty within chapter:** 3/5
- **Story:** Grace calls back with the missing contact detail. Nadia lets the learner make a tightly scoped correction.
- **Task:** Update Grace Hopper's phone number to `07700 900123`, targeting her by email.
- **Kind:** `mutation`
- **New concept(s):** UPDATE
- **Reuses:** WHERE natural key
- **Tables:** customers
- **Depends on state from:** L14 Grace exists
- **Canonical state change:** UPDATE exactly one customer; only `phone` changes to 07700 900123.
- **Enables later:** L20 contact-gap checkpoint and later complete customer record.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 17 — Our customer footprint

- **Difficulty within chapter:** 3/5
- **Story:** Support wants the set of countries Brightcart currently serves, not one row per customer.
- **Task:** Return the distinct countries represented in `customers`, alphabetically.
- **Kind:** `query`
- **New concept(s):** DISTINCT
- **Reuses:** ORDER BY
- **Tables:** customers
- **Depends on state from:** L14 adds another UK customer
- **Enables later:** —
- **Validation notes:** Ordered alphabetically.

#### Level 18 — Catalogue at a glance

- **Difficulty within chapter:** 4/5
- **Story:** Lena wants one compact line summarising the catalogue before a planning call.
- **Task:** Return four columns: product count as `product_count`, cheapest price as `cheapest_price`, most expensive price as `highest_price`, and average price rounded to 2 decimals as `average_price`.
- **Kind:** `query`
- **New concept(s):** COUNT/MIN/MAX/AVG, ROUND, column aliases
- **Reuses:** SELECT
- **Tables:** products
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Single row. Requires `match_column_names: true` once D2 is implemented.

#### Level 19 — Remove the QA account

- **Difficulty within chapter:** 4/5
- **Story:** A test account accidentally survived into the production-like dataset. It has no orders, so Support approves its deletion before exports are produced.
- **Task:** Delete the customer whose email is `qa.test@brightcart.example`.
- **Kind:** `mutation`
- **New concept(s):** DELETE
- **Reuses:** WHERE natural key
- **Tables:** customers
- **Depends on state from:** Seed fixture guarantees QA account has no child rows
- **Canonical state change:** DELETE exactly the QA customer and nothing else.
- **Enables later:** All later customer counts use the cleaned population.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 20 — Support handover

- **Difficulty within chapter:** 5/5
- **Story:** At the end of the learner's first fortnight, Nadia wants a handover list of UK customers who still cannot be reached by phone.
- **Task:** Return first name, last name, email and signup date for the five most recently signed-up UK customers whose phone is NULL. Sort by signup date descending, then email ascending.
- **Kind:** `query`
- **New concept(s):** Chapter-1 consolidation
- **Reuses:** WHERE, AND, IS NULL, ORDER BY, LIMIT
- **Tables:** customers
- **Depends on state from:** L16 removes Grace from the missing-phone set; L19 removes QA account
- **Enables later:** —
- **Validation notes:** Ordered, five rows. Chapter checkpoint; hints should be less explicit than earlier levels.

### Chapter 2: Relational SQL — Orders in motion (19 Jan–6 Feb 2026)

#### Level 21 — Orders by status

- **Difficulty within chapter:** 1/5
- **Story:** Kwame begins the learner's operations rotation with a simple question: how many orders are currently in each state?
- **Task:** Return `status` and the number of orders in that status, ordered by count descending then status.
- **Kind:** `query`
- **New concept(s):** GROUP BY
- **Reuses:** COUNT, ORDER BY
- **Tables:** orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by count DESC, status ASC.

#### Level 22 — Who orders most?

- **Difficulty within chapter:** 1/5
- **Story:** Operations wants a first view of repeat activity, even before names are joined in.
- **Task:** Return customer id and order count for customers who have placed orders, highest count first then customer id.
- **Kind:** `query`
- **New concept(s):** Aggregate per group
- **Reuses:** GROUP BY, COUNT, ORDER BY
- **Tables:** orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered.

#### Level 23 — Frequent buyers only

- **Difficulty within chapter:** 2/5
- **Story:** The previous report is too long. Kwame wants only customers with at least four orders.
- **Task:** Return customer id and order count for customers with at least four orders, highest count first then customer id.
- **Kind:** `query`
- **New concept(s):** HAVING
- **Reuses:** GROUP BY, COUNT, ORDER BY
- **Tables:** orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered.

#### Level 24 — Put names to orders

- **Difficulty within chapter:** 2/5
- **Story:** IDs are useful to databases, not people. The learner now connects each order to its customer.
- **Task:** Return order id, order date, status, customer first name, customer last name and email for all orders, ordered by order date descending then order id descending.
- **Kind:** `query`
- **New concept(s):** INNER JOIN, table aliases
- **Reuses:** ORDER BY
- **Tables:** orders, customers
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered.

#### Level 25 — Products and departments

- **Difficulty within chapter:** 2/5
- **Story:** Lena wants a readable product list with department names instead of category ids.
- **Task:** Return product name, category name, price and stock quantity for all products, ordered by category name then product name.
- **Kind:** `query`
- **New concept(s):** JOIN through a foreign key
- **Reuses:** INNER JOIN, aliases
- **Tables:** products, categories
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered.

#### Level 26 — Customers with no orders

- **Difficulty within chapter:** 2/5
- **Story:** Marketing wants a re-engagement list of customers who have never ordered. This is the learner's first outer join.
- **Task:** Return customer id, first name, last name and email for customers with no matching order, ordered by customer id.
- **Kind:** `query`
- **New concept(s):** LEFT JOIN + anti-join pattern
- **Reuses:** IS NULL, joins
- **Tables:** customers, orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered; seed guarantees several matches.

#### Level 27 — Revenue by category

- **Difficulty within chapter:** 3/5
- **Story:** Femi asks for a basic sales view. The learner has to follow order items through products into categories and aggregate money at the category level.
- **Task:** Return category name and gross item revenue (`quantity * unit_price`) rounded to 2 decimals for all historical order items, highest revenue first then category name.
- **Kind:** `query`
- **New concept(s):** Three-table join + GROUP BY
- **Reuses:** JOIN, SUM, ROUND, ORDER BY
- **Tables:** order_items, products, categories
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered. Revenue must use `order_items.unit_price`, never current product price.

#### Level 28 — Prepare Grace's first order

- **Difficulty within chapter:** 2/5
- **Story:** Grace is ready to buy. Before entering the order, the learner must retrieve the database key that links an order to her customer row.
- **Task:** Return Grace Hopper's customer id using her email.
- **Kind:** `query`
- **New concept(s):** Foreign-key lookup as workflow
- **Reuses:** WHERE
- **Tables:** customers
- **Depends on state from:** L14 Grace exists
- **Enables later:** L29
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 29 — Open Grace's first order

- **Difficulty within chapter:** 3/5
- **Story:** Grace places an order on `2026-01-20`. The learner creates the order header first, mirroring how relational records are built in stages.
- **Task:** Insert one `pending` order for Grace dated `2026-01-20`, using the customer id found in L28 (or an equivalent lookup inside the statement).
- **Kind:** `mutation`
- **New concept(s):** INSERT into a child table
- **Reuses:** Foreign keys
- **Tables:** orders
- **Depends on state from:** L28 identifies Grace
- **Canonical state change:** INSERT exactly one pending order for Grace on 2026-01-20; lifecycle dates NULL.
- **Enables later:** L30–35, L55, L74.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 30 — Confirm Grace's new order

- **Difficulty within chapter:** 3/5
- **Story:** Before adding items, Operations verifies that the correct order header exists.
- **Task:** Return the order id, order date and status for Grace Hopper's order dated `2026-01-20`.
- **Kind:** `query`
- **New concept(s):** Join-based verification
- **Reuses:** INNER JOIN, WHERE
- **Tables:** orders, customers
- **Depends on state from:** L29 created order
- **Enables later:** L32/L34/L35
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 31 — Pick Grace's products

- **Difficulty within chapter:** 2/5
- **Story:** Grace ordered two familiar items. The learner looks up the product keys and current prices needed for the order lines.
- **Task:** Return product id, name and price for `SQL for Beginners` and `French Press`, ordered by product name.
- **Kind:** `query`
- **New concept(s):** IN as a practical lookup
- **Reuses:** IN, ORDER BY
- **Tables:** products
- **Depends on state from:** —
- **Enables later:** L32
- **Validation notes:** Ordered by name.

#### Level 32 — Fill Grace's basket

- **Difficulty within chapter:** 3/5
- **Story:** The order header exists, so the learner can add its two line items in one statement.
- **Task:** Insert two order-item rows for Grace's 2026-01-20 order: 1 × `SQL for Beginners` and 1 × `French Press`, using the product ids/prices identified in L31 and the order id from L30.
- **Kind:** `mutation`
- **New concept(s):** Multi-row INSERT
- **Reuses:** Foreign keys, VALUES
- **Tables:** order_items
- **Depends on state from:** L29 order; L30 order id; L31 products
- **Canonical state change:** INSERT exactly two order_items with quantity 1 and the correct price-at-sale for each product.
- **Enables later:** L33–34, L55, L74 and all later revenue.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 33 — What is the basket worth?

- **Difficulty within chapter:** 3/5
- **Story:** The payment provider needs the exact amount to capture. Rather than adding prices manually, the learner calculates the order total from its lines.
- **Task:** Return Grace's 2026-01-20 order id and total value rounded to 2 decimals.
- **Kind:** `query`
- **New concept(s):** Aggregate over joined detail
- **Reuses:** JOIN, SUM, GROUP BY
- **Tables:** orders, customers, order_items
- **Depends on state from:** L32 added lines
- **Enables later:** L34
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 34 — Record the payment

- **Difficulty within chapter:** 3/5
- **Story:** The card payment succeeds for the amount calculated in the previous level.
- **Task:** Insert one card payment for Grace's 2026-01-20 order, using the order id and exact total from L33, with `paid_at = '2026-01-20'`.
- **Kind:** `mutation`
- **New concept(s):** INSERT related financial row
- **Reuses:** Foreign keys
- **Tables:** payments
- **Depends on state from:** L33 establishes order total
- **Canonical state change:** INSERT exactly one payment for Grace's order with the correct amount/method/date.
- **Enables later:** Finance reconciliation in L63/L79/L80.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 35 — Ship Grace's order

- **Difficulty within chapter:** 3/5
- **Story:** The warehouse dispatches Grace's parcel two days later.
- **Task:** Update Grace's 2026-01-20 order to status `shipped` and set `shipped_date` to `2026-01-22`; do not set delivered_date yet.
- **Kind:** `mutation`
- **New concept(s):** UPDATE multiple columns
- **Reuses:** WHERE through a precise order target
- **Tables:** orders
- **Depends on state from:** L29 order exists; S1 lifecycle columns
- **Canonical state change:** UPDATE exactly Grace's order: status shipped, shipped_date 2026-01-22, delivered_date remains NULL.
- **Enables later:** L41 delivery completion and later lifecycle analysis.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 36 — Inventory value by category

- **Difficulty within chapter:** 3/5
- **Story:** Kwame and Lena compare how much current stock value is tied up in each department.
- **Task:** Return category name and current inventory value (`price * stock_quantity`) rounded to 2 decimals, highest value first then category name.
- **Kind:** `query`
- **New concept(s):** Join + grouped computed metric
- **Reuses:** JOIN, GROUP BY, SUM, ROUND
- **Tables:** categories, products
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered.

#### Level 37 — Restock the monitor

- **Difficulty within chapter:** 3/5
- **Story:** A shipment of 27-inch Monitors arrives. This is a simple operational update with a visible later consequence.
- **Task:** Set the `27-inch Monitor` stock quantity to exactly 40.
- **Kind:** `mutation`
- **New concept(s):** UPDATE by natural key
- **Reuses:** WHERE
- **Tables:** products
- **Depends on state from:** —
- **Canonical state change:** UPDATE exactly one product stock_quantity to 40.
- **Enables later:** Later stock/product-health reports.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 38 — Linnea joins by referral

- **Difficulty within chapter:** 4/5
- **Story:** Grace recommends Brightcart to her friend Linnea Berg in Stockholm. Linnea becomes the company's first Swedish customer, and the referral relationship is stored rather than just mentioned in prose.
- **Task:** Insert Linnea Berg (`linnea.berg@example.com`, phone NULL, Stockholm, Sweden, signup `2026-01-27`) with `referred_by_customer_id` pointing to Grace. Prefer `INSERT ... SELECT` so Grace is found by email.
- **Kind:** `mutation`
- **New concept(s):** INSERT ... SELECT; self-referencing FK
- **Reuses:** INSERT, SELECT
- **Tables:** customers
- **Depends on state from:** L14 Grace; S4 referral column
- **Canonical state change:** INSERT exactly one Linnea row with referral pointing to Grace.
- **Enables later:** L58–59, L68–69, L96 and Sweden appearing in later country analysis.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 39 — January clearance

- **Difficulty within chapter:** 4/5
- **Story:** Lena starts a 10% Toys & Games clearance. Historical order lines must keep their original unit prices while the current catalogue price changes.
- **Task:** Reduce every Toys & Games product's current `price` by 10%, rounded to 2 decimals, and no other products. Category id 6 is stable reference data; an equivalent category-name subquery is also valid.
- **Kind:** `mutation`
- **New concept(s):** Set-based UPDATE with arithmetic
- **Reuses:** UPDATE, IN/reference key, ROUND
- **Tables:** products
- **Depends on state from:** Stable categories fixture
- **Canonical state change:** UPDATE exactly the Toys & Games products; price = ROUND(old_price * 0.90, 2).
- **Enables later:** Later distinction between current price and historical `unit_price`.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 40 — January operations brief

- **Difficulty within chapter:** 5/5
- **Story:** Kwame asks for the learner's first substantial operational report: which countries are generating meaningful order volume and value?
- **Task:** For non-cancelled orders, return country, order count and gross order value rounded to 2 decimals. Keep countries with at least 5 orders. Sort by gross value descending then country.
- **Kind:** `query`
- **New concept(s):** Chapter-2 consolidation
- **Reuses:** JOINs, GROUP BY, HAVING, WHERE, SUM, ROUND
- **Tables:** customers, orders, order_items
- **Depends on state from:** Includes L29/L32; customer population includes L38
- **Enables later:** —
- **Validation notes:** Ordered; chapter checkpoint with reduced hint specificity.

### Chapter 3: Intermediate SQL — Service recovery (9–27 Feb 2026)

#### Level 41 — Grace's parcel arrives

- **Difficulty within chapter:** 1/5
- **Story:** Grace confirms delivery. The learner completes the lifecycle started in Chapter 2 before moving into analytical work.
- **Task:** Update Grace's 2026-01-20 order to status `delivered` and set `delivered_date` to `2026-01-24`, preserving its shipped date.
- **Kind:** `mutation`
- **New concept(s):** Lifecycle UPDATE callback
- **Reuses:** UPDATE, precise targeting
- **Tables:** orders
- **Depends on state from:** L35 shipped Grace's order
- **Canonical state change:** UPDATE exactly Grace's order status/delivered_date; shipped_date unchanged.
- **Enables later:** L47+ delivery analysis and L55/L74 story consistency.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 42 — Stock labels people can read

- **Difficulty within chapter:** 1/5
- **Story:** A warehouse export currently shows only numbers. Kwame wants a human-readable stock condition beside each product.
- **Task:** Return product name, stock quantity and a `stock_status`: `Out of stock` for 0, `Low` for 1–9, otherwise `Healthy`. Order by stock quantity then product name.
- **Kind:** `query`
- **New concept(s):** CASE
- **Reuses:** ORDER BY
- **Tables:** products
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered. Alias may be visually shown; only require name matching if D2 is enabled for this level.

#### Level 43 — Never leave contact blank

- **Difficulty within chapter:** 1/5
- **Story:** Support's call sheet should display a useful fallback rather than NULL phone values.
- **Task:** Return first name, last name, email and phone display, using `No phone provided` when phone is NULL.
- **Kind:** `query`
- **New concept(s):** COALESCE
- **Reuses:** NULL handling
- **Tables:** customers
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 44 — Clean display names

- **Difficulty within chapter:** 2/5
- **Story:** Marketing exports need consistent display text even when source strings contain whitespace or odd casing.
- **Task:** Return customer id, a `display_name` made from first and last name, and a normalized email preview using trimming/lowercasing. Order by customer id.
- **Kind:** `query`
- **New concept(s):** String concatenation and text functions
- **Reuses:** Aliases, ORDER BY
- **Tables:** customers
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered. This prepares the learner to recognise defects before modifying data.

#### Level 45 — Audit messy emails

- **Difficulty within chapter:** 2/5
- **Story:** The preview reveals that a handful of seeded records are not stored in canonical email form.
- **Task:** Return customer id and email for rows where the stored email differs from `LOWER(TRIM(email))`, ordered by customer id.
- **Kind:** `query`
- **New concept(s):** Use functions in a predicate
- **Reuses:** LOWER, TRIM, WHERE
- **Tables:** customers
- **Depends on state from:** Seed S5 provides deterministic dirty emails
- **Enables later:** L46
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 46 — Clean the emails

- **Difficulty within chapter:** 2/5
- **Story:** The audit has been approved. The learner normalises only the rows that actually need correction.
- **Task:** Update non-canonical customer emails to `LOWER(TRIM(email))`; canonical emails must remain untouched.
- **Kind:** `mutation`
- **New concept(s):** UPDATE using expressions
- **Reuses:** LOWER, TRIM, WHERE
- **Tables:** customers
- **Depends on state from:** L45 identifies dirty rows
- **Canonical state change:** UPDATE exactly the seeded dirty-email rows; only email changes.
- **Enables later:** Stable email matching in all later work.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 47 — How long did delivery take?

- **Difficulty within chapter:** 2/5
- **Story:** The holiday service review begins. The learner calculates a duration between two ISO dates for the first time.
- **Task:** For delivered orders in Dec 2025, return order id, order date, delivered date and delivery days as an integer difference using SQLite date functions. Order by order id.
- **Kind:** `query`
- **New concept(s):** Date arithmetic with `julianday()`
- **Reuses:** WHERE, ORDER BY
- **Tables:** orders
- **Depends on state from:** S1 dates + seeded Dec 2025 delivered orders
- **Enables later:** —
- **Validation notes:** Ordered; task explains SQLite stores dates as text.

#### Level 48 — Delay bands

- **Difficulty within chapter:** 3/5
- **Story:** A raw number of days is hard to scan, so Isabel wants deliveries grouped into service bands.
- **Task:** For delivered Dec 2025 orders, return order id, delivery days and a label: `On time` (0–3), `Watch` (4–5), `Late` (>5). Order by delivery days descending then order id.
- **Kind:** `query`
- **New concept(s):** CASE combined with date arithmetic
- **Reuses:** CASE, julianday, ORDER BY
- **Tables:** orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered.

#### Level 49 — Above-average products

- **Difficulty within chapter:** 3/5
- **Story:** Lena wants products priced above the catalogue's average without calculating that average separately first.
- **Task:** Return product name and current price for products above the overall average current product price, highest price first then name.
- **Kind:** `query`
- **New concept(s):** Scalar subquery
- **Reuses:** AVG, WHERE, ORDER BY
- **Tables:** products
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered.

#### Level 50 — Electronics buyers

- **Difficulty within chapter:** 3/5
- **Story:** Marketing wants customers who have bought at least one Electronics product. The learner uses a query result as the filter for another query.
- **Task:** Return distinct customer id, first name, last name and email for customers who have an order containing an Electronics product, ordered by customer id.
- **Kind:** `query`
- **New concept(s):** IN subquery
- **Reuses:** JOINs, DISTINCT
- **Tables:** customers, orders, order_items, products, categories
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered; equivalent JOIN/EXISTS solutions are valid.

#### Level 51 — Customers who have ordered

- **Difficulty within chapter:** 3/5
- **Story:** The learner now expresses existence directly rather than joining rows they do not need to display.
- **Task:** Return customer id, first name, last name and email for customers for whom at least one order exists, ordered by customer id.
- **Kind:** `query`
- **New concept(s):** EXISTS
- **Reuses:** Correlated predicate, ORDER BY
- **Tables:** customers, orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered.

#### Level 52 — Customers who never ordered — revisited

- **Difficulty within chapter:** 3/5
- **Story:** Earlier the learner solved this with a LEFT JOIN. Isabel asks for the same business population again, but the hint path introduces the `NOT EXISTS` alternative.
- **Task:** Return customer id, first name, last name and email for customers with no orders, ordered by customer id.
- **Kind:** `query`
- **New concept(s):** NOT EXISTS
- **Reuses:** EXISTS, prior anti-join concept
- **Tables:** customers, orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered; LEFT JOIN remains an accepted equivalent outcome.

#### Level 53 — One recovery mailing list

- **Difficulty within chapter:** 4/5
- **Story:** Isabel wants one deduplicated list containing customers affected by a late Dec-2025 delivery *or* customers who have never ordered.
- **Task:** Return customer id and email for the union of those two audiences, ordered by customer id.
- **Kind:** `query`
- **New concept(s):** UNION
- **Reuses:** Subqueries/EXISTS, date logic
- **Tables:** customers, orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered. Alternative equivalent formulations pass, but hints teach UNION.

#### Level 54 — Delay rate by country

- **Difficulty within chapter:** 4/5
- **Story:** The service issue is no longer about individual orders. Leadership wants to know which markets were disproportionately affected.
- **Task:** For delivered Dec-2025 orders, return country, delivered order count, late order count (>5 days), and late-rate percentage rounded to 1 decimal. Order by late rate descending then country.
- **Kind:** `query`
- **New concept(s):** Conditional aggregation
- **Reuses:** JOIN, GROUP BY, CASE, dates
- **Tables:** customers, orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered; guard denominator via delivered-order filter.

#### Level 55 — Grace reviews her book

- **Difficulty within chapter:** 4/5
- **Story:** Grace emails a five-star review of `SQL for Beginners`: `Clear and practical`. Her purchase is now delivered, so the new review becomes useful later in verified-purchase analysis.
- **Task:** Insert Grace's 5-star review for `SQL for Beginners`, dated `2026-02-16`, with review text `Clear and practical`. Find the customer/product by natural keys in the statement rather than hard-coding generated ids.
- **Kind:** `mutation`
- **New concept(s):** INSERT ... SELECT across lookup tables
- **Reuses:** Subqueries/joins, natural keys
- **Tables:** product_reviews, customers, products
- **Depends on state from:** L41 delivered Grace's order; S3 reviews
- **Canonical state change:** INSERT exactly one review with the specified rating/date/text and correct FKs.
- **Enables later:** L67 verified-review audit and L98 product health.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 56 — Launch Smart Kettle Pro

- **Difficulty within chapter:** 4/5
- **Story:** Lena's new Home & Kitchen product is ready to go live. The learner creates the catalogue row rather than merely reporting on existing data.
- **Task:** Insert `Smart Kettle Pro` into Home & Kitchen at £59.99, stock 80, active 1. Resolve the category by name rather than depending on a generated product id.
- **Kind:** `mutation`
- **New concept(s):** INSERT using a lookup subquery
- **Reuses:** Scalar subquery, INSERT
- **Tables:** products, categories
- **Depends on state from:** S3/S5 not required; Home & Kitchen exists
- **Canonical state change:** INSERT exactly one active product with specified price/stock/category.
- **Enables later:** L57–59 and L98 callback.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 57 — Launch check

- **Difficulty within chapter:** 4/5
- **Story:** Before the campaign goes out, Lena wants to see how the new product sits against the rest of its department.
- **Task:** Return the Smart Kettle Pro name, price, Home & Kitchen category name, and the category's average product price rounded to 2 decimals.
- **Kind:** `query`
- **New concept(s):** Combine join + grouped/subquery comparison
- **Reuses:** JOIN, subquery, AVG
- **Tables:** products, categories
- **Depends on state from:** L56 created product
- **Enables later:** —
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 58 — Linnea places a kettle order

- **Difficulty within chapter:** 4/5
- **Story:** Linnea responds to the launch email and places her first order on `2026-02-20`.
- **Task:** Insert one pending order for `linnea.berg@example.com` dated `2026-02-20`, resolving her customer id inside the statement.
- **Kind:** `mutation`
- **New concept(s):** INSERT with scalar lookup
- **Reuses:** Subquery, foreign key
- **Tables:** orders, customers
- **Depends on state from:** L38 Linnea exists
- **Canonical state change:** INSERT exactly one pending Linnea order dated 2026-02-20.
- **Enables later:** L59 and later referral/customer history.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 59 — Add the kettle to Linnea's order

- **Difficulty within chapter:** 4/5
- **Story:** The order header is ready. The learner adds one Smart Kettle Pro at its launch price without relying on hard-coded ids.
- **Task:** Insert one order item for Linnea's 2026-02-20 order: quantity 1, product Smart Kettle Pro, unit price £59.99. Resolve order/product keys within the statement.
- **Kind:** `mutation`
- **New concept(s):** INSERT ... SELECT with several lookups
- **Reuses:** JOINs/subqueries, natural keys
- **Tables:** order_items, orders, customers, products
- **Depends on state from:** L56 product; L58 order
- **Canonical state change:** INSERT exactly one Kettle order_item on Linnea's order.
- **Enables later:** L69/L96 referral value and L98 product-health callback.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 60 — Delivery incident report

- **Difficulty within chapter:** 5/5
- **Story:** The service-recovery review closes with a country-level report on the Dec-2025 delay cluster. The task states the output, not the SQL technique.
- **Task:** For countries with at least 5 delivered Dec-2025 orders, return country, delivered_orders, late_orders (>5 days), late_rate_pct (1 decimal), and avg_delivery_days (1 decimal). Sort by late rate descending then country.
- **Kind:** `query`
- **New concept(s):** Chapter-3 consolidation
- **Reuses:** Dates, CASE, conditional aggregation, JOIN, GROUP BY, HAVING
- **Tables:** customers, orders
- **Depends on state from:** Seeded holiday delay cluster
- **Enables later:** —
- **Validation notes:** Ordered; checkpoint. Hints should guide decomposition but not provide a complete query.

### Chapter 4: Advanced Query Construction — Audit and recall (2–20 Mar 2026)

#### Level 61 — Name the working set

- **Difficulty within chapter:** 1/5
- **Story:** Femi starts the finance rotation with a readability problem: a query has the same filtered order set repeated several times. The learner gives that set a name.
- **Task:** Use a CTE representing delivered 2025 orders, then return order id, customer id and order date from it for December 2025, ordered by order id.
- **Kind:** `query`
- **New concept(s):** Single CTE
- **Reuses:** Date filtering, ORDER BY
- **Tables:** orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered. The task explicitly asks for a CTE because the construct itself is the lesson.

#### Level 62 — Build order totals once

- **Difficulty within chapter:** 2/5
- **Story:** Finance repeatedly needs an order-level total derived from line items. A CTE makes that reusable intermediate result explicit.
- **Task:** Create an `order_totals` CTE that calculates each order's gross value from `quantity * unit_price`, then return order id and total for delivered 2025 orders, highest total first then order id.
- **Kind:** `query`
- **New concept(s):** Aggregate CTE
- **Reuses:** CTE, GROUP BY, JOIN, SUM
- **Tables:** order_items, orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered; use price-at-sale from order_items, a callback to L39.

#### Level 63 — Paid versus ordered

- **Difficulty within chapter:** 2/5
- **Story:** Femi warns that payments are not guaranteed to be one row per order. The learner must aggregate both sides before comparing them.
- **Task:** Using separate order-total and payment-total CTEs, return delivered 2025 order id, order total, amount paid and payment difference (`paid - order_total`), rounded to 2 decimals, for orders where the difference is not zero or payment is missing.
- **Kind:** `query`
- **New concept(s):** Multiple/chained CTEs
- **Reuses:** CTE, GROUP BY, LEFT JOIN, COALESCE
- **Tables:** orders, order_items, payments
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by absolute difference descending then order id; seeded anomalies guarantee rows.

#### Level 64 — Net revenue after returns

- **Difficulty within chapter:** 2/5
- **Story:** Gross sales are not revenue after refunds. The learner now stages order sales and returns separately and combines them.
- **Task:** For each delivered 2025 order, return order id, gross sales, refund amount and net revenue, all rounded to 2 decimals. Sort by net revenue descending then order id.
- **Kind:** `query`
- **New concept(s):** Multi-stage CTE analysis
- **Reuses:** CTEs, LEFT JOIN, aggregates, COALESCE
- **Tables:** orders, order_items, returns
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered; return amounts are not assumed correct until L72.

#### Level 65 — Customer value pipeline

- **Difficulty within chapter:** 3/5
- **Story:** Isabel wants a reusable customer-spend dataset rather than a single giant SELECT.
- **Task:** Build one CTE for customer net spend and a second stage that labels each customer `High`, `Medium` or `Low` using explicit spend thresholds supplied in the task. Return email, spend and segment, highest spend first.
- **Kind:** `query`
- **New concept(s):** Chained CTEs + CASE
- **Reuses:** CTEs, CASE, net revenue
- **Tables:** customers, orders, order_items, returns
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered; thresholds are explicit in final challenge content.

#### Level 66 — Compared with their market

- **Difficulty within chapter:** 3/5
- **Story:** A £500 customer may be exceptional in one country and ordinary in another. The learner compares each customer's value with an aggregate that depends on that customer's own country.
- **Task:** Return customers whose net spend is above the average net spend of customers in the same country. Show email, country, net_spend and country_average, rounded to 2 decimals, ordered by country then net_spend descending.
- **Kind:** `query`
- **New concept(s):** Correlated scalar subquery
- **Reuses:** CTEs, aggregates, correlation
- **Tables:** customers, orders, order_items, returns
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered. An equivalent join-to-country-averages solution is valid.

#### Level 67 — Verified review audit

- **Difficulty within chapter:** 3/5
- **Story:** Product ratings are only trustworthy if reviewers actually bought the product. Grace's new review should pass this check.
- **Task:** Return review id, customer email, product name and rating for reviews where a matching purchase by that customer of that product exists. Order by review id.
- **Kind:** `query`
- **New concept(s):** Correlated EXISTS across a relationship chain
- **Reuses:** EXISTS, joins
- **Tables:** product_reviews, customers, products, orders, order_items
- **Depends on state from:** L55 added Grace review
- **Enables later:** —
- **Validation notes:** Ordered; Grace's review is an intentional callback.

#### Level 68 — Who referred whom?

- **Difficulty within chapter:** 3/5
- **Story:** Marketing finally analyses the referral field that has been quietly accumulating. Linnea should appear with Grace as her referrer.
- **Task:** Return referred customer's email and referrer's email for every customer with a referrer, ordered by referred customer email.
- **Kind:** `query`
- **New concept(s):** Self join
- **Reuses:** INNER JOIN, aliases
- **Tables:** customers
- **Depends on state from:** S4 referrals; L38 Linnea→Grace
- **Enables later:** —
- **Validation notes:** Ordered.

#### Level 69 — Did referrals create value?

- **Difficulty within chapter:** 4/5
- **Story:** Isabel wants to move beyond a referral count and understand the downstream spend those referrals generated.
- **Task:** For each referrer, return referrer email, number of referred customers and total gross order value generated by those referred customers, rounded to 2 decimals. Sort by referred revenue descending then referrer email.
- **Kind:** `query`
- **New concept(s):** Self join + downstream aggregation
- **Reuses:** Self join, multi-table JOIN, GROUP BY, SUM
- **Tables:** customers, orders, order_items
- **Depends on state from:** L38 referral; L58–59 add Linnea activity
- **Enables later:** —
- **Validation notes:** Ordered; use LEFT JOINs where needed so referrers with zero referred spend can still be represented if challenge content chooses.

#### Level 70 — Delivered but unpaid

- **Difficulty within chapter:** 3/5
- **Story:** Femi asks for an audit list that is naturally phrased as one set minus another.
- **Task:** Return order ids for orders marked delivered that do not appear in the payment table, ordered by order id. The hint path introduces `EXCEPT`.
- **Kind:** `query`
- **New concept(s):** EXCEPT / set difference
- **Reuses:** Set operations, ORDER BY
- **Tables:** orders, payments
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered. Equivalent NOT EXISTS/LEFT JOIN solutions remain correct.

#### Level 71 — Refunds that do not reconcile

- **Difficulty within chapter:** 4/5
- **Story:** The audit finds a few historical returns whose stored refund amount does not equal returned quantity × price paid.
- **Task:** Return return id, order item id, stored refund, expected refund and difference for mismatched returns. Round money to 2 decimals; order by absolute difference descending then return id.
- **Kind:** `query`
- **New concept(s):** Audit comparison across relationships
- **Reuses:** JOIN, arithmetic, ROUND
- **Tables:** returns, order_items
- **Depends on state from:** Seed S5 refund anomalies
- **Enables later:** L72
- **Validation notes:** Ordered and non-empty.

#### Level 72 — Correct the refund amounts

- **Difficulty within chapter:** 4/5
- **Story:** Femi approves the correction. This is the first advanced mutation whose new value is derived from another table rather than typed as a literal.
- **Task:** Update only mismatched returns so `refund_amount` equals `returns.quantity * order_items.unit_price`, rounded to 2 decimals.
- **Kind:** `mutation`
- **New concept(s):** UPDATE driven by another table/subquery
- **Reuses:** UPDATE, correlated lookup or UPDATE FROM
- **Tables:** returns, order_items
- **Depends on state from:** L71 identifies anomalies
- **Canonical state change:** UPDATE exactly the anomalous return rows; only refund_amount changes.
- **Enables later:** L80, L98–100 clean net-revenue metrics.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 73 — Remove bot reviews

- **Difficulty within chapter:** 4/5
- **Story:** The review moderation queue contains a few deliberately obvious bot posts. Unlike the Chapter 1 single-row delete, this cleanup targets a set defined by a text rule.
- **Task:** Delete only product reviews whose `review_text` begins with `BOT:`.
- **Kind:** `mutation`
- **New concept(s):** Set-based DELETE with a text predicate
- **Reuses:** DELETE, LIKE
- **Tables:** product_reviews
- **Depends on state from:** Seed S5 moderation fixtures
- **Canonical state change:** DELETE exactly the seeded `BOT:` review rows and no genuine reviews.
- **Enables later:** Later rating/product-health analysis uses the cleaned review population.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 74 — Record Grace's return

- **Difficulty within chapter:** 4/5
- **Story:** Grace decides the French Press from her January order is not for her. At this stage the learner is expected to find the correct order-item row inside the mutation rather than completing a separate lookup exercise first.
- **Task:** Insert a return for the French Press on Grace Hopper's delivered `2026-01-20` order: return date `2026-03-10`, quantity 1, reason `changed_mind`, refund amount equal to that item's unit price. Resolve the order item by joining natural keys in the statement.
- **Kind:** `mutation`
- **New concept(s):** INSERT ... SELECT through a relationship chain
- **Reuses:** INSERT SELECT, JOINs, natural keys
- **Tables:** returns, order_items, orders, customers, products
- **Depends on state from:** L32 item; L41 delivery
- **Canonical state change:** INSERT exactly one return for Grace's French Press with specified date/reason/full refund.
- **Enables later:** L80 and later customer/product return metrics.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 75 — Scope the charger recall

- **Difficulty within chapter:** 4/5
- **Story:** A supplier recall arrives for the USB-C Charger. Femi and Kwame need to know every delivered charger unit that has not already been returned.
- **Task:** Return order item id, order id, customer email, quantity and unit price for delivered USB-C Charger order items with no existing return, ordered by order item id.
- **Kind:** `query`
- **New concept(s):** Complex anti-join/NOT EXISTS across several tables
- **Reuses:** JOINs, NOT EXISTS
- **Tables:** order_items, orders, products, customers, returns
- **Depends on state from:** Seed guarantees several historical charger purchases
- **Enables later:** L76–77
- **Validation notes:** Ordered and non-empty.

#### Level 76 — Pause the recalled product

- **Difficulty within chapter:** 4/5
- **Story:** The product must disappear from active sale immediately while the returns process runs.
- **Task:** Set `USB-C Charger` to inactive (`is_active = 0`) and change nothing else.
- **Kind:** `mutation`
- **New concept(s):** Targeted UPDATE callback
- **Reuses:** UPDATE, natural key
- **Tables:** products
- **Depends on state from:** L75 recall story
- **Canonical state change:** UPDATE exactly one product active flag to 0.
- **Enables later:** L78/L98 product-health context.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 77 — Create the recall returns

- **Difficulty within chapter:** 5/5
- **Story:** Rather than entering each affected return by hand, the learner creates all recall rows from the affected order items in one set-based statement.
- **Task:** Insert one full-quantity return for every delivered USB-C Charger order item that has no existing return: return date `2026-03-13`, reason `product_recall`, refund = quantity × unit_price rounded to 2 decimals.
- **Kind:** `mutation`
- **New concept(s):** Bulk INSERT ... SELECT with anti-join
- **Reuses:** INSERT SELECT, NOT EXISTS, joins, arithmetic
- **Tables:** returns, order_items, orders, products
- **Depends on state from:** L75 defines scope; L76 product paused
- **Canonical state change:** INSERT exactly the canonical recall-return set; no duplicates for already-returned items.
- **Enables later:** L78, L80, L98–100.
- **Validation notes:** Outcome validation; unordered unless stated otherwise.

#### Level 78 — Recall impact

- **Difficulty within chapter:** 4/5
- **Story:** Kwame needs the operational impact now that the returns have been created.
- **Task:** Return country, affected customer count, returned unit count and recall refund total for `product_recall` returns, ordered by refund total descending then country.
- **Kind:** `query`
- **New concept(s):** Post-mutation impact analysis
- **Reuses:** JOIN, GROUP BY, COUNT DISTINCT, SUM
- **Tables:** returns, order_items, orders, customers
- **Depends on state from:** L77 created recall returns
- **Enables later:** —
- **Validation notes:** Ordered.

#### Level 79 — Finance exception pack

- **Difficulty within chapter:** 5/5
- **Story:** Femi wants one list of outstanding financial exceptions after the refund corrections: delivered orders with no payment and delivered orders whose summed payments differ from gross order value.
- **Task:** Return order id, order total, amount paid, difference and an exception label (`No payment`, `Underpaid`, `Overpaid`). Build the logic in stages and order by absolute difference descending then order id.
- **Kind:** `query`
- **New concept(s):** Independent multi-stage problem
- **Reuses:** Multiple CTEs, CASE, COALESCE, aggregates
- **Tables:** orders, order_items, payments
- **Depends on state from:** L72 refunds fixed but payments remain intentionally imperfect
- **Enables later:** —
- **Validation notes:** Ordered; task does not prescribe exact CTE count.

#### Level 80 — Finance reconciliation checkpoint

- **Difficulty within chapter:** 5/5
- **Story:** The audit closes with a country-level reconciliation that must agree across sales, refunds and payments.
- **Task:** For delivered 2025 orders, return country, gross_sales, refunds, net_revenue, payments_received and payment_gap (`payments_received - gross_sales`), each rounded to 2 decimals. Sort by absolute payment gap descending then country.
- **Kind:** `query`
- **New concept(s):** Chapter-4 consolidation
- **Reuses:** Chained CTEs, JOINs, GROUP BY, returns, payments, COALESCE
- **Tables:** customers, orders, order_items, returns, payments
- **Depends on state from:** L72 corrected refunds; L77 recall is 2026 so should not contaminate 2025 scope
- **Enables later:** —
- **Validation notes:** Ordered. Checkpoint should reward decomposition rather than one giant query.

### Chapter 5: Advanced Analytics — Board week (23 Mar–3 Apr 2026)

#### Level 81 — Windows without collapsing rows

- **Difficulty within chapter:** 1/5
- **Story:** Margaret's board-prep work starts with a conceptual shift: keep each order visible while also showing a metric calculated across all orders.
- **Task:** Using an order-total CTE for delivered 2025 orders, return order id, order total and the overall average order total on every row, rounded to 2 decimals. Order by order id.
- **Kind:** `query`
- **New concept(s):** Window aggregate with OVER()
- **Reuses:** CTE, aggregates
- **Tables:** orders, order_items
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered. First window lesson explicitly names the construct.

#### Level 82 — Number the timeline

- **Difficulty within chapter:** 1/5
- **Story:** The CEO wants a stable sequence number beside each delivered 2025 order.
- **Task:** Return order id, order date and a row number ordered by order date then order id.
- **Kind:** `query`
- **New concept(s):** ROW_NUMBER
- **Reuses:** ORDER BY, window OVER
- **Tables:** orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by the same deterministic keys used in ROW_NUMBER.

#### Level 83 — Sequence each customer's orders

- **Difficulty within chapter:** 2/5
- **Story:** A global row number is less useful for customer behaviour. The learner resets the sequence independently for each customer.
- **Task:** For non-cancelled 2025 orders, return customer id, order id, order date and that customer's order sequence number.
- **Kind:** `query`
- **New concept(s):** PARTITION BY
- **Reuses:** ROW_NUMBER, ORDER BY
- **Tables:** orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by customer id, order sequence.

#### Level 84 — Rank products within category

- **Difficulty within chapter:** 2/5
- **Story:** Lena wants to compare current product prices inside each department and understand what ties do to rankings.
- **Task:** Return category, product, price, `RANK()` and `DENSE_RANK()` by price descending within each category. Order by category, rank, product.
- **Kind:** `query`
- **New concept(s):** RANK vs DENSE_RANK
- **Reuses:** PARTITION BY
- **Tables:** products, categories
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered; challenge intentionally shows both ranking functions.

#### Level 85 — Top three sellers in every category

- **Difficulty within chapter:** 2/5
- **Story:** The board pack needs the strongest products per department, not just one global top list.
- **Task:** For delivered 2025 sales, calculate product revenue and return the top 3 products by revenue inside each category, including category, product, revenue and rank. Use product name as the deterministic tie-breaker.
- **Kind:** `query`
- **New concept(s):** Filter a window result via outer query/CTE
- **Reuses:** CTE, ROW_NUMBER/RANK, JOIN, SUM
- **Tables:** categories, products, order_items, orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by category, rank, product. No QUALIFY in SQLite.

#### Level 86 — Time since the previous order

- **Difficulty within chapter:** 2/5
- **Story:** Isabel wants to understand purchase cadence. The learner compares each order with the previous one for the same customer.
- **Task:** For customers with at least two non-cancelled orders in 2025, return customer id, order id, order date, previous order date and days since previous order.
- **Kind:** `query`
- **New concept(s):** LAG
- **Reuses:** PARTITION BY, dates
- **Tables:** orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by customer id, order date, order id; first order rows may be excluded explicitly in outer query.

#### Level 87 — What comes next?

- **Difficulty within chapter:** 2/5
- **Story:** Support planning also cares how long it takes until a customer orders again.
- **Task:** Return customer id, order id, order date, next order date and days until next order for non-cancelled 2025 orders that have a later order.
- **Kind:** `query`
- **New concept(s):** LEAD
- **Reuses:** PARTITION BY, date arithmetic
- **Tables:** orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by customer id, order date, order id.

#### Level 88 — Running revenue

- **Difficulty within chapter:** 3/5
- **Story:** Femi wants a cumulative view of 2025 trading rather than isolated monthly totals.
- **Task:** Build monthly delivered gross revenue for 2025, then return month, monthly revenue and running revenue through that month, rounded to 2 decimals.
- **Kind:** `query`
- **New concept(s):** Running window aggregate / ROWS frame
- **Reuses:** CTE, date grouping, SUM OVER
- **Tables:** orders, order_items
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by month; use an explicit deterministic window frame.

#### Level 89 — Three-month moving average

- **Difficulty within chapter:** 3/5
- **Story:** Monthly revenue is noisy, so Margaret asks for a smoother trend.
- **Task:** Using the monthly revenue series, return month, monthly revenue and the trailing 3-month average including the current month, rounded to 2 decimals.
- **Kind:** `query`
- **New concept(s):** Window frame `ROWS BETWEEN`
- **Reuses:** CTE, AVG OVER, monthly grouping
- **Tables:** orders, order_items
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by month; early months average the rows available.

#### Level 90 — Share of category revenue

- **Difficulty within chapter:** 3/5
- **Story:** Lena wants to know whether each category relies on one dominant product.
- **Task:** For delivered 2025 sales, return category, product, product revenue, category revenue and product share of category revenue as a percentage rounded to 1 decimal.
- **Kind:** `query`
- **New concept(s):** Partitioned window total
- **Reuses:** JOIN, GROUP BY, SUM OVER(PARTITION BY)
- **Tables:** categories, products, order_items, orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by category then share descending then product.

#### Level 91 — Customer value quartiles

- **Difficulty within chapter:** 3/5
- **Story:** Marketing cannot hand-review every customer, so Isabel wants equal-sized spend bands.
- **Task:** Calculate each customer's delivered 2025 net spend and assign `NTILE(4)` over spend descending. Return email, net spend and quartile, ordered by quartile then spend descending then email.
- **Kind:** `query`
- **New concept(s):** NTILE
- **Reuses:** CTEs, net revenue, windows
- **Tables:** customers, orders, order_items, returns
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered; explain that quartile 1 is the highest-spend group for this ordering.

#### Level 92 — Spend percentiles

- **Difficulty within chapter:** 3/5
- **Story:** Quartiles are useful but coarse. The next view shows where each customer sits across the full spend distribution.
- **Task:** Return customer email, delivered-2025 net spend and `PERCENT_RANK()` by spend ascending, rounded to 3 decimals. Show only customers at or above the 90th percentile.
- **Kind:** `query`
- **New concept(s):** PERCENT_RANK / filter window output
- **Reuses:** CTE, window ranking
- **Tables:** customers, orders, order_items, returns
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Filter in an outer query/CTE; ordered by percentile descending then email.

#### Level 93 — First and latest purchase

- **Difficulty within chapter:** 4/5
- **Story:** The board pack needs each customer's purchase range on every order row. This level exposes the frame subtlety of `LAST_VALUE`.
- **Task:** For non-cancelled 2025 orders, return customer id, order id, order date, first 2025 order date and final 2025 order date for that customer.
- **Kind:** `query`
- **New concept(s):** FIRST_VALUE / LAST_VALUE with full frame
- **Reuses:** PARTITION BY, window frames
- **Tables:** orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by customer id, order date, order id. Hints explicitly address LAST_VALUE's default frame.

#### Level 94 — Cohort speed to first purchase

- **Difficulty within chapter:** 4/5
- **Story:** Isabel asks whether newer sign-up cohorts convert faster. The learner must reduce customer/order history into a cohort measure rather than rank raw rows.
- **Task:** For customers who signed up in 2025 and later ordered, return signup month, customer count, average days from signup to first order (1 decimal), ordered by signup month.
- **Kind:** `query`
- **New concept(s):** Cohort construction
- **Reuses:** CTEs, MIN/date arithmetic, GROUP BY
- **Tables:** customers, orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by signup month; exact approach open.

#### Level 95 — Month-on-month growth

- **Difficulty within chapter:** 4/5
- **Story:** Femi wants growth rather than just the revenue curve.
- **Task:** For each month of 2025, return month, delivered net revenue attributed to that order month after all returns known by the current story date, previous month's net revenue and month-on-month percentage change rounded to 1 decimal. January's change should be NULL.
- **Kind:** `query`
- **New concept(s):** LAG over an aggregated series
- **Reuses:** CTEs, net revenue, LAG, NULL handling
- **Tables:** orders, order_items, returns
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Ordered by month; explicitly guard previous-month zero if seed ever changes.

#### Level 96 — Referral leaderboard

- **Difficulty within chapter:** 4/5
- **Story:** The referral programme finally reaches the board pack. Grace's referral of Linnea should be part of the same analysis as the older seeded referral network.
- **Task:** For each referrer with at least one referred customer, return referrer email, referred-customer count, referred customers' delivered net revenue, and rank by that revenue descending. Order by rank then email.
- **Kind:** `query`
- **New concept(s):** Window ranking over self-join aggregates
- **Reuses:** Self join, CTEs, net revenue, RANK
- **Tables:** customers, orders, order_items, returns
- **Depends on state from:** L38 referral; L58–59 Linnea activity
- **Enables later:** —
- **Validation notes:** Ordered. Pending orders contribute no delivered revenue unless later story state changes.

#### Level 97 — Did late delivery hurt retention?

- **Difficulty within chapter:** 5/5
- **Story:** Margaret asks a causal-looking question but the learner must answer only what the data supports: whether customers with a late 2025 delivery were less likely to order again within 60 days.
- **Task:** Split customers into `Late delivery` vs `No late delivery` based on delivered 2025 orders. For each group, return customer count, customers with another non-cancelled order within 60 days after a delivered order, and repeat-within-60-days rate rounded to 1 decimal.
- **Kind:** `query`
- **New concept(s):** Independent multi-stage behavioural analysis
- **Reuses:** CTEs, EXISTS/LEAD-style reasoning, dates, conditional aggregation
- **Tables:** customers, orders
- **Depends on state from:** —
- **Enables later:** —
- **Validation notes:** Two deterministic rows. Task wording explicitly avoids claiming causation.

#### Level 98 — Product health leaderboard

- **Difficulty within chapter:** 5/5
- **Story:** Lena wants one view that balances sales, customer sentiment and returns. The recently launched Smart Kettle and the recalled USB-C Charger are useful edge cases rather than separate stories.
- **Task:** For every active-or-historically-sold product, return category, product, delivered net revenue, returned-unit rate, average review rating, current stock and a health rank within category using the explicit scoring/ranking rules supplied in the final task. Sort by category then health rank.
- **Kind:** `query`
- **New concept(s):** Multi-source product scoring + partition ranking
- **Reuses:** CTEs, joins, returns, reviews, conditional aggregation, window rank
- **Tables:** categories, products, orders, order_items, returns, product_reviews
- **Depends on state from:** L55 review; L56 Smart Kettle; L76–77 recall
- **Enables later:** —
- **Validation notes:** Scoring formula must be explicit and deterministic; no hidden subjective weighting.

#### Level 99 — Country executive scorecard

- **Difficulty within chapter:** 5/5
- **Story:** Margaret wants one page of comparable market metrics before deciding where to focus. This is the rehearsal for the final level.
- **Task:** For each country with at least 5 ordering customers in 2025, return ordering_customers, delivered_orders, net_revenue, average_order_value, repeat_customer_rate, late_delivery_rate and return_rate, with required rounding. Treat returns recorded by the current story date against items sold on 2025 delivered orders as part of the retrospective return/net-revenue metrics, so the Chapter 4 recall is visible. Order by net revenue descending then country.
- **Kind:** `query`
- **New concept(s):** Executive multi-metric scorecard
- **Reuses:** Multiple CTEs, joins, conditional aggregation, dates, returns
- **Tables:** customers, orders, order_items, returns
- **Depends on state from:** All data clean-ups and finance corrections; Linnea adds Sweden only if eligibility threshold is met
- **Enables later:** —
- **Validation notes:** Ordered; all metric definitions are written explicitly in the challenge.

#### Level 100 — Board priority ranking

- **Difficulty within chapter:** 5/5
- **Story:** The CEO's final question is not 'use a window function'. It is: given Brightcart's 2025 performance, which eligible markets should receive the first retention-and-growth attention, under an agreed scoring rule?
- **Task:** Starting from the country metrics, calculate five component ranks for eligible countries: net revenue (higher better), H2-vs-H1 net-revenue growth (higher better), repeat-customer rate (higher better), late-delivery rate (lower better), and return rate (lower better). Compute `priority_score = 0.25*revenue_rank + 0.25*growth_rank + 0.20*repeat_rank + 0.15*late_rank + 0.15*return_rank` (lower is better). Return the top 3 countries with the five metrics/ranks and priority score, ordered by score then country.
- **Kind:** `query`
- **New concept(s):** Final synthesis: staged metrics + multiple window ranks
- **Reuses:** CTEs, joins, conditional aggregation, dates, returns, LAG-style period comparison, DENSE_RANK/RANK
- **Tables:** customers, orders, order_items, returns, payments as optional cross-check
- **Depends on state from:** Requires the canonical state after all prior mutations and corrected refunds
- **Enables later:** —
- **Validation notes:** Exactly 3 rows if seed eligibility rules are met. All formulas/rounding/tie-breakers must be explicit. The technique is not prescribed; the output is.

---

## 8. Mutation dependency ledger

The design contains **21 mutation levels out of 100**. That is deliberate: roughly one persistent story event in five, with the final analytics chapter primarily reading the history the learner created.

| Level | Event/state change | Important later dependencies |
|---:|---|---|
| 14 | INSERT exactly one Grace Hopper row; phone NULL; deterministic date 2026-01-12. | L15–16, L28–35, L55, L68–69, L74, L96 and later customer metrics. |
| 16 | UPDATE exactly one customer; only `phone` changes to 07700 900123. | L20 contact-gap checkpoint and later complete customer record. |
| 19 | DELETE exactly the QA customer and nothing else. | All later customer counts use the cleaned population. |
| 29 | INSERT exactly one pending order for Grace on 2026-01-20; lifecycle dates NULL. | L30–35, L55, L74. |
| 32 | INSERT exactly two order_items with quantity 1 and the correct price-at-sale for each product. | L33–34, L55, L74 and all later revenue. |
| 34 | INSERT exactly one payment for Grace's order with the correct amount/method/date. | Finance reconciliation in L63/L79/L80. |
| 35 | UPDATE exactly Grace's order: status shipped, shipped_date 2026-01-22, delivered_date remains NULL. | L41 delivery completion and later lifecycle analysis. |
| 37 | UPDATE exactly one product stock_quantity to 40. | Later stock/product-health reports. |
| 38 | INSERT exactly one Linnea row with referral pointing to Grace. | L58–59, L68–69, L96 and Sweden appearing in later country analysis. |
| 39 | UPDATE exactly the Toys & Games products; price = ROUND(old_price * 0.90, 2). | Later distinction between current price and historical `unit_price`. |
| 41 | UPDATE exactly Grace's order status/delivered_date; shipped_date unchanged. | L47+ delivery analysis and L55/L74 story consistency. |
| 46 | UPDATE exactly the seeded dirty-email rows; only email changes. | Stable email matching in all later work. |
| 55 | INSERT exactly one review with the specified rating/date/text and correct FKs. | L67 verified-review audit and L98 product health. |
| 56 | INSERT exactly one active product with specified price/stock/category. | L57–59 and L98 callback. |
| 58 | INSERT exactly one pending Linnea order dated 2026-02-20. | L59 and later referral/customer history. |
| 59 | INSERT exactly one Kettle order_item on Linnea's order. | L69/L96 referral value and L98 product-health callback. |
| 72 | UPDATE exactly the anomalous return rows; only refund_amount changes. | L80, L98–100 clean net-revenue metrics. |
| 73 | DELETE exactly the seeded `BOT:` review rows and no genuine reviews. | Later rating/product-health analysis uses the cleaned review population. |
| 74 | INSERT exactly one return for Grace's French Press with specified date/reason/full refund. | L80 and later customer/product return metrics. |
| 76 | UPDATE exactly one product active flag to 0. | L78/L98 product-health context. |
| 77 | INSERT exactly the canonical recall-return set; no duplicates for already-returned items. | L78, L80, L98–100. |


---

## 9. Concept progression map

The table below is a curriculum contract, not merely a topic list. `I` means introduced, `P` practised, `C` combined, and `A` applied with limited technique guidance.

| Concept | I | Early practice | Later combination / independent use |
|---|---:|---|---|
| SELECT / columns / FROM | 1–2 | 3–13 | Everywhere |
| WHERE / comparisons | 3–4 | 5–13 | Everywhere |
| AND / OR | 5–6 | 20 | 40, 53+, checkpoints |
| ORDER BY / tie-breakers | 7 | 8–13 | All ordered reporting |
| LIMIT | 9 | 20 | Top-N/window work later uses different techniques |
| NULL / IS NULL | 10 | 20 | LEFT JOINs, COALESCE, lifecycle dates |
| LIKE | 11 | later text/data-quality tasks | Independent filters where useful |
| IN / BETWEEN | 12–13 | 31, 39 | Subquery form at 50 |
| INSERT | 14 | 29, 32, 34, 38 | 55–59, 74, 77 |
| UPDATE | 16 | 35, 37, 39, 41, 46 | 72, 76 |
| DELETE | 19 | 73 | Revisited later as a safe set-based moderation cleanup rather than a contrived destructive exercise |
| DISTINCT | 17 | 50, 69, 78 | Executive metrics |
| Basic aggregates | 18 | 21–23 | Every analytical chapter |
| GROUP BY | 21 | 22–23, 27 | 40, 54, 60, 69+, analytics |
| HAVING | 23 | 40, 60 | Later eligibility thresholds |
| INNER JOIN | 24 | 25, 27 | Every later chapter |
| LEFT JOIN / anti-join | 26 | 63–64 | Finance/quality work |
| Multi-table joins | 27 | 40 | 50+, advanced reports |
| Multi-row INSERT | 32 | — | Bulk INSERT SELECT at 77 is a more advanced recurrence |
| INSERT ... SELECT | 38 | 55–59 | 77 |
| CASE | 42 | 48, 54 | 65, 79, executive metrics |
| COALESCE | 43 | 63–64 | Finance/analytics |
| String functions | 44–46 | data clean-up | Used where needed rather than artificially repeated |
| Date functions | 47 | 48, 54, 60 | 86–97 |
| Scalar subquery | 49 | 56, 58 | 66, advanced DML alternatives |
| IN subquery | 50 | later lookup variants | Accepted alternative where natural |
| EXISTS / NOT EXISTS | 51–52 | 53, 67 | 75, 77, retention work |
| UNION / set ops | 53 | EXCEPT at 70 | Available independently later |
| Conditional aggregation | 54 | 60 | 80, 97–100 |
| CTE | 61 | 62 | 63–80, then standard tool in Ch5 |
| Multiple CTEs | 63 | 64–65 | 79–100 |
| Correlated subquery | 66 | 67 | Advanced DML/analysis alternatives |
| Self join | 68 | 69 | 96 |
| Window OVER() | 81 | 82–85 | 86–100 |
| ROW_NUMBER | 82 | 83, 85 | Cohorts/top-N |
| PARTITION BY | 83 | 84–90 | 91–98 |
| RANK / DENSE_RANK | 84 | 85 | 96, 98, 100 |
| LAG / LEAD | 86–87 | 95 | 97 and independent time-series reasoning |
| Window frames | 88–89 | 93 | Advanced analytics |
| NTILE / percentiles | 91–92 | — | Segmentation/leadership interpretation |
| FIRST_VALUE / LAST_VALUE | 93 | — | Introduces frame nuance; not overused artificially |
| Cohort analysis | 94 | 97 | Executive metrics/retention reasoning |

### Important pacing notes

- `JOIN` does not appear until learners have already seen foreign-key ids in aggregate outputs.
- `GROUP BY` is introduced before joins so later grouped joins combine two known skills.
- Subqueries arrive only after the learner is comfortable following relationships with joins.
- CTEs are framed as a readability/decomposition tool for subqueries and aggregates the learner already understands.
- Windows begin with `OVER()` and row numbering before partitions, ranking, offsets and frames.
- The final five levels do not name the technique in the business prompt; they define the metric/output and let the learner choose the structure.

---

## 10. Chapter pacing audit

### Chapter 1

**What changes:** learner goes from reading a six-row reference table to safely inserting/updating/deleting one customer row.

**Why it should feel progressive:** new clauses are isolated first; L8 is the first deliberate combination; L14–19 alternate reads and writes rather than throwing three mutations together; L20 combines familiar clauses without introducing syntax.

**End capability:** read a single table confidently, filter/search/sort, handle NULLs, summarise a table and make tightly scoped basic DML changes.

### Chapter 2

**What changes:** learner stops treating tables as islands. Grace's order is intentionally built as header → lines → total → payment → shipment, so foreign keys become part of a story rather than a diagram.

**Why it should feel progressive:** aggregation comes first, then joins, then multi-table aggregation, then those relationships are used in mutations. L40 is the first real reporting task.

**End capability:** understand one-to-many relationships, write common joins, group/have, create related records and reason about historical price-at-sale vs current catalogue price.

### Chapter 3

**What changes:** the work moves from operations to investigation. The same data is transformed, compared with subqueries and grouped conditionally; the story includes data quality, service recovery and product launch work.

**Why it should feel progressive:** CASE/COALESCE/string/date functions are introduced before nested query forms. EXISTS/NOT EXISTS revisit earlier anti-join concepts, and UNION combines whole audiences rather than being a syntax stunt.

**End capability:** solve intermediate analytical questions, clean deterministic data, use subqueries/set logic, and create rows by selecting keys from related tables.

### Chapter 4

**What changes:** queries become multi-stage. Finance and recall work make correctness consequential: duplicate payments, refunds and return rows must be aggregated or anti-joined correctly.

**Why it should feel progressive:** a single CTE becomes two CTEs, then staged analysis, then correlation/self-joins. Advanced mutations are preceded by a query that proves the target set.

**End capability:** decompose complex SQL, reconcile multiple business facts, use correlated logic/self-joins, and perform set-based mutations safely.

### Chapter 5

**What changes:** no new operational story machinery is needed; the learner finally exploits the history they have helped create. The chapter is intentionally query-heavy.

**Why it should feel progressive:** windows advance in a strict sequence: OVER → ROW_NUMBER → PARTITION → ranking → filtered top-N → LAG/LEAD → frames → segmentation → multi-stage scorecards.

**End capability:** build leadership-grade trend, cohort, ranking and multi-metric analyses without being told which SQL construct to use.

---

## 11. Story and dependency audit

The course should preserve these long-running cause→consequence chains:

1. **Grace:** L14 signup → L16 phone → L29/L32 order → L34 payment → L35/L41 delivery → L55 review → L74 return → L67/L80/L98+ analysis.
2. **Linnea/referrals:** L38 referral signup → L58/L59 order → L68/L69 referral analysis → L96 referral leaderboard → country metrics if Sweden reaches eligibility.
3. **Price history:** L39 current-price clearance → L62/L64/L80 revenue still uses historical `unit_price`, teaching why mutable product price is not historical revenue.
4. **Data quality:** L45 audit → L46 cleanup → later email matching is dependable.
5. **Refunds:** seeded bad refunds → L71 discovery → L72 correction → L80/L95/L99/L100 use corrected net revenue.
6. **Recall:** L75 scope → L76 product pause → L77 returns → L78 immediate impact → L98 product health → L99/L100 market metrics.

### Fragile dependencies deliberately avoided

- No later level depends on Grace's or Linnea's generated numeric customer id.
- No later level depends on an auto-generated review/return id except when the learner just retrieved it in the immediately preceding task.
- No task depends on `CURRENT_TIMESTAMP` or the machine's real date.
- Bulk mutations use named products, explicit story dates and predicates that exclude future story-created rows unless inclusion is intentional.
- Final analytics are scoped to 2025 where appropriate so 2026 story mutations do not accidentally rewrite historical KPI definitions.

---

## 12. Current prototype migration

The three existing YAML challenges should not be discarded; they should be repositioned when implementation begins:

| Existing challenge | Final destination | Change |
|---|---|---|
| `01_customer_contact_list.yaml` | **Level 2** | Add Brightcart/Nadia story framing; behaviour unchanged |
| `02_premium_products.yaml` | **Level 8** | Keep core task, add deterministic name tie-breaker and story framing |
| `03_add_new_customer.yaml` | **Level 14** | Keep Grace, change signup date to `2026-01-12`, add story metadata/refined instructions |

Before these files are renumbered, implement the schema/seed prerequisites and bump `SEED_VERSION` so the canonical IDs/counts are final.

---

## 13. Implementation sequence after curriculum approval

Do **not** ask an agent to implement all 100 challenge files at once.

### Phase A — one-time platform prerequisites

1. Implement S1–S5 schema/seed changes and rebuild the template.
2. Add completed-query historical Review mode (D1).
3. Add optional `match_column_names` (D2).
4. Add narrow parser-based `required_features` support for concept-introduction levels (D5).
5. If desired, add `story`/`level`/`chapter`/`concepts` content metadata (D3).
6. Expand content tests to enforce deterministic ordered tie-breakers and replay every query at its canonical point in the chain.

### Phase B — implement by ten-level blocks

Recommended batches:

- 1–10
- 11–20
- 21–30
- 31–40
- 41–50
- 51–60
- 61–70
- 71–80
- 81–90
- 91–100

For each block:

1. create challenge content;
2. add/adjust accepted alternatives where useful;
3. run every existing backend test;
4. run the canonical replay chain through the new final level;
5. manually complete at least the first, hardest and mutation challenge in the block;
6. audit the block against story continuity and concept recurrence before moving on.

### Phase C — whole-course audit

After Level 100 exists, run a deliberate editorial pass for:

- duplicate-feeling exercises;
- difficulty spikes;
- concepts introduced but not revisited;
- overly prescriptive later tasks;
- mutations with no later consequence;
- story events with no database consequence;
- query outputs that can exceed 500 rows;
- ordered outputs without unique tie-breakers;
- chapter checkpoints that are easier than the levels immediately before them;
- replay/review behaviour from early completed levels after the database has reached Level 100.

---

## 14. Content quality gates

A level is not ready to ship unless all applicable checks pass:

- [ ] Story is 1–3 sentences and gives a real business reason for the SQL.
- [ ] Task states exact output/change without prescribing unnecessary syntax.
- [ ] New concept load is appropriate for its position.
- [ ] At least one earlier concept is meaningfully reused after the opening levels.
- [ ] Query reference result is non-empty at its canonical point in the chain.
- [ ] Query returns ≤500 rows.
- [ ] Ordered query has deterministic tie-breakers.
- [ ] Mutation changes at least one row and ≤1,000 rows.
- [ ] Mutation uses explicit deterministic values.
- [ ] Mutation changes only the intended visible table(s).
- [ ] Any story-created row is referenced later by a natural key or a freshly retrieved id.
- [ ] Review-mode reconstruction produces the same canonical pre-challenge state.
- [ ] Reference SQL passes.
- [ ] At least one materially different correct SQL solution passes for lessons where equivalence is important.
- [ ] If a construct is explicitly the lesson, any `required_features` rule checks only broad feature presence and does not overconstrain equivalent SQL.
- [ ] Failure feedback does not reveal the expected answer.
- [ ] The challenge contributes either new learning, meaningful practice, a story consequence, or consolidation — preferably more than one.

---

## 15. Final design assessment

This curriculum deliberately avoids two common failure modes:

1. **100 unrelated exercises with a shared theme.** Brightcart has actual continuity: Grace, Linnea, price changes, payments, reviews, returns, refunds and a recall alter later work.
2. **A syntax checklist disguised as progression.** Core ideas recur under different business pressures, and later chapters increasingly state *what the business needs* instead of *which clause to type*.

The existing engine's persistent per-learner database is therefore not a gimmick: it becomes part of the pedagogy. Learners can see that SQL does not just answer questions about a static toy dataset; correct statements create the data context that later questions depend on.
