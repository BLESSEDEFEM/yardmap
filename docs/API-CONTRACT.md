# YARDMAP · API CONTRACT

**Version 0.1 — pre-release. Last updated: 2026-10-10**

**Every line is marked `PLANNED` or `LIVE`.** `PLANNED` means decided and not answering yet. **You may build against a `PLANNED` line** — record which lines were `PLANNED` when you read them.

---

## 1 · WHERE THE SERVER IS

```
   Development    http://127.0.0.1:8000                      PLANNED
   Production     not yet deployed                           PLANNED

   Interactive documentation, which lists every endpoint
   and lets you try it:
                  http://127.0.0.1:8000/docs                 PLANNED
```

---

## 2 · EVERY ENDPOINT

```
   #   METHOD  PATH                                            WHAT IT IS FOR               STATE
   1   POST    /sessions                                       sign in                      PLANNED
   2   POST    /vehicles-containers                            register a vehicle/container PLANNED
   3   GET     /vehicles-containers                            list them, filtered          PLANNED
   4   POST    /appointments                                   reserve a slot for a window  PLANNED
   5   GET     /appointments                                   list them, filtered          PLANNED
   6   POST    /vehicles-containers/{id}/check-ins             check one in at the gate     PLANNED
   7   POST    /vehicles-containers/{id}/check-outs            check one out at the gate    PLANNED
   8   GET     /movements                                      yard activity history        PLANNED
   9   GET     /users                                          list users                   PLANNED
   10  PATCH   /users/{user_id}                                change a role or status      PLANNED
   11  GET     /activity-reports/{report_job_id}               collect a report             PLANNED
   12  POST    /vehicles-containers/{id}/movements             place or move into a slot    PLANNED
   13  GET     /slots                                          the yard map                 PLANNED
   14  POST    /activity-reports                               ask for a report             PLANNED

   Fourteen endpoints.
```

---

## 3 · WHAT IS NOT THERE YET

```
   Nothing answers yet.  Every line in this contract is PLANNED.

   IMPLEMENTATION ORDER, so you know what to expect first:

      Reads first        3, 5, 8, 9, 11, 13
      Then writes        2, 4, 6, 7, 10, 12, 14
      Sign-in last       1

   AND ONE ENDPOINT THAT WILL ANSWER AND DO NOTHING:

      Endpoint 14 returns 202 Accepted and a report_job_id.  The report
      itself is produced by a SEPARATE WORKER PROCESS, which is not part
      of this service and is not yet implemented.  Until it exists, every
      report job stays at state "queued" indefinitely.
      THIS IS EXPECTED BEHAVIOUR, NOT A BUG.
      Build your polling against it anyway — the states are real and the
      shape will not change.

   AND THESE ARE OUT OF SCOPE, deliberately, and will not be built:
      payments of any kind · GPS or IoT tracking · crane management ·
      customs or shipping integrations · multi-move route optimisation ·
      notifications of any kind · more than one yard ·
      customer-facing booking · tracking outside the yard ·
      automated gate hardware or plate recognition ·
      A LIVE-UPDATING YARD MAP — the map is a normal read, refresh it ·
      haulier self-registration, email verification, password reset —
         staff create haulier accounts ·
      hauliers scheduling their own arrivals — a haulier reads, staff write ·
      hauliers seeing the yard map — it cannot be usefully filtered
```

---

## ENDPOINT 1 · POST /sessions — `PLANNED`

```
WHAT IT IS FOR     sign in, and receive the token every other endpoint
                   needs

WHO MAY CALL IT    anybody.  This is how you obtain a token.

WHERE EACH VALUE RIDES
                   email, password → both in the body

WHAT TO SEND
   email           text            required     must be a valid email
   password        text            required     1 to 72 BYTES.  Longer is
                                                refused — a real limit of
                                                the hashing we use, not a
                                                choice.  Check it before
                                                sending so the person gets
                                                a faster answer

WHAT COMES BACK · 200 OK
   access_token    text            never empty
   token_type      text            never empty    always "bearer"

EVERY FAILURE
   422 Unprocessable     a field is missing or not an email
       Content           The message is in:  detail[].msg
                         The field name is in:  detail[].loc
   401 Unauthorized      the email and password do not match.
                         WE DO NOT SAY WHICH ONE WAS WRONG, deliberately —
                         saying "no such email" tells anybody which
                         addresses have accounts.
                         The message is in:  detail
   500 Internal Server   our fault.  You may retry once.
       Error             The message is in:  detail

   NOTE ON SPEED:  this endpoint takes about 300 ms on purpose, because
   hashing a password slowly is what makes it hard to attack.  It is the
   slowest endpoint here and that is correct.  Do not treat it as a
   timeout.

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## ENDPOINT 2 · POST /vehicles-containers — `PLANNED`

```
WHAT IT IS FOR     register a vehicle or container, owned by a haulier

