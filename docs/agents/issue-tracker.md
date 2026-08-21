# Issue Tracker: Local Markdown

Issues live as files under `.scratch/` in this repo. There is no remote issue
tracker (GitHub CLI unavailable), so all issue operations are file reads/writes.

## Layout

```
.scratch/
├── 001-<slug>/           # one directory per issue
│   ├── issue.md          # title, labels, status, body
│   └── comments/         # 001-*.md, 002-*.md, ... appended in order
└── 002-<slug>/
    └── ...
```

The numeric prefix is the issue id, assigned in creation order (scan `.scratch/`
for the current max, increment). The slug is a short kebab-case title.

## `issue.md` format

```markdown
# <title>

- Labels: <comma-separated>
- Status: open | closed
- Assignee: <name | none>
- Blocked-by: <comma-separated issue ids, or empty>
- Parent: <issue id of parent, or empty>

<body>
```

Edit `Status` to `closed` to close. Append comments as new numbered files in
`comments/`.

## Wayfinding operations

This tracker expresses wayfinder's operations as follows:

- **Map**: an issue labelled `wayfinder:map` (`.scratch/001-leftover-bureau-map/issue.md`).
  Its body follows the wayfinder map template (Destination / Notes / Decisions so
  far / Not yet specified / Out of scope). Child tickets set `Parent: 1`.
- **Claim a ticket**: set `Assignee` in `issue.md` to the dev driving the map
  before any work.
- **Blocking**: `Blocked-by` field in `issue.md` lists blocking issue ids. A
  ticket is unblocked when every id in its `Blocked-by` is closed.
- **Frontier**: open, unblocked, `Assignee: none` children of the map. Find via:
  `grep -L "Status: closed" .scratch/*/issue.md` then filter by Parent/Blocked-by/Assignee.
- **Resolve a ticket**: append a `00N-resolution.md` comment with the answer,
  set `Status: closed`, then append one line to the map's "Decisions so far".
- **Map as index**: decisions live in their ticket (the resolution comment);
  the map only gists + links each ticket by title.
