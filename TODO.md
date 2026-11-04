# Change Request Portal: to-do list

*Created 4 Nov 2026. Tick items off (`- [x]`) as they're done.*

## Phase 1: build on the test site (before migration)

**Updates document ([DetailScreen-Fixes.md](DetailScreen-Fixes.md)), all parts except the email ones:**
- [ ] **Part 1:** new SharePoint columns (Impact details, Justification, Location, Affected systems, Outage expected, Outage duration)
- [ ] **Part 2:** New Request screen clean-up and the new fields
- [ ] **Part 3:** new fields on the detail screen
- [ ] **Part 6:** board quick filters (`drpFilterCategory`, `drpFilterType`) and the header layout
- [ ] **Part 8:** detail screen clean-up (decisions side by side, empty fields hidden, Yes/No, Assignee name, one-line dates)
- [ ] **Part 9:** Technical Review Board, routes for each change type, PIR rename, Needs changes, TRB checklist, Completed button. *Do step 9a.4 (rename Review → PIR) before replacing the `Stages` table.*
- ⏭ **Skip Parts 4, 5 and 7** (email flows and the email link). These get built in production.

**Other app work:**
- [ ] **Forward Schedule of Change** (calendar), from [Forward-Schedule-of-Change.md](Forward-Schedule-of-Change.md). Build it after Part 9.
- [ ] **Retire the old Microsoft Form and its flow,** if not done yet: turn off the flow, and stop the form accepting responses.
- [ ] **Run the test checklists** in Parts 1–3, 6, 8 and 9, and in the calendar guide.

**Documents (ask Claude when ready):**
- [ ] Fold every update into the **main guide** ([Change-Request-PowerApp-Guide.md](Change-Request-PowerApp-Guide.md)).
- [ ] Update the **migration guide**: skip the form and flow steps, add Office 365 Users, add the TRB and PIR SharePoint changes.
- [ ] Redraw the guide's **board and detail-screen diagrams** (`docs/Build-Mockups.ps1`).

## Phase 2: migrate to production

Using [Migration-Guide.md](Migration-Guide.md):
- [ ] Create the production lists. Use *From existing list*, or run the updated [Provision-ChangeRequestLists.ps1](Provision-ChangeRequestLists.ps1).
- [ ] Upload the Rollback Plan template and copy its new link.
- [ ] ⏭ Skip Steps 2–3 (Microsoft Form and its flow).
- [ ] Copy the app with **Save as**, swap both lists to production, and check **Office 365 Users** is connected.
- [ ] Update App.Formulas with the production template link and the production people: `CMTeam`, `TRBMembers`, `CABMembers`, `ChangeAuthorities`.
- [ ] Set site permissions and share the app.
- [ ] Run the Step 6 production tests, then delete the test tickets.
- [ ] Go live, and label the test copies **(TEST)**. There are **no emails yet** at this point.

## Phase 3: in production, after go-live

- [ ] **App Roles** list: one list holding the CM, TRB, CAB, Authority and SW/HW manager emails. *Guide still to be written by Claude.*
- [ ] Switch App.Formulas (`IsCM`, `IsTRB`, `IsCAB`, `IsAuthority`) to read from App Roles.
- [ ] **Part 4 flow:** new-request emails (CM always, SW/HW managers by category), reading recipients from App Roles.
- [ ] **Part 7 flow:** stage emails, including TRB, Needs changes, Completed and PIR.
- [ ] **Part 5:** the email link that opens the request, using the production app's web link.
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
