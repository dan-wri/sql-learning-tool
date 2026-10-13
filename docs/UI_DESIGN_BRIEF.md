# Brightcart SQL Studio — UI/UX Design Brief

**Status:** Approved visual/design direction for implementation  
**Companion document:** `docs/SQL_CURRICULUM.md`  
**Intended location:** `docs/UI_DESIGN_BRIEF.md`

---

# 1. Purpose

This document defines the visual language, interaction model, layout principles, navigation system, and presentation standards for the Brightcart SQL learning application.

It should be treated as the **source of truth for presentation and UX decisions**.

`docs/SQL_CURRICULUM.md` remains the source of truth for:

- curriculum content
- challenge ordering
- story progression
- SQL concepts
- mutation dependencies
- chapter gating rules
- replay/determinism requirements

This document governs **how that experience should look and feel**.

When implementing UI work:

1. preserve all existing challenge, validation, progression, security, replay, and database behaviour;
2. do not alter curriculum content merely to fit a visual design;
3. use this document to make the existing functionality feel cohesive, polished, modern, and intentionally designed.

The goal is not simply to “make the CSS nicer”.

The goal is to make Brightcart feel like a **premium interactive SQL learning environment**.

---

# 2. Product feeling

Brightcart SQL Studio should feel like a cross between:

- a modern data workspace;
- a thoughtfully designed learning platform;
- a lightweight professional SQL IDE;
- a progressive course with a sense of journey.

It should **not** feel like:

- a university worksheet rendered in a browser;
- a generic Bootstrap admin dashboard;
- a raw developer/debug interface;
- a collection of white rectangles with borders;
- an overly gamified children's learning app;
- an imitation of VS Code;
- a neon “hacker” terminal.

The desired tone is:

> **calm, intelligent, modern, colourful, focused, and rewarding.**

The learner should feel that they are working inside **Brightcart's internal data studio** as their skills and responsibilities grow.

---

# 3. Core design principles

## 3.1 Clear hierarchy before decoration

Every screen should immediately answer:

1. Which chapter am I in?
2. Which level am I on?
3. What is happening in the story?
4. What do I need to do?
5. Where do I write SQL?
6. What happened when I submitted?
7. What can I do next?

Visual decoration must support those answers rather than compete with them.

## 3.2 Colour should communicate meaning

Colour should be used deliberately for:

- chapter identity;
- current selection;
- completion;
- unlocked/open state;
- locked state;
- mutations;
- Review mode;
- success;
- warnings/errors;
- hints.

Avoid using unrelated colours simply because they look attractive.

The interface can be colourful without becoming noisy.

## 3.3 Reduce page-level scrolling

The application will eventually contain **100 levels** and a non-trivial schema.

The learner should not have to scroll through the entire application page to move between:

- challenges;
- schema tables;
- editor;
- results.

Prefer a **viewport-based application shell** with independently scrollable regions.

The browser page itself should normally remain close to one viewport high on desktop.

Use internal scroll containers with:

- visible but unobtrusive scrollbars;
- sticky headings where helpful;
- clear scroll boundaries;
- no nested scrolling where it becomes confusing.

“Death scrolling” through 100 challenges is explicitly unacceptable.

## 3.4 The story is part of the interface

Story text must not look like an afterthought above a coding exercise.

The situation should have a deliberate visual treatment that distinguishes it from the exact task.

The learner should feel:

> “Something has happened at Brightcart; I need SQL to solve it.”

not:

> “Here is some flavour text before another question.”

## 3.5 The database should feel alive

A major differentiator of this project is the persistent evolving database.

The visual design should reinforce that.

When the learner:

- inserts a customer;
- updates an order;
- changes a price;
- records a return;
- deletes a record;

the interface should make that change feel tangible.

Query results, mutation previews, schema presentation, story callbacks, and Review mode should all reinforce the sense that this is **one living database with a history**.

## 3.6 Professional, not sterile

This is a technical learning tool, but technical does not mean grey.

Use:

- confident typography;
- soft surfaces;
- purposeful accent colours;
- small icons;
- considered spacing;
- subtle depth;
- restrained motion.

Avoid:

- giant shadows;
- excessive gradients;
- glassmorphism everywhere;
- novelty fonts;
- excessive rounded pills;
- emoji as primary interface icons;
- overly dense enterprise-dashboard styling.

---

# 4. Problems in the current visual design

The current application is functional, but its presentation still feels close to an engineering prototype.

From the current interface, the major UX/visual weaknesses are:

## 4.1 Navigation and schema compete for the same sidebar

The challenge list and schema are stacked in one long left column.

This creates several problems:

- challenge navigation becomes vertically expensive;
- the schema begins below the challenge list and encourages long scrolling;
- as the course grows from 10 to 100 levels this structure will become impractical;
- challenge progression and database reference feel like the same type of information even though they serve different purposes.

These should become separate, intentionally designed regions.

## 4.2 The interface has weak visual identity

The current presentation is primarily:

- white;
- pale grey;
- blue buttons;
- rectangular borders.

It works, but it does not yet feel recognisably like **Brightcart SQL Studio**.

The redesign should establish a coherent product identity.

## 4.3 The challenge list will not scale to 100 levels

Showing every level in one long list is not acceptable for the final course.

The redesign must introduce **chapter-aware navigation**.

Only the selected/unlocked chapter's 20 challenges should need to be visible at once.

## 4.4 The main challenge area is visually flat

Level metadata, status, story, task, hints, and editor are present, but most elements occupy similar visual weight.

The learner's eye should be guided deliberately through:

**level → situation → task → SQL → feedback**

## 4.5 Technical/system information is too visually prominent

Items such as:

- API status;
- SQLite version;
- learner identifier;

are useful, but they should not compete with the learning experience.

They should remain available while becoming visually secondary.

## 4.6 Reset is too visually dominant

“Reset database” is a destructive/recovery action, not a primary learning action.

It should remain easy to find but should not visually compete with:

- Run/Submit;
- Next challenge;
- chapter progression.

## 4.7 The schema feels like raw debug output