WHO MAY CALL IT    Operator or Manager.  A haulier may NOT register its
                   own containers — staff do it on their behalf.

WHERE EACH VALUE RIDES
                   everything → the body

WHAT TO SEND
   type            text            required     "vehicle" or "container"
   identifier      text            required     1 to 50 characters.
                                                Must be unique across all
                                                vehicles/containers
   size            text            required     "small", "standard" or
                                                "large"
   haulier_id      whole number    required     the id of a user whose
                                                role is "haulier"
   description     text            optional     max 500 characters.
                                                Absent → stored as empty

WHAT COMES BACK · 201 Created
   id              whole number    never empty
   type            text            never empty
   identifier      text            never empty
   size            text            never empty
   haulier_id      whole number    never empty
   description     text            MAY BE EMPTY   empty means none was
                                                  given.  Show nothing,
                                                  not the word "null"
   status          text            never empty    always "registered" on
                                                  a new one

EVERY FAILURE
   422 Unprocessable     a field is missing, wrong, or too long
       Content           The message is in:  detail[].msg
   401 Unauthorized      not signed in.  Send the person to sign in
                         The message is in:  detail
   403 Forbidden         signed in and not an Operator or Manager.
                         Tell them they may not.  Do NOT send them to
                         sign in again
                         The message is in:  detail
   404 Not Found         no user with that haulier_id
                         The message is in:  detail
   409 Conflict          that user exists but is not a haulier
                         The message is in:  detail
   409 Conflict          that identifier is already registered
                         The message is in:  detail
   500 Internal Server   our fault
       Error             The message is in:  detail

   THE TWO 409s ARE DIFFERENT and you should show different messages.
   One means "pick a different haulier", the other means "that
   container is already in the system".

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## ENDPOINT 3 · GET /vehicles-containers — `PLANNED`

```
WHAT IT IS FOR     a list of vehicles/containers, narrowed

WHO MAY CALL IT    any signed-in user.
                   STAFF SEE ALL.  A HAULIER SEES ONLY ITS OWN —
                   we filter it for you, automatically, from the token.

WHERE EACH VALUE RIDES
                   type, status, haulier_id → all in the query

WHAT TO SEND  — every one may be left out
   type            text            optional     "vehicle" or "container".
                                                Absent → both
   status          text            optional     "registered", "in_yard"
                                                or "departed".
                                                Absent → all
   haulier_id      whole number    optional     STAFF ONLY.  A haulier
                                                sending this gets 403.
                                                Absent → all, for staff

   These combine.  ?type=container&status=in_yard is allowed.

WHAT COMES BACK · 200 OK
   a list.  Each item carries:
   id              whole number    never empty
   type            text            never empty
   identifier      text            never empty
   size            text            never empty
   haulier_id      whole number    never empty
   status          text            never empty
   current_slot_id whole number    MAY BE EMPTY   empty means it is not
                                                  in a slot right now.
                                                  Show "not in yard" or a
                                                  dash, not "null"

   NOT included, deliberately:  description.  Fetch endpoint 2's reply or
   a future detail endpoint for it.

WHEN THE ANSWER IS EMPTY
   []  with 200 OK.

   THIS IS NOT A FAILURE.  A narrowing that matches nothing is a correct
   answer meaning "none".  It is never a 404.  Show "no vehicles or
   containers match" rather than "not found" — those are different
   things to a person.

THE LIMIT AND THE ORDER
   Limit    50 per request.  PLANNED
   Order    by identifier, alphabetically.
   Pagination      PLANNED — the mechanism is not yet decided, and this
                   line is updated when it is.

EVERY FAILURE
   422 Unprocessable     a filter is not one of the allowed values
       Content           The message is in:  detail[].msg
   401 Unauthorized      not signed in
                         The message is in:  detail
   403 Forbidden         a haulier sent haulier_id.  A haulier is always
                         filtered to itself and may not ask about another
                         The message is in:  detail
   500 Internal Server   our fault
       Error             The message is in:  detail

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## ENDPOINT 4 · POST /appointments — `PLANNED`

```
WHAT IT IS FOR     reserve a yard slot for one vehicle/container over a
                   time window, before it arrives

