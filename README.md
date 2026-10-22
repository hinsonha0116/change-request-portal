# Change Request Portal (Power Apps)

A Microsoft 365 change-request portal. Requests are submitted through a Microsoft Form and tracked on a Power Apps board through six stages:

1. Requested
2. Change Advisory Board
3. Change Authority
4. Implementation
5. Review
6. Close

## Contents

| File | Purpose |
|---|---|
| [Change-Request-PowerApp-Guide.md](Change-Request-PowerApp-Guide.md) | Step-by-step build of the canvas app (board, detail screen, stage rules, Power Fx formulas) |
| [Change-Request-Form-Setup.md](Change-Request-Form-Setup.md) | Microsoft Form questions and the Power Automate flow that turns each response into a ticket |
| [Provision-ChangeRequestLists.ps1](Provision-ChangeRequestLists.ps1) | Creates the SharePoint lists and uploads the rollback template (PnP.PowerShell) |
| [Rollback-Plan-Template.pdf](Rollback-Plan-Template.pdf) | Fillable Rollback Plan form that requesters attach to every change |
| [Build-RollbackPdf.ps1](Build-RollbackPdf.ps1) | Regenerates the Rollback Plan PDF: `./Build-RollbackPdf.ps1 -OutFile .\Rollback-Plan-Template.pdf` |
| [DetailScreen-Fixes.md](DetailScreen-Fixes.md) | Role-based access changes (CM-only buttons, users see only their own requests) for apps built from an earlier version of the guide. Already included in the guide |
| [docs/](docs/) | Screen layout diagrams used in the guide, and `Build-Mockups.ps1`, which regenerates them |

## Setup order

1. Run `Provision-ChangeRequestLists.ps1` against your SharePoint site.
2. Build the form and the flow by following `Change-Request-Form-Setup.md`.
3. Build the app by following `Change-Request-PowerApp-Guide.md`, then paste the form link and the template link into `App.Formulas`.