The schema currently communicates useful information, but visually it is close to a formatted text/tree dump.

The redesign should make it feel like a proper database explorer.

---

# 5. Visual identity — “Brightcart Data Studio”

The recommended visual theme is **Brightcart Data Studio**.

Think:

- clean white work surfaces;
- a very light blue-grey canvas;
- deep ink typography;
- confident indigo as the core brand colour;
- chapter-specific accents;
- mint/teal for success and data freshness;
- warm amber for mutations/changes;
- restrained colour gradients used only in high-value areas.

The interface should feel bright and contemporary during long learning sessions.

---

# 6. Colour system

Use semantic design tokens rather than scattered hard-coded colours.

The exact values may be tuned slightly during implementation for contrast, but this is the target palette.

## 6.1 Core palette

| Token | Suggested value | Purpose |
|---|---:|---|
| `--canvas` | `#F5F7FB` | Main application background |
| `--surface` | `#FFFFFF` | Primary cards/panels |
| `--surface-subtle` | `#F8FAFC` | Secondary surfaces |
| `--surface-hover` | `#F1F5F9` | Hover states |
| `--border` | `#E2E8F0` | Default borders |
| `--border-strong` | `#CBD5E1` | Strong separators |
| `--text` | `#0F172A` | Primary text |
| `--text-secondary` | `#475569` | Supporting text |
| `--text-muted` | `#64748B` | Metadata |
| `--text-disabled` | `#94A3B8` | Locked/disabled content |
| `--primary` | `#4F46E5` | Main interactive accent |
| `--primary-hover` | `#4338CA` | Primary hover |
| `--primary-soft` | `#EEF2FF` | Selected/soft primary background |
| `--teal` | `#0F766E` | Secondary/data accent |
| `--teal-soft` | `#CCFBF1` | Soft teal |
| `--success` | `#15803D` | Completion/success |
| `--success-soft` | `#DCFCE7` | Success backgrounds |
| `--warning` | `#B45309` | Mutation/change warning |
| `--warning-soft` | `#FEF3C7` | Mutation/change backgrounds |
| `--danger` | `#B91C1C` | Errors/destructive actions |
| `--danger-soft` | `#FEE2E2` | Error backgrounds |
| `--review` | `#2563EB` | Review-mode status |
| `--review-soft` | `#DBEAFE` | Review-mode background |

## 6.2 Chapter colours

Each chapter should have its own accent identity.

These colours should appear in:

- chapter tabs;
- chapter progress;
- current-level accent;
- selected navigation state;
- subtle story-card accents.

Do **not** recolour the entire application for each chapter.

| Chapter | Name | Accent |
|---|---|---:|
| 1 | Foundations | `#2563EB` — cobalt blue |
| 2 | Relational SQL | `#0F766E` — teal |
| 3 | Intermediate SQL | `#D97706` — warm amber |
| 4 | Advanced Query Construction | `#7C3AED` — violet |
| 5 | Advanced Analytics | `#DB2777` — magenta/rose |

Use chapter colours as **controlled accents**, not full backgrounds.

## 6.3 Status semantics

### Completed
- green check icon;
- subtle green text/background;
- should feel positive without overpowering navigation.

### Current / Open
- chapter accent;
- stronger border/background;
- clearly identifiable at a glance.

### Locked
- muted grey;
- lock icon;
- reduced contrast;
- still readable;
- do not use opacity so low that text becomes inaccessible.

### Mutation
- warm amber “Changes data” badge;
- amber accent in ChangePreview.

### Review mode
- blue/indigo treatment;
- visually distinct from ordinary success;
- clearly says changes will not persist.

### Error
- red should be used carefully and locally;
- never turn an entire large panel bright red.

---

# 7. Typography

The application should feel crisp and editorial rather than overly “developer tool” heavy.

## 7.1 UI typography

Preferred stack:

```css
font-family:
  Inter,
  ui-sans-serif,
  system-ui,
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  sans-serif;
```

Do not require an external font download if it complicates local/offline development.

Use weight and scale to establish hierarchy.

Suggested hierarchy:

- App/Product title: 18–20px, 700
- Challenge title: 24–30px, 700
- Section heading: 12–13px, 700, subtle uppercase/letter-spacing only where appropriate
- Body: 14–16px, 400–500
- Metadata: 12–13px
- Buttons: 14px, 600

Avoid excessively small text.

## 7.2 Code typography

Use a high-quality monospace stack:

```css
font-family:
  "JetBrains Mono",
  "SFMono-Regular",
  Consolas,
  "Liberation Mono",
  monospace;
```

The editor should be visually distinct from narrative text.

---

# 8. Spacing, radius, and depth

Use a consistent spacing system based broadly on 4px/8px increments.

Recommended spacing tokens:

- 4px — micro gap
- 8px — small
- 12px — compact
- 16px — standard
- 20px — card padding
- 24px — major card spacing
- 32px — large separation

Recommended radii:

- buttons/chips: 8–10px;
- small cards: 10–12px;
- primary panels: 14–16px;
- large shell panels: 16–18px.

Use borders more often than shadows.

Recommended surface depth:

- normal panel: border only or extremely soft shadow;
- floating drawer/menu: subtle medium shadow;
- current challenge: slight accent shadow is acceptable;
- avoid large diffuse shadows behind every card.

---

# 9. Desktop application shell

The primary desktop experience should use a **fixed-height application shell**.

Recommended structure:

```text
┌───────────────────────────────────────────────────────────────────────────┐
│ Product header                                                            │
├───────────────────────────────────────────────────────────────────────────┤
│ Chapter progression rail                                                  │
├─────────────────┬───────────────────────────────────┬─────────────────────┤
│ Challenge       │ Main learning workspace           │ Database explorer   │
│ navigator       │                                   │                     │
│                 │ Situation / task                  │ Schema              │
│  scrolls        │ SQL editor                        │                     │
│  independently  │ Feedback / results                │ scrolls             │
│                 │                                   │ independently       │
└─────────────────┴───────────────────────────────────┴─────────────────────┘
```