WHO MAY CALL IT    Operator or Manager.  A haulier may NOT book its own
                   arrivals.

WHERE EACH VALUE RIDES
                   everything → the body

WHAT TO SEND
   vehicle_container_id  whole number  required
   slot_id               whole number  required
   reserved_from         moment in time required
   reserved_until        moment in time required   must be AFTER
                                                   reserved_from
   notes                 text          optional    max 500 characters

WHAT COMES BACK · 201 Created
   id                    whole number   never empty
   vehicle_container_id  whole number   never empty
   slot_id               whole number   never empty
   reserved_from         moment in time never empty
   reserved_until        moment in time never empty
   notes                 text           MAY BE EMPTY   empty means none
                                                       given
   status                text           never empty    always "open" on
                                                       a new one

EVERY FAILURE
   422 Unprocessable     a field is missing or invalid, or
       Content           reserved_until is not after reserved_from
                         The message is in:  detail[].msg
   401 Unauthorized      not signed in
   403 Forbidden         not an Operator or Manager
   404 Not Found         the vehicle/container or the slot does not exist
   409 Conflict          that slot is already held over an overlapping
                         window.  Carries held_by_appointment_id and
                         their_window so you can tell the person WHEN it
                         is free
   409 Conflict          that slot does not accept this size.  Carries
                         slot_accepts_size and container_size
   409 Conflict          this vehicle/container already has an open
                         appointment
   500 Internal Server   our fault
       Error             The message is in:  detail

   EVERY 409 CARRIES A SHORT FIXED WORD in detail.error that you can
   branch on without reading English, plus what it collided with.

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## ENDPOINT 5 · GET /appointments — `PLANNED`

```
WHAT IT IS FOR     a list of appointments, narrowed

WHO MAY CALL IT    any signed-in user.
                   STAFF SEE ALL.  A HAULIER SEES ONLY APPOINTMENTS FOR
                   ITS OWN CONTAINERS — filtered automatically.

WHERE EACH VALUE RIDES
                   status, date → both in the query

WHAT TO SEND  — both may be left out
   status          text            optional     "open", "fulfilled" or
                                                "cancelled".  Absent → all
   date            a day           optional     Absent → all dates

WHAT COMES BACK · 200 OK
   a list.  Each item carries:
   id                    whole number   never empty
   vehicle_container_id  whole number   never empty
   slot_id               whole number   never empty
   reserved_from         moment in time never empty
   reserved_until        moment in time never empty
   notes                 text           MAY BE EMPTY   none given
   status                text           never empty

WHEN THE ANSWER IS EMPTY
   []  with 200 OK.  A correct answer meaning "none".  Never a 404.

THE LIMIT AND THE ORDER
   Limit    50 per request.  PLANNED
   Order    by reserved_from, earliest first.
   Pagination      PLANNED

EVERY FAILURE
   422 Unprocessable     a filter is invalid
       Content           The message is in:  detail[].msg
   401 Unauthorized      not signed in
                         The message is in:  detail
   500 Internal Server   our fault
       Error             The message is in:  detail

   NO 403 HERE, deliberately.  A haulier may call this; it is simply
   filtered.  403 appears only where a haulier asks about somebody else.

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## ENDPOINT 6 · POST /vehicles-containers/{id}/check-ins — `PLANNED`

```
WHAT IT IS FOR     record that a vehicle/container arrived at the gate

WHO MAY CALL IT    Operator or Manager

WHERE EACH VALUE RIDES
                   vehicle_container_id → the path
                   everything else      → the body

WHAT TO SEND
   vehicle_container_id  whole number   required   in the path
   appointment_id        whole number   optional   absent means checked
                                                   in without one, which
                                                   is allowed
   checked_in_at         moment in time optional   absent means the
                                                   server uses now.
                                                   PREFER LEAVING IT OUT —
                                                   our clock is the one
                                                   every record shares

WHAT COMES BACK · 201 Created
   id                    whole number   never empty
   vehicle_container_id  whole number   never empty
   appointment_id        whole number   MAY BE EMPTY   empty means no
                                                       appointment was
                                                       used
   checked_in_at         moment in time never empty

