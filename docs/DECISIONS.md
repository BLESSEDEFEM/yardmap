# YardMap · Decision Record

Each entry states what was decided, what was rejected, why, and what it costs.
Status is `accepted` unless a later entry supersedes it.
Entries are numbered in the order they were written down, and never renumbered.
The index below groups them by area.

---

## Index, by area

| Area           | #   | Decision                                                              |
| -------------- | --- | --------------------------------------------------------------------- |
| Scope          | 1   | One yard, internal operations only                                    |
| Scope          | 3   | Appointments reserve a slot for a time window                         |
| Scope          | 4   | Four roles, one of them external                                      |
| Scope          | 5   | Hauliers read; staff write                                            |
| Scope          | 6   | Sign-up, email verification and password reset are out of scope       |
| Scope          | 16  | Nine features, fourteen things left out on purpose                    |
| API            | 7   | Slot suggestion is one rule, computed on the server                   |
| API            | 8   | Reports are requested, then collected                                 |
| API            | 9   | PATCH, not PUT                                                        |
| API            | 17  | Check-in and check-out are two addresses                              |
| API            | 18  | A report is collected through an ordinary read                        |
| API            | 19  | One address both suggests a slot and places into it                   |
| API            | 20  | A haulier asking about another haulier's container gets 404, not 403  |
| API            | 31  | The API contract is written before the code                           |
| API            | 32  | The contract says plainly that reports do not finish yet              |
| Data model     | 13  | Yard zone names are unique                                            |
| Data model     | 14  | Yard slot labels are unique within a zone                             |
| Data model     | 21  | Rows are numbered; a report job also gets an unguessable id           |
| Data model     | 22  | Three tables mark rows as gone; four never delete                     |
| Data model     | 23  | Yard zones and yard slots are two tables                              |
| Data model     | 24  | The database refuses every delete of a row something points at        |
| Data model     | 25  | One slot holds at most one vehicle/container                          |
| Data model     | 39  | The type annotation alone decides whether a column may be empty       |
| Data model     | 40  | One live report per person and date range                             |
| Code structure | 10  | The data layer does not speak HTTP                                    |
| Code structure | 26  | Files are split by layer first, then by the thing they are about      |
| Code structure | 27  | The slot suggestion has a file of its own, in no layer                |
| Code structure | 28  | Everything that runs sits under `app/`                                |
| Repository     | 2   | One repository, two subfolders                                        |
| Dependencies   | 11  | Dependencies are pinned exactly                                       |
| Dependencies   | 29  | Ten libraries, each one with a reason                                 |
| Dependencies   | 30  | bcrypt is used directly, not through passlib                          |
| Dependencies   | 33  | `requirements.txt` lists only what I asked for                        |
| Configuration  | 12  | Configuration comes from the environment                              |
| Configuration  | 34  | `DEBUG` never switches on the framework's detailed error page         |
| Configuration  | 35  | Secret settings are plain strings                                     |
| Database       | 36  | The app connects as its own database user, not the superuser          |
| Database       | 37  | PostgreSQL is installed on my machine                                 |
| Database       | 38  | Objects stay readable after a commit (`expire_on_commit=False`)       |
| Database       | 41  | Every change to the tables' shape is a migration, read before it runs |
| Seed data      | 15  | Starting rows come from a seed file that is safe to run again         |
| Queries        | 42  | Only the lists that can grow are limited                              |

---

## 1 · One yard, internal operations only

Area: Scope
Status: accepted

Context: a yard-management system can grow without limit — multiple sites,
customer-facing booking, customs paperwork, equipment control.

Decision: scope is a single yard and the staff who work it. Deliberately out:
payments, GPS/IoT tracking, crane and equipment management, customs and
shipping-line integrations, multi-move route optimisation and re-shuffling,
notifications, multiple yards, customer-facing booking, and a live-updating
yard map.

Rejected: a general yard platform covering several yards, outside customers
and outside systems.

Consequence: every one of those is a named exclusion rather than an oversight.
Re-admitting any of them changes the data model, not just the API.

---

## 2 · One repository, two subfolders