Suggested widths at large desktop sizes:

- Challenge navigation: **260–300px**
- Main workspace: flexible, minimum **650px**
- Database explorer: **280–340px**

The main app should comfortably fill screens around 1366–1600px wide.

---

# 10. Product header

The header should become calmer and more product-like.

## 10.1 Left side

Show:

**Brightcart**  
**SQL Studio**

Possible treatment:

- small abstract database/grid mark;
- “Brightcart” in primary text;
- “SQL Studio” in accent or muted text.

Do not use a huge logo.

## 10.2 Centre / progress

The most useful global information is **course progress**, not API internals.

Show something similar to:

> **Level 7 of 100** · 7% complete

Optionally include a thin progress bar.

This should become more prominent than learner ID / API status.

## 10.3 Right side

Keep technical/system information available but visually secondary.

Recommended:

- small green status dot;
- compact “Connected” or “SQLite” indicator;
- learner ID hidden behind a small profile/system popover if practical;
- Reset database as a restrained secondary/destructive action.

Reset should require confirmation.

Do not make Reset the strongest button in the header.

---

# 11. Chapter progression rail

This is a major new component.

It should sit beneath the product header and represent the full 100-level journey.

Show five chapter tabs:

1. Foundations
2. Relational SQL
3. Intermediate SQL
4. Advanced Query Construction
5. Advanced Analytics

Each tab should communicate:

- chapter number;
- short name;
- completion state;
- progress such as `7/20`;
- locked/unlocked state.

## 11.1 Chapter gating

Chapter 1 is available initially.

Chapter N+1 remains locked until all 20 levels in Chapter N are complete.

Locked chapters:

- remain visible;
- show a lock icon;
- use reduced emphasis;
- cannot be entered;
- may show a tooltip/message:

> Complete Chapter 1 to unlock Relational SQL.

Do not hide future chapters. The learner should be able to see the journey ahead.

## 11.2 Active chapter

The active tab should use:

- its chapter colour;
- a strong underline or subtle filled surface;
- its progress count;
- clear selected state.

Avoid using only a thin border.

## 11.3 Responsive chapter rail

On narrower screens:

- shorten labels;
- allow horizontal scrolling if necessary;
- retain chapter numbers;
- never wrap the rail into an ugly multi-row grid.

---

# 12. Challenge navigator

The left panel should show **only the 20 levels of the selected chapter**.

This solves the 100-level scaling problem.

The list itself should be independently scrollable.

Use a constrained height derived from the viewport and `overflow-y: auto`.

The chapter heading/progress at the top should remain sticky.

## 12.1 Challenge row design

Each challenge row should show:

- level number;
- concise title;
- status;
- optional tiny concept indicator;
- mutation marker where applicable.

Recommended structure:

```text
┌──────────────────────────────────┐
│ 07   Price list             ✓    │
│      ORDER BY                    │
└──────────────────────────────────┘
```

Do not overload each row.

## 12.2 States

### Current/Open

Use:

- chapter-colour left accent;
- soft chapter-colour background;
- clear level number;
- “Open” may be represented by a small dot rather than a large pill.

### Completed

Use:

- subtle green check;
- slightly muted surface;
- title remains readable;
- do not fill every row with a large green “Completed” pill.

### Locked

Use:

- lock icon;
- muted title;
- no hover implying clickability.

### Mutation

Add a small amber database/edit icon or compact marker.

## 12.3 Challenge list scrollbar

The scrollbar should be:

- visible enough to indicate more content;
- narrow;
- styled consistently;
- not aggressively coloured.

Do not hide scrollbars completely.

The user should understand that the list is scrollable.

---

# 13. Main challenge workspace

The main workspace should have a deliberate vertical hierarchy.

Recommended order:

1. Breadcrumb / level metadata
2. Challenge title + status
3. Story / situation
4. Exact task
5. Hint controls
6. SQL workspace
7. Feedback / result / changes
8. Next-level action

Avoid unnecessary page-level scrolling by sizing sections carefully.

---

# 14. Challenge header

Replace the current flat metadata line with a stronger composition.

Example:

```text
CHAPTER 1 · FOUNDATIONS                      LEVEL 7 / 100

Price list
Sort the catalogue so Lena can review the most expensive products first.

[ORDER BY] [sorting]                         Difficulty ●●○○○
```

Use the chapter accent subtly.

## 14.1 Difficulty

Difficulty should be readable but not dominant.

Prefer something like:

```text
Difficulty  ●●○○○
```

or a compact label:

```text
Beginner · 2/5
```

Do not create an overly game-like star system.

---

# 15. Story / “The Situation” card

Story is a first-class part of the course.

Create a visually distinctive **Situation card**.

Recommended treatment:

- chapter-colour accent bar;
- very soft tinted background;
- small story/context icon;
- heading: `THE SITUATION`;
- readable 1–3 sentence narrative;
- optional stakeholder name/role where such metadata exists.

Example:

```text
╭──────────────────────────────────────────────────────────╮
│  THE SITUATION                                           │
│                                                          │
│  Nadia needs a clean contact sheet for a routine         │
│  campaign. This is your first chance to choose only      │
│  the customer details the support team actually needs.   │
╰──────────────────────────────────────────────────────────╯
```

Do not over-decorate it.

---

# 16. Task card

The exact SQL requirement should be visually firmer than the story.

Recommended:

- heading: `YOUR TASK`;
- white/neutral surface;
- task text in 15–16px;
- inline code formatting for table names, column names, literal values, and SQL keywords only when appropriate.

The task must remain precise.

Do not let decorative copy obscure required:

- column order;
- sorting;
- rounding;
- exact values.

---

# 17. Concepts

Concept labels should be small and useful.

Examples:

- `WHERE`
- `ORDER BY`
- `NULL`
- `JOIN`
- `CTE`
- `window functions`

Avoid rendering a wall of pills.

Show at most the few concepts most relevant to the current level.

---

# 18. Review mode

Review mode must look intentional rather than like a generic information alert.

Use an indigo/blue treatment.

Example:

```text
↻ Review mode
You already completed this level.
Your attempt runs against the database as it existed here,
so later changes won't affect this practice attempt.
```

It should be:

- compact;
- clearly visible;
- visually distinct from errors and success;
- consistent between query and mutation Review mode.

Do not use an enormous banner that pushes the editor far down.

---

# 19. Mutation levels

Mutation levels should feel meaningfully different without becoming alarming.

Use:

- amber `Changes data` marker;
- database/edit icon;
- warm accent around ChangePreview;
- copy explaining persistence when relevant.

The visual message should be:

> “This action changes your Brightcart database.”

not:

> “Danger!”

---

# 20. Hint experience

Hints should feel like progressive coaching.

The existing `Show hint (1 of 3)` behaviour should be redesigned into a cleaner component.

Recommended:

```text
Need a hint?     0 / 3 used
[Reveal hint]
```

After revealing:

```text
Hint 1
Start by identifying which table contains the fields the task asks for.

[Reveal next hint]
```

Guidelines:

- keep hints close to the task/editor;
- use a soft amber/yellow treatment;
- do not push the editor dramatically down the page;
- consider an expandable/collapsible panel;
- retain all previously revealed hints during the attempt.

---

# 21. SQL workspace

The editor should feel like the centre of the application.

Create a dedicated **SQL Workspace** card.

Recommended header:

```text
SQL WORKSPACE                               SQLite
                                           ⌘ Enter to run
```

The Run/Submit action should be attached to this workspace rather than visually floating at the bottom-right of a large empty region.

## 21.1 Editor toolbar

Consider:

- `Run query` / `Submit` as primary action;
- keyboard shortcut `Cmd/Ctrl + Enter`;
- small dialect badge: `SQLite`;
- optional reset-editor/clear button only if useful.

The primary execution action should be easy to find without scrolling.

## 21.2 Editor sizing

The editor should:

- have a comfortable default height;
- avoid huge unused blank regions;
- have a sensible minimum and maximum height;
- use its own scrollbar for long SQL;
- retain line numbers;
- preserve CodeMirror functionality.

Suggested default:

- ~220–320px on standard desktop;
- expandable if the query becomes long.

Advanced levels may require larger SQL.

Consider a drag-to-resize handle if it can be implemented cleanly, but this is optional.

## 21.3 Editor theme

Use a light editor theme aligned with the app.

Recommended:

- very pale blue/grey editor background;
- clear line-number gutter;
- indigo/blue syntax accents;
- subtle active-line highlight;
- visible selection;
- clear focus ring.

Do not create a dark editor inside an otherwise light app unless a full dark mode is implemented later.

---

# 22. Results workspace

After submission, the result should appear directly beneath the editor in a dedicated panel.

Recommended states:

- not run yet;
- executing;
- passed;
- failed;
- blocked/security error;
- mutation change preview.

Use animation carefully so results feel responsive.

---

# 23. Query result table

The result table should feel like a small professional data grid.

Required:

- sticky column headers;
- alternating or hover row treatment;
- horizontal scroll for wide results;
- vertical scroll for larger result sets;
- row-count indicator;
- clear NULL rendering;
- monospace for raw values where appropriate;
- no giant page expansion for hundreds of rows.

Example header:

```text
RESULTS                                  61 rows
```

The table container should have a maximum height and its own scroll.

This is another key anti-death-scroll measure.

---

# 24. Feedback

Feedback should be visually distinct from raw query results.

## Success

Use a restrained success panel:

```text
✓ Challenge complete
Your query returned the expected result.
```

Then provide a clear **Next challenge** action.

Do not cover the interface in green.

## Failure

Use:

- concise heading;
- learner-friendly message;
- optional explanation;
- no reference values that leak the answer.

Example:

```text
Not quite yet

You returned the right rows, but they're in the wrong order.
Check the sorting requirement in the task.
```

## Security/blocking feedback

Should feel explanatory, not punitive.

Example:

```text
This level is read-only.
Only SELECT queries are allowed here.
```

---

# 25. ChangePreview

Mutation feedback deserves a polished “database diff” treatment.

Use sections:

- Added
- Updated
- Removed

For updates, show:

```text
phone
Before   NULL
After    07700 900123
```

Use:

- green for additions;
- amber/blue for changed values;
- red only lightly for deletions.

Clearly state:

- `Saved to your training database`
or
- `Review attempt — changes were not saved`

The learner should understand exactly what their SQL did.

---

# 26. Database explorer

Move the schema out of the challenge-navigation column.

Create a dedicated right-side **Database Explorer**.

This is one of the most important visual upgrades.

## 26.1 Header

Use:

```text
DATABASE
Brightcart
```

Optional:

- table search/filter;
- collapse-all button.

## 26.2 Table presentation

Tables should be collapsible cards/accordions.

Example:

```text
▼ customers                         62 rows
  🔑 customer_id        INTEGER
     first_name         TEXT
     last_name          TEXT
     email              TEXT
     phone              TEXT · nullable
  ↗  referred_by...     INTEGER · FK
```

Use proper visual semantics for:

- primary key;
- foreign key;
- nullable;
- type.

Do not underline primary keys like web links.

Use small icons or labels instead.

## 26.3 Schema search

Once the schema grows, allow the learner to search:

- table names;
- column names.

This becomes especially useful in later chapters.

## 26.4 Schema scrolling

The Database Explorer must scroll independently from the main workspace.

Its header/search should remain sticky.

## 26.5 Relationships

Where foreign keys exist, show a subtle relationship label.

Example:

```text
customer_id  → customers.customer_id
```

Do not build a complex interactive ERD unless specifically requested later.

A clean relationship display is enough for the core interface.

---

# 27. Optional schema-panel controls

Nice-to-have after the core redesign:

```text
[Schema] [Relationships]
```

`Schema` is required.

A lightweight relationship view may later show:

- source table;
- FK;
- target table.

Do not let this side quest become a full database modelling application.

---

# 28. Progress presentation

Progress should feel motivating without becoming gamified.

Recommended global displays:

- `Level 7 of 100`;
- `7% complete`;
- current chapter `7 / 20`.

Use progress bars sparingly.

Do not add:

- XP;
- coins;
- streak pressure;
- leaderboards;
- fake achievements.

The satisfaction should come from genuine mastery and the evolving story.

---

# 29. Chapter completion

Completing level 20/40/60/80 should feel meaningful.

When a chapter completes:

- mark the chapter tab complete;
- unlock the next tab;
- show a short completion panel;
- summarise what the learner can now do;
- allow them to enter the new chapter.

A subtle 300–600ms visual celebration is welcome:

- progress bar completes;
- chapter accent briefly glows;
- checkmark transitions in.

Avoid large confetti effects unless added much later as an optional flourish.

---

# 30. Level completion transition

After a successful challenge:

1. show success;
2. mark the challenge complete in navigation;
3. unlock the next level;
4. show a prominent but elegant `Continue to Level N` button.

Do not automatically jump immediately.

Give the learner a moment to inspect their result.

---

# 31. Locked content

Locked levels/chapters should communicate **progression**, not punishment.

Use:

- lock icon;
- subdued surface;
- readable title;
- optional tooltip explaining requirement.

Do not completely blur or hide future titles.

Seeing future topics creates anticipation.

---

# 32. Button hierarchy

Use consistent hierarchy.

## Primary
Examples:

- Run query
- Submit
- Continue / Next challenge

Filled primary colour.

## Secondary
Examples:

- Reveal hint
- Collapse schema
- View chapter

Outline/soft background.

## Tertiary
Examples:

- copy;
- clear;
- system details.

Ghost/text button.

## Destructive
Examples:

- Reset database.

Red/danger treatment only on confirmation or hover; not a giant red button.

---

# 33. Icons

Use a consistent icon family.

If adding a dependency is acceptable, **Lucide**-style icons are appropriate.

Useful icons include:

- database;
- table;
- key;
- link/relationship;
- lock;
- check;
- play/run;
- lightbulb;
- rotate/review;
- edit/change;
- search;
- chevron;
- warning.

Do not mix several icon styles.

Do not use emoji as the primary UI icon system.

---

# 34. Motion

Motion should make state changes understandable.

Recommended transition speed:

- hover: 120–160ms;
- panel/state change: 180–250ms;
- chapter completion: 300–600ms.

Animate:

- challenge selection;
- accordion opening;
- success state;
- unlocking next level;
- chapter tab progression.

Do not animate:

- large layout shifts;
- long bouncing effects;
- looping decorative elements.

Respect `prefers-reduced-motion`.

---

# 35. Accessibility

Beauty must not come at the cost of usability.

Required:

- WCAG-conscious colour contrast;
- keyboard navigability;
- visible focus states;
- status not communicated by colour alone;
- buttons with meaningful accessible names;
- semantic headings;
- ARIA labels where icons have no visible label;
- minimum comfortable click targets;
- screen-reader-friendly progress/status text;
- reduced-motion support.

Avoid tiny grey-on-grey metadata.

---

# 36. Responsive behaviour

Desktop is the primary experience, but the layout must degrade gracefully.

## ≥ 1280px

Use full three-panel layout:

- challenge navigator;
- workspace;
- database explorer.

## ~1024–1279px

Keep challenge navigator.

Database explorer may collapse into a drawer/button.

## < 1024px

Use:

- main workspace;
- navigation drawer;
- database drawer;
- chapter rail remains accessible.

Do not squeeze three narrow columns onto a tablet-sized viewport.

---

# 37. Scroll architecture

This is important enough to define explicitly.

On desktop, prefer:

```text
body / app shell
    no meaningful vertical page scroll

chapter navigator
    fixed/sticky

challenge list
    own vertical scroll

main workspace
    own vertical scroll only when necessary

SQL editor
    own scroll for long code

results table
    own vertical + horizontal scroll

schema explorer
    own vertical scroll
```

Avoid:

- the entire browser page becoming thousands of pixels tall;
- challenge list expanding indefinitely;
- result tables pushing everything far below the editor;
- schema tables expanding the whole page.

---

# 38. Scrollbar styling

Use subtle custom scrollbar styling where supported.

Goals:

- narrow;
- rounded;
- neutral thumb;
- slightly darker on hover;
- chapter colour may be used very subtly in challenge navigation.

Do not make scrollbars invisible.

---

# 39. Loading states

The application should never look broken while data loads.

Use:

- small skeleton rows for challenge navigation;
- spinner/progress inside Run button;
- skeleton schema sections;
- disabled Run button while submission is executing.

Avoid full-screen blocking spinners for ordinary actions.

---

# 40. Empty states

Examples:

## No query run yet

```text
Run your query to see the result here.
```

Use subtle database/table illustration/icon.

## No rows returned

Clearly distinguish:

> Query succeeded — 0 rows returned.

from an error.

## No hints used

Do not show a large empty hints panel.

---

# 41. Error resilience

API/network failures should be presented as product-level messages.

Example:

```text
We couldn't reach the local SQL service.
Check that the backend is running, then try again.
```

Do not expose raw stack traces to learners.

Developer details can optionally be available in a disclosure.

---

# 42. Technical details placement

API health, SQLite version, learner UUID, and similar details should remain accessible because they are useful during development.

Recommended placement:

**System popover** in the header:

```text
System
✓ Backend connected
SQLite 3.54.0
Learner 16395757
```

These are secondary to learning progress.

---

# 43. Reset database experience

Reset should be visually subdued until intentionally selected.

Use:

`Settings / System → Reset training database`

or a restrained outline button.

Confirmation dialog should clearly state:

> Resetting will remove your Brightcart database changes and all course progress for this learner.

Actions:

- Cancel
- Reset database

The destructive button becomes red inside the confirmation dialog.

---

# 44. Surface composition

Avoid putting a border around absolutely everything.

Use hierarchy:

- app canvas;
- major panel surfaces;
- nested sections separated by spacing/background;
- dividers only when they clarify grouping.

The current prototype is somewhat “boxy”.

The redesign should feel more spacious and intentional.

---

# 45. Avoid pill overload

Pills/chips are useful for:

- concepts;
- status;
- difficulty;
- mutation markers.

But not every piece of metadata should become a pill.

Use normal text where possible.

---

# 46. Sidebar density

Challenge rows should be compact enough that roughly **10–13 levels** can be visible at once on a common laptop display.

The remaining levels are reached by the sidebar scrollbar.

Do not make each challenge card 90–120px tall.

---

# 47. Story continuity visual cue

Because Brightcart is an ongoing narrative, recurring entities can occasionally be emphasised subtly.

For example:

- `Grace Hopper`
- `Summer Sale`
- `Smart Kettle Pro`

could use semibold text in story copy.

Do not create a separate “character card” for every recurring entity.

Keep the narrative mature and lightweight.

---

# 48. Chapter personality

Each chapter should feel slightly distinct through its accent colour and tone, while keeping the same base interface.

## Chapter 1 — Foundations / cobalt

Feeling:
- clear;
- welcoming;
- structured.

## Chapter 2 — Relational SQL / teal

Feeling:
- connected;
- operational;
- database relationships become more visible.

## Chapter 3 — Intermediate / amber

Feeling:
- investigative;
- data quality;
- business problems.

## Chapter 4 — Advanced Query Construction / violet

Feeling:
- analytical;
- layered;
- professional.

## Chapter 5 — Advanced Analytics / rose

Feeling:
- senior;
- strategic;
- board-level analysis.

Do not completely reskin the app between chapters.

---

# 49. Visual progression

As later chapters become harder, the interface should not become harder to use.

Instead:

- hints become less explicit due to curriculum rules;
- tasks become more open-ended;
- editor may naturally contain longer SQL;
- result panels may become richer.

Navigation and workspace clarity should remain consistent.

---

# 50. Editor/result balance

At present, the editor can create a large empty visual region.

The redesigned workspace should adapt.

Before submission:

- editor gets the majority of the lower workspace.

After submission:

- editor and result should form a balanced stack;
- results should be immediately visible without requiring a large scroll.

On tall screens, consider a resizable editor/results split.

---

# 51. Current-level context

The learner should always be able to see:

- chapter;
- level;
- title.

If the main workspace scrolls, consider a sticky compact challenge header.

Do not make the learner scroll to the top to remember what they are solving.

---

# 52. Keyboard experience

Important shortcuts:

- `Cmd/Ctrl + Enter` — submit/run;
- `Esc` — close transient menus/autocomplete where appropriate.

Do not overload shortcuts.

Show the run shortcut subtly in the SQL Workspace header.

---

# 53. Focus mode — optional future enhancement

A future enhancement may allow:

> Focus mode

which collapses:

- challenge navigator;
- database explorer;

leaving:

- story/task;
- editor;
- results.

This is especially useful for advanced levels.

This is **nice-to-have**, not required for the first visual redesign.

---

# 54. Dark mode — future, not required

The token system should make future dark mode possible.

Do not spend the current redesign effort implementing full dark mode unless it is trivial.

The priority is one excellent light theme.

---

# 55. Visual quality bar

The target is closer to:

- Linear;
- Vercel dashboards;
- modern educational platforms;
- polished database SaaS tools;

than to:

- default Bootstrap;
- raw HTML form layouts;
- admin templates;
- VS Code clone styling.

Do not copy those products literally.

Use them as a standard for:

- spacing;
- visual hierarchy;
- polish;
- restraint.

---

# 56. Information hierarchy — priority order

When deciding what receives the strongest visual emphasis, use:

1. Challenge title
2. Exact task
3. SQL editor / Run
4. Feedback/results
5. Story context
6. Current chapter/progress
7. Hints
8. Schema
9. Technical/system metadata

This prevents developer information from dominating the learning flow.

---

# 57. Recommended component architecture

Names may differ in code, but visually the app should move toward components equivalent to:

```text
AppShell
├── ProductHeader
├── ChapterRail
├── ChallengeNavigator
│   ├── ChapterProgress
│   └── ChallengeList
├── LearningWorkspace
│   ├── ChallengeHeader
│   ├── ReviewBanner
│   ├── SituationCard
│   ├── TaskCard
│   ├── HintPanel
│   ├── SqlWorkspace
│   │   ├── EditorToolbar
│   │   └── SqlEditor
│   └── OutputWorkspace
│       ├── FeedbackPanel
│       ├── ResultTable
│       └── ChangePreview
└── DatabaseExplorer
    ├── SchemaSearch
    └── TableAccordion
```

This is a conceptual UX decomposition, not an instruction to rewrite working code unnecessarily.

---

# 58. Design tokens

Centralise visual values.

Prefer CSS variables such as:

```css
:root {
  --canvas: #F5F7FB;
  --surface: #FFFFFF;
  --text: #0F172A;
  --text-secondary: #475569;
  --border: #E2E8F0;

  --primary: #4F46E5;
  --primary-soft: #EEF2FF;

  --success: #15803D;
  --success-soft: #DCFCE7;

  --warning: #B45309;
  --warning-soft: #FEF3C7;

  --danger: #B91C1C;
  --danger-soft: #FEE2E2;

  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;

  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
}
```

Do not scatter dozens of arbitrary hex colours and spacing values through component files.

---

# 59. Use of gradients

Gradients may be used sparingly.

Good places:

- tiny product mark;
- chapter completion indicator;
- subtle header background;
- active progress line.

Bad places:

- every button;
- every card;
- large rainbow backgrounds;
- code editor.

The design should still look strong if gradients are removed.

---

# 60. Background treatment

The canvas should not be flat medium grey.

Use:

- very light blue/neutral background;
- white panels;
- optional extremely subtle radial/linear tint near the top of the workspace.

No distracting patterns behind code.

---

# 61. Challenge-state icons

Recommended:

| State | Icon idea |
|---|---|
| Completed | check-circle |
| Current | play-circle / filled dot |
| Locked | lock |
| Mutation | database/edit |
| Review | rotate/rewind |
| Hint | lightbulb |

State should still include accessible text/labels where necessary.

---

# 62. Database state as a learning asset

Where appropriate, add small copy such as:

> **Your Brightcart database**  
> Changes from completed mutation levels persist here.

This reinforces the core product concept.

Do not repeat this on every challenge.

The Database Explorer is a natural place for the message.

---

# 63. “Live database” visual language

Mutation success can include a short status:

```text
Database updated
```

Query levels can use:

```text
Read-only challenge
```

only where useful.

Avoid technical transaction language in ordinary learner UI.

---

# 64. Status persistence

After refreshing, the interface should visually restore:

- current progress;
- completed levels;
- active chapter;
- unlocked chapter;
- existing database state.

Avoid flashes where everything briefly looks locked/uncompleted if practical.

---

# 65. Tooltips

Use tooltips for secondary explanations:

- locked chapter requirement;
- primary/foreign key icons;
- Review mode icon;
- SQLite badge.

Do not hide essential instructions solely in tooltips.

---

# 66. Table rows and numeric data

For result tables:

- align numeric values right where sensible;
- textual values left;
- header text medium weight;
- use tabular numerals if supported;
- make NULL visibly distinct, e.g. muted italic `NULL`.

---

# 67. Long SQL and advanced chapters

By Chapters 4–5 SQL will become significantly longer.

The design must anticipate:

- 20–50+ lines of SQL;
- CTEs;
- window functions;
- larger result sets.

Do not design the editor around only Chapter 1 queries.

The workspace should remain comfortable when code becomes substantial.

---

# 68. Long task descriptions

Later business problems may need more context.

Story and task areas should:

- wrap cleanly;
- allow modest internal expansion;
- avoid forcing the editor below the fold unnecessarily.

If a task becomes long, use collapsible secondary context rather than shrinking text.

---

# 69. Chapter summaries

When entering a newly unlocked chapter, a short optional chapter intro may show:

- chapter name;
- story phase;
- what the learner is about to learn;
- 2–3 sentence context.

Keep it skippable/compact.

Do not block every visit with a modal.

---

# 70. First-time experience

For Level 1, the interface should feel immediately understandable without a tutorial overlay.

The visual structure itself should teach:

- left = levels;
- middle = task/workspace;
- right = database.

Avoid a multi-step product tour unless testing later proves it necessary.

---

# 71. Layout at the screenshot's approximate size

At roughly 1600×900:

- header ~56–64px;
- chapter rail ~52–60px;
- remaining viewport used by three-column shell;
- challenge list shows roughly half the chapter at once;
- Database Explorer visible;
- main workspace should show situation, task, and most/all SQL editor without browser-level scrolling;
- result panel should appear within the workspace rather than pushing the entire page downward.

This screen size should look excellent.

---

# 72. Do not waste horizontal space

The current main workspace has large regions of unused whitespace.

The redesigned application should use available width for:

- clearer story/task composition;
- editor;
- results;
- schema.

But do not make text lines excessively long.

Story/task text should have a reasonable maximum measure.

---

# 73. Visual consistency rules

All panels should agree on:

- border colour;
- radius family;
- headings;
- padding;
- icon style;
- hover states;
- focus rings.

Do not implement each component with its own unrelated aesthetic.

---

# 74. Interaction consistency rules

If clicking a challenge selects it:

- all selectable challenge rows should behave consistently.

If cards expand:

- all accordions should use the same chevron and transition.

If status chips exist:

- status wording/capitalisation should be consistent.

---

# 75. Copy tone

UI copy should be:

- concise;
- supportive;
- professional;
- direct.

Avoid:

- childish congratulations;
- overly enthusiastic exclamation marks;
- patronising language;
- developer jargon unless relevant to SQL learning.

Good:

> Challenge complete.

---

# 76. Mutation copy tone

Good:

> Saved to your Brightcart database.

Review mode:

> Practice attempt — changes were rolled back and not saved.

Failure:

> Your query changed 4 rows, but this task expects 1.

These messages reinforce the persistent-database model.

---

# 77. Chapter-specific accent application

Apply chapter colour to:

- chapter tab;
- challenge selected state;
- small progress indicator;
- Situation card accent;
- perhaps active editor top border.

Do not recolour:

- success;
- error;
- mutation;
- Review mode;

because those have semantic colours of their own.

---

# 78. Performance considerations

Visual polish must not make the app sluggish.

Avoid:

- large animation libraries for trivial transitions;
- giant image assets;
- expensive continuous effects;
- rerender-heavy schema visualisations.

Prefer CSS transitions and lightweight icons.

---

# 79. Implementation philosophy

When implementing this design:

1. preserve functionality;
2. establish tokens first;
3. establish shell/layout;
4. fix navigation/chapter scaling;
5. improve main workspace;
6. improve editor/output;
7. improve schema explorer;
8. polish interactions;
9. test responsiveness/accessibility.

Do not randomly restyle components one-by-one without first establishing the shell and design system.

---

# 80. Recommended implementation phases

## Phase 1 — Foundation

Implement:

- design tokens;
- typography;
- canvas/surface system;
- product header;
- viewport app shell;
- chapter progression rail.

## Phase 2 — Navigation

Implement:

- chapter gating UI;
- chapter tabs;
- 20-level-per-chapter navigator;
- challenge states;
- independent scrolling.

## Phase 3 — Learning workspace

Implement:

- improved challenge header;
- Situation card;
- Task card;
- concepts;
- hints;
- Review mode;
- mutation badge.

## Phase 4 — SQL workspace

Implement:

- editor toolbar;
- Run/Submit placement;
- keyboard shortcut;
- editor sizing/theme;
- output panel.

## Phase 5 — Results and mutations

Implement:

- polished ResultTable;
- feedback states;
- ChangePreview;
- completion/continue flow.

## Phase 6 — Database explorer

Implement:

- right-side panel;
- schema accordion;
- PK/FK/nullability/type styling;
- schema search;
- independent scrolling.

## Phase 7 — Polish

Implement:

- responsive behaviour;
- transitions;
- hover/focus states;
- system popover;
- reset flow;
- accessibility pass.

---

# 81. What should NOT change during the visual redesign

The redesign must not break or casually rewrite:

- FastAPI contracts unless necessary for visual metadata;
- SQL validation;
- learner-specific databases;
- mutation commit/rollback;
- review sandbox;
- reference-query secrecy;
- security authorizer;
- progress persistence;
- curriculum ordering;
- challenge answers;
- schema behaviour;
- replay tests.

If a visual requirement genuinely needs new API metadata, add the smallest clean addition.

---

# 82. What may change

It is acceptable to:

- reorganise React component structure;
- add presentation components;
- add CSS variables/tokens;
- change layout;
- change typography;
- move controls;
- add icons;
- add chapter navigation;
- add scroll containers;
- add schema search;
- add accessibility attributes;
- add small metadata fields needed for presentation;
- improve loading/error/empty states.

---

# 83. Automated UI testing expectations

Where existing frontend tests assert old layout text/structure, update them to reflect the new design.

Preserve behavioural tests.

Add coverage for:

- chapter tabs;
- locked chapters;
- chapter unlock behaviour;
- current challenge selection;
- challenge list scrolling structure where practical;
- story/task separation;
- schema explorer rendering;
- Review mode;
- mutation badge;
- result/feedback states;
- reset confirmation.

Do not write brittle tests that depend on exact pixel values.

---

# 84. Manual visual QA

After implementation, manually inspect at least:

- 1440×900 desktop;
- ~1280×800 laptop;
- ~1024px width;
- narrower/mobile layout.

Verify:

- no horizontal page overflow;
- no giant page-level vertical scroll on desktop;
- challenge list scroll works;
- schema scroll works;
- editor remains usable;
- result table scroll works;
- chapter rail remains legible;
- focus states visible;
- locked content understandable;
- colours readable.

---

# 85. Acceptance criteria — overall

The redesign is successful when:

1. A learner can identify their current chapter/level within 2 seconds.
2. The app visibly feels like one designed product rather than assembled components.
3. 100 challenges can be navigated without a single 100-item death-scroll list.
4. Only the current chapter's 20 levels need to occupy the challenge navigator.
5. Locked chapters are visible but inaccessible until prerequisite completion.
6. Challenges, schema, editor, and results use independent scroll regions where appropriate.
7. The Situation and Task are visually distinct.
8. The SQL editor feels like the primary work area.
9. Results never expand the browser page excessively.
10. The schema looks like a database explorer, not raw debug output.
11. Colour is purposeful and consistent.
12. Chapter identity is clear without overwhelming the interface.
13. Completed/open/locked/review/mutation/error states are visually distinct.
14. Reset and technical status no longer dominate the header.
15. The interface remains professional and comfortable for long sessions.
16. Existing learning/database behaviour still works.
17. The visual design scales to later, more complex SQL.
18. The app is meaningfully more attractive than the current prototype.

---

# 86. Acceptance criteria — chapter navigation

- Five chapters are always visible on desktop.
- Chapter 1 starts unlocked.
- Chapter N+1 unlocks only after all 20 challenges in Chapter N are complete.
- Locked chapters clearly communicate why they are locked.
- Selecting an unlocked chapter updates the challenge navigator to those 20 levels.
- Current chapter has strong selected styling.
- Completed chapters show completion clearly.
- Chapter progress displays `x/20`.
- The chapter rail does not become a multi-line visual mess at narrower widths.

---

# 87. Acceptance criteria — challenge navigation

- Challenge navigation has a fixed/constrained height.
- It scrolls independently.
- Current, completed, open, locked, mutation states are obvious.
- Rows remain compact.
- Active challenge has a strong but tasteful visual state.
- Completed challenges remain accessible for Review mode.
- Challenge navigation does not share its scroll with the schema.

---

# 88. Acceptance criteria — workspace

- Challenge title is prominent.
- Story has its own visual container.
- Exact task is visually separate.
- Concepts are visible but secondary.
- Hints are progressive and compact.
- Review mode is clear without dominating.
- Editor Run/Submit action is always easy to find.
- Feedback/results appear close to the editor.
- Long results remain inside a scrollable panel.

---

# 89. Acceptance criteria — schema explorer

- Dedicated panel on wide desktop.
- Tables collapse/expand.
- Search/filter available or straightforward to add.
- PK/FK/nullability/type are visually understandable.
- Internal `_app_*` tables remain hidden.
- Schema panel scrolls independently.
- Relationship information is readable.
- No full interactive ERD is required.

---

# 90. Acceptance criteria — visual polish

The final UI should not look like:

> “the same app with a new blue colour.”

The redesign should produce noticeable improvements in:

- layout;
- hierarchy;
- navigation;
- spacing;
- typography;
- colour;
- state communication;
- editor presentation;
- results;
- schema;
- progress;
- responsive behaviour.

---

# 91. Design decision priority

If two requirements conflict, prioritise:

1. correctness and safety;
2. curriculum behaviour;
3. clarity/usability;
4. accessibility;
5. visual hierarchy;
6. visual polish;
7. decorative effects.

Never sacrifice SQL correctness or learning clarity for aesthetics.

---

# 92. Source-of-truth rule

For any future Agent task:

- `docs/SQL_CURRICULUM.md` = **what learners experience and learn**
- `docs/UI_DESIGN_BRIEF.md` = **how the application presents that experience**

If a conflict is discovered between the two:

- do not silently resolve it;
- preserve curriculum correctness;
- report the conflict before making a product-level change.

---

# 93. Final design statement

Brightcart SQL Studio should ultimately feel like a place the learner **wants to spend time**.

They should be able to open it and immediately feel:

- where they are;
- what they are working on;
- how far they have progressed;
- how the Brightcart database is evolving;
- what they need to do next.

The interface should support the 100-level journey without becoming visually heavier as the curriculum grows.

The strongest version of this product is not merely a website that checks SQL answers.

It is a **beautiful, coherent data workspace in which the learner gradually becomes more capable while the company, database, story, and interface all reinforce that progression.**