EVERY FAILURE
   404 Not Found         the vehicle/container or the appointment does
                         not exist
   422 Unprocessable     input is invalid
       Content           The message is in:  detail[].msg
   401 Unauthorized      not signed in
   403 Forbidden         not an Operator or Manager
   409 Conflict          already checked in
   500 Internal Server   our fault
       Error             The message is in:  detail

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## ENDPOINT 7 · POST /vehicles-containers/{id}/check-outs — `PLANNED`

```
WHAT IT IS FOR     record that a vehicle/container left the yard

WHO MAY CALL IT    Operator or Manager

WHERE EACH VALUE RIDES
                   vehicle_container_id → the path
                   checked_out_at       → the body

WHAT TO SEND
   vehicle_container_id  whole number   required   in the path
   checked_out_at        moment in time optional   absent means now.
                                                   Prefer leaving it out

WHAT COMES BACK · 201 Created
   id                    whole number   never empty
   vehicle_container_id  whole number   never empty
   checked_out_at        moment in time never empty

EVERY FAILURE
   404 Not Found         the vehicle/container does not exist
   422 Unprocessable     input is invalid
       Content           The message is in:  detail[].msg
   401 Unauthorized      not signed in
   403 Forbidden         not an Operator or Manager
   409 Conflict          NOT CURRENTLY CHECKED IN.  Different from
                         endpoint 6's 409 and you should say so
                         differently
   500 Internal Server   our fault
       Error             The message is in:  detail

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## ENDPOINT 8 · GET /movements — `PLANNED`

```
WHAT IT IS FOR     yard activity — what moved, where, and when

WHO MAY CALL IT    any signed-in user.
                   STAFF SEE ALL.  A HAULIER SEES ONLY ITS OWN
                   CONTAINERS' MOVEMENTS — filtered automatically.

WHERE EACH VALUE RIDES
                   vehicle_container_id, from, to → all in the query

WHAT TO SEND  — every one may be left out
   vehicle_container_id  whole number   optional   absent means every one
                                                   you may see
   from                  a day          optional   absent means the
                                                   beginning
   to                    a day          optional   absent means up to now

WHAT COMES BACK · 200 OK
   a list, NEWEST FIRST.  Each item carries:
   id                    whole number   never empty
   vehicle_container_id  whole number   never empty
   kind                  text           never empty   what happened
   from_slot_id          whole number   MAY BE EMPTY  empty means it was
                                                      in no slot before
                                                      this — which is
                                                      normal on a check-in
   to_slot_id            whole number   MAY BE EMPTY  empty means it is in
                                                      no slot after this —
                                                      normal on a check-out
   moved_at              moment in time never empty
   reason                text           MAY BE EMPTY  none was given

   BOTH SLOT FIELDS EMPTY AT ONCE is possible and is not an error.

WHEN THE ANSWER IS EMPTY
   []  with 200 OK.  A correct answer meaning "none".  Never a 404.

THE LIMIT AND THE ORDER
   Limit    50 per request.  PLANNED
   Order    by moved_at, NEWEST FIRST.
   Pagination      PLANNED

EVERY FAILURE
   422 Unprocessable     a filter is invalid, or "from" is after "to"
       Content           The message is in:  detail[].msg
   401 Unauthorized      not signed in
                         The message is in:  detail
   404 Not Found         A HAULIER ASKED FOR A vehicle_container_id THAT
                         IS NOT ITS OWN.
                         THIS IS DELIBERATELY 404 AND NOT 403.  A 403
                         would confirm that container exists, which tells
                         a haulier something about another haulier's
                         business.  404 says only "nothing here for you".
                         Treat it as "not found", not as a permissions
                         problem
                         The message is in:  detail
   500 Internal Server   our fault
       Error             The message is in:  detail

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## ENDPOINT 9 · GET /users — `PLANNED`