Area: Repository
Status: accepted

Context: the backend and the frontend are built by the same person, in step,
and share one set of decisions.

Decision: a single repository with `backend/` and `frontend/` beside each
other. Backend commands run from `backend/`, not from the repository root.

Rejected: one repository for the backend and another for the frontend.

Consequence: one history, one issue list, one `.gitignore`. The cost is that
the two halves cannot be deployed from separate repositories without a split
later.

Revisit if: the two halves are ever owned by different people, or deployed on
different schedules.

---

## 3 · Appointments reserve a slot for a time window

Area: Scope
Status: accepted

Context: an appointment recorded as a single arrival time cannot be checked
for conflicts — two vehicles arriving twenty minutes apart may still need the
same slot at the same moment.

Decision: an appointment holds a yard slot for a window, with a start and an
end.

Rejected: an appointment as a single arrival time.

Consequence: overlap is now a real condition the database must enforce, not a
convention the application hopes to follow.

---

## 4 · Four roles, one of them external

Area: Scope
Status: accepted

Context: hauliers need to see their own containers without seeing the yard.

Decision: four roles. Three are internal staff roles with write access. The
fourth, `haulier`, is external and read-only, and sees only its own
containers, appointments and movements.

Rejected: leaving hauliers outside the system, or letting them see the whole
yard.

Consequence: every read endpoint needs a role check *and* an ownership check.
A role check alone would let one haulier read another's records.

---

## 5 · Hauliers read; staff write

Area: Scope
Status: accepted

Context: letting an external party schedule its own arrival puts yard capacity
in the hands of someone who cannot see the yard.

Decision: hauliers cannot create appointments, register containers, or see the
yard map. Staff do all writing on their behalf.

Rejected: hauliers booking their own arrivals and registering their own
containers.

Consequence: the haulier role needs no write endpoints at all, which removes a
whole class of authorisation bug.

---

## 6 · Sign-up, email verification and password reset are out of scope

Area: Scope
Status: accepted

Context: accounts have to exist before anyone signs in.

Decision: users are created by an administrator. There is no self-registration,
no email verification, and no password-reset flow.

Rejected: self-registration with email verification and a reset flow.

Consequence: no mail sending, no token-expiry logic, no rate limiting on
public endpoints. Sign-in is the only unauthenticated route.

---

## 7 · Slot suggestion is one rule, computed on the server

Area: API
Status: accepted

Context: picking the best free slot for an arriving container could be an
optimisation problem of any size.

Decision: a single, stated rule, applied server-side, returning one suggestion.
No re-shuffling of what is already placed, and no multi-move planning.

Rejected: an optimiser that re-shuffles placed containers or plans several
moves at once.

Consequence: the answer is explainable and testable. It is not optimal, and the
rule is a line the code can point at.

---

## 8 · Reports are requested, then collected

Area: API
Status: accepted

Context: a yard-activity report over a long date range cannot be produced
inside the time a request is allowed to take.

Decision: asking for a report creates a report job and returns its identifier
immediately (`202 Accepted`). The caller collects the result later by that
identifier. The work itself runs in a separate worker process, which is not
part of this service.

Rejected: holding the request open while the report is built.

Consequence: report jobs are a stored kind of thing with a state of their own,
and a job can be pending when it is asked for. The worker is not yet
implemented.

---

## 9 · PATCH, not PUT

Area: API
Status: accepted

Context: changing one field should not require sending every field.

Decision: partial updates use `PATCH`. A request body carries only the fields
being changed, and unknown fields are rejected outright rather than ignored.

Rejected: `PUT`, which replaces the whole record.

Consequence: a typo in a field name is an error the caller sees, not a silent
no-op.

---

## 10 · The data layer does not speak HTTP

Area: Code structure
Status: accepted

Context: a data-access function that raises an HTTP error cannot be reused
outside a request.

Decision: the data-access layer returns values or `None`. Translating a missing
row into a status code is the HTTP layer's job.

Rejected: raising HTTP errors inside data-access functions.

Consequence: data-access functions are callable from the worker process and
from tests without a request in sight.

---

