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
| [Change-Request-PowerApp-Guide.md](Change-Request-PowerApp-Guide.md) | Step-by-step build of the whole app: SharePoint lists, board, New Request screen, detail screen, stage rules and routes, publishing, email flows, tests and troubleshooting |
| [Change-Request-Form-Setup.md](Change-Request-Form-Setup.md) | *Retired.* The Microsoft Form and flow used before requests were submitted in the app |
| [Provision-ChangeRequestLists.ps1](Provision-ChangeRequestLists.ps1) | Creates the SharePoint lists and uploads the rollback template (PnP.PowerShell) |
| [Rollback-Plan-Template.pdf](Rollback-Plan-Template.pdf) | Fillable Rollback Plan form that requesters attach to every change |
| [Build-RollbackPdf.ps1](Build-RollbackPdf.ps1) | Regenerates the Rollback Plan PDF: `./Build-RollbackPdf.ps1 -OutFile .\Rollback-Plan-Template.pdf` |
| [Migration-Guide.md](Migration-Guide.md) | Step-by-step move from the test SharePoint site to production: lists, template, app copy, permissions, testing, go-live, and the email flows and roles to build afterwards |
| [DetailScreen-Fixes.md](DetailScreen-Fixes.md) | App updates not yet in the build guide: change-type help, "Other" A6 program, several assignees, the Emergency CAB route, and a History line for every field change |
| [Change-Archive-Guide.md](Change-Archive-Guide.md) | Archive flow: when a change closes, a PDF of the whole record plus its attachments is filed in a SharePoint library by program, year, month and CR |
| [Forward-Schedule-of-Change.md](Forward-Schedule-of-Change.md) | Step-by-step build of the Schedule screen: a month calendar of planned changes with clash warnings and a day panel |
| [SharePoint-Intro.md](SharePoint-Intro.md) | Intro text for the Change Management SharePoint page: how to submit a request, the routes for each change type, and the schedule |
| [TODO.md](TODO.md) | Everything left to implement, in order: test-site build, migration, and production follow-ups |
| [Troubleshooting-Notes.md](Troubleshooting-Notes.md) | Resolved notes from the New Request screen work. Explains why the choice fields use classic Drop downs |
| [docs/](docs/) | Screen layout diagrams used in the guide, and `Build-Mockups.ps1`, which regenerates them |

## Setup order

1. Run `Provision-ChangeRequestLists.ps1` against your SharePoint site, or create the lists by hand (build guide, Step 1).
2. Build the app and the email flows by following `Change-Request-PowerApp-Guide.md`, including the Schedule screen from `Forward-Schedule-of-Change.md`.
3. To move from a test site to production, follow `Migration-Guide.md`.