```
WHAT IT IS FOR     list the people with accounts

WHO MAY CALL IT    Manager or Admin only

WHERE EACH VALUE RIDES
                   role, status → both in the query

WHAT TO SEND  — both may be left out
   role            text            optional     "operator", "manager",
                                                "admin" or "haulier".
                                                Absent → all
   status          text            optional     "active" or "inactive".
                                                Absent → both

WHAT COMES BACK · 200 OK
   a list.  Each item carries:
   id              whole number    never empty
   email           text            never empty
   full_name       text            never empty
   role            text            never empty
   status          text            never empty

   NEVER SENT, EVER:  password_hash.  It is stored and never leaves.
   Do not expect it and do not ask for it.

WHEN THE ANSWER IS EMPTY
   []  with 200 OK.  A correct answer meaning "none".  Never a 404.

THE LIMIT AND THE ORDER
   Limit    50 per request.  PLANNED
   Order    by email, alphabetically.
   Pagination      PLANNED

EVERY FAILURE
   422 Unprocessable     a filter is invalid
       Content           The message is in:  detail[].msg
   401 Unauthorized      not signed in
   403 Forbidden         signed in and not a Manager or Admin
   500 Internal Server   our fault
       Error             The message is in:  detail

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## ENDPOINT 10 · PATCH /users/{user_id} — `PLANNED`

```
WHAT IT IS FOR     change somebody's role, or make an account inactive

WHO MAY CALL IT    Manager or Admin only

WHERE EACH VALUE RIDES
                   user_id → the path
                   role, status → the body

WHAT TO SEND  — send either, or both
   user_id         whole number    required     in the path
   role            text            optional     absent means leave it
                                                unchanged
   status          text            optional     absent means leave it
                                                unchanged

   SENDING NEITHER is a 422.  A change with nothing in it is not a change.

WHAT COMES BACK · 200 OK
   id              whole number    never empty
   email           text            never empty
   full_name       text            never empty
   role            text            never empty
   status          text            never empty

EVERY FAILURE
   404 Not Found         no user with that id
   422 Unprocessable     role or status is not an allowed value, or
       Content           neither was sent
                         The message is in:  detail[].msg
   401 Unauthorized      not signed in
   403 Forbidden         not a Manager or Admin
   409 Conflict          THIS WOULD LEAVE NO ACTIVE ADMIN.  Refused
   409 Conflict          A CALLER MAY NOT CHANGE THEIR OWN ROLE.
                         Refused, even for an Admin
   409 Conflict          A HAULIER WITH CONTAINERS REGISTERED TO IT
                         CANNOT BE MADE STAFF.  Its containers would
                         belong to nobody
   500 Internal Server   our fault
       Error             The message is in:  detail

   THREE DIFFERENT 409s, each needing a different message on screen.
   Branch on detail.error, not on the English.

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## ENDPOINT 11 · GET /activity-reports/{report_job_id} — `PLANNED`

```
WHAT IT IS FOR     find out what happened to a report you asked for, and
                   collect it

WHO MAY CALL IT    Manager or Admin

WHERE EACH VALUE RIDES
                   report_job_id → the path

WHAT TO SEND
   report_job_id   text            required     THE UUID we gave you in
                                                endpoint 14's reply.  Not
                                                a number

WHAT COMES BACK · 200 OK
   id              text            never empty    the same uuid
   from            a day           never empty
   to              a day           never empty
   state           text            never empty    "queued", "running",
                                                  "done" or "failed"
   requested_at    moment in time  never empty
   started_at      moment in time  MAY BE EMPTY   EMPTY MEANS NOBODY HAS
                                                  PICKED IT UP YET.  See
                                                  the note below — this is
                                                  the most useful field
                                                  here
   finished_at     moment in time  MAY BE EMPTY   empty means not finished
   failure_reason  text            MAY BE EMPTY   EMPTY MEANS IT DID NOT
                                                  FAIL
   download_url    text            MAY BE EMPTY   empty until state is
                                                  "done"

   HOW TO READ THIS, which matters more than the field list:

      state=queued, started_at EMPTY, and old
          → nobody ever picked it up.  Our worker is down.  This is OUR
            problem, not the report's.  Tell the person it is delayed,
            not that it failed
      state=failed, started_at FILLED, failure_reason filled
          → it ran and failed.  The reason is there, in plain words
      state=done, download_url filled
          → collect it

      THOSE ARE THREE DIFFERENT SITUATIONS and only the two timestamps
      together tell them apart.

   HOW OFTEN TO ASK:  every 5 seconds while state is "queued" or
   "running".  Stop when it reaches "done" or "failed".  Do not ask more
   often than that — it changes nothing and costs us both.

   NEVER SENT, EVER:  where the file sits on our disk, the attempt count,
   and the raw error text.  download_url is a link we control; build
   nothing from a path.

EVERY FAILURE
   404 Not Found         no report with that id
                         The message is in:  detail
   422 Unprocessable     the id is not a valid uuid
       Content           The message is in:  detail[].msg
   401 Unauthorized      not signed in
   403 Forbidden         not a Manager or Admin
   500 Internal Server   our fault
       Error             The message is in:  detail

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## ENDPOINT 12 · POST /vehicles-containers/{id}/movements — `PLANNED`

```
WHAT IT IS FOR     place a vehicle/container into a yard slot, or move it
                   between slots.  IF YOU DO NOT NAME A SLOT, WE WORK OUT
                   THE BEST FREE ONE AND USE IT.

