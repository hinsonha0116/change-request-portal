# Change Request Portal: to-do list

*Created 4 Nov 2026, updated 16 Nov 2026. The Part numbers refer to the old updates document, now folded into the build guide. Tick items off (`- [x]`) as they're done.*

## Current updates ([DetailScreen-Fixes.md](DetailScreen-Fixes.md))

- [ ] **Part 1:** hover text explaining the change types on New Request
- [ ] **Part 2:** "Other" in the A6 program list, with a free-text box
- [ ] **Part 3:** several assignees (SharePoint *Allow multiple selections*, then the Assignee card)
- [ ] **Part 4:** Emergency CAB route (Requested → ECAB → Implementation → PIR → Close). *Finish any Emergency requests at CAB or Change Authority first.*
- [ ] **Part 5:** a History line listing every field change on save
- [ ] **Part 6:** software and hardware details on each request, the CMDB tasker email to the HW or SW managers, and the required *CMDB updated* check
- [ ] Once done, fold these into the build guide and clear the updates doc.

## Change archive ([Change-Archive-Guide.md](Change-Archive-Guide.md))

- [ ] Check OneDrive's **Convert file** action is available in your cloud (otherwise use the HTML fallback).
- [ ] Create the **Change Archive** library (read-only for members) and the `ArchiveLink` column.
- [ ] Build the **Archive on close** flow and the **Open archive** button.
- [ ] Apply the fixes in [Archive-Flow-Fixes.md](Archive-Flow-Fixes.md) to the original archive flow, and the A6 program fix to the new-request email.
- [ ] Optional: archive changes that closed earlier with the manual copy of the flow.

## Phase 1: build on the test site (before migration)

**Updates document ([DetailScreen-Fixes.md](DetailScreen-Fixes.md)), all parts except the email ones:**
- [x] **Part 1:** new SharePoint columns (Impact details, Justification, Location, Affected systems, Outage expected, Outage duration)
- [x] **Part 2:** New Request screen clean-up and the new fields
- [x] **Part 3:** new fields on the detail screen
- [x] **Part 6:** board quick filters (`drpFilterCategory`, `drpFilterType`) and the header layout
- [x] **Part 8:** detail screen clean-up (decisions side by side, empty fields hidden, Yes/No, Assignee name, one-line dates)
- [x] **Part 9:** Technical Review Board, routes for each change type, PIR rename, Needs changes, TRB checklist, Completed button. *Do step 9a.4 (rename Review → PIR) before replacing the `Stages` table.*
- [x] **Parts 10 and 11:** tidy the action bar and notes tabs; line up read-only values
- ⏭ **Skip Parts 4, 5 and 7** (email flows and the email link). These get built in production.

**Other app work:**
- [x] **Forward Schedule of Change** (calendar), from [Forward-Schedule-of-Change.md](Forward-Schedule-of-Change.md). Build it after Part 9.
- [ ] **Retire the old Microsoft Form and its flow,** if not done yet: turn off the flow, and stop the form accepting responses.
- [ ] **Run the test checklists** in Parts 1–3, 6, 8 and 9, and in the calendar guide.

**Documents (ask Claude when ready):**
- [x] Fold every update into the **main guide** ([Change-Request-PowerApp-Guide.md](Change-Request-PowerApp-Guide.md)).
- [x] Update the **migration guide**: skip the form and flow steps, add Office 365 Users, add the TRB and PIR SharePoint changes.
- [ ] Redraw the guide's **board and detail-screen diagrams** (`docs/Build-Mockups.ps1`).

## Phase 2: migrate to production

Using [Migration-Guide.md](Migration-Guide.md) (updated 5 Nov 2026 for the current app):
- [ ] Create the production lists. Use *From existing list*, or run the updated [Provision-ChangeRequestLists.ps1](Provision-ChangeRequestLists.ps1).
- [ ] Upload the Rollback Plan template and copy its new link.
- [ ] ⏭ Skip Steps 2–3 (Microsoft Form and its flow).
- [ ] Copy the app with **Save as**, swap both lists to production, and check **Office 365 Users** is connected.
- [ ] Update App.Formulas with the production template link and the production people: `CMTeam`, `TRBMembers`, `CABMembers`, `ChangeAuthorities`.
- [ ] Set site permissions and share the app.
- [ ] Run the Step 6 production tests, then delete the test tickets.
- [ ] Go live, and label the test copies **(TEST)**. There are **no emails yet** at this point.

## Phase 3: in production, after go-live

- [x] **Part 12:** CR numbers by year (`CR-2026-001`): new `CRNumber` column, hidden card on New Request, new number on the board, detail, calendar and emails.

- [ ] **App Roles** list: one list holding the CM, TRB, CAB, Authority and SW/HW manager emails. *Guide still to be written by Claude.*
- [ ] Switch App.Formulas (`IsCM`, `IsTRB`, `IsCAB`, `IsAuthority`) to read from App Roles.
- [x] **Part 4 flow:** new-request emails (CM always, SW/HW managers by category), reading recipients from App Roles.
- [x] **Part 7 flow:** stage emails, including TRB, Needs changes, Completed and PIR.
- [x] **Part 5:** the email link that opens the request, using the production app's web link.
- [ ] Test the emails with a couple of "TEST – ignore" requests, then delete them and their History rows.

## Later / optional

- [ ] **Emergency process:** when it's finalised, update the routes in the `Stages` **Types** field.
- [ ] **TRB checklist:** make some checks required, if you decide to later.
- [ ] **Hide other people's requests in SharePoint itself** (item-level permissions), if the in-app filtering isn't enough.
- [ ] **Ideas not picked up yet:**
  - a shared banner component and theme across all screens
  - aging and outage badges on board cards
  - a lead-time warning for Normal changes
  - a "Duplicate request" button
