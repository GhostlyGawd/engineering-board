# Board Entry Frontmatter Schema

## Common Fields (all types)

| Field | Required | Values | Notes |
|---|---|---|---|
| `id` | Yes | B###, F###, Q###, O### | Zero-padded 3 digits |
| `type` | Yes | `bug`, `feature`, `question`, `observation` | Lowercase |
| `status` | Yes (except observations) | `open`, `blocked`, `in_progress`, `resolved` | |
| `title` | Yes | Short string | Present-tense for bugs/features; interrogative for questions |
| `discovered` | Yes | `YYYY-MM-DD` | Date first observed |

## Bug / Feature Additional Fields

| Field | Required | Values | Notes |
|---|---|---|---|
| `priority` | Yes | `P0`, `P1`, `P2`, `P3` | P0 = production down/data loss; P1 = broken output delivered; P2 = quality degraded; P3 = minor/cosmetic |
| `affects` | Yes | Relative file path | The prompt, script, or module where the fix lands |
| `blocked_by` | Conditional | `[Q###]` or `[Q###, Q###]` | Required when a question must be answered before this can be fixed |
| `pattern` | No | `[tag1, tag2]` | Root cause pattern tags — free-form kebab-case strings encoding the failure mode (not the product area). Multiple tags per entry. Examples: `instruction-ambiguity`, `yaml-output`, `token-limit-scaling`, `silent-failure`. Used for systemic issue detection across entries. Apply to **all entry types**: bugs and features always; observations when the failure area is identifiable; questions when the investigation area is clear (even before the Finding is written). |

## Question Additional Fields

| Field | Required | Values | Notes |
|---|---|---|---|
| `source` | No | Free text | What surfaced this question (e.g. "B002 fix direction 3") |
| `affects` | No | Relative file path | Component the answer will inform |

## Observation Fields

Observations have no `status`, `priority`, `affects`, or `blocked_by`. They are run logs.

| Field | Required | Notes |
|---|---|---|
| `id` | Yes | O### |
| `type` | Yes | `observation` |
| `title` | Yes | Format: `YYYY-MM-DD ASIN — brief summary` |
| `discovered` | Yes | Date of run |

## Priority Definitions

| Level | Meaning |
|---|---|
| P0 | Production down, data loss, or a delivered output is completely missing |
| P1 | Broken output delivered to client — wrong content, wrong format, critical field absent |
| P2 | Output delivered but quality degraded — content present but suboptimal |
| P3 | Minor or cosmetic — barely noticeable, no client impact |

## Status Transitions

```
open → in_progress → resolved
open → blocked (when blocked_by set)
blocked → open (when all blocking questions resolved)
```

Only one item should be `in_progress` per session.

## Required Body Sections by Type

### Bug
- `## Done when` — **required** — exact verification criteria
- `## Observed behavior` — recommended
- `## Root cause hypothesis` — recommended
- `## Fix direction` — recommended

### Feature
- `## Done when` — **required**
- `## Motivation` — recommended

### Question
- `## Done when` — **required** — the binary answer or code location that closes this question
- `## Why it matters` — recommended
- `## Where to look` — recommended
- `## Finding` — written when resolving (before status change)

### Observation
- No `## Done when` required
- Document run date, ASIN(s), what happened, what was notable