WHO MAY CALL IT    Operator or Manager

WHERE EACH VALUE RIDES
                   vehicle_container_id → the path
                   everything else      → the body

WHAT TO SEND
   vehicle_container_id  whole number   required   in the path
   to_slot_id            whole number   OPTIONAL   LEAVING THIS OUT IS
                                                   HOW YOU ASK FOR A
                                                   SUGGESTION.  Send it
                                                   and we check that slot;
                                                   omit it and we choose
   zone_id               whole number   optional   only useful when
                                                   to_slot_id is absent.
                                                   Narrows the suggestion
                                                   to one zone.
                                                   Absent → every zone
   reason                text           optional   max 200 characters

   SO THERE ARE TWO WAYS TO CALL THIS, and both are normal:
      with to_slot_id      → "put it in A3, refuse if you can't"
      without to_slot_id   → "pick the best free slot and tell me which"

WHAT COMES BACK · 201 Created
   id                    whole number   never empty
   vehicle_container_id  whole number   never empty
   from_slot_id          whole number   MAY BE EMPTY   empty means it was
                                                       in no slot before
   to_slot_id            whole number   never empty    where it is NOW
   slot_label            text           never empty    the human name,
                                                       like "A3", so you
                                                       do not have to look
                                                       it up
   moved_at              moment in time never empty
   reason                text           MAY BE EMPTY   none given
   slot_was_suggested    true or false  never empty    TRUE means WE chose
                                                       the slot.  Show the
                                                       operator which one,
                                                       prominently — they
                                                       did not pick it

EVERY FAILURE
   404 Not Found         the vehicle/container or the named slot does not
                         exist
   422 Unprocessable     input is invalid
       Content           The message is in:  detail[].msg
   401 Unauthorized      not signed in
   403 Forbidden         not an Operator or Manager
   409 Conflict  slot_occupied        the named slot already holds
                                      something.  Carries
                                      occupied_by_vehicle_container_id
   409 Conflict  not_checked_in       it is not in the yard, so it cannot
                                      be placed
   409 Conflict  size_not_accepted    carries slot_accepts_size and
                                      container_size
   409 Conflict  slot_held            an appointment holds that slot now.
                                      Carries held_by_appointment_id and
                                      their_window, so you can say WHEN it
                                      frees up
   409 Conflict  no_slot_available    ONLY WHEN YOU OMITTED to_slot_id.
                                      We looked and found nothing that
                                      fits.  Carries reason and
                                      candidates_considered.
                                      THIS IS NOT AN ERROR ON YOUR SIDE —
                                      the yard is full for that size.
                                      Suggest trying another zone or
                                      waiting
   500 Internal Server   our fault
       Error             The message is in:  detail

   EVERY 409 CARRIES detail.error — a short fixed word you branch on.
   Five different ones here.  Do not branch on the English.

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## ENDPOINT 13 · GET /slots — `PLANNED`