## 11 · Dependencies are pinned exactly

Area: Dependencies
Status: accepted

Context: a version range means the environment that passes today can differ
from the one that runs tomorrow.

Decision: every dependency is pinned to an exact version.

Rejected: version ranges.

Consequence: upgrades are deliberate and visible in the history. The cost is
that security updates must be taken by hand.

---

## 12 · Configuration comes from the environment

Area: Configuration
Status: accepted

Context: a connection string in the source is a connection string in the
history, for ever.

Decision: all configuration is read from environment variables. A committed
example file lists every variable by name with no real values. The real file
is never committed.

Rejected: values written into the source code.

Consequence: a leaked credential is rotated, not retracted — and the example
file is the one place that records what the service needs to run.

---

## 13 · Yard zone names are unique

Area: Data model
Status: accepted

Context: zones were planned with a name and no uniqueness rule. A seed file
run twice silently created a second "Zone A" and a second "Zone B", and
nothing could tell the two apart.

Decision: the database enforces one zone per name (`yard_zones_name_key`).

Rejected: no rule, or checking for duplicates in code only.

Consequence: re-running the seed file fails loudly instead of doubling the
zones, until the seed file was made safe to re-run (entry 15).

---

## 14 · Yard slot labels are unique within a zone

Area: Data model
Status: accepted

Context: slots had a label and no uniqueness rule. Two slots called "A1" could
exist in the same zone, staff could not tell them apart, and looking a slot up
by its label crashed with `MultipleResultsFound` once two shared one.

Decision: the database enforces one label per zone
(`yard_slots_zone_id_label_key`, on `zone_id` and `label` together). "A1" in
Zone A and "A1" in Zone B are both allowed.

Rejected: no rule, or a label unique across the whole yard.

Consequence: a slot is identified by its zone and label together, never by
the label alone.

---

## 15 · Starting rows come from a seed file that is safe to run again

Area: Seed data
Status: accepted

Context: an empty database cannot be checked or demonstrated, and the
development database is wiped often. The starting rows are a handful of
reference rows (zones and slots) that anyone should be able to read.

Decision: a Python module, `app/seed.py`, run with `python -m app.seed`. Each
row is looked up by a unique column and added only if it is missing
(get-or-create). `--wipe` empties the seeded tables by name, never with
`CASCADE`, then refills them.

Rejected: `INSERT ... ON CONFLICT DO NOTHING`, wipe-then-insert, and putting
the rows in a data migration.

Consequence: running the seed any number of times leaves the same rows, so
the loud failure on a second run described in entry 13 no longer happens.
The costs: one lookup per row, and an existing row is never updated from the
file. Users are not seeded until password hashing exists.

Revisit if: the seed grows to thousands of rows (then `ON CONFLICT`), or the
file must stay the single source of truth for those rows (then an upsert).

---

## 16 · Nine features, fourteen things left out on purpose

Area: Scope
Status: accepted

Context: a project this size stays buildable and explainable at five to nine
things a person can do.

Decision: nine features. Fourteen things a reasonable person might expect are
written down as left out, each with its reason (entry 1 lists the largest).

Rejected: a longer feature list.

Consequence: "why doesn't it do X?" has a written answer. Every later table
is sized by these nine.

---

## 17 · Check-in and check-out are two addresses

Area: API
Status: accepted

Context: arriving at the gate and leaving it fail in different ways:
check-in fails with "already checked in", check-out with "not currently
checked in".

Decision: `POST /vehicles-containers/{id}/check-ins` and
`POST /vehicles-containers/{id}/check-outs`.

Rejected: one gate address that works out from the body which direction is
meant.

Consequence: one extra address and two code paths, but each address has one
failure list and one meaning.

Revisit if: a third gate direction appears, or the two failure lists
converge.

---

## 18 · A report is collected through an ordinary read

Area: API
Status: accepted

Context: a `202 Accepted` with no way to come back and ask is a dead end.

Decision: `GET /activity-reports/{report_job_id}` reads the stored job row
and sends it. Reading the row about the job finishes when the reply leaves,
so it is an ordinary read.

