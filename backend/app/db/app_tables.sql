-- Internal tables. Learner SQL must never read or write anything prefixed _app_.

CREATE TABLE _app_meta (
    key    TEXT PRIMARY KEY,
    value  TEXT NOT NULL
);

CREATE TABLE _app_progress (
    challenge_id  TEXT PRIMARY KEY,
    completed_at  TEXT NOT NULL
);

CREATE TABLE _app_hints (
    challenge_id    TEXT PRIMARY KEY,
    hints_revealed  INTEGER NOT NULL DEFAULT 0 CHECK (hints_revealed >= 0)
);
