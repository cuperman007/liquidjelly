CREATE TABLE enquiries (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
  name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 100),
  email TEXT NOT NULL CHECK(length(email) <= 254),
  company TEXT NOT NULL DEFAULT '' CHECK(length(company) <= 150),
  interest TEXT NOT NULL,
  message TEXT NOT NULL CHECK(length(message) BETWEEN 20 AND 5000)
);
CREATE INDEX enquiries_created_at ON enquiries(created_at);