Rejected: no collect address at all, or delivering the report some other way.

Consequence: one more address, and a polling pattern the caller must follow
(every 5 seconds while the job is queued or running).

Revisit if: the report ever needs to be pushed to the manager instead of
collected.

---

## 19 · One address both suggests a slot and places into it

Area: API
Status: accepted

Context: with one address to ask "which slot?" and another to place, two
operators can both be told slot A3 and both place there. Both were told the
truth, and the yard is wrong.

Decision: one `POST /vehicles-containers/{id}/movements`, where `to_slot_id`
may be left out; the server then picks the best free slot and uses it in the
same request.

Rejected: two addresses, one to suggest and one to place.

Consequence: the reply must say which slot was used and whether the server
chose it (`slot_was_suggested`). Splitting it later would bring the race back.

Revisit if: an operator needs to compare several candidate slots before
choosing — and even then the read for comparing slots is `GET /slots`, not a split of
this address.

---

## 20 · A haulier asking about another haulier's container gets 404, not 403

Area: API
Status: accepted

Context: a `403 Forbidden` confirms the container exists, which tells one
haulier something about another haulier's business.

Decision: `GET /movements` answers `404 Not Found` when a haulier names a
container that is not its own.

Rejected: `403 Forbidden`.

Consequence: the status looks wrong at first sight, so the reason is written
beside it in the contract, or it gets reported as a bug.

---

## 21 · Rows are numbered; a report job also gets an unguessable id

Area: Data model
Status: accepted

Context: no table is reached by an identifier a caller could change to see
someone else's rows — except a report job, whose id the caller is given and
types back.

Decision: every table is identified by a counted-up number. `report_jobs`
also carries `public_id`, a uuid, and that is the only id a caller ever sees
for a report.

Rejected: uuids for every table.

Consequence: a caller can roughly count containers from an id in a reply.
Nothing commercial leaks, because writes are staff-only.

Revisit if: an address is added that takes a row's own id and returns
something private; that table then gets an unguessable id too.

---

## 22 · Three tables mark rows as gone; four never delete

Area: Data model
Status: accepted

Context: something points at every table. Removing a row would orphan its
history, and the history is a feature.

Decision: `users`, `vehicles_containers` and `yard_slots` mark a row as gone
with `deleted_at`. `yard_zones`, `appointments`, `movements` and
`report_jobs` are never deleted.

Rejected: removing rows.

Consequence: every query against the three marked tables must leave out
marked rows, for ever. One forgotten filter shows a deleted container as
live, with no error anywhere.

---

## 23 · Yard zones and yard slots are two tables

Area: Data model
Status: accepted

Context: the first plan counted "zones and slots" as one kind of thing.

Decision: `yard_zones` and `yard_slots`, with each slot pointing at its zone.

Rejected: one table for both.

Consequence: a zone and a slot are different things, and one row cannot be
both. One more table to join.

---

## 24 · The database refuses every delete of a row something points at

Area: Data model
Status: accepted

Context: entry 22 means no row is ever really removed, so the question
"what happens to the rows pointing at it?" cannot arise in normal use.

Decision: all thirteen connections are written as `ON DELETE RESTRICT`.

Rejected: deleting the pointing rows too (`CASCADE`), or leaving them
pointing at nothing (`SET NULL`).

Consequence: if a delete ever happens by mistake, the database refuses it
instead of silently removing history.

---

## 25 · One slot holds at most one vehicle/container

Area: Data model
Status: accepted

Context: two containers in one slot is a real-world impossibility the data
must never show.

Decision: `vehicles_containers.current_slot_id` is unique. Many rows may be
in no slot at once, because PostgreSQL does not treat two empty values as
equal.

Rejected: checking in code before placing.

Consequence: the database makes "two containers in one slot" impossible,
even when two operators place at the same moment. It arrives as
`vehicles_containers_current_slot_id_key`, which the address turns into
`409 slot_occupied`.

---

## 26 · Files are split by layer first, then by the thing they are about

Area: Code structure
Status: accepted

Context: six of the database questions are needed by two or more addresses.
Written inside the address files, they would be copied many times, and the
copies would drift.

Decision: one layer per job — addresses, shapes, database questions, tables,
settings, the session — and within a layer, one file per kind of thing.

Rejected: fewer files with more in each, or more files with less.

Consequence: about 28 files for 14 addresses, so following one request means
opening several.

Revisit if: the project stays at one address per thing, where the
duplication never happens.

---

## 27 · The slot suggestion has a file of its own, in no layer

Area: Code structure
Status: accepted

Context: the suggestion rule is not an address, a shape, a database question,
a table, a setting or the session.

Decision: `app/slot_suggestion.py`, at the top of `app/`.

Rejected: putting the rule inside the address file or the questions file.

Consequence: the rule can be read and tested on its own.

Revisit if: a second rule of this sort appears; both then move into a folder.

---

## 28 · Everything that runs sits under `app/`

Area: Code structure
Status: accepted

Context: when the project is packaged for a server, something must say which
files are the project.

Decision: everything that runs is under `app/`, with a folder per layer that
has two or more files.

Rejected: everything at the project's top, or a folder named after the
project.

Consequence: "which files are my project" is one word, not a hand-kept list.
Every import names the folder, so moving it later means editing every file.

---

## 29 · Ten libraries, each one with a reason

Area: Dependencies
Status: accepted

Context: each library replaces work that would otherwise be written by hand.
Three replace weeks of work, and two replace work that should never be
written by hand at all (password hashing and token signing).

Decision: fastapi · uvicorn · sqlalchemy · psycopg · alembic ·
pydantic-settings · pytest · httpx · bcrypt · PyJWT. pytest and httpx are
needed only while building.

Rejected: writing what each replaces, and adding anything I could not explain.

Consequence: ten pieces of somebody else's work to depend on, which is why
every version is written down (entry 11).

---

## 30 · bcrypt is used directly, not through passlib

Area: Dependencies
Status: accepted

Context: run together with current bcrypt, passlib fails on hashing:
`AttributeError: module 'bcrypt' has no attribute '__about__'`. passlib's
last release was in 2020.

Decision: bcrypt's own functions, called directly.

Rejected: passlib with bcrypt, which most guides recommend.

Consequence: two functions in one file instead of one wrapper call, and no
built-in way to move to a second hashing algorithm.

Revisit if: passlib ships a release that works with current bcrypt.

---

## 31 · The API contract is written before the code

Area: API
Status: accepted

Context: the other half of the project cannot be built against nothing.

Decision: `docs/API-CONTRACT.md`, issued before anything answers, with every
line marked `PLANNED` or `LIVE`.

Rejected: waiting until the addresses answer, explaining it in conversation,
or pointing the other half at the code.

Consequence: every line that becomes `LIVE` must be watched answering, and a
change to a `LIVE` line needs a date and a reason.

---

## 32 · The contract says plainly that reports do not finish yet

Area: API
Status: accepted

Context: `202 Accepted` reads as "it worked" to anybody who has not met it.

Decision: the contract states that the worker does not exist yet, so every
report job stays `queued`, and that this is expected.

Rejected: listing the report address like the others and leaving the reader
to find out.

Consequence: the frontend can build its polling against real states without
mistaking "never finishes" for a bug.

---

## 33 · `requirements.txt` lists only what I asked for

Area: Dependencies
Status: accepted

Context: the ten libraries bring many more packages with them.

Decision: `requirements.txt` holds the ten, written by hand, each pinned.

Rejected: the full `pip freeze` output.

Consequence: the file shows what the project chose. It must be kept current
by hand.

Revisit if: a byte-identical environment is needed on another machine, which
is what the frozen list is for.

---

## 34 · `DEBUG` never switches on the framework's detailed error page

Area: Configuration
Status: accepted

Context: measured: the detailed error page was 5,550 bytes and carried a
password; the plain one was 21 bytes.

Decision: the `DEBUG` setting is not wired to FastAPI's debug mode.

Rejected: wiring `DEBUG` to the framework's debug mode, as most examples do.

Consequence: no detailed error page while developing; errors are read in the
terminal instead.

