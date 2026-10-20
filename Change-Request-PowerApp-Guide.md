# Change Request Portal: Power Apps build guide

A canvas app that shows change requests as a board with one column per stage. Users submit new requests and move them through the stages:

| # | Stage | What happens | Rule before it can move on |
|---|-------|--------------|------------------|
| 1 | **Requested** | Requester submits the change | — |
| 2 | **Change Advisory Board** | CAB reviews risk and impact | `CABDecision` = Approved |
| 3 | **Change Authority** | Authority gives the final sign-off | `AuthorityDecision` = Approved |
| 4 | **Implementation** | Assignee carries out the change | Implementation notes filled in |
| 5 | **Review** | Post-implementation review | Review outcome chosen |
| 6 | **Close** | Done (or rejected) | — |

**Architecture:** the data lives in SharePoint lists (no premium license needed) and the user interface is a Power Apps canvas app. Each time a request changes stage, the app writes a row to a history list, which gives you an audit trail.

---

## Step 1 — Create the SharePoint lists

### Option A: script (recommended)
Run [Provision-ChangeRequestLists.ps1](Provision-ChangeRequestLists.ps1) in PowerShell 7.4 or later:

```powershell
./Provision-ChangeRequestLists.ps1 -SiteUrl "https://<tenant>.sharepoint.com/sites/<site>" -ClientId "<your PnP Entra app id>"
```

> PnP PowerShell needs its own Entra ID app registration. You can create one with `Register-PnPEntraIDAppForInteractiveLogin`.

### Option B: by hand
Create a list named **Change Requests** with these columns, **one column per row**. *Internal names must match exactly* or the formulas below won't work.

| Column | Type | Values / default |
|---|---|---|
| Title *(built-in)* | Single line | change title |
| Stage | Choice (required) | Requested, Change Advisory Board, Change Authority, Implementation, Review, Close — default **Requested** |
| A6Program | Single line | |
| DSN | Single line | |
| RequestedBy | Single line | |
| RequesterEmail | Single line | |
| Category | Choice | Hardware, Software, Network |
| ChangeType | Choice | Standard, Normal, Emergency, Informational |
| Description | Multiple lines (plain) | |
| Priority | Choice | 4 - Low, 3 - Moderate, 2 - High, 1 - Critical |
| Risk | Choice | 3 - Moderate, 2 - High, 1 - Critical |
| Impact | Choice | 3 - Moderate, 2 - High, 1 - Critical |
| FormResponseId | Number | links the item back to its Forms response |
| PlannedStart | Date and time | |
| PlannedEnd | Date and time | |
| Assignee | Person | |
| CABDecision | Choice | Pending, Approved, Rejected — default Pending |
| CABNotes | Multiple lines (plain) | |
| AuthorityDecision | Choice | Pending, Approved, Rejected — default Pending |
| AuthorityNotes | Multiple lines (plain) | |
| ImplementationNotes | Multiple lines (plain) | |
| ActualStart | Date and time | |
| ActualEnd | Date and time | |
| ReviewOutcome | Choice | Successful, Successful with issues, Failed, Rolled back, Rejected |
| ReviewNotes | Multiple lines (plain) | |
| ClosedDate | Date and time | |

The Rollback Plan PDF and any additional files are saved as **attachments** on the list item. Attachments are switched on by default.

Then create a second list named **Change Request History** with these columns: `RequestID` (Number), `FromStage` (Text), `ToStage` (Text), `Comment` (Multiple lines).

---

## Step 2 — Create the app

1. Go to **make.powerapps.com**, choose **Create**, then **Blank app**, then **Blank canvas app**. Pick the **Tablet** format and name the app *Change Request Portal*.
2. Under **Data**, choose **Add data**, then **SharePoint**, select your site, and tick both lists.
3. Under **Settings**, then **General**, set **Data row limit** to `2000`.
4. Create two screens: **BoardScreen** and **DetailScreen**.

### App.Formulas (named formulas)
Select **App** in the tree view, then set its **Formulas** property:

```powerfx
Stages = Table(
    {Order: 1, Name: "Requested",             Color: ColorValue("#6B7280")},
    {Order: 2, Name: "Change Advisory Board", Color: ColorValue("#2563EB")},
    {Order: 3, Name: "Change Authority",      Color: ColorValue("#7C3AED")},
    {Order: 4, Name: "Implementation",        Color: ColorValue("#D97706")},
    {Order: 5, Name: "Review",                Color: ColorValue("#0891B2")},
    {Order: 6, Name: "Close",                 Color: ColorValue("#16A34A")}
);

// Who can record decisions. Use lower-case emails.
CABMembers        = ["cab.chair@contoso.com", "cab.member@contoso.com"];
ChangeAuthorities = ["change.manager@contoso.com"];

IsCAB       = Lower(User().Email) in CABMembers;
IsAuthority = Lower(User().Email) in ChangeAuthorities;

// Links used by the board buttons. See Change-Request-Form-Setup.md.
FormUrl             = "https://forms.office.com/r/REPLACE_ME";
RollbackTemplateUrl = "https://<tenant>.sharepoint.com/sites/<site>/Shared%20Documents/Change%20Templates/Rollback-Plan-Template.pdf";

PriorityColor(p: Text): Color =
    Switch(p, "1 - Critical", Color.Red, "2 - High", Color.DarkOrange, "3 - Moderate", Color.Goldenrod, Color.Gray);
```

> To manage approvers without editing the app, you can replace the hard-coded email lists with an Entra security group (use the Office 365 Groups connector) or with a small "Approvers" SharePoint list.

---

## Step 3 — BoardScreen (the board)

**BoardScreen.OnVisible**
```powerfx
Refresh('Change Requests')
```

### Header controls
Select **BoardScreen** in the Tree view before inserting each control. The positions assume the default Tablet size (1366 × 768). Keep every header control above **Y = 80**, because that's where `galStages` starts.

> Use the **classic** controls. If your Insert panel shows *Text label*, *Pen input* and *List box*, you're already on classic. The formulas use classic property names such as `txtSearch.Text` and `tglMine.Value`.

| # | Insert | Rename to | Properties |
|---|---|---|---|
| 1 | Text label *(optional title)* | `lblAppTitle` | Text: `"Change Request Portal"` · Size: `20` · FontWeight: `FontWeight.Bold` · X `20` · Y `15` · Width `300` · Height `40` |
| 2 | Text input | `txtSearch` | Default: `""` · HintText: `"Search by title…"` *(grey placeholder shown while empty)* · X `340` · Y `15` · Width `260` · Height `40` |
| 3 | Toggle | `tglMine` | Default: `false` · TrueText: `"My requests"` · FalseText: `"All requests"` · X `620` · Y `15` · Width `200` · Height `40` |
| 4 | Icons › Reload | `icoRefresh` | OnSelect: `Refresh('Change Requests')` · X `840` · Y `20` · Width `30` · Height `30` |
| 5 | Button | `btnTemplate` | Text: `"Download Rollback Plan template"` · OnSelect: `Launch(RollbackTemplateUrl, {}, LaunchTarget.New)` · Fill: `Color.White` · Color: `ColorValue("#1E3A6B")` · BorderColor: `ColorValue("#1E3A6B")` · X `890` · Y `15` · Width `230` · Height `40` |
| 6 | Button | `btnNew` | Text: `"+ Request a New Change"` · OnSelect: `Launch(FormUrl, {}, LaunchTarget.New)` · Fill: `ColorValue("#1E3A6B")` · X `1130` · Y `13` · Width `216` · Height `44` |
| 7 | Timer | `tmrRefresh` | Duration: `60000` · Repeat: `true` · AutoStart: `true` · Visible: `false` · OnTimerEnd: `Refresh('Change Requests')` |

To check the buttons, hold **Alt** and click **btnNew**, which should open the form, then **btnTemplate**, which should open the PDF. The search box and toggle start working once `galCards` (below) is built.

> New requests now come in through the Microsoft Form, and a Power Automate flow creates the list item (see [Change-Request-Form-Setup.md](Change-Request-Form-Setup.md)). It takes a few seconds for a new request to show up. The timer refreshes the board every minute, and users can click the refresh icon to update it immediately.

### `galStages`: one column per stage
Insert a **Blank horizontal gallery** under the header.

| Property | Value |
|---|---|
| Items | `Stages` |
| TemplateSize | `300` |
| TemplatePadding | `8` |
| X / Y | `0` / `80` |
| Height | `Parent.Height - Self.Y` |

Add these controls inside its template:

| Control | Property | Value |
|---|---|---|
| `rectHeader` (Rectangle) | Fill | `ThisItem.Color` |
| | Height / Width | `50` / `Parent.TemplateWidth` |
| `lblHeader` (Label, on top of rectHeader) | Text | `ThisItem.Order & ". " & ThisItem.Name & "  (" & CountRows(galCards.AllItems) & ")"` |
| | Color / FontWeight | `Color.White` / `FontWeight.Semibold` |

### `galCards`: the tickets in each stage
Insert a **Blank vertical gallery** *inside* the `galStages` template, below the header.

| Property | Value |
|---|---|
| Y | `rectHeader.Height + 8` |
| Height | `Parent.TemplateHeight - Self.Y` |
| TemplateSize | `110` |

**Items**: in this property, `ThisItem` refers to the stage (the outer gallery's item):
```powerfx
Sort(
    Filter(
        'Change Requests',
        Stage.Value = ThisItem.Name,
        !tglMine.Value || RequesterEmail = User().Email,
        IsBlank(txtSearch.Text) || StartsWith(Title, txtSearch.Text)
    ),
    Modified,
    SortOrder.Descending
)
```

Add these controls inside the `galCards` template. Here, `ThisItem` refers to the ticket:

| Control | Property | Value |
|---|---|---|
| `rectCard` (Rectangle) | Fill / BorderColor | `Color.White` / `RGBA(0,0,0,0.12)` |
| `rectPriority` (thin rectangle on the left edge) | Fill | `PriorityColor(ThisItem.Priority.Value)` |
| `lblId` | Text | `"CR-" & Text(ThisItem.ID, "00000")` |
| `lblTitle` | Text | `ThisItem.Title` |
| `lblMeta` | Text | `"P" & Left(ThisItem.Priority.Value, 1) & " · " & ThisItem.Category.Value & " · " & ThisItem.ChangeType.Value` |
| `lblRisk` | Text | `"Risk " & Left(ThisItem.Risk.Value, 1) & " · Impact " & Left(ThisItem.Impact.Value, 1)` |
| `lblOwner` | Text | `ThisItem.RequestedBy & " · " & ThisItem.A6Program & " · " & Text(ThisItem.Created, "dd mmm yyyy")` |
| *(gallery)* `galCards` | OnSelect | `Set(varCR, ThisItem); Navigate(DetailScreen, ScreenTransition.Cover)` |

> **Optional:** if the Close column gets too long, add `ClosedDate >= DateAdd(Today(), -30) || Stage.Value <> "Close"` to the Filter so that column only shows changes closed in the last 30 days.

---

## Step 4 — New requests (Microsoft Form + Power Automate)

New change requests are submitted through a **Microsoft Form** rather than a screen in the app. The **+ Request a New Change** button on the board opens the form. When someone submits it, a Power Automate flow:
- creates the item in *Change Requests* with Stage = **Requested**,
- attaches the Rollback Plan PDF and any additional files to that item,
- and writes the first row to the history list.

Full setup is in **[Change-Request-Form-Setup.md](Change-Request-Form-Setup.md)**. When you've finished it, paste the form link into `FormUrl` in App.Formulas.

You don't need a NewScreen. If you already built it, you can delete it.

---

## Step 5 — DetailScreen (view, decide, move the request)

**DetailScreen.OnVisible**: reloads the latest copy of the request:
```powerfx
Set(varCR, LookUp('Change Requests', ID = varCR.ID))
```

### Header
| Control | Property | Value |
|---|---|---|
| `btnHome` | OnSelect | `Navigate(BoardScreen, ScreenTransition.UnCover)` |
| `lblCRTitle` | Text | `"CR-" & Text(varCR.ID, "00000") & " — " & varCR.Title` |

### Progress tracker: `galProgress` (Blank horizontal gallery)
| Property | Value |
|---|---|
| Items | `Stages` |
| TemplateSize | `Parent.Width / 6` |
| Height | `70` |

Inside the template, add a circle (`icoStep`) and a label:
- **icoStep.Fill**
  ```powerfx
  With({cur: LookUp(Stages, Name = varCR.Stage.Value).Order},
      If(ThisItem.Order < cur, ColorValue("#16A34A"),
         ThisItem.Order = cur, ThisItem.Color,
         RGBA(0,0,0,0.15)))
  ```
- **Label.Text**: `ThisItem.Name`
- **Label.FontWeight**: `If(ThisItem.Name = varCR.Stage.Value, FontWeight.Bold, FontWeight.Normal)`

### `frmDetail` (Edit form)
| Property | Value |
|---|---|
| DataSource | `'Change Requests'` |
| Item | `varCR` |
| DefaultMode | `FormMode.Edit` |

Add every field **except Stage, ClosedDate and FormResponseId**. The buttons below control the stage, so leaving it off the form means a save can never overwrite it. Then set each card's **Visible** and **DisplayMode** according to the stage:

| Cards | Visible | DisplayMode |
|---|---|---|
| Request fields: A6Program, DSN, RequestedBy, RequesterEmail, Category, ChangeType, Title, Description, Priority, Risk, Impact, PlannedStart, PlannedEnd | `true` | `If(varCR.Stage.Value = "Requested", DisplayMode.Edit, DisplayMode.View)` |
| **Attachments** (Rollback Plan PDF and additional files; click a file to open it) | `true` | `If(varCR.Stage.Value = "Close", DisplayMode.View, DisplayMode.Edit)` |
| CABDecision, CABNotes | `LookUp(Stages, Name = varCR.Stage.Value).Order >= 2` | `If(varCR.Stage.Value = "Change Advisory Board" && IsCAB, DisplayMode.Edit, DisplayMode.View)` |
| AuthorityDecision, AuthorityNotes | `... .Order >= 3` | `If(varCR.Stage.Value = "Change Authority" && IsAuthority, DisplayMode.Edit, DisplayMode.View)` |
| Assignee, ActualStart, ActualEnd, ImplementationNotes | `... .Order >= 4` | `If(varCR.Stage.Value = "Implementation", DisplayMode.Edit, DisplayMode.View)` |
| ReviewOutcome, ReviewNotes | `... .Order >= 5` | `If(varCR.Stage.Value = "Review", DisplayMode.Edit, DisplayMode.View)` |

**frmDetail.OnSuccess**
```powerfx
Set(varCR, Self.LastSubmit);
Notify("Saved", NotificationType.Success)
```

### Action bar
Add a text input `txtComment` (HintText: `"Comment for the history log"`) and these buttons:

**`btnSave`**
- OnSelect: `SubmitForm(frmDetail)`
- DisplayMode: `If(frmDetail.Unsaved, DisplayMode.Edit, DisplayMode.Disabled)`

**`btnAdvance`**
- Visible: `varCR.Stage.Value <> "Close"`
- DisplayMode: `If(frmDetail.Unsaved, DisplayMode.Disabled, DisplayMode.Edit)`. This forces users to save before moving a request, so the checks below always look at saved data.
- Text:
  ```powerfx
  "Move to " & LookUp(Stages, Order = LookUp(Stages, Name = varCR.Stage.Value).Order + 1).Name & " →"
  ```
- OnSelect:
  ```powerfx
  With({cur: LookUp(Stages, Name = varCR.Stage.Value)},
  With({nxt: LookUp(Stages, Order = cur.Order + 1)},
      If(
          cur.Name = "Change Advisory Board" && varCR.CABDecision.Value <> "Approved",
              Notify("The CAB decision must be Approved before this change can move on.", NotificationType.Error),
          cur.Name = "Change Authority" && varCR.AuthorityDecision.Value <> "Approved",
              Notify("The Change Authority decision must be Approved before this change can move on.", NotificationType.Error),
          cur.Name = "Implementation" && IsBlank(varCR.ImplementationNotes),
              Notify("Add implementation notes before moving to Review.", NotificationType.Error),
          cur.Name = "Review" && IsBlank(varCR.ReviewOutcome.Value),
              Notify("Choose a review outcome before closing.", NotificationType.Error),

          // all checks passed
          Set(varCR, Patch('Change Requests', varCR, {
              Stage:      {Value: nxt.Name},
              ClosedDate: If(nxt.Name = "Close", Now())
          }));
          Patch('Change Request History', Defaults('Change Request History'), {
              Title:     "CR-" & Text(varCR.ID, "00000"),
              RequestID: varCR.ID,
              FromStage: cur.Name,
              ToStage:   nxt.Name,
              Comment:   txtComment.Text
          });
          Reset(txtComment);
          Notify("Moved to " & nxt.Name, NotificationType.Success)
      )
  ))
  ```

**`btnSendBack`**: returns the request to the previous stage (a comment is required)
- Visible: `With({o: LookUp(Stages, Name = varCR.Stage.Value).Order}, o >= 2 && o <= 5)`
- DisplayMode: `If(frmDetail.Unsaved, DisplayMode.Disabled, DisplayMode.Edit)`
- OnSelect:
  ```powerfx
  If(IsBlank(txtComment.Text),
      Notify("Add a comment explaining why it's being sent back.", NotificationType.Warning),
      With({cur: LookUp(Stages, Name = varCR.Stage.Value)},
      With({prv: LookUp(Stages, Order = cur.Order - 1)},
          Set(varCR, Patch('Change Requests', varCR, {Stage: {Value: prv.Name}}));
          Patch('Change Request History', Defaults('Change Request History'), {
              Title:     "CR-" & Text(varCR.ID, "00000"),
              RequestID: varCR.ID,
              FromStage: cur.Name,
              ToStage:   prv.Name,
              Comment:   txtComment.Text
          });
          Reset(txtComment);
          Notify("Sent back to " & prv.Name, NotificationType.Warning)
      ))
  )
  ```

**`btnReject`**: lets approvers reject the request, which moves it straight to Close
- Visible: `(varCR.Stage.Value = "Change Advisory Board" && IsCAB) || (varCR.Stage.Value = "Change Authority" && IsAuthority)`
- Fill: `Color.Firebrick`
- OnSelect:
  ```powerfx
  If(IsBlank(txtComment.Text),
      Notify("Add a comment explaining the rejection.", NotificationType.Warning),
      With({prevStage: varCR.Stage.Value},
          If(prevStage = "Change Advisory Board",
              Set(varCR, Patch('Change Requests', varCR, {
                  Stage: {Value: "Close"}, ReviewOutcome: {Value: "Rejected"}, ClosedDate: Now(),
                  CABDecision: {Value: "Rejected"}, CABNotes: txtComment.Text
              })),
              Set(varCR, Patch('Change Requests', varCR, {
                  Stage: {Value: "Close"}, ReviewOutcome: {Value: "Rejected"}, ClosedDate: Now(),
                  AuthorityDecision: {Value: "Rejected"}, AuthorityNotes: txtComment.Text
              }))
          );
          Patch('Change Request History', Defaults('Change Request History'), {
              Title:     "CR-" & Text(varCR.ID, "00000"),
              RequestID: varCR.ID,
              FromStage: prevStage,
              ToStage:   "Close",
              Comment:   "REJECTED: " & txtComment.Text
          });
          Reset(txtComment);
          Notify("Change rejected and closed", NotificationType.Warning)
      )
  )
  ```

### History panel: `galHistory` (Blank vertical gallery)
- Items:
  ```powerfx
  Sort(Filter('Change Request History', RequestID = varCR.ID), Created, SortOrder.Descending)
  ```
- Line 1: `If(IsBlank(ThisItem.FromStage), "Created", ThisItem.FromStage & " → " & ThisItem.ToStage)`
- Line 2: `ThisItem.Author.DisplayName & " · " & Text(ThisItem.Created, "dd mmm yyyy hh:mm")`
- Line 3: `ThisItem.Comment`

---

## Step 6 — Publish & share

1. Choose **Save**, then **Publish**.
2. Use **Share** to give the app to your users.
3. On the SharePoint site, give the same users **Contribute** permission on both lists. The app works under each user's own permissions.

## Optional extras

- **Email or Teams notifications:** create a Power Automate flow with the trigger *When an item is created or modified* on Change Requests, plus a condition on `Stage`. For example, when Stage = *Change Advisory Board*, post an adaptive card to the CAB Teams channel.
- **Stricter enforcement:** the stage rules are enforced only inside the app, and anyone with Contribute permission could still edit the list directly in SharePoint. If you need rules that can't be bypassed, move stage changes into a Power Automate flow that runs under a service account and make the list read-only for users, or move the data to Dataverse and use security roles.
- **Calendar view:** add a SharePoint calendar view on `PlannedStart`/`PlannedEnd` to get a forward schedule of changes.
