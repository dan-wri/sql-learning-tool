# SQL Curriculum — Brightcart

Status: **architecture only.** No individual levels are designed yet.
Future sessions add the detailed level designs to the end of this file (see §14 and the Level designs section).

---

## 1. Course vision

The course has **100 core levels**. They all run against **one persistent database belonging to one fictional company**. Each learner has their own copy of that database.

Three things grow together over the course:

| Dimension | Level 1 | Level 100 |
|---|---|---|
| **SQL ability** | `SELECT * FROM` one table | Analysis in several stages, combining CTEs, window functions and conditional aggregation |
| **Responsibility** | New support assistant looking up customer details | Analyst whose findings go to the board |
| **Database and story** | The company as it is on day one | A database the learner helped build: customers they signed up, orders they placed, prices they changed, returns they processed |

The goal is that the learner feels they **joined a company**, not that they worked through a list of exercises. Each level answers two questions:

1. **Learning purpose:** what SQL skill does this practise?
2. **Story purpose:** why does Brightcart need this today?

---

## 2. Fictional company

**Brightcart Ltd** is a small online retailer based in Manchester. It was founded in 2023 and sells everyday goods in six categories: Electronics, Books, Home & Kitchen, Clothing, Sports & Outdoors, and Toys & Games. It ships to the UK, Ireland and parts of the EU (France, Germany, the Netherlands, Spain).

The current seed data supports this setting directly:

- 60 customers in 14 cities across 6 countries, signed up between Jan 2023 and Dec 2024
- 30 products, 6 categories
- 150 orders from Mar 2023 to **30 Jun 2025**
- 316 order lines and 127 payments

**Story clock.** The story starts on **Tuesday 1 July 2025**, the morning after the last order in the seed data. Story time only moves forward, and **every date used in a task is written out explicitly** (see §12).

| Chapter | Story time | Season / business context |
|---|---|---|
| 1 | 1–11 Jul 2025 | Learner's first two weeks |
| 2 | 14 Jul – 29 Aug 2025 | Peak summer, the Summer Sale |
| 3 | Sep – Oct 2025 | Autumn range, data-quality clean-up, delivery incident |
| 4 | Nov 2025 | Black Friday preparation, finance audit, review of the referral programme |
| 5 | Dec 2025 – Jan 2026 | Year-end analysis and the board review |

---

## 3. Learner role and career progression

| Chapter | Learner's role | Reports to / works with | Kind of work |
|---|---|---|---|
| 1 | **Customer Support Data Assistant** (new starter) | Nadia Brooks, Support Lead | Looking up customers, products and orders. Small, closely supervised edits. |
| 2 | **Operations Assistant** | Kwame Mensah (Fulfilment), Lena Fischer (Merchandising) | Placing and fulfilling orders, stock, pricing changes, team reports that join tables |
| 3 | **Operations & Marketing Analyst** | Isabel Torres (Marketing), Kwame | Investigations, data-quality clean-ups, campaign lists, the delivery incident |
| 4 | **Business Analyst** | Femi Adeyemi (Finance Director), Isabel | Audits, reconciling refunds, Black Friday planning, reviewing the referral programme. Analysis built from several stages. |
| 5 | **Senior Analyst** | Margaret Lowe (CEO), the board | Trends, rankings, cohorts, the year-end board pack. Ambiguous questions; the learner chooses the method. |

The way tasks are worded changes along with the role:

- **Ch 1–2:** the task says exactly what to retrieve or change. It usually names the columns and often names the clause.
- **Ch 3:** the task describes the outcome needed. It may hint at the technique.
- **Ch 4–5:** the task describes a business question. The learner works out the structure. The required output (columns, order, rounding) is always stated exactly, so outcome validation still works.

Staff names were chosen not to clash with customer first names in the seed data. Staff are **not** stored in the database; they exist only in the story text.

---

## 4. Five-chapter overview

### Chapter 1 — Foundations (Levels 1–20)
**Story:** The learner's first fortnight on the support desk. They learn what Brightcart sells and who its customers are. They make their first careful edits: signing up Grace Hopper, correcting her details, and removing a leftover test account.
**SQL:** `SELECT`, specific columns, `WHERE`, comparisons, `AND`/`OR`, `IN`, `BETWEEN`, `LIKE`, `IS NULL`, `ORDER BY`, `LIMIT`, `DISTINCT`, aliases, `COUNT`/`SUM`/`AVG`/`MIN`/`MAX` (no grouping yet), first `INSERT`, `UPDATE` and `DELETE`.
**Shape:** one or two new ideas per level. Each concept is introduced, practised alone, then combined with one earlier concept.
**Checkpoint (L20):** a support-desk briefing that needs filtering, NULL handling, sorting and one aggregate together.

### Chapter 2 — Relational SQL (Levels 21–40)
**Story:** Grace places her first order, and the learner creates it. Summer peak arrives: a backlog of pending orders, a restock, the Summer Sale price cut, Linnea Berg joining through Grace's referral, and the first return.
**SQL:** `GROUP BY`, `HAVING`, `INNER JOIN`, `LEFT JOIN`, joining 3–4 tables, how foreign keys relate tables, filtering combined with joins, multi-row `INSERT`, `INSERT … SELECT`, `UPDATE`/`DELETE` with subqueries that look up a value (introduced lightly), orphan/anti-join patterns with `LEFT JOIN … IS NULL`.
**Shape:** the chapter starts with relationships *before* JOIN syntax. Learners look up a foreign key by hand across two queries, then learn the JOIN that does it in one. `GROUP BY` comes before joins, so that grouping over joined data later is a combination of two known ideas.
**Checkpoint (L40):** an end-of-summer report for operations that joins orders, items, products and customers, with grouping and `HAVING`.