Revisit if: there is a way to show the detailed page only on my own machine
and never anywhere else.

---

## 35 · Secret settings are plain strings

Area: Configuration
Status: accepted

Context: pydantic-settings can wrap a secret (`SecretStr`) so that printing
the settings shows `**********`.

Decision: `database_url` and `secret_key` are plain `str`.

Rejected: `SecretStr`.

Consequence: one less thing to unwrap wherever the values are used. Printing
the settings object prints the secrets.

Revisit if: I ever find myself printing the settings object while debugging.

---

## 36 · The app connects as its own database user, not the superuser

Area: Database
Status: accepted

Context: the superuser can do anything on the database server, including
dropping other databases.

Decision: a project user, `yardmap_app`, owns the `yardmap` database and
cannot create databases.

Rejected: connecting as the superuser, which would also have worked.

Consequence: a mistake in my code cannot reach anything outside my own
database. Creating a database (for example the practice copy) needs the
`postgres` account.

---

## 37 · PostgreSQL is installed on my machine

Area: Database
Status: accepted

Context: while learning to read the database's errors, the fewer programs
between me and the database, the better.

Decision: PostgreSQL 16, installed directly on my machine.

Rejected: running it in a container.

Consequence: PostgreSQL starts with the machine. The choice is local only:
the deployed database will run somewhere else.

Revisit if: two projects need different PostgreSQL versions at once.

---

## 38 · Objects stay readable after a commit (`expire_on_commit=False`)

Area: Database
Status: accepted

Context: by default, a commit clears every object's values, and reading one
afterwards asks the database again, or fails once the session is closed.

Decision: `SessionLocal` is built with `expire_on_commit=False`.

Rejected: the default, converting each object into a plain shape before the
session closes.

Consequence: an object can show a value that is out of date, and nothing
warns.

Revisit if: response schemas are in place, which may make the setting
unnecessary.

---

## 39 · The type annotation alone decides whether a column may be empty

Area: Data model
Status: accepted

Context: with both a `nullable=` argument and an annotation present, the
argument wins and the annotation is ignored. Two places that can disagree
will one day disagree.

Decision: `Mapped[str]` means required and `Mapped[str | None]` means may be
empty. No `nullable=` anywhere. Types are written out (`Text`,
`DateTime(timezone=True)`), so every moment in time carries its time zone.

Rejected: the `nullable=` argument, and bare `mapped_column()`.

Consequence: `Text` and `DateTime(timezone=True)` are typed by hand on every
such column.

---

## 40 · One live report per person and date range

Area: Data model
Status: accepted

Context: a double-click on "ask for a report" would queue the same report
twice.

Decision: a partial unique index, `one_live_report_per_request`, on
(`requested_by`, `from_date`, `to_date`) where the state is `queued` or
`running`.

Rejected: a plain unique rule, which would refuse the same report ever being
asked for again, and a check in code, which two clicks can both pass.

Consequence: the second identical request is refused by the database, and
the contract turns it into a `409`. The index is PostgreSQL-specific.

---

## 41 · Every change to the tables' shape is a migration, read before it runs

Area: Database
Status: accepted

Context: the migration generator can guess wrong (a rename read as a drop
and an add) and still report success.

Decision: Alembic generates each migration from the models; every generated
file is read before it runs, and every constraint is given its name in the
model, so the name travels into the migration. Three so far: the seven
tables, unique zone names, unique slot labels within a zone.

Rejected: changing tables by hand, and running generated files unread.

Consequence: the database's shape has a history that any copy can be brought
up to with one command (`alembic upgrade head`).

---

## 42 · Only the lists that can grow are limited

Area: Queries
Status: accepted

Context: `vehicles_containers` grows every day. A yard has a fixed number of
slots, and the map needs all of them at once.

Decision: the vehicles/containers list returns at most 50 rows per request,
in identifier order. The slot list has no limit, and its code says why.

Rejected: limiting every list, or none.

Consequence: a reviewer may "fix" the unlimited slot list unless the reason
is written beside it. The paging mechanism (offset or cursor) is still to be
decided.