# Change Request Portal (Power Apps)

A Microsoft 365 change-request portal. Requests are submitted in a Power Apps app and tracked on a board through up to seven stages:

1. Requested
2. Technical Review Board (TRB), for Normal changes only
3. Change Advisory Board
4. Change Authority
5. Implementation
6. PIR (post-implementation review)
7. Close

Standard changes go straight from Requested to Implementation, then Close. Emergency changes skip the TRB.

## Contents

| File | Purpose |
|---|---|
| [Change-Request-PowerApp-Guide.md](Change-Request-PowerApp-Guide.md) | Step-by-step build of the canvas app (board, detail screen, stage rules, Power Fx formulas) |
| [Change-Request-Form-Setup.md](Change-Request-Form-Setup.md) | Microsoft Form questions and the Power Automate flow that turns each response into a ticket |
| [Provision-ChangeRequestLists.ps1](Provision-ChangeRequestLists.ps1) | Creates the SharePoint lists and uploads the rollback template (PnP.PowerShell) |
| [Rollback-Plan-Template.pdf](Rollback-Plan-Template.pdf) | Fillable Rollback Plan form that requesters attach to every change |
| [Build-RollbackPdf.ps1](Build-RollbackPdf.ps1) | Regenerates the Rollback Plan PDF: `./Build-RollbackPdf.ps1 -OutFile .\Rollback-Plan-Template.pdf` |
| [Migration-Guide.md](Migration-Guide.md) | Step-by-step move from the test SharePoint site to production: lists, template, app copy, permissions, testing, go-live, and the email flows and roles to build afterwards |
| [DetailScreen-Fixes.md](DetailScreen-Fixes.md) | Latest app update, not yet in the guide: new request fields (Impact details, Justification, Location, Affected systems, Outage), New Request clean-up, board filters, and email notifications for new requests and stage changes |
| [Forward-Schedule-of-Change.md](Forward-Schedule-of-Change.md) | Step-by-step build of the Schedule screen: a month calendar of planned changes with clash warnings and a day panel |
| [SharePoint-Intro.md](SharePoint-Intro.md) | Intro text for the Change Management SharePoint page: how to submit a request, the routes for each change type, and the schedule |
| [TODO.md](TODO.md) | Everything left to implement, in order: test-site build, migration, and production follow-ups |
| [Troubleshooting-Notes.md](Troubleshooting-Notes.md) | Resolved notes from the New Request screen work. Explains why the choice fields use classic Drop downs |
| [docs/](docs/) | Screen layout diagrams used in the guide, and `Build-Mockups.ps1`, which regenerates them |

## Setup order

1. Run `Provision-ChangeRequestLists.ps1` against your SharePoint site.
2. Build the form and the flow by following `Change-Request-Form-Setup.md`.
3. Build the app by following `Change-Request-PowerApp-Guide.md`, then paste the form link and the template link into `App.Formulas`.
