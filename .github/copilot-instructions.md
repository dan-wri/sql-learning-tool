For any work involving SQL challenges, curriculum design, challenge ordering, database evolution, story progression, schema changes, replay behaviour, learning progression, frontend presentation, UI/UX, visual styling, layout, navigation, responsiveness, or accessibility:

- Read `docs/SQL_CURRICULUM.md` before making any curriculum, challenge, database, progression, story, schema, or replay-related changes.
- Read `docs/UI_DESIGN_BRIEF.md` before making any frontend presentation, visual design, layout, navigation, styling, responsive, accessibility, editor, results, schema-explorer, or interaction-design changes.

## Sources of truth

- `docs/SQL_CURRICULUM.md` is the source of truth for **what the learner experiences and learns**, including:
  - the 100-level curriculum
  - challenge ordering
  - SQL concept progression
  - story continuity
  - chapter pacing
  - database evolution
  - mutation dependencies
  - determinism
  - replay behaviour
  - schema assumptions
  - learning progression

- `docs/UI_DESIGN_BRIEF.md` is the source of truth for **how the application presents that experience**, including:
  - visual identity
  - colour and typography
  - application layout
  - chapter navigation
  - challenge navigation
  - scroll behaviour
  - story/task presentation
  - SQL editor presentation
  - results and feedback
  - ChangePreview
  - Database Explorer
  - responsive behaviour
  - accessibility
  - visual polish

## General rules

- Preserve the curriculum's story continuity, concept progression, mutation dependencies, determinism rules and chapter pacing.
- Preserve the UI brief's visual hierarchy, navigation model, design system and interaction principles.
- Do not independently invent a conflicting curriculum or visual direction.
- Do not alter working SQL/database behaviour purely to simplify a UI implementation.
- Do not alter curriculum content purely to fit a visual design.
- Prefer extending existing working architecture over unnecessary rewrites.
- Preserve security, validation, replay, persistence and reference-solution secrecy.

## Conflicts

If implementation reveals a genuine conflict:

1. correctness and safety take priority;
2. `docs/SQL_CURRICULUM.md` determines curriculum/learning behaviour;
3. `docs/UI_DESIGN_BRIEF.md` determines presentation/UX behaviour;
4. report any unresolved product-level conflict before changing either source-of-truth document.

Do not silently change either design document to accommodate implementation difficulties.