# YardMap · Decision Record

Each entry states what was decided, why, and what it costs.
Status is `accepted` unless a later entry supersedes it.

---

## 1 · One yard, internal operations only

Status: accepted

Context: a yard-management system can grow without limit — multiple sites,
customer-facing booking, customs paperwork, equipment control.

Decision: scope is a single yard and the staff who work it. Deliberately out:
payments, GPS/IoT tracking, crane and equipment management, customs and
shipping-line integrations, multi-move route optimisation and re-shuffling,
notifications, multiple yards, customer-facing booking, and a live-updating
yard map.

Consequence: every one of those is a named exclusion rather than an oversight.
Re-admitting any of them changes the data model, not just the API.

---

## 2 · One repository, two subfolders

Status: accepted

Context: the backend and the frontend are built by the same person, in step,
and share one set of decisions.

Decision: a single repository with `backend/` and `frontend/` beside each
other. Backend commands run from `backend/`, not from the repository root.

Consequence: one history, one issue list, one `.gitignore`. The cost is that
the two halves cannot be deployed from separate repositories without a split
later.

---

## 3 · Appointments reserve a slot for a time window

Status: accepted

Context: an appointment recorded as a single arrival time cannot be checked
for conflicts — two vehicles arriving twenty minutes apart may still need the
same slot at the same moment.

Decision: an appointment holds a yard slot for a window, with a start and an
end.

Consequence: overlap is now a real condition the database must enforce, not a
convention the application hopes to follow.

---

## 4 · Four roles, one of them external

Status: accepted

Context: hauliers need to see their own containers without seeing the yard.

Decision: four roles. Three are internal staff roles with write access. The
fourth, `haulier`, is external and read-only, and sees only its own
containers, appointments and movements.

Consequence: every read endpoint needs a role check *and* an ownership check.
A role check alone would let one haulier read another's records.

---

## 5 · Hauliers read; staff write

Status: accepted

Context: letting an external party schedule its own arrival puts yard capacity
in the hands of someone who cannot see the yard.

Decision: hauliers cannot create appointments, register containers, or see the
yard map. Staff do all writing on their behalf.

Consequence: the haulier role needs no write endpoints at all, which removes a
whole class of authorisation bug.

---

## 6 · Sign-up, email verification and password reset are out of scope

Status: accepted

Context: accounts have to exist before anyone signs in.

Decision: users are created by an administrator. There is no self-registration,
no email verification, and no password-reset flow.

Consequence: no mail sending, no token-expiry logic, no rate limiting on
public endpoints. Sign-in is the only unauthenticated route.

---

## 7 · Slot suggestion is one rule, computed on the server

Status: accepted

Context: picking the best free slot for an arriving container could be an
optimisation problem of any size.

Decision: a single, stated rule, applied server-side, returning one suggestion.
No re-shuffling of what is already placed, and no multi-move planning.

Consequence: the answer is explainable and testable. It is not optimal, and the
rule is a line the code can point at.

---

## 8 · Reports are requested, then collected

Status: accepted

Context: a yard-activity report over a long date range cannot be produced
inside the time a request is allowed to take.

Decision: asking for a report creates a report job and returns its identifier
immediately. The caller collects the result later by that identifier. The work
itself runs in a separate worker process, which is not part of this service.

Consequence: report jobs are a stored kind of thing with a state of their own,
and a job can be pending when it is asked for. The worker is not yet
implemented.

---

## 9 · PATCH, not PUT

Status: accepted

Context: changing one field should not require sending every field.

Decision: partial updates use `PATCH`. A request body carries only the fields
being changed, and unknown fields are rejected outright rather than ignored.

Consequence: a typo in a field name is an error the caller sees, not a silent
no-op.

---

## 10 · The data layer does not speak HTTP

Status: accepted

Context: a data-access function that raises an HTTP error cannot be reused
outside a request.

Decision: the data-access layer returns values or `None`. Translating a missing
row into a status code is the HTTP layer's job.

Consequence: data-access functions are callable from the worker process and
from tests without a request in sight.

---

## 11 · Dependencies are pinned exactly

Status: accepted

Context: a version range means the environment that passes today can differ
from the one that runs tomorrow.

Decision: every dependency is pinned to an exact version.

Consequence: upgrades are deliberate and visible in the history. The cost is
that security updates must be taken by hand.

---

## 12 · Configuration comes from the environment

Status: accepted

Context: a connection string in the source is a connection string in the
history, for ever.

Decision: all configuration is read from environment variables. A committed
example file lists every variable by name with no real values. The real file
is never committed.

Consequence: a leaked credential is rotated, not retracted — and the example
file is the one place that records what the service needs to run.

## 13 · Yard zone names are unique

Status: accepted

Context: zones were planned with a name and no uniqueness rule. A seed file
run twice silently created a second "Zone A" and a second "Zone B", and
nothing could tell the two apart.

Decision: the database enforces one zone per name (yard_zones_name_key).

Consequence: re-running the seed file fails loudly instead of doubling the
zones, until step 17 makes the seed file safe to re-run.