```
WHAT IT IS FOR     the yard map — every slot and what is in it.  With a
                   window given, only the slots free across that window

WHO MAY CALL IT    STAFF ONLY.  NEVER A HAULIER.
                   The map shows every haulier's containers and where
                   each one sits.  It cannot be usefully filtered for one
                   haulier, so it is closed rather than filtered badly.

WHERE EACH VALUE RIDES
                   everything → the query

WHAT TO SEND  — every one may be left out
   zone_id         whole number    optional     absent → every zone
   only_free       true or false   optional     absent → every slot
   free_from       moment in time  optional     MUST BE SENT WITH
                                                free_until
   free_until      moment in time  optional     MUST BE SENT WITH
                                                free_from, and must be
                                                after it

   SENDING ONLY ONE OF free_from / free_until IS A 422.  They are one
   value in two fields.

WHAT COMES BACK · 200 OK
   a list.  Each item carries:
   id              whole number    never empty
   zone_id         whole number    never empty
   label           text            never empty    the human name, "A3"
   accepts_size    text            never empty
   occupied_by     whole number    MAY BE EMPTY   empty means nothing is
                                                  parked there right now
   reserved_windows  a list        MAY BE EMPTY   empty means nothing
                                                  holds it.  Each entry
                                                  has from and until

   With free_from and free_until, only slots held by nothing over that
   window are returned.

   THIS IS THE ENDPOINT TO CALL BEFORE OFFERING AN OPERATOR A CHOICE OF
   SLOTS.  Show the free ones, let them click, then call endpoint 12 with
   that slot_id.  We re-check at that moment — never assume this list is
   still true a minute later.

WHEN THE ANSWER IS EMPTY
   []  with 200 OK.  A correct answer meaning "no slots match" — the yard
   is full for that window or that zone.  Never a 404.

THE LIMIT AND THE ORDER
   Limit    NONE.  A yard has a few hundred slots and the map needs all
            of them at once.  PLANNED
   Order    by zone_id, then label, alphabetically.

EVERY FAILURE
   422 Unprocessable     a filter is invalid, or only one of
       Content           free_from / free_until was sent, or free_until is
                         not after free_from
                         The message is in:  detail[].msg
   401 Unauthorized      not signed in
   403 Forbidden         THE CALLER IS A HAULIER.  Deliberate.  Do not
                         offer a haulier a yard map at all
   500 Internal Server   our fault
       Error             The message is in:  detail

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## ENDPOINT 14 · POST /activity-reports — `PLANNED`

```
WHAT IT IS FOR     ask for a yard activity report over a date range.
                   THE REPORT IS NOT BUILT WHILE YOU WAIT.

WHO MAY CALL IT    Manager or Admin

WHERE EACH VALUE RIDES
                   everything → the body

WHAT TO SEND
   from                  a day          required
   to                    a day          required   must be on or after
                                                   "from"
   vehicle_container_id  whole number   optional   absent means every
                                                   container

WHAT COMES BACK IMMEDIATELY · 202 Accepted
   accepted        true or false   never empty    always true
   report_job_id   text            never empty    A UUID.  KEEP IT — it
                                                  is the only way to ever
                                                  find out what happened
   state           text            never empty    always "queued" here

   202 DOES NOT MEAN IT WORKED.  It means we have your request and have
   not done it.  SHOW "in progress", NOT a tick.

   THEN:  poll endpoint 11 with that report_job_id, every 5 seconds.

   AND THE HONEST PART:  the worker process that builds the report is not
   implemented yet.  Until it exists, every job stays at "queued".  Your
   polling will be correct and will never finish.  This is expected, and
   endpoint 11's block tells you how to show it.

EVERY FAILURE
   422 Unprocessable     a field is missing or invalid, or "to" is before
       Content           "from"
                         The message is in:  detail[].msg
   401 Unauthorized      not signed in
   403 Forbidden         not a Manager or Admin
   404 Not Found         no vehicle/container with that id
   409 Conflict          YOU ALREADY HAVE AN IDENTICAL REPORT QUEUED OR
                         RUNNING.  Same person, same dates.  This is the
                         double-click guard.  Do not retry — poll the one
                         you already have
   500 Internal Server   our fault
       Error             The message is in:  detail

ONE REAL REQUEST   to be added when implemented
ONE REAL REPLY     to be added when implemented
```

---

## 4 · AUTHENTICATION

### What needs signing in

```
   Endpoint 1   POST /sessions                    no — this is how you sign in
   Endpoint 2   POST /vehicles-containers         YES — Operator or Manager
   Endpoint 3   GET /vehicles-containers          YES — any account
   Endpoint 4   POST /appointments                YES — Operator or Manager
   Endpoint 5   GET /appointments                 YES — any account
   Endpoint 6   POST .../check-ins                YES — Operator or Manager
   Endpoint 7   POST .../check-outs               YES — Operator or Manager
   Endpoint 8   GET /movements                    YES — any account
   Endpoint 9   GET /users                        YES — Manager or Admin
   Endpoint 10  PATCH /users/{user_id}            YES — Manager or Admin
   Endpoint 11  GET /activity-reports/{id}        YES — Manager or Admin
   Endpoint 12  POST .../movements                YES — Operator or Manager
   Endpoint 13  GET /slots                        YES — STAFF ONLY, never
                                                  a haulier
   Endpoint 14  POST /activity-reports            YES — Manager or Admin

   THIRTEEN OF FOURTEEN need a token.  NINE need a particular role.
   There are four roles: operator, manager, admin, haulier.

   AND THE PART THAT IS NOT IN THE LIST:  three endpoints — 3, 5 and 8 —
   are open to any account AND return different rows depending on who
   asks.  A haulier gets only its own.  You do not filter; we do.  Do not
   build a "my containers" toggle — there is nothing to toggle.