### Chapter 3 — Intermediate SQL (Levels 41–60)
**Story:** Autumn. A new product launches, a seasonal product comes back, and marketing segments customers. A delivery-delay incident from the summer is investigated. A data-quality project cleans up inconsistent emails and cities and removes spam reviews.
**SQL:** `CASE`, `COALESCE`/`IFNULL`/`NULLIF`, string functions, date functions, more complex NULL handling, scalar and `IN` subqueries, `EXISTS`/`NOT EXISTS`, `UNION`/`UNION ALL`/`INTERSECT`/`EXCEPT`, conditional aggregation, `UPDATE` with expressions and subqueries.
**Shape:** tasks increasingly leave the approach open, e.g. "find customers who never…" could be solved with `NOT EXISTS`, `NOT IN` or `LEFT JOIN`.
**Checkpoint (L60):** the delivery-incident report for operations. It needs dates, `CASE` buckets, conditional aggregation and a subquery.

### Chapter 4 — Advanced Query Construction (Levels 61–80)
**Story:** November. Finance audits refunds and payments. Marketing reviews whether the referral programme worked. Black Friday pricing is planned and applied. A product recall creates returns in bulk.
**SQL:** CTEs, several chained CTEs, correlated subqueries, self joins (referrals), complex join conditions, analysis in several stages, advanced conditional aggregation, DML driven by CTEs or subqueries.
**Shape:** analysis in several steps where the learner breaks the problem down. CTEs are introduced as a way to organise the subqueries they already know, so it isn't a jump.
**Checkpoint (L80):** a reconciliation for the finance audit of payments against order totals, net of refunds, flagging exceptions.

### Chapter 5 — Advanced Analytics (Levels 81–100)
**Story:** Year end. The CEO's board pack needs trends, rankings, cohorts and an honest account of the year, including the incidents the learner handled earlier.
**SQL:** window functions, `PARTITION BY`, `ROW_NUMBER`/`RANK`/`DENSE_RANK`, `LAG`/`LEAD`, running totals, moving and cumulative windows, `NTILE`, ranking within groups, medians and percentiles calculated with window functions, CTEs combined with windows.
**Shape:** windows are introduced over the first ~8 levels, then used without being named. The last five levels are open business questions.
**Final level (L100):** a board question that needs the learner to choose and combine CTEs, joins, conditional aggregation, window functions and the database history they built over the course.

---

## 5. SQL concept progression

Key: **I** = introduced, **P** = practised, **C** = combined with other concepts, **A** = applied independently (task doesn't name the technique).

| Concept | Ch1 | Ch2 | Ch3 | Ch4 | Ch5 |
|---|---|---|---|---|---|
| SELECT / columns / `*` | I P | C | A | A | A |
| WHERE, comparisons, AND/OR | I P C | C | A | A | A |
| IN, BETWEEN, LIKE | I P | C | C (LIKE with string functions) | A | A |
| NULL / IS NULL | I P | C (LEFT JOIN NULLs) | C (COALESCE, NULLIF) | A | A |
| ORDER BY, LIMIT, tie-breaking | I P | C | A | A | C (windows) |
| DISTINCT | I P | C (COUNT DISTINCT) | A | A | A |
| Aliases (columns, tables) | I | P (table aliases in joins) | A | A | A |
| Aggregates without GROUP BY | I P | C | A | A | A |
| INSERT single row | I | P | A | A | — |
| INSERT multi-row / INSERT…SELECT | — | I P | C | A | A |
| UPDATE (literal) | I | P | C (expressions) | A | — |
| UPDATE with subquery / UPDATE…FROM | — | I (lookup only) | P | C (CTE-driven) | A |
| DELETE | I | P (with lookup) | C (subquery) | A | — |
| GROUP BY | — | I P | C | A | A |
| HAVING | — | I P | C | A | A |
| INNER JOIN | — | I P C | A | A | A |
| LEFT JOIN / anti-join | — | I P | C | A | A |
| Multi-table joins (3–4) | — | I P | C | A | A |
| CASE | — | — | I P C | A | A |
| COALESCE / IFNULL / NULLIF | — | — | I P | C | A |
| String functions | — | — | I P | C | A |
| Date functions | — | — | I P C | C | A |
| Scalar / IN subqueries | — | (lookup in DML) | I P | C | A |
| EXISTS / NOT EXISTS | — | — | I P | C (correlated) | A |
| Set operations | — | — | I P | C | A |
| Conditional aggregation | — | — | I P | C | A |
| CTEs (single, then several) | — | — | — | I P C | A |
| Correlated subqueries | — | — | (EXISTS) | I P | A |
| Self joins | — | — | — | I P | A |
| Window functions | — | — | — | — | I P C A |
| PARTITION BY, ranking | — | — | — | — | I P C A |
| LAG / LEAD | — | — | — | — | I P C |
| Running / moving totals, frames | — | — | — | — | I P C |

**Rule:** every concept marked **I** must reappear in at least **three** later levels, and at least one of those must be in a later chapter.

---

## 6. Story progression

### Chapter 1 — "First fortnight" (1–11 Jul)
- **Day one:** the learner explores Brightcart's catalogue and customers (categories, products, customer list).
- Nadia gives them support tickets: find a customer by email, check where an order is, list customers with no phone number on file.
- Merchandising points out products that are out of stock (Monitor, Denim Jacket, Camping Tent) or inactive (Webcam HD, Rain Jacket).
- **First INSERT:** Grace Hopper signs up by phone and the learner creates her record.
- **First UPDATE:** Grace calls back with a phone number.
- **First DELETE:** a leftover QA test account (seeded, never ordered) must be removed before the marketing export.
- **Checkpoint:** an end-of-fortnight support briefing.

### Chapter 2 — "Summer peak" (14 Jul – 29 Aug)
- **Grace's first order.** The learner creates the order, then its order lines (two levels, because each submission is one statement).
- **Pending backlog:** older pending orders are bulk-marked as shipped with an explicit shipped date.
- **Restock:** the 27-inch Monitor is restocked.
- **Linnea Berg joins.** She is Brightcart's first Swedish customer, referred by Grace. The learner records the referral by looking up Grace (`INSERT … SELECT`). This pays off in Ch4.
- **Summer Sale:** Toys & Games prices are cut by a stated percentage. From then on, order lines carry the old prices and the product table carries the new ones.
- Linnea places an order. One line is removed before dispatch (a DELETE with real meaning).
- **First return:** Grace returns an item from her first order.
- Kwame's team asks for reports joining orders, customers and products: best sellers, customers by country, orders with no payment.
- **Checkpoint:** an end-of-summer operations report.

### Chapter 3 — "Autumn clean-up" (Sep – Oct)
- **Autumn range:** the Rain Jacket is reactivated. A new product, the *Smart Kettle Pro*, launches and receives its first orders.
- **Data-quality project:** inconsistent email casing and whitespace, inconsistent city names, a duplicate-looking customer investigation (the seeded duplicate names), and spam reviews.
- **Delivery-delay incident:** customers complain that summer deliveries were slow. Using shipped and delivered dates, the learner measures delays, buckets them with CASE, and records the delayed deliveries.
- **Marketing segmentation:** customers grouped by recency (dates), spend (CASE) and activity (EXISTS). Lists are built with set operations.
- Grace writes a review. A follow-up question checks whether reviewers actually bought the product (EXISTS).
- **Checkpoint:** the delivery incident report.

### Chapter 4 — "November" (Black Friday and audit)
- **Finance audit:** payments against order totals, refunds against returns, and orders that were delivered but never paid. The answers need staged CTE logic.
- **Referral programme review:** who referred whom (self join), and whether referred customers spend more. Grace → Linnea is the first story example.
- **Black Friday:** the discount plan is calculated, then applied with a CTE-driven or correlated UPDATE. A loyal customer's repeat order is created by copying their previous order lines (`INSERT … SELECT`).
- **Product recall:** a batch of the Smart Kettle Pro is recalled, creating return records for every affected order line in one statement.
- **Checkpoint:** the finance reconciliation, a staged analysis with exceptions flagged.

### Chapter 5 — "Year end" (Dec 2025 – Jan 2026)
- Monthly revenue trends, month-over-month change (`LAG`), and running totals for the year.
- Ranking products within categories, and top customers per country.
- Cohort retention by signup month. Gaps between each customer's orders (`LAG`).
- Looking back: did the Summer Sale help? How did the delivery incident affect repeat purchases? How much revenue came through referrals?
- Few mutations. Possibly one year-end stock adjustment driven by an analysis query.
- **Level 100:** the CEO's board question (see §4, Chapter 5).

---

## 7. Major recurring characters, entities and events

### Staff (story text only)
| Name | Role | Chapters |
|---|---|---|
| Nadia Brooks | Support Lead, the learner's first manager | 1–2, cameo in 5 |
| Kwame Mensah | Fulfilment & Warehouse Manager | 2–4 |
| Lena Fischer | Merchandising Manager (prices, products) | 1–4 |
| Isabel Torres | Head of Marketing | 3–5 |
| Femi Adeyemi | Finance Director | 4–5 |
| Margaret Lowe | CEO | 5 (mentioned earlier) |

### Customers
| Customer | Origin | Story arc |
|---|---|---|
| **Grace Hopper** | Created by the learner (Ch1 INSERT) | Phone correction (Ch1) → first order (Ch2) → return (Ch2) → review (Ch3) → referrer of Linnea, analysed in Ch4 → appears in the cohort and top-customer analysis (Ch5) |
| **Linnea Berg** (Stockholm, Sweden) | Created by the learner (Ch2, referred by Grace) | First Swedish customer → order with a line removed (Ch2) → Smart Kettle Pro buyer (Ch3) → affected by the recall (Ch4) → the new market in the board pack (Ch5) |
| The three seeded "Grace"s (Davies, Wilson, Hall) | Seed | Ch1 lesson: filtering on first name alone is ambiguous, so filter on a unique column |
| Duplicate names (Arthur Khan ×2, Ava Green ×2, Jack Hall ×2) | Seed | Ch3 investigation: same name but different people, so names are not identifiers |
| Customer 40 (7 orders, the most of anyone) | Seed | Ch2 "most loyal customer" → Ch4 repeat-order copy → Ch5 top-customer ranking |
| The 9 customers who have never ordered | Seed | Ch2 anti-join → Ch3 re-engagement campaign list |
| QA test account | **Seed addition** (§9) | Deleted in Ch1 |

### Products
| Product | Story arc |
|---|---|
| 27-inch Monitor (out of stock) | Ch1 stock check → Ch2 restock → Ch5 ranked among top revenue products |
| Denim Jacket / Camping Tent (out of stock) | Ch1 stock checks; supporting data for stock questions in later chapters |
| Webcam HD (inactive) | Ch1 "why can't customers see this?" Ch2 lesson: products with order history are deactivated, not deleted (foreign keys) |
| Rain Jacket (inactive) | Ch3 reactivated for autumn → seasonal sales in Ch5 |
| Toys & Games range | Ch2 Summer Sale → Ch3 comparing price at sale against current price → Ch5 "did the sale work?" |
| **Smart Kettle Pro** (new) | Ch3 launch (INSERT) → first orders → reviews → Ch4 recall → Ch5 lifecycle analysis |

### Events (cause → consequence)
| Event | Introduced | Consequences later |
|---|---|---|
| Grace signs up | Ch1 | Every later Grace story beat; she appears in later aggregates |
| Test account removed | Ch1 | Customer counts in later reports exclude it |
| Pending backlog cleared | Ch2 | Shipped dates feed the Ch3 delay incident |
| Summer Sale | Ch2 | Ch3 price-at-sale analysis; Ch5 sale evaluation |
| Linnea referred by Grace | Ch2 | Ch4 self join; Ch5 revenue from referrals |
| First return | Ch2 | Ch4 refund reconciliation |
| Delivery-delay incident | Ch3 | Ch4 audit context; Ch5 effect on repeat purchases |
| Data-quality clean-up | Ch3 | Grouping in Ch4–5 works correctly only because cities and emails were normalised |
| Smart Kettle Pro launch → recall | Ch3 → Ch4 | Ch5 product lifecycle and returns rate |
| Black Friday pricing | Ch4 | Ch5 November spike in trend analysis |

---

## 8. Database evolution plan

These are approximate milestones; exact levels are set during level design. Target: **about 22–26 mutation levels out of 100**. More of them fall in the operational chapters (1–3) and only 1–2 in Chapter 5.

| ≈ Level | Mutation | Kind | Later levels that depend on it |
|---|---|---|---|
| 11 | Grace Hopper signs up | INSERT customers | 12–13 (find her), 14 (update), Ch2 order, referral, Ch4–5 analysis |
| 14 | Grace's phone number added | UPDATE customers (one row, found by email) | L20 checkpoint (no-phone list shrinks) |
| 17 | QA test account removed | DELETE customers (no orders, so no foreign-key conflict) | All later customer counts |
| 19 | Monitor restock *announced*; Ch1 only checks it | (query) | — (keeps Ch1 light on DML) |
| 22 | Grace's first order created (status `pending`, explicit date) | INSERT orders | 23, 24, 27, Ch2 reports |
| 23 | Lines added to Grace's order (unit price copied from the product) | multi-row INSERT order_items | Revenue reports, Ch2 return |
| 26 | Monitor restocked | UPDATE products (stock) | Stock reports, Ch5 |
| 28 | Linnea Berg joins, `referred_by` = Grace (looked up) | INSERT … SELECT customers | Ch2 order, Ch4 self join |
| 30 | Pending backlog shipped (rows chosen by date cutoff; explicit shipped date) | UPDATE orders (many rows) | Ch3 delay incident |
| 33 | Summer Sale: Toys & Games prices cut by a stated %, `ROUND(…, 2)` | UPDATE products (subquery on category) | Ch3 price comparison, Ch5 sale evaluation |
| 35–36 | Linnea's order and its lines | INSERT orders, INSERT order_items | 37, Ch3, Ch4 recall |
| 37 | A line removed from Linnea's order before dispatch | DELETE order_items (one row) | Order totals in later reports |
| 39 | Grace returns one item | INSERT returns | Ch4 refund reconciliation |
| 43 | Rain Jacket reactivated | UPDATE products | Ch5 seasonal analysis |
| 45 | Smart Kettle Pro launched | INSERT products | 47, reviews, Ch4 recall |
| 47 | First Smart Kettle Pro orders (added to existing pending orders, or new ones) | INSERT order_items | Ch4 recall, Ch5 lifecycle |
| 50 | Delayed summer orders: delivered dates recorded from the courier report | UPDATE orders (dates, explicit) | L60 checkpoint, Ch4–5 |
| 52 | Emails normalised (`LOWER`/`TRIM`) | UPDATE customers (only the rows that need it) | Ch3–5 matching on email |
| 54 | City names normalised | UPDATE customers | Correct grouping by city in Ch4–5 |
| 56 | Grace's review | INSERT product_reviews | Ch3 verified-purchase check (EXISTS) |
| 57 | Spam reviews removed (found by pattern or rule) | DELETE product_reviews (subquery) | Review averages from then on |
| 66 | Black Friday discount applied (prices calculated in a CTE) | UPDATE products | Ch5 November analysis |
| 70 | Repeat order for customer 40 (copy their previous order's lines) | INSERT … SELECT order_items (after INSERT orders at ~69) | Ch5 top customers |
| 74 | Refund amounts corrected per policy | UPDATE returns (correlated) | L80 reconciliation |
| 77 | Smart Kettle Pro recall: returns created for every affected line | INSERT … SELECT returns (many rows) | L80, Ch5 returns rate |
| 88 | Year-end stock count correction (driven by analysis) | UPDATE products (CTE) | Ch5 stock valuation |

Grace's order is placed on a date **after** the backlog cutoff used at L30, so the bulk update doesn't touch it. Every bulk mutation must state its row-selection rule precisely enough that the set of affected rows can't be misread (see §12).

---

## 9. Schema assessment

### What the current schema supports well
- Chapters 1–2 almost entirely: customers, products, categories, orders, order_items and payments give clear one-to-many relationships, a fact table (order_items), and a natural chain of 3–4 tables to join.
- Basic aggregates, grouping, joins and simple DML.

### Gaps that would make 100 levels repetitive or impossible
1. **Each order has only one date** (`order_date`). There is nothing to measure a duration against, so the course can't have meaningful date arithmetic, a delivery-delay incident, or NULL-means-not-yet-happened logic.
2. **No second many-to-many relationship.** Every join path goes through `order_items`, so Chapters 3–5 would keep re-joining the same four tables.
3. **No natural self-referencing relationship.** Self joins would have to be contrived.
4. **No refunds or returns.** Without them there's no net revenue, no reconciliation, and no recall story.
5. **Seed data is too clean.** Unit price always equals the current price. Payments always match order totals exactly. No inconsistent text. So data-quality, reconciliation and price-history tasks have nothing to find.
6. **The order history is thin for analytics:** 1–12 orders per month, with gaps in 2023. Monthly windows, `LAG` and running totals would be noisy, and some months would be missing.

### Recommended changes (minimum useful set)

All changes belong in the **template**, not in DDL challenges. Increase `SEED_VERSION` when they land.

#### S1. `orders.shipped_date`, `orders.delivered_date` (nullable TEXT)
- **Why:** to have a second and third date per order.
- **Enables:** date arithmetic (`julianday`), `IS NULL` meaning "hasn't happened yet", `CASE` buckets for delays, data-quality checks (shipped before ordered?), `LAG` between events.
- **Chapters:** 2 (backlog sets `shipped_date`), 3 (delivery incident), 4 (audit), 5 (trends).
- **Seed rule:** `pending` → both NULL; `shipped` → `shipped_date` only; `delivered` → both set; `cancelled` → both NULL. A deliberate cluster of slow deliveries in Jun 2025 starts the incident story.
- **Why existing schema isn't enough:** there is no other per-order date.

#### S2. `returns` table
`return_id, order_item_id → order_items, return_date, quantity, reason, refund_amount`
- **Enables:** net revenue (sales minus refunds), anti-joins ("delivered and never returned"), `EXISTS`, set operations, reconciliation CTEs, bulk `INSERT … SELECT` (the recall), conditional aggregation on returns rate.
- **Chapters:** 2 (first return), 3 (analysis), 4 (reconciliation, recall), 5 (returns rate trends).
- **Seed:** about 15–25 historical returns, including one or two deliberately over-refunded for the audit.
- **Why existing schema isn't enough:** refunds stored as negative payments would teach bad modelling and confuse revenue sums.

#### S3. `product_reviews` table
`review_id, product_id → products, customer_id → customers, rating (1–5), review_date, review_text`
- **Enables:** a second many-to-many path (customer ↔ product without going through orders), `HAVING` on rating counts, `LEFT JOIN` for products nobody has reviewed, correlated `EXISTS` (did the reviewer actually buy the product?), string pattern cleanup (spam), ranking in Ch5.
- **Chapters:** 2 (light: average rating per product), 3 (verified purchase, spam DELETE), 4 (correlated), 5 (ranking).
- **Seed:** about 60–90 reviews, including a few from customers who never bought the product, and 3–4 obvious spam reviews with a detectable text pattern.

#### S4. `customers.referred_by_customer_id` (nullable, foreign key to customers)
- **Enables:** a natural self join (referrer ↔ referred), `LEFT JOIN` on itself, analysis of the referral programme, and optionally one recursive-CTE extension.
- **Chapters:** 2 (Linnea's referral recorded), 4 (self join), 5 (referral revenue).
- **Seed:** about 10–12 existing referrals, including at least one two-step chain.
- **Why existing schema isn't enough:** there is no relationship inside a single table.

#### S5. Changes to the seed data (no new tables)
| Change | Why | Enables | Chapters |
|---|---|---|---|
| About 300 orders from Jan 2024 to Jun 2025 (at least 10 per month), plus the existing 2023 history | Analytics needs consistent monthly data | Monthly trends, `LAG`, running totals, cohorts | 4–5 |
| A price change on about 6 products in Jan 2025, so older order lines carry the old price | `unit_price` ≠ `price` should mean something | Price-at-sale vs current price; revenue must use `unit_price` | 2–5 |
| A **QA test account** (`qa.test@brightcart.example`, no orders) | Something safe to delete for the first DELETE | DELETE with a clear target | 1 |
| A few data-quality defects: 4–5 emails with uppercase or surrounding spaces; 3–4 city variants (`london`, `London `); a product name with a trailing space | Gives the clean-up tasks something real to fix | String functions, `UPDATE` with expressions | 3 |
| 2–3 delivered orders with no payment, and 1–2 underpaid orders | Finance audit findings | Anti-join, reconciliation | 2 (light), 4 |
| Keep the 3 duplicate customer names and the 3 seeded "Grace"s | Ambiguity lessons | Filtering on unique keys | 1, 3 |

Expected size after the changes: about 62 customers, 30 products, about 300 orders, about 650 order lines. Every **level** must still return at most 500 rows (§12).

#### Considered and rejected
- **Employees / staff table:** would only be used for a self join, and referrals already cover that with a better story.
- **Suppliers, addresses, coupons, inventory movements:** add complexity without new SQL concepts.
- **Category hierarchy:** categories are flat and easy to understand; hierarchy isn't needed.
- **Loyalty tiers stored as a column:** tiers are better *calculated* (CASE, NTILE) than stored.

---

## 10. Review of existing Levels 1–3

| Current | Recommendation | Reason |
|---|---|---|
| **01 Customer contact list** (specific columns from customers) | **Rewrite and move to Level 2** | Good idea, but Level 1 should be even gentler: `SELECT *` on the 6-row `categories` table ("what does Brightcart sell?"). Reframe this as Nadia's first request for a support contact sheet. Keep it unordered. |
| **02 Premium products** (`WHERE` + `ORDER BY DESC`, ordered) | **Rewrite and move to about Level 7** | It combines two concepts that haven't been introduced yet. Keep it as the first "combine" level, after `WHERE` (L3–5) and `ORDER BY` (L6) are taught separately. Reframe as a request from Lena (Merchandising). The ties check is fine (prices > 50 are unique), but check again after the S5 price changes. |
| **03 Welcome a new customer** (Grace Hopper INSERT) | **Keep the values; move to about Level 11; light rewrite** | Grace becomes the course's main recurring character. Moving her to L11 means the learner has already seen NULL (`IS NULL` at about L9), so leaving out `phone` makes sense. Story timing becomes 7 Jul 2025, and `signup_date` should match the story date (currently 2025-07-01; change to the level's story date). Her `customer_id` will change if the seed changes; later tasks identify her by email (§12). |

The behaviours these prototypes prove (outcome validation, the ordered flag, mutation diff, Review mode) are all kept. Only their position and story framing change.

---

## 11. Curriculum design rules

### 11.1 Difficulty
- Difficulty rises gradually: each level adds **at most one new idea**, or combines **at most two familiar ones in a new way**.
- Chapter boundaries are milestones, not jumps. The first 3 levels of each chapter reuse the previous chapter's skills in new contexts while starting the new topic.
- Every 5-level block within a chapter follows: introduce → practise → combine → apply.
- From Ch3 onwards, at least a third of levels describe the business goal rather than the SQL clause.
- From Ch4 onwards, most levels have more than one valid approach, and the validator accepts all of them.

### 11.2 Concept recurrence
- learn → practise → revisit → combine → apply independently.
- Each concept appears in **at least 3 later levels**, at least one of them in a later chapter (§5).
- Each chapter checkpoint uses at least one concept from **every** earlier chapter.
- No concept goes unused for more than about 15 levels after it was introduced.

### 11.3 Story continuity
- Each level has a 1–3 sentence introduction: **what happened**, **why the business cares**, **why SQL is needed**.
- Vary the trigger: customer contacts, warehouse reports, a stakeholder request, an incident, a deadline, curiosity about something seen earlier. Never more than two levels in a row phrased as "X asks you to…".
- At least **one callback per 5 levels** to an earlier event, customer, product or decision.
- Mutations are **story events**, never demonstrations of syntax.
- Prefer recurring entities over new made-up ones. Introducing a new named entity needs a story reason.

### 11.4 Repetition
These are not allowed:
- two levels that differ only by a `WHERE` value, a customer name, or the table used with identical logic
- more than 3 consecutive levels whose main skill is aggregation
- more than 2 consecutive mutation levels, except the planned order → order lines pairs

Repeated practice must add something: a new combination, a trap (NULLs, ties, duplicates), a larger scope, or less guidance.

### 11.5 Chapter checkpoints (L20, L40, L60, L80, L100)
- A realistic deliverable (briefing, report, reconciliation, board answer).
- Combines most concepts from the chapter, plus at least one from each earlier chapter.
- A query, not a mutation, so the result can be checked against a reference result.
- Hints are less explicit than in normal levels; the third hint still unblocks the learner.

### 11.6 Validation philosophy
- Validate the **outcome**: the result set for queries, the state change for mutations.
- Each query task states exactly: the output columns **in order**, any sort order **with tie-breakers**, rounding, and NULL display. Column *names* are not validated, except for the one alias level (see §14, decision D2).
- Use `ordered: true` only when order is part of the task. The sort keys must give a unique order.
- Require a specific construct only when it *is* the learning goal and outcome validation can't tell the difference. The default is never.
- Hardcoding answers (`SELECT 'Grace', …`) is an accepted risk. Make it impractical by using results with several rows and several columns.

### 11.7 Balance targets
| Metric | Target |
|---|---|
| Mutation levels | 22–26 overall; Ch1: 3, Ch2: 7–8, Ch3: 6–7, Ch4: 4–5, Ch5: 1–2 |
| Levels where aggregation is the main skill | ≤ 25 overall |
| Levels with at least one join | Ch2 ≥ 10, Ch3–5 ≥ 12 each |
| Levels that introduce a new concept | ~40% in Ch1, falling to ~25% in Ch5 |
| Levels with a story callback | ≥ 1 per 5 levels |
| Longest run without a story development | ≤ 4 levels |

---

## 12. Replay and determinism rules

These come from how the engine works today:
- Learner databases persist.
- Each submission runs as one transaction.
- Mutations are validated by comparing the state change against the reference.
- Review mode for completed mutations runs in a sandbox built from the template plus the reference solutions of all earlier mutations.
- The chain test replays every reference solution in order.

1. **Explicit values only.** Every mutation states every value the learner must write: dates, amounts, statuses, text. No `date('now')`, `CURRENT_TIMESTAMP`, `random()` or `randomblob()`.
2. **Story dates are always written out.** "Today" is stated in the task when it matters ("as of 2025-08-29"). A learner using `date('now')` must fail, and a hint should explain why.
3. **Auto-generated IDs.** IDs are deterministic (`INTEGER PRIMARY KEY` = max + 1), but tasks **identify new rows by natural keys** (email, product name, customer + date). They never quote a numeric ID that the seed data could change. If the learner must use an ID, they look it up (Ch2 onwards).
4. **Don't delete the highest-ID row of a table that receives later inserts.** It is still deterministic, but SQLite reuses the ID, which confuses learners.
5. **Bulk mutations state their row-selection rule exactly**, e.g. "pending orders placed before 2025-07-01". The rule must never accidentally match rows created by the learner.
6. **Money stays at 2 decimal places.** Calculated prices and refunds say "rounded to 2 decimal places" and the reference uses `ROUND(…, 2)`. The validator ignores float noise up to 6 decimal places.
7. **Use `ignore_columns` only as a last resort.** Later levels must never read an ignored column. Normally no level needs it.
8. **One statement per submission.** A business action that touches two tables becomes two levels (e.g. order header → order lines). Never require triggers or several statements.
9. **Each mutation changes at least one row and at most `MAX_CHANGES` (1,000).** Writable tables are as narrow as possible, usually one.
10. **Foreign keys are enforced.** A mutation must not depend on deleting a parent that has children. Teach that error deliberately, through hints or query levels.
11. **Every level states its assumptions about earlier state**: the mutations it relies on and the facts it expects. Level design records these as dependencies (§14).
12. **The canonical chain must pass.** The replay test (template → every reference solution in order) and the content tests must pass whenever content changes. Query levels must return at least 1 row and at most 500 at their point in the chain.
13. **Completed query levels must stay true when replayed.** Today a completed *query* level is validated against the learner's **current** database. A level whose text describes a moment ("Grace's order is still pending") becomes false later. Either:
    - **(a)** change the engine so completed query levels also run in the pre-challenge sandbox, **or**
    - **(b)** write query instructions so they stay true in every later state.
   
   **Recommended: (a)** — decision D1.
14. **Every level returns at most 500 result rows** (`MAX_ROWS`) at its point in the chain, including after the S5 seed growth.
15. **Changing the seed or schema means bumping `SEED_VERSION`.** Existing learner databases then show as out of date and must reset.

---

## 13. SQLite constraints

The app's bundled SQLite is **3.53.4** (shown by `/api/health`). All levels must work on it.

### Supported and used in the curriculum
- `RIGHT` / `FULL OUTER JOIN` (3.39+). **Teach `LEFT JOIN` as the main tool.** Mention RIGHT/FULL once in Ch2–3 and note they're missing from older SQLite versions.
- Window functions: `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`, `PERCENT_RANK`, `CUME_DIST`, `LAG`, `LEAD`, `FIRST_VALUE`, `LAST_VALUE`, `NTH_VALUE`, `ROWS`/`RANGE`/`GROUPS` frames, named `WINDOW`.
- `FILTER (WHERE …)` on aggregates (3.30+). Teach `CASE` inside aggregates first, then `FILTER` as a shorter form.
- `NULLS FIRST` / `NULLS LAST` (3.30+).
- CTEs, including recursive (recursive is optional and at most one level).
- `UNION`, `UNION ALL`, `INTERSECT`, `EXCEPT` (no `INTERSECT ALL` or `EXCEPT ALL`).
- `UPDATE … FROM` (3.33+), `RETURNING` (3.35+), `INSERT … SELECT`, multi-row `VALUES`.
- `iif`, `COALESCE`, `IFNULL`, `NULLIF`, `concat`, `concat_ws`, `string_agg` / `group_concat` with `ORDER BY`.

### Differences from other databases to point out to learners
| Behaviour | Where it matters |
|---|---|
| **No date type.** Dates are ISO text. Use `date()`, `strftime()`, `julianday()`, modifiers like `'-1 month'` and `'start of month'`. There's no `DATEDIFF`, `EXTRACT`, `INTERVAL` or `DATE_TRUNC`. | Ch3+ (a level that explicitly translates these ideas into SQLite) |
| **Integer division:** `7/2 = 3`. Use `* 1.0` or `CAST`. | Ch1 averages note; Ch3 percentages (a planned trap) |
| **Division by zero returns NULL**, not an error | Ch3 `NULLIF` |
| **`LIKE` ignores case for ASCII**; `GLOB` is case-sensitive; no `ILIKE`, no regex | Ch1 LIKE level; Ch3 data quality (`LOWER`/`=` vs `LIKE`) |
| **String functions:** `||`, `substr`, `instr`, `replace`, `trim`, `upper`/`lower`, `length`, `printf`/`format`. No `LEFT`/`RIGHT`/`POSITION`/`SPLIT_PART`. | Ch3 |
| **NULLs sort first** in ascending order | Ch1 ORDER BY + NULL level |
| **Booleans are 0/1** (`is_active`) | Ch1 |
| **Bare columns in `GROUP BY`** are accepted (non-standard) | Ch2: hint warns about it; avoid tasks where the bare-column shortcut happens to give the right answer |
| **`median()` / `percentile()` exist in this build but are not portable** | Ch5: the median level must also be solvable with window functions. The validator accepts either. |
| **No `QUALIFY`.** Filter on a window result in an outer query or CTE. | Ch5 |
| **Money is `REAL`** | Every money output says "rounded to 2 decimal places" |
| **`DELETE`/`UPDATE` can't use `JOIN` directly.** Use subqueries (or `UPDATE … FROM`). | Ch2–4 DML |
| **UPSERT (`ON CONFLICT DO UPDATE`) needs UPDATE permission** | Not taught; blocked in INSERT-only levels |

### Engine limits (current)
- One statement per submission
- 5,000-character limit on SQL
- 2 s timeout
- 500 result rows
- 1,000 changed rows per mutation
- Floats compared to 6 decimal places
- Column names ignored
- `sqlite_schema` and `PRAGMA` are blocked; learners use the Schema panel

---

## 14. Guidance for future level-design sessions

### Order of work
1. Settle the open decisions (below).
2. Design levels **in blocks of 10**, adding them under "Level designs". After each block, update the running **dependency ledger** and **concept tracker** at the end of this file.
3. Before writing YAML for a block, review it against §11 and §12.
4. Implement schema changes S1–S5 **before** any level that uses them. Ideally do all of them before redesigning L1–10, so IDs and counts are final.

### Level entry template
Each level must use this format:

```
### Level N — Title
- Chapter / block: …            Difficulty in chapter: 1–5
- Story: (1–3 sentences: what happened, why it matters, why SQL)
- Task: (exact deliverable: columns in order, ordering + tie-breakers, rounding)
- Kind: query | mutation        Ordered: yes/no
- New concept(s): …             Reused concepts: …
- Tables: …
- Depends on state from: L.. (what exactly)
- Mutation (if any): operation, table(s), rows affected, exact values
- Enables later: L.. (what they use)
- Validation notes: (only if something special is needed)
- Hint ladder: 1) nudge 2) technique 3) near-solution (no full SQL)
```

### Before approving a block, check:
- [ ] Each level introduces at most one new idea
- [ ] At least one callback in the block
- [ ] No two levels differ only by values
- [ ] Each mutation has a story reason and a later dependency
- [ ] Every value in every mutation is stated explicitly
- [ ] Each query's output is fully specified, and `ordered` tasks have a unique sort order
- [ ] Row counts are between 1 and 500 at this point in the chain
- [ ] Concepts introduced so far are still recurring on schedule (§5, §11.2)

### Open decisions (needed before Levels 1–10 are designed)
- **D1.** How completed *query* levels are replayed (§12.13): pre-challenge sandbox in the engine (recommended) or the "stays true forever" wording rule.
- **D2.** Validating aliases: add an optional `match_column_names: true` per level (recommended, used rarely), or teach aliases without validating them.
- **D3.** Approve schema changes **S1–S4** and seed changes **S5** (§9), and agree they land before L1–10 are finalised.
- **D4.** Approve the company, cast and story calendar (§2–§7).

---

## Level designs

_Added in future sessions, in blocks of 10._

### Chapter 1 — Foundations (Levels 1–20)
_Not yet designed._

### Chapter 2 — Relational SQL (Levels 21–40)
_Not yet designed._

### Chapter 3 — Intermediate SQL (Levels 41–60)
_Not yet designed._

### Chapter 4 — Advanced Query Construction (Levels 61–80)
_Not yet designed._

### Chapter 5 — Advanced Analytics (Levels 81–100)
_Not yet designed._

---

## Dependency ledger

_Updated after each block: mutation level → state change → levels that depend on it._

| Mutation level | State change | Depended on by |
|---|---|---|
| — | — | — |

## Concept tracker

_Updated after each block: concept → level introduced → levels where it recurs._

| Concept | Introduced | Recurs at |
|---|---|---|
| — | — | — |