```

### How the token is obtained

```
   POST /sessions
   with a body:   {"email":"…","password":"…"}

   The password rides in the BODY.  Never in the path, never in the
   query — both are written into access logs and kept in browser history.

   Back:  200 OK  with  {"access_token":"…","token_type":"bearer"}

   PASSWORD RULES, which we enforce and you should check first so the
   person gets a faster answer:
      at most 72 BYTES.  Longer is refused.
      (a real limit of the hashing used, not a choice)
```

### Where the token goes on each request

```
   A header named  Authorization,  with the word  Bearer,  a space,
   then the token:

      Authorization: Bearer <the token>

   SPELL IT EXACTLY.  It is the American spelling — Authorization,
   with a z.  Authorisation with an s is silently ignored, the request
   is treated as having NO token at all, and you get a 401 rather than
   anything telling you the header name was wrong.

   NOT in the query.  NOT in the body.  A header.
```

### How long it lasts

```
   30 minutes from being issued.           PLANNED

   WHAT IS INSIDE IT, which you should know:
      Anyone holding the token can READ what is inside it.  It is not
      encrypted.  It carries which person it is for, and when it expires.
      It carries NOTHING secret, by design.
      Our secret stops anybody CHANGING it — not reading it.

   SO:  you may read the expiry out of the token to know when to send
   the person back to sign in.  You may NOT trust anything in it that
   you did not get from us in a reply — including the role.  Ask us.

   THERE IS NO REFRESH TOKEN.  When it expires, sign in again.  PLANNED
```

### What comes back when the token is missing or stale

```
   No header at all:
      401 Unauthorized      {"detail":"Not authenticated"}

   A header with a token we will not accept — wrong, tampered with,
   or expired:
      401 Unauthorized      {"detail":"Proof is not valid"}

   A valid token, but the person is not allowed to do this:
      403 Forbidden         {"detail":"…"}

   401 AND 403 ARE DIFFERENT AND YOU SHOULD TREAT THEM DIFFERENTLY.
      401  we do not know who you are      → send them to sign in
      403  we know, and they may not       → tell them they may not.
                                             Sending them to sign in
                                             again will not help and
                                             will confuse them.

   AND ONE EXCEPTION WORTH KNOWING:  endpoint 8 answers 404, not 403,
   when a haulier asks about a container that is not its own.  That is
   deliberate — a 403 would confirm the container exists.
```

---

## 5 · REAL REQUESTS AND REPLIES

```
   Nothing answers yet, so there are none.  Each endpoint's block gets
   its two lines filled when that endpoint is implemented.

   WHY THIS MATTERS TO YOU:  the field lists above tell you what the
   fields are.  These will tell you the exact characters — in
   particular how a moment in time is written, which you cannot work
   out from "a moment in time", and what a uuid looks like in a reply.
```

---

## 6 · CROSS-ORIGIN — WHERE YOU MAY CALL FROM

```
   NOT YET CONFIGURED.

   WHAT THIS MEANS FOR YOU:  until it is, a browser will refuse to let
   your site read our replies, even though the request arrives and we
   answer it correctly.  The failure appears in your browser's console
   and NOT in our logs — so if you see it, the fix is on our side and
   not yours.

   WHAT WE NEED FROM YOU:  the exact origins your half runs at, in
   development and in production.  For example http://localhost:5173
   and whatever your deployed address is.
   SEND THEM TO US — we cannot guess them.
```

---

## 7 · WHAT THE CONSUMER FILLS IN

```
   Which endpoints it actually calls           ___
   Which fields it actually uses               ___
   Any field it needed and did not find        ___
   Its origins, for section 6                  ___
```

---

## 8 · CHANGES TO LIVE LINES

```
   (none yet — nothing is LIVE)
```