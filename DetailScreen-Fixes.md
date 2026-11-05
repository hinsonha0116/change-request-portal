# App updates: new request fields, New Request clean-up, board filters and email notifications

These changes build on the app from [Change-Request-PowerApp-Guide.md](Change-Request-PowerApp-Guide.md), with all earlier updates already applied, including the New Request screen and the compact detail form.

**What changes:**
1. **New fields on every request:**
   - **Impact details** and **Justification** (large text boxes)
   - **Location** and **Affected systems**
   - **Outage expected?** (Yes/No) and **Outage duration**
2. **The New Request screen gets the same clean-up as the detail screen:** three columns, smaller text and friendly labels, with the large text boxes and Attachments full width at the bottom.
3. **The detail screen** shows all the new fields.
4. **Email when a request is submitted:**
   - **CM team:** every new request.
   - **SW managers:** when Category = **Software**.
   - **HW managers:** when Category = **Hardware**.
5. **Optional:** each email contains a link that opens the request straight in the app.
6. **Board quick filters** for **Category** and **Change type**.
7. **Email at every stage change:**
   - the **CAB** when a request reaches CAB,
   - the **Change Authority** at their stage,
   - the **requester** when it's sent back, approved, rejected or closed,
   - the **CM team** when it's implemented.
8. **Detail screen clean-up** (Part 8, at the end): the newer fields get compact sizes and labels, the decisions share a row, empty fields are hidden once read-only, the outage switch shows *Yes/No*, Assignee shows a name, and read-only dates show on one line.
9. **Technical Review Board and PIR** (Part 9, at the end): a TRB stage for Normal changes, the Review stage renamed **PIR**, a route for each change type (Standard goes straight to Implementation, then Close), *Needs changes*, a TRB checklist, Informational removed for new requests, and a **Completed** button that emails the CM team.
10. **Tidy the action bar and notes tabs** (Part 10, at the end): smaller buttons side by side so they don't cover the comment box, and tab labels that don't wrap.
11. **Line up read-only values** (Part 11, at the end): in read-only mode, drop-down values like Priority and Risk show as plain text lined up under their titles.

> **How to set a property:** select the control in the **Tree view**, choose the property in the dropdown at the left of the formula bar, and paste the value into the formula bar. You can also type X, Y, Width and Height into the **Properties** pane on the right.

> **Control names:** each field (card) has a label `DataCardKeyN` and a value `DataCardValueN`. The numbers differ in every app, so expand a card in the Tree view to see its real names.

**Time:** about 5½ hours in total. Do the parts in order, because the emails and filters use the columns from Part 1.

**Coming later** (after the move to production): **App Roles**, a SharePoint list that holds the CM, CAB, Authority and manager emails in one place, for both the app and the flows.

---

## Part 1 — Add the new columns in SharePoint

Open the **Change Requests** list and add these columns (**+ Add column**). Type each **name exactly as shown**, with no spaces, then click **Save**.

| Name | Type | Settings |
|---|---|---|
| `ImpactDetails` | Multiple lines of text | More options › *Use enhanced rich text* **off** |
| `Justification` | Multiple lines of text | More options › *Use enhanced rich text* **off** |
| `Location` | Single line of text | |
| `AffectedSystems` | Single line of text | |
| `OutageExpected` | Yes/No | Default value **No** |
| `OutageDuration` | Single line of text | Free text, e.g. *30 minutes* |

Once they exist, you can rename the *display* names (e.g. "Impact details", "Outage expected?"). The internal names stay the same.

**Refresh the app's connection:**
1. In Power Apps Studio, click **Data** (the cylinder icon).
2. Next to **Change Requests**, click **⋯ › Refresh**.

Without this, the new columns won't appear in **Edit fields**.

> **Other files to update later:** the provisioning script and the main guide's column table don't include these columns yet. Add them if you ever rebuild the lists from scratch.

---

## Part 2 — New Request screen (`frmNew`): new fields and clean-up

### 2a. Three columns and the new fields
1. Select `frmNew` and set **Columns** to `3` in the **Properties** pane.
2. Click **Edit fields › + Add field** and tick these six: **ImpactDetails**, **Justification**, **Location**, **AffectedSystems**, **OutageExpected** and **OutageDuration**. Click **Add**.
3. **Unlock** each new card: **Properties › Advanced › 🔒 Unlock to change properties**.

### 2b. Put the fields in order
In **Edit fields**, drag the fields into this order:

> A6Program · RequestedBy · DSN · RequesterEmail · Title · Category · ChangeType · Priority · Risk · Impact · PlannedStart · PlannedEnd · OutageExpected · OutageDuration · Location · AffectedSystems · **Description** · **ImpactDetails** · **Justification** · **Attachments** · Stage · SubmittedBy · CABDecision · AuthorityDecision

That gives these rows of three:

| Row | Column 1 | Column 2 | Column 3 |
|---|---|---|---|
| 1 | A6 program | Requested by | DSN |
| 2 | Requester email | Title | Category |
| 3 | Change type | Priority | Risk |
| 4 | Impact | Planned start | Planned end |
| 5 | Outage expected? | Outage duration | Location |
| 6 | Affected systems *(spans all three columns, one line tall)* | | |

Below those rows come the four full-width fields (2d). The four hidden system fields stay at the bottom.

### 2c. Location, Affected systems and the outage fields
1. **Location card:**
   - **Required** = `true`
   - text box **HintText** = `"Base and building, e.g. Ramstein AB, Bldg 400"`
2. **AffectedSystems card:** full width, but only one line tall.
   - **Required** = `true`
   - **WidthFit** = `false` and **Width** = `frmNew.Width - 40` (on the card)
   - text box **HintText** = `"e.g. VDI servers, Exchange"`, **Mode** = `TextMode.SingleLine`, **Height** = `FormValueHeight`
3. **OutageExpected card:** the card contains a **Toggle**. Rename it `tglOutage` and set:
   - **TrueText** = `"Yes"`
   - **FalseText** = `"No"`
4. **OutageDuration card:** set these on the **card**:

   | Property | Value |
   |---|---|
   | Required | `tglOutage.Value` |
   | DisplayMode | `If(tglOutage.Value, DisplayMode.Edit, DisplayMode.Disabled)` |

   Set the text box's **HintText** to `"e.g. 30 minutes"`.

The duration box is greyed out until **Outage expected?** is switched to **Yes**. Once it's Yes, the duration is required.

### 2d. Make the four big fields full width
For each of the **Description**, **ImpactDetails**, **Justification** and **Attachments** cards:

1. Select the **card** and set:

   | Property | Value |
   |---|---|
   | WidthFit | `false` |
   | Width | `frmNew.Width - 40` |

2. Select the **value control** inside it and set:

   | Card | Value control settings |
   |---|---|
   | Description | **Mode** `TextMode.MultiLine` · **Height** `90` |
   | ImpactDetails | **Mode** `TextMode.MultiLine` · **Height** `90` · **HintText** `"Who and what is affected, and how"` |
   | Justification | **Mode** `TextMode.MultiLine` · **Height** `90` · **HintText** `"Why this change is needed"` |
   | Attachments | attachment control **Height** `110` |

3. **Required:** decide whether **ImpactDetails** and **Justification** must be filled in, and set each card's **Required** to `true` or `false`.

   To require Justification **only for Emergency changes**, set its card's **Required** to:
   ```powerfx
   drpChangeType.Selected.Value = "Emergency"
   ```

### 2e. Smaller text and tighter spacing
This uses the sizes already in App.Formulas (`FormLabelSize`, `FormLabelHeight`, `FormValueHeight`). For each **visible** card in `frmNew`, expand it in the Tree view, then:

| Select | Property | Value |
|---|---|---|
| **Ctrl+click** the `DataCardKey…` **and** the value control (same card, so this works) | Size | `FormLabelSize` |
| The `DataCardKey…` only | Height | `FormLabelHeight` |
| The value control only | Height | `FormValueHeight` |

**Which is the value control?**
- **Text cards:** the `DataCardValue…`.
- **Drop-down and picker cards:** `drpA6Program`, `cmbRequestedBy`, and the five choice drop-downs (`drpCategory` and so on), not their hidden combo boxes.
- **Outage expected?:** `tglOutage`.
- **Dates:** `DateValue…`, `HourValue…` and `MinuteValue…` together, with the small hour and minute settings from the detail screen.
- **The four full-width cards:** set **Size** only, and keep their taller heights from 2d.

> **If a card's controls overlap or leave a gap:** select the value control and set its **Y** to `DataCardKeyN.Y + DataCardKeyN.Height + 2`, using that card's own label name.

### 2f. Friendly labels
Select each card's `DataCardKey…` and set **Text**:

| Card | Text |
|---|---|
| A6Program | `"A6 program"` |
| RequestedBy | `"Requested by"` |
| RequesterEmail | `"Requester email"` |
| ChangeType | `"Change type"` |
| PlannedStart / PlannedEnd | `"Planned start"` / `"Planned end"` |
| AffectedSystems | `"Affected systems"` |
| OutageExpected | `"Outage expected?"` |
| OutageDuration | `"Outage duration"` |
| ImpactDetails | `"Impact details"` |
| Attachments | `"Rollback Plan (required) and other attachments"` |

### 2g. Reset the outage switch
Set **`tglOutage` › Reset** to `varResetNew`. Then **+ Request a New Change** always opens with the outage switch on **No**.

---

## Part 3 — Show the new fields on the detail screen (`frmDetail`)

1. Select `frmDetail`, click **Edit fields › + Add field**, tick all six new fields, and click **Add**.
2. Drag them into place:
   - **OutageExpected**, **OutageDuration**, **Location** and **AffectedSystems** go just after **PlannedEnd**.
   - **ImpactDetails** and **Justification** go just before **Attachments**.
3. **Unlock** the six cards, then set on each **card**:
   - **DisplayMode** = `If(varCR.Stage.Value = "Requested", DisplayMode.Edit, DisplayMode.View)`
4. **ImpactDetails and Justification:** set the **card**'s **WidthFit** = `false` and **Width** = `frmDetail.Width - 40`. Set the text box's **Mode** = `TextMode.MultiLine` and **Height** = `90`.
   **AffectedSystems:** set the **card**'s **WidthFit** = `false` and **Width** = `frmDetail.Width - 40` as well, but keep its text box one line tall.
5. **Sizes:** apply the sizes from 2e, and the labels from 2f.


---

## Part 4 — Email when a request is submitted (Power Automate)

A flow watches the **Change Requests** list. Whenever a new request is created, which now happens straight from the app, it emails:
- the **CM team**, every time,
- the **SW managers**, if Category = Software,
- the **HW managers**, if Category = Hardware.

**Network** requests go to the CM team only. Step 4e shows how to add Network managers too.

### 4a. Create the flow
1. Go to **make.powerautomate.com**. Use the government address if your tenant has one.
2. Sign in as the **shared change-management account**, if you have one. Emails are sent from this account's mailbox.
3. Click **+ Create › Automated cloud flow**.
4. Name it **Change Request – New request notifications**.
5. Pick the trigger **When an item is created** (SharePoint) and click **Create**.
6. Set **Site Address** to your site and **List Name** to **Change Requests**.

> The SharePoint trigger checks for new items every few minutes, so emails can arrive **1–5 minutes** after a request is submitted.

### 4b. Who gets the emails
Add three **Initialize variable** actions (under *Variables*):

| Name | Type | Value |
|---|---|---|
| `CMTeamEmails` | String | `cm.lead@us.af.mil;cm.analyst@us.af.mil` |
| `SWManagerEmails` | String | `sw.manager1@us.af.mil;sw.manager2@us.af.mil` |
| `HWManagerEmails` | String | `hw.manager1@us.af.mil;hw.manager2@us.af.mil` |

Replace the example addresses with the real ones, separated by **semicolons**. If your teams have **distribution lists**, use those addresses instead, so membership changes don't need flow edits.

### 4c. Build the email text once
Add these **Compose** actions (under *Data Operation*) and rename each as shown. Paste the expressions using **fx / Expression**:

| Rename to | Inputs (expression) |
|---|---|
| `CRNumber` | `concat('CR-', formatNumber(triggerOutputs()?['body/ID'], '00000'))` |
| `PlannedStartText` | `if(empty(triggerOutputs()?['body/PlannedStart']), 'Not set', convertFromUtc(triggerOutputs()?['body/PlannedStart'], 'W. Europe Standard Time', 'dd MMM yyyy HH:mm'))` |
| `PlannedEndText` | `if(empty(triggerOutputs()?['body/PlannedEnd']), 'Not set', convertFromUtc(triggerOutputs()?['body/PlannedEnd'], 'W. Europe Standard Time', 'dd MMM yyyy HH:mm'))` |
| `OutageText` | `if(equals(triggerOutputs()?['body/OutageExpected'], true), concat('YES – ', triggerOutputs()?['body/OutageDuration']), 'No')` |
| `EmailBody` | see below |

SharePoint stores dates in UTC, so the expressions convert them to **W. Europe Standard Time** (Germany). Change that text if your users work in another time zone.

**`EmailBody` › Inputs:** paste this HTML as plain text. Each `@{...}` becomes the request's value when the flow runs:

```html
<p>A new change request has been submitted.</p>
<table cellpadding="6" style="border-collapse:collapse;font-family:Segoe UI,Arial,sans-serif;font-size:14px">
<tr><td><b>CR number</b></td><td>@{outputs('CRNumber')}</td></tr>
<tr><td><b>Title</b></td><td>@{triggerOutputs()?['body/Title']}</td></tr>
<tr><td><b>Requested by</b></td><td>@{triggerOutputs()?['body/RequestedBy']} (@{triggerOutputs()?['body/RequesterEmail']})</td></tr>
<tr><td><b>A6 program</b></td><td>@{triggerOutputs()?['body/A6Program']}</td></tr>
<tr><td><b>Category / type</b></td><td>@{triggerOutputs()?['body/Category/Value']} / @{triggerOutputs()?['body/ChangeType/Value']}</td></tr>
<tr><td><b>Priority</b></td><td>@{triggerOutputs()?['body/Priority/Value']}</td></tr>
<tr><td><b>Risk / Impact</b></td><td>@{triggerOutputs()?['body/Risk/Value']} / @{triggerOutputs()?['body/Impact/Value']}</td></tr>
<tr><td><b>Planned</b></td><td>@{outputs('PlannedStartText')} to @{outputs('PlannedEndText')}</td></tr>
<tr><td><b>Outage</b></td><td>@{outputs('OutageText')}</td></tr>
<tr><td><b>Location</b></td><td>@{triggerOutputs()?['body/Location']}</td></tr>
<tr><td><b>Affected systems</b></td><td>@{triggerOutputs()?['body/AffectedSystems']}</td></tr>
<tr><td valign="top"><b>Description</b></td><td>@{triggerOutputs()?['body/Description']}</td></tr>
<tr><td valign="top"><b>Impact details</b></td><td>@{triggerOutputs()?['body/ImpactDetails']}</td></tr>
<tr><td valign="top"><b>Justification</b></td><td>@{triggerOutputs()?['body/Justification']}</td></tr>
</table>
<p>Open the Change Request Portal to review it.</p>
```

> If the `@{...}` parts stay as plain text in the email, rebuild each one by hand. Delete it, then insert the matching item from **Dynamic content** (e.g. *Title*, *Category Value*) or the Compose output.

### 4d. Email the CM team (every request)
Add **Send an email (V2)** (Office 365 Outlook):

| Field | Value |
|---|---|
| To | `variables('CMTeamEmails')` *(expression)* |
| Subject | `concat('New change request ', outputs('CRNumber'), ': ', triggerOutputs()?['body/Title'])` *(expression)* |
| Body | **Code view** (`</>`), then insert **Outputs** of `EmailBody` |

### 4e. Email SW or HW managers, by Category
1. Add a **Switch** (under *Control*). Set **On** to `triggerOutputs()?['body/Category/Value']`.
2. **Case `Software`:** add **Send an email (V2)**:
   - **To** = `variables('SWManagerEmails')`
   - **Subject** = `concat('New SOFTWARE change request ', outputs('CRNumber'), ': ', triggerOutputs()?['body/Title'])`
   - **Body** = `EmailBody`
3. **Case `Hardware`:** add the same email, but with:
   - **To** = `variables('HWManagerEmails')`
   - **Subject** using `'New HARDWARE change request '`.
4. **Default:** leave it empty.

The case values must match the SharePoint choices exactly: `Software`, `Hardware`.

To email **Network managers** too, add a `NetworkManagerEmails` variable and a case `Network`.

> **Flag emergencies and outages:** in each email, open **Show advanced options**, click into **Importance**, choose **Enter custom value**, and use:
> `if(or(equals(triggerOutputs()?['body/ChangeType/Value'], 'Emergency'), equals(triggerOutputs()?['body/OutageExpected'], true)), 'High', 'Normal')`

> **Sending from a shared mailbox:** use **Send an email from a shared mailbox (V2)** and put the team mailbox in **Original Mailbox Address**. The flow owner needs *Send As* rights on that mailbox.

### 4f. Save and test
1. Click **Save** and make sure the flow is **On**.
2. Submit a **Software**, a **Hardware** and a **Network** request.
3. Within a few minutes, check that:
   - **CM** gets all three,
   - **SW managers** get only the Software one,
   - **HW managers** get only the Hardware one.

---

## Part 5 — A link in the email that opens the request (optional)

### 5a. Get the app's link
1. In **Power Apps**, go to **Apps**.
2. Click **⋯** next to the app, then **Details**, and copy the **Web link**.

### 5b. Let the app open a request from a link
1. **App › StartScreen:**
   ```powerfx
   If(!IsBlank(Param("crid")), DetailScreen, BoardScreen)
   ```
2. **DetailScreen › OnVisible:** change only the **first line**, the `Set(varCR, …)`, to:
   ```powerfx
   Set(varCR, LookUp('Change Requests', ID = If(IsBlank(varCR), Value(Param("crid")), varCR.ID)));
   ```
   Keep the `Set(varNoteTab, …)` line after it.
3. **Save** and **Publish**.

### 5c. Add the link to the emails
In **`EmailBody`** (Part 4) and **`StageBody`** (Part 7), replace the last line with this, pasting your web link where shown:
```html
<p><a href="YOUR-WEB-LINK&crid=@{triggerOutputs()?['body/ID']}">Open @{outputs('CRNumber')} in the Change Request Portal</a></p>
```

Two adjustments:
- **In `StageBody`**, use `@{triggerOutputs()?['body/RequestID']}` instead of `body/ID`.
- **If your web link has no `?`**, use `?crid=` instead of `&crid=`.

> Anyone who receives the link can open that request, even if the board would normally hide it from them.

---

## Part 6 — Board quick filters: Category and Change type

### 6a. Filter lists (App.Formulas)
Add to the **end**:
```powerfx
CategoryFilter   = ["All categories", "Hardware", "Software", "Network"];
ChangeTypeFilter = ["All types", "Standard", "Normal", "Emergency", "Informational"];
```

### 6b. Make room in the board header
**Download Rollback Plan template** is now on the New Request screen, so the board doesn't need it. Select **`btnTemplate`** and either delete it or set **Visible** to `false`.

Then position the header controls like this, all at **Y** `15` and **Height** `40`:

| Control | X | Width | Notes |
|---|---|---|---|
| `lblAppTitle` | `20` | `280` | |
| `txtSearch` | `310` | `190` | |
| `drpFilterCategory` | `510` | `130` | new (6c) |
| `drpFilterType` | `650` | `140` | new (6c) |
| `tglMine` | `800` | `150` | |
| `icoRefresh` | `960` | `30` | Y `20`, Height `30` |
| *(free)* | `1000` | `120` | kept for the **Schedule** button in [Forward-Schedule-of-Change.md](Forward-Schedule-of-Change.md) |
| `btnNew` | `1130` | `216` | Y `13`, Height `44` |

### 6c. Add the two filter drop-downs
Select **BoardScreen** (not a gallery). Insert two **Drop down** controls and set:

| Property | `drpFilterCategory` | `drpFilterType` |
|---|---|---|
| Items | `CategoryFilter` | `ChangeTypeFilter` |
| Default | `"All categories"` | `"All types"` |
| Size | `11` | `11` |
| X / Y / Width / Height | from the table in 6b | from the table in 6b |

### 6d. Use them in the card filter
Select **`galCards`** (inside `galStages`) and replace **Items** with:
```powerfx
Sort(
    Filter(
        'Change Requests',
        Stage.Value = ThisItem.Name,
        (CanSeeAll && !tglMine.Value) || SubmittedBy = User().Email || RequesterEmail = User().Email,
        IsBlank(txtSearch.Text) || StartsWith(Title, txtSearch.Text),
        drpFilterCategory.Selected.Value = "All categories" || Category.Value = drpFilterCategory.Selected.Value,
        drpFilterType.Selected.Value = "All types" || ChangeType.Value = drpFilterType.Selected.Value
    ),
    Modified,
    SortOrder.Descending
)
```

The column counts in the stage headers follow the filters automatically.

---

## Part 7 — Email at every stage change (Power Automate)

Every Move, Send back and Reject already adds a row to **Change Request History**. A second flow watches that list and emails the right people for the stage the request moved **to**:

| Moved to | Who gets the email | Subject starts with |
|---|---|---|
| Requested *(sent back, or TRB "needs changes")* | Requester | *CR-… was sent back to you* or *CR-… needs changes before TRB review* |
| Technical Review Board | TRB members | *CR-… is ready for TRB review* |
| Change Advisory Board | CAB members | *CR-… is ready for CAB review* |
| Change Authority | Change Authorities | *CR-… is awaiting Change Authority approval* |
| Implementation | Requester, CC CM team | *CR-… is approved for implementation* |
| Implementation complete *(the **Completed** button, Part 9)* | CM team | *CR-… has been completed by the implementer* |
| PIR *(post-implementation review)* | CM team | *CR-… has been implemented and is ready for PIR* |
| Close | Requester, CC CM team | *CR-… is closed* or *CR-… was rejected* |

Comments (Add comment) and new submissions don't send these emails.

### 7a. Create the flow
1. **+ Create › Automated cloud flow.** Name it **Change Request – Stage notifications**.
2. Pick the trigger **When an item is created** (SharePoint), with **List Name** = **Change Request History**.
3. **Skip comments and new submissions.** On the trigger, open **⋯ › Settings**, then under **Trigger conditions** click **+ Add** and paste:
   ```
   @and(not(empty(triggerBody()?['FromStage'])), not(equals(triggerBody()?['FromStage'], triggerBody()?['ToStage'])))
   ```
   Click **Done**. The flow now runs only for real stage moves.

### 7b. Get the request and the recipients
1. Add **Get item** (SharePoint):
   - **Site Address** = your site
   - **List Name** = **Change Requests**
   - **Id** = **RequestID** (dynamic content from the trigger)
2. Add **Initialize variable** actions:

   | Name | Type | Value |
   |---|---|---|
   | `CMTeamEmails` | String | same as Part 4 |
   | `TRBEmails` | String | `trb.chair@us.af.mil;trb.member@us.af.mil` |
   | `CABEmails` | String | `cab.chair@us.af.mil;cab.member@us.af.mil` |
   | `AuthorityEmails` | String | `change.authority@us.af.mil` |

3. Add **Compose** actions:

   | Rename to | Inputs (expression) |
   |---|---|
   | `CRNumber` | `concat('CR-', formatNumber(triggerOutputs()?['body/RequestID'], '00000'))` |
   | `RequesterEmails` | `concat(body('Get_item')?['RequesterEmail'], ';', body('Get_item')?['SubmittedBy'])` |
   | `StageBody` | see below |

**`StageBody` › Inputs:**
```html
<p><b>@{outputs('CRNumber')} — @{body('Get_item')?['Title']}</b> moved from <b>@{triggerOutputs()?['body/FromStage']}</b> to <b>@{triggerOutputs()?['body/ToStage']}</b>.</p>
<table cellpadding="6" style="border-collapse:collapse;font-family:Segoe UI,Arial,sans-serif;font-size:14px">
<tr><td><b>By</b></td><td>@{triggerOutputs()?['body/Author/DisplayName']}</td></tr>
<tr><td valign="top"><b>Comment</b></td><td>@{triggerOutputs()?['body/Comment']}</td></tr>
<tr><td><b>Requested by</b></td><td>@{body('Get_item')?['RequestedBy']}</td></tr>
<tr><td><b>Category / type</b></td><td>@{body('Get_item')?['Category']?['Value']} / @{body('Get_item')?['ChangeType']?['Value']}</td></tr>
<tr><td><b>Priority</b></td><td>@{body('Get_item')?['Priority']?['Value']}</td></tr>
<tr><td><b>Location</b></td><td>@{body('Get_item')?['Location']}</td></tr>
</table>
<p>Open the Change Request Portal to see the full request.</p>
```

### 7c. Send to the right people
1. Add a **Switch**. Set **On** to `triggerOutputs()?['body/ToStage']`.
2. Add one case per row below. Inside each case, add **Send an email (V2)** with **Body** = **Code view** + the `StageBody` output. To use **CC**, open **Show advanced options**.

| Case equals | To | CC | Subject (expression) |
|---|---|---|---|
| `Requested` | `outputs('RequesterEmails')` | | `concat(outputs('CRNumber'), if(startsWith(triggerOutputs()?['body/Comment'], 'NEEDS CHANGES'), ' needs changes before TRB review: ', ' was sent back to you: '), body('Get_item')?['Title'])` |
| `Technical Review Board` | `variables('TRBEmails')` | | `concat(outputs('CRNumber'), ' is ready for TRB review: ', body('Get_item')?['Title'])` |
| `Change Advisory Board` | `variables('CABEmails')` | | `concat(outputs('CRNumber'), ' is ready for CAB review: ', body('Get_item')?['Title'])` |
| `Change Authority` | `variables('AuthorityEmails')` | | `concat(outputs('CRNumber'), ' is awaiting Change Authority approval: ', body('Get_item')?['Title'])` |
| `Implementation` | `outputs('RequesterEmails')` | `variables('CMTeamEmails')` | `concat(outputs('CRNumber'), ' is approved for implementation: ', body('Get_item')?['Title'])` |
| `Implementation complete` | `variables('CMTeamEmails')` | | `concat(outputs('CRNumber'), ' has been completed by the implementer: ', body('Get_item')?['Title'])` |
| `PIR` | `variables('CMTeamEmails')` | | `concat(outputs('CRNumber'), ' has been implemented and is ready for PIR: ', body('Get_item')?['Title'])` |
| `Close` | `outputs('RequesterEmails')` | `variables('CMTeamEmails')` | `concat(outputs('CRNumber'), if(equals(body('Get_item')?['ReviewOutcome']?['Value'], 'Rejected'), ' was rejected: ', ' is closed: '), body('Get_item')?['Title'])` |

The case values must match the stage names exactly, including spaces and capitals.

### 7d. Save and test
1. Click **Save** and make sure the flow is **On**.
2. Take a test request through every stage, then send it back once and reject another.
3. Check that each email reaches the right people, as in the table at the top of Part 7.
4. Add a comment with **Add comment**. **No** email should be sent.

---

## Test

| # | Do this | Expect |
|---|---|---|
| 1 | Click **+ Request a New Change** | Three columns and smaller text; rows match 2b; the four big fields are full width at the bottom |
| 2 | Look at **Outage duration** | Greyed out while **Outage expected?** is *No*; editable and required once it's *Yes* |
| 3 | Submit without Location or Affected systems | Error: *Fill in every field marked with a red star* |
| 4 | Submit a full **Software** request with an outage | Saved; SharePoint shows all the new fields filled in |
| 5 | Open it on the detail screen | The new fields show, editable while in *Requested* |
| 6 | Wait up to 5 minutes | **CM** and **SW managers** get the new-request email, with the Outage and Location rows; marked High importance if you did the tip in 4e |
| 7 | Submit a **Hardware** and a **Network** request | HW managers get only the Hardware one; Network goes to CM only |
| 8 | On the board, choose **Software** in the category filter | Only Software cards show, and the column counts update |
| 9 | Choose **Emergency** in the type filter, then set both back to *All* | Only Emergency cards show, then everything again |
| 10 | **Move** a request to CAB | The CAB gets *"… is ready for CAB review"*, with the comment |
| 11 | **Send back** a request to Requested | The requester gets *"… was sent back to you"* |
| 12 | **Reject** a request | The requester (CC CM) gets *"… was rejected"* |
| 13 | Use **Add comment** | No stage email is sent |
| 14 | Click a link in an email *(if you did Part 5)* | The app opens on that request |

**If something goes wrong:**
- **The new fields aren't in Edit fields:** refresh the data source (end of Part 1).
- **`tglOutage` isn't recognized:** rename the toggle inside the OutageExpected card to exactly `tglOutage`.
- **No email at all:** check the flow is **On** and look at its **Run history**. If there's no run, check the trigger's site and list. If a run failed, open it to see which step.
- **A stage flow runs for comments too:** check the trigger condition in 7a was saved (**⋯ › Settings**).
- **A stage email goes to nobody:** the Switch case must match the stage name exactly, e.g. `Change Advisory Board`.
- **Filters show nothing:** the filter lists must match the SharePoint choices exactly, and the "All" entries must match the text in the `galCards` formula (`All categories`, `All types`).
- **The email shows `@{...}` text:** rebuild those parts with **Dynamic content** (see the note in 4c).
- **The times are off:** change the time zone name in `PlannedStartText` and `PlannedEndText`.
- **Anything else in the app:** open the **App checker** (the stethoscope icon) and send me the exact text of any red error banner.

---

## Part 8 — Detail screen clean-up (read-only fields)

This tidies the detail screen once a request has moved past *Requested*:
- the newer fields get the compact sizes and friendly labels,
- the decisions share a row,
- empty fields are hidden,
- the Outage switch reads *Yes/No*,
- Assignee shows a name,
- read-only dates show on one line.

All changes are in `frmDetail` on the **DetailScreen**. Unlock each card first if needed: **Properties › Advanced › 🔒 Unlock to change properties**.

### 8a. Sizes and labels on the newer cards
For **OutageExpected**, **OutageDuration**, **Location**, **AffectedSystems**, **ImpactDetails**, **Justification**, **CABDecision**, **AuthorityDecision**, **Assignee**, **ActualStart**, **ActualEnd** and **ReviewOutcome**, apply the same steps as the rest of the form:

| Select | Property | Value |
|---|---|---|
| **Ctrl+click** the `DataCardKey…` **and** the value control (same card) | Size | `FormLabelSize` |
| The `DataCardKey…` only | Height | `FormLabelHeight` |
| The value control only | Height | `FormValueHeight` *(not ImpactDetails or Justification, which keep `90`)* |

Then set each label's **Text**:

| Card | Text |
|---|---|
| OutageExpected | `"Outage expected?"` |
| OutageDuration | `"Outage duration"` |
| AffectedSystems | `"Affected systems"` |
| ImpactDetails | `"Impact details"` |
| CABDecision | `"CAB decision"` |
| AuthorityDecision | `"Authority decision"` |
| ActualStart / ActualEnd | `"Actual start"` / `"Actual end"` |
| ReviewOutcome | `"PIR outcome"` |

### 8b. Let the decisions share a row
If **CABDecision** or **AuthorityDecision** sits alone on its row, its card is stretching to fill the row. Select each of those **cards** and set **WidthFit** = `false`.

Check **Assignee**, **ActualStart**, **ActualEnd** and **ReviewOutcome** the same way. Only the full-width cards should have a fixed full **Width**: ImpactDetails, Justification, AffectedSystems and Attachments.

**Still on their own row?** Two more things to check:
1. **Hidden cards in between.** In **Edit fields**, drag every hidden card to the very **bottom** of the list, below Attachments: Description, CABNotes, AuthorityNotes, ImplementationNotes, ReviewNotes, and later TRBNotes and ImplementationComplete. Hidden cards sitting between visible ones upset the 3-column layout. Moving them fixed it when this was first built.
2. **An old width.** If a card still has its width from the 2-column layout (about 400), set the card's **Width** to `frmDetail.Width / 3 - 15`, and the control inside it to `Parent.Width - 40`.

### 8c. Hide empty fields once they can't be edited
Set each **card**'s **Visible**:

| Card | Visible |
|---|---|
| OutageDuration | `ThisItem.OutageExpected \|\| varCR.Stage.Value = "Requested"` |
| Location | `!IsBlank(ThisItem.Location) \|\| varCR.Stage.Value = "Requested"` |
| AffectedSystems | `!IsBlank(ThisItem.AffectedSystems) \|\| varCR.Stage.Value = "Requested"` |
| ImpactDetails | `!IsBlank(ThisItem.ImpactDetails) \|\| varCR.Stage.Value = "Requested"` |
| Justification | `!IsBlank(ThisItem.Justification) \|\| varCR.Stage.Value = "Requested"` |

How it behaves:
- **While the request is in *Requested*,** every field shows, so it can be filled in.
- **At later stages,** an empty field disappears and the rest move up.
- **Hidden cards still save** their existing values, so nothing is lost.

### 8d. "Off" → "Yes / No"
Select the toggle inside **OutageExpected** and set:
- **TrueText** = `"Yes"`
- **FalseText** = `"No"`

### 8e. Assignee shows a name, not `i:0#.f|membership…`
1. Select the combo box inside the **Assignee** card and set **DisplayFields** = `["DisplayName"]`.
2. If it **still** shows the long ID when the request is read-only:
   1. Set the combo box's **Visible** to `Parent.DisplayMode = DisplayMode.Edit`.
   2. Select the **card**, insert a **Text label** inside it, rename it `lblAssigneeView`, and set:

      | Property | Value |
      |---|---|
      | Text | see below |
      | Visible | `Parent.DisplayMode = DisplayMode.View` |
      | X / Y / Width | the combo box's X, Y and Width |
      | Height / Size | `FormValueHeight` / `FormLabelSize` |

      **Text** shows the short name, in the same *First Last* style as the board:
      ```powerfx
      With({n: ThisItem.Assignee.DisplayName},
          If(Find(",", n) > 0,
              Proper(First(Split(Trim(Mid(n, Find(",", n) + 1)), " ")).Value & " " & Trim(Left(n, Find(",", n) - 1))),
              n))
      ```

### 8f. Read-only dates on one line
For each date card (**PlannedStart**, **PlannedEnd**, **ActualStart**, **ActualEnd**):

1. **Ctrl+click** its `DateValue…`, `HourValue…` and `MinuteValue…` (same card) and set **Visible** = `Parent.DisplayMode = DisplayMode.Edit`. Also hide the small `:` label if there is one.
2. Select the **card**, insert a **Text label** inside it, and set:

   | Property | Value |
   |---|---|
   | Text | `If(IsBlank(ThisItem.PlannedStart), "—", Text(ThisItem.PlannedStart, "dd mmm yyyy  hh:mm"))` *(use that card's own column, e.g. `ThisItem.ActualEnd`)* |
   | Visible | `Parent.DisplayMode = DisplayMode.View` |
   | X / Y | the `DateValue…` control's X and Y |
   | Width | `Parent.Width - 40` |
   | Height / Size | `FormValueHeight` / `FormLabelSize` |

Read-only dates show as **22 Oct 2026  11:00**. Whenever the card is editable, the pickers come back instead:
- **PlannedStart and PlannedEnd** in *Requested*,
- **ActualStart and ActualEnd** in *Implementation*.

The card still saves from the hidden pickers, so nothing changes in SharePoint.

### Part 8 tests

| # | Do this | Expect |
|---|---|---|
| 1 | Open a request past *Requested* with no Location, Affected systems or outage | Those fields are hidden; the rest move up with no gaps |
| 2 | Open a request in *Requested* | Every field shows and can be edited, including empty ones |
| 3 | Look at **CAB decision** and **Authority decision** | They sit side by side with other fields, not alone on a row |
| 4 | Look at **Outage expected?** | Shows *Yes* or *No*, not *On/Off* |
| 5 | Open a request with an Assignee, at *PIR* or *Close* | Shows a short name, e.g. *Hayley Hinson* |
| 6 | Look at the planned dates on a request at *CAB* or later | One line each, e.g. *22 Oct 2026  11:00* |
| 7 | Open a request in *Implementation* | Actual start and end show date pickers; set them, **Save changes**, and reopen to check they saved |
| 8 | Open a request in *Requested*, change a planned date and save | The pickers show, and the new date saves |

---

## Part 9 — Technical Review Board, routing by change type, PIR, and a Completed button

**What changes:**
- **New stage: Technical Review Board (TRB),** between Requested and CAB. **Only Normal changes** go through it.
- **Each change type follows its own route:**

  | Change type | Route |
  |---|---|
  | **Normal** | Requested → **TRB** → CAB → Change Authority → Implementation → PIR → Close |
  | **Emergency** | Requested → CAB → Change Authority → Implementation → PIR → Close |
  | **Standard** | Requested → Implementation → Close |
  | *Informational (existing requests only)* | Requested → CAB → Change Authority → Implementation → PIR → Close |

- **Informational** can no longer be chosen for new requests. Existing Informational requests are left as they are and keep their old route.
- **The Review stage is renamed PIR** (post-implementation review), everywhere in the app, the emails and SharePoint.
- **TRB decision:** *Approved*, *Needs changes* or *Rejected*.
  - **Needs changes** sends the request straight back to the requester, with the TRB's comment.
  - When the CM team moves it on again, the decision resets to *Pending*.
- **TRB checklist:** three Yes/No checks (rollback plan reviewed, tested, security/STIG impact reviewed). **None is required** for now.
- **A TRB tab** in the notes box, and the **progress tracker** shows only the stages on that request's route.
- **The Completed button:** during **Implementation**, it marks the work as done and emails the **CM team** (Part 7 flow), who then move the request on. On the board, the card shows **✔ Complete**.

> **How to set a property:** select the control in the **Tree view**, choose the property in the dropdown at the left of the formula bar, and paste the value into the formula bar. Unlock form cards first if needed: **Properties › Advanced › 🔒 Unlock to change properties**.

**Time:** about 2 hours.

### 9a. SharePoint changes (Change Requests list)
1. **Stage column:** open its settings and add the choice `Technical Review Board`, directly **after** `Requested`. Keep the spelling and capitals exactly as shown.
2. **ChangeType column:** delete the choice `Informational`. Existing requests keep their value. It just can't be picked for new ones.
3. **Add these columns:**

   | Name | Type | Settings |
   |---|---|---|
   | `TRBDecision` | Choice | `Pending`, `Approved`, `Needs changes`, `Rejected` · default **Pending** |
   | `TRBNotes` | Multiple lines of text | More options › *Use enhanced rich text* **off** |
   | `TRBRollbackReviewed` | Yes/No | Default **No** |
   | `TRBTested` | Yes/No | Default **No** |
   | `TRBSecurityReviewed` | Yes/No | Default **No** |
   | `ImplementationComplete` | Yes/No | Default **No** |

4. **Rename Review to PIR** in the **Stage** column:
   1. Open the column's settings, change the choice `Review` to `PIR`, and click **Save**.
   2. SharePoint doesn't update requests that are *already* in Review. In the **Change Requests** list, filter **Stage** to *Review*, then edit each of those requests and set Stage to **PIR**. In a list view, **Edit in grid view** makes this quick.
   3. Old **History** rows keep saying *Review*. They're a record of what happened, so leave them as they are.
5. In Power Apps Studio, go to **Data › ⋯ › Refresh** next to **Change Requests**.

### 9b. App.Formulas
**Replace** the existing `Stages` table with the one below. The new **Short** field gives the board shorter column titles. The **Types** field lists the change types that pass through each stage, and that one list controls every route in the app.

```powerfx
Stages = Table(
    {Order: 1, Name: "Requested",              Short: "Requested",      Color: ColorValue("#6B7280"), Types: "Standard,Normal,Emergency,Informational"},
    {Order: 2, Name: "Technical Review Board", Short: "TRB",            Color: ColorValue("#0D9488"), Types: "Normal"},
    {Order: 3, Name: "Change Advisory Board",  Short: "CAB",            Color: ColorValue("#2563EB"), Types: "Normal,Emergency,Informational"},
    {Order: 4, Name: "Change Authority",       Short: "Authority",      Color: ColorValue("#7C3AED"), Types: "Normal,Emergency,Informational"},
    {Order: 5, Name: "Implementation",         Short: "Implementation", Color: ColorValue("#D97706"), Types: "Standard,Normal,Emergency,Informational"},
    {Order: 6, Name: "PIR",                    Short: "PIR",            Color: ColorValue("#0891B2"), Types: "Normal,Emergency,Informational"},
    {Order: 7, Name: "Close",                  Short: "Close",          Color: ColorValue("#16A34A"), Types: "Standard,Normal,Emergency,Informational"}
);
```

To change a route later, for example when the Emergency process is finalised, edit the **Types** text on the stages concerned.

Then make these changes:

1. **Add the TRB members**, next to the CAB lines:
   ```powerfx
   TRBMembers = ["trb.chair@us.af.mil", "trb.member@us.af.mil"];
   IsTRB      = Lower(User().Email) in TRBMembers;
   ```
2. **Let TRB members see every request.** Change `CanSeeAll` to:
   ```powerfx
   CanSeeAll = IsCM || IsTRB || IsCAB || IsAuthority;
   ```
3. **Remove `"Informational"`** from both `ChangeTypeChoices` and `ChangeTypeFilter`.
4. **Replace the `NoteTabs` table** with this one, which adds the TRB tab:
   ```powerfx
   NoteTabs = Table(
       {Key: "Description",    Label: "Description", StageName: "Requested"},
       {Key: "TRB",            Label: "TRB",         StageName: "Technical Review Board"},
       {Key: "CAB",            Label: "CAB",         StageName: "Change Advisory Board"},
       {Key: "Authority",      Label: "Authority",   StageName: "Change Authority"},
       {Key: "Implementation", Label: "Implement",   StageName: "Implementation"},
       {Key: "Review",         Label: "PIR",         StageName: "PIR"}
   );
   ```

### 9c. The board: seven columns
1. **`galStages` › TemplateSize:** `Self.Width / 7 - 9`.
2. **`lblHeader` › Text:** this uses the short names:
   ```powerfx
   ThisItem.Order & ". " & ThisItem.Short & "  (" & CountRows(galCards.AllItems) & ")"
   ```
3. **`lblId` (on each card):** shows **✔ Complete** once the implementer clicks Completed.
   - **Text:**
     ```powerfx
     "CR-" & Text(ThisItem.ID, "00000") & If(ThisItem.Stage.Value = "Implementation" && ThisItem.ImplementationComplete, "   ✔ Complete", "")
     ```
   - **Color:**
     ```powerfx
     If(ThisItem.Stage.Value = "Implementation" && ThisItem.ImplementationComplete, ColorValue("#16A34A"), RGBA(0,0,0,0.55))
     ```

> Columns are about 186 pixels wide now, so long titles and names wrap or cut off sooner. If the **Close** column gets crowded, add `Stage.Value <> "Close" || ClosedDate >= DateAdd(Today(), -30)` to the `galCards` Filter to show only the last 30 days there.

### 9d. Progress tracker shows only this request's route
On the **DetailScreen**, set:

| Control | Property | Value |
|---|---|---|
| `galProgress` | Items | `Filter(Stages, Coalesce(varCR.ChangeType.Value, "Normal") in Types)` |
| `galProgress` | TemplateSize | `Self.Width / CountRows(Filter(Stages, Coalesce(varCR.ChangeType.Value, "Normal") in Types)) - 1` |
| `lblStepNum` | Text | `CountRows(Filter(Stages, Coalesce(varCR.ChangeType.Value, "Normal") in Types, Order <= ThisItem.Order))` |

The numbers count steps on that request's route. A Standard change shows **1 Requested · 2 Implementation · 3 Close**. `circStep` and `lblStepName` stay as they are.

### 9e. TRB fields on the detail form
1. Select `frmDetail` and click **Edit fields › + Add field**. Tick **TRBDecision**, **TRBRollbackReviewed**, **TRBTested**, **TRBSecurityReviewed**, **TRBNotes** and **ImplementationComplete**, then click **Add**.
2. **Placement:**
   - Drag the four TRB fields to just **before** CABDecision.
   - Drag **TRBNotes** and **ImplementationComplete** to the **bottom**, with the other hidden cards.
3. **Hidden cards:**
   - On **TRBNotes**, set **Visible** = `false` and **Update** = `If(lblEditableNote.Text = "TRB", txtNote.Text, ThisItem.TRBNotes)`.
   - On **ImplementationComplete**, set **Visible** = `false`. Leave its Update as it is.
4. **On the four TRB cards:**
   - **DisplayMode** = `If(varCR.Stage.Value = "Technical Review Board" && IsTRB, DisplayMode.Edit, DisplayMode.View)`
   - Inside each of the three checklist cards, set the toggle's **TrueText** = `"Yes"` and **FalseText** = `"No"`.
   - **Labels:** *TRB decision*, *Rollback plan reviewed*, *Tested in lab / test*, *Security / STIG impact reviewed*.
   - Apply the sizes from Part 8a.
5. **Update every stage card's Visible.** Each card appears once its stage is reached, but only if that stage is on the request's route. Use this pattern, putting the card's stage name in `"STAGE"`:
   ```powerfx
   With({s: LookUp(Stages, Name = "STAGE")},
       LookUp(Stages, Name = varCR.Stage.Value).Order >= s.Order &&
       Coalesce(varCR.ChangeType.Value, "Normal") in s.Types)
   ```

   | Cards | `"STAGE"` |
   |---|---|
   | TRBDecision, TRBRollbackReviewed, TRBTested, TRBSecurityReviewed | `"Technical Review Board"` |
   | CABDecision | `"Change Advisory Board"` |
   | AuthorityDecision | `"Change Authority"` |
   | Assignee, ActualStart, ActualEnd | `"Implementation"` |
   | ReviewOutcome | `"PIR"` |

   This **replaces** the old `.Order >= 2` / `>= 3` rules, which no longer line up now that the stages have moved. A Standard change will never show CAB, Authority or TRB fields.

6. **Rename the PIR labels:** set the **ReviewOutcome** card's label **Text** to `"PIR outcome"`. The notes tab already says **PIR** (from `NoteTabs` in 9b).

   Inside the formulas, the PIR notes tab keeps the key `"Review"` on purpose. It's only an internal name that links the tab to the **ReviewNotes** column, so it doesn't need to change.

### 9f. Notes tabs
| Control | Property | New value |
|---|---|---|
| `galNoteTabs` | Items | see below |
| `galNoteTabs` | TemplateSize | `Self.Width / 6` |
| `lblTab` | Size | `9` *(six tabs are tighter)* |

**`galNoteTabs` › Items:**
```powerfx
With({curOrder: LookUp(Stages, Name = varCR.Stage.Value).Order, type: Coalesce(varCR.ChangeType.Value, "Normal")},
    Filter(NoteTabs As t,
        With({s: LookUp(Stages, Name = t.StageName)}, s.Order <= curOrder && type in s.Types)))
```

**`lblEditableNote` › Text:** add the TRB line:
```powerfx
Switch(varCR.Stage.Value,
    "Requested",              "Description",
    "Technical Review Board", If(IsTRB, "TRB", ""),
    "Change Advisory Board",  If(IsCAB, "CAB", ""),
    "Change Authority",       If(IsAuthority, "Authority", ""),
    "Implementation",         "Implementation",
    "PIR",                    "Review",
    "")
```

**Add `"TRB", varCR.TRBNotes,`** to the `Switch` in both of these, right after the `"Description"` line:
- `txtNote` › **Default**
- `lblNote` › **Text**

**DetailScreen › OnVisible:** replace the `Set(varNoteTab, …)` line with this, which adds TRB:
```powerfx
Set(varNoteTab, Switch(varCR.Stage.Value,
    "Technical Review Board", "TRB",
    "Change Advisory Board",  "CAB",
    "Change Authority",       "Authority",
    "Implementation",         "Implementation",
    "PIR",                    "Review",
    "Close",                  "Review",
    "Description"))
```

### 9g. Action bar: Needs changes, Completed, and route-aware buttons
**New layout** (every control at Y `Parent.Height - 62`, Height `44`):

| Control | X | Width | Shown when |
|---|---|---|---|
| `btnSendBack` | 20 | 150 | CM, any stage except Requested and Close |
| `btnReject` | 180 | 130 | TRB / CAB / Authority members at their stage |
| `btnCompleted` *(new)* | 180 | 130 | Implementation, until marked complete |
| `btnAddComment` | 320 | 120 | always |
| `btnNeedsChanges` *(new)* | 450 | 150 | TRB members at the TRB stage |
| `txtComment` | 610 | 395 | always |
| `btnAdvance` | 1015 | 331 | CM, any stage except Close |

`btnReject` and `btnCompleted` share a spot, because they're never visible at the same time.

**`btnAdvance`** (OnSelect unchanged):
- **Text:**
  ```powerfx
  With({type: Coalesce(varCR.ChangeType.Value, "Normal"), cur: LookUp(Stages, Name = varCR.Stage.Value)},
      "Move to " & First(Sort(Filter(Stages, Order > cur.Order, type in Types), Order)).Name & " →")
  ```
- **Visible:** `varCR.Stage.Value <> "Close" && IsCM`

**`btnSendBack`** (OnSelect unchanged) › **Visible:**
```powerfx
!(varCR.Stage.Value in ["Requested", "Close"]) && IsCM
```

**`btnReject`** (OnSelect unchanged) › **Visible:**
```powerfx
(varCR.Stage.Value = "Technical Review Board" && IsTRB) ||
(varCR.Stage.Value = "Change Advisory Board" && IsCAB) ||
(varCR.Stage.Value = "Change Authority" && IsAuthority)
```

**`btnNeedsChanges`:** insert a **Button** on DetailScreen and set:

| Property | Value |
|---|---|
| Text | `"Needs changes"` |
| Fill | `Color.White` |
| Color / BorderColor | `ColorValue("#B45309")` |
| Visible | `varCR.Stage.Value = "Technical Review Board" && IsTRB` |
| OnSelect | `If(IsBlank(Trim(txtComment.Text)), Notify("Add a comment saying what needs to change.", NotificationType.Warning), Set(varAction, "needschanges"); SubmitForm(frmDetail))` |

**`btnCompleted`:** insert a **Button** on DetailScreen and set:

| Property | Value |
|---|---|
| Text | `"✔ Completed"` |
| Fill | `ColorValue("#16A34A")` |
| Visible | `varCR.Stage.Value = "Implementation" && !varCR.ImplementationComplete` |
| OnSelect | `Set(varAction, "complete"); SubmitForm(frmDetail)` |

Anyone who can open the request can click **Completed**, usually the implementer. It requires **Implementation notes** first. The comment box is optional and goes into the History.

### 9h. `frmDetail` › OnSuccess (replace the whole formula)
This version:
- follows each change type's route,
- adds the TRB approval rule, Needs changes and Completed,
- resets the TRB decision when a request comes back to the TRB,
- includes the TRB tab.

```powerfx
Set(varCR, Self.LastSubmit);
With({type: Coalesce(varCR.ChangeType.Value, "Normal"), cur: LookUp(Stages, Name = varCR.Stage.Value)},
Switch(varAction,
    "advance",
        With({nxt: First(Sort(Filter(Stages, Order > cur.Order, type in Types), Order))},
            If(
                cur.Name = "Technical Review Board" && varCR.TRBDecision.Value <> "Approved",
                    Notify("The TRB decision must be Approved before this change can move on.", NotificationType.Error),
                cur.Name = "Change Advisory Board" && varCR.CABDecision.Value <> "Approved",
                    Notify("The CAB decision must be Approved before this change can move on.", NotificationType.Error),
                cur.Name = "Change Authority" && varCR.AuthorityDecision.Value <> "Approved",
                    Notify("The Change Authority decision must be Approved before this change can move on.", NotificationType.Error),
                cur.Name = "Implementation" && IsBlank(varCR.ImplementationNotes),
                    Notify("Add implementation notes before moving on.", NotificationType.Error),
                cur.Name = "PIR" && IsBlank(varCR.ReviewOutcome.Value),
                    Notify("Choose a PIR outcome before closing.", NotificationType.Error),
                Set(varCR, Patch('Change Requests', varCR, {
                    Stage:      {Value: nxt.Name},
                    ClosedDate: If(nxt.Name = "Close", Now())
                }));
                If(nxt.Name = "Technical Review Board",
                    Set(varCR, Patch('Change Requests', varCR, {TRBDecision: {Value: "Pending"}})));
                Patch('Change Request History', Defaults('Change Request History'), {
                    Title: "CR-" & Text(varCR.ID, "00000"), RequestID: varCR.ID,
                    FromStage: cur.Name, ToStage: nxt.Name, Comment: txtComment.Text
                });
                Reset(txtComment);
                Notify("Moved to " & nxt.Name, NotificationType.Success)
            )
        ),
    "back",
        With({prv: First(Sort(Filter(Stages, Order < cur.Order, type in Types), Order, SortOrder.Descending))},
            Set(varCR, Patch('Change Requests', varCR, {Stage: {Value: prv.Name}, ImplementationComplete: false}));
            Patch('Change Request History', Defaults('Change Request History'), {
                Title: "CR-" & Text(varCR.ID, "00000"), RequestID: varCR.ID,
                FromStage: cur.Name, ToStage: prv.Name, Comment: txtComment.Text
            });
            Reset(txtComment);
            Notify("Sent back to " & prv.Name, NotificationType.Warning)
        ),
    "reject",
        Switch(cur.Name,
            "Technical Review Board",
                Set(varCR, Patch('Change Requests', varCR, {
                    Stage: {Value: "Close"}, ReviewOutcome: {Value: "Rejected"}, ClosedDate: Now(),
                    TRBDecision: {Value: "Rejected"},
                    TRBNotes: Trim(varCR.TRBNotes & Char(10) & "REJECTED: " & txtComment.Text)})),
            "Change Advisory Board",
                Set(varCR, Patch('Change Requests', varCR, {
                    Stage: {Value: "Close"}, ReviewOutcome: {Value: "Rejected"}, ClosedDate: Now(),
                    CABDecision: {Value: "Rejected"},
                    CABNotes: Trim(varCR.CABNotes & Char(10) & "REJECTED: " & txtComment.Text)})),
            "Change Authority",
                Set(varCR, Patch('Change Requests', varCR, {
                    Stage: {Value: "Close"}, ReviewOutcome: {Value: "Rejected"}, ClosedDate: Now(),
                    AuthorityDecision: {Value: "Rejected"},
                    AuthorityNotes: Trim(varCR.AuthorityNotes & Char(10) & "REJECTED: " & txtComment.Text)}))
        );
        Patch('Change Request History', Defaults('Change Request History'), {
            Title: "CR-" & Text(varCR.ID, "00000"), RequestID: varCR.ID,
            FromStage: cur.Name, ToStage: "Close", Comment: "REJECTED: " & txtComment.Text
        });
        Reset(txtComment);
        Notify("Change rejected and closed", NotificationType.Warning),
    "needschanges",
        Set(varCR, Patch('Change Requests', varCR, {
            Stage: {Value: "Requested"},
            TRBDecision: {Value: "Needs changes"},
            TRBNotes: Trim(varCR.TRBNotes & Char(10) & "NEEDS CHANGES: " & txtComment.Text)
        }));
        Patch('Change Request History', Defaults('Change Request History'), {
            Title: "CR-" & Text(varCR.ID, "00000"), RequestID: varCR.ID,
            FromStage: cur.Name, ToStage: "Requested", Comment: "NEEDS CHANGES: " & txtComment.Text
        });
        Reset(txtComment);
        Notify("Sent back to the requester for changes", NotificationType.Warning),
    "complete",
        If(IsBlank(varCR.ImplementationNotes),
            Notify("Add implementation notes before marking it complete.", NotificationType.Error),
            Set(varCR, Patch('Change Requests', varCR, {ImplementationComplete: true}));
            Patch('Change Request History', Defaults('Change Request History'), {
                Title: "CR-" & Text(varCR.ID, "00000"), RequestID: varCR.ID,
                FromStage: "Implementation", ToStage: "Implementation complete", Comment: txtComment.Text
            });
            Reset(txtComment);
            Notify("Marked complete. The CM team will be notified.", NotificationType.Success)
        ),
    Notify("Saved", NotificationType.Success)
));
If(varAction <> "save",
    Set(varNoteTab, Switch(varCR.Stage.Value,
        "Technical Review Board", "TRB",
        "Change Advisory Board",  "CAB",
        "Change Authority",       "Authority",
        "Implementation",         "Implementation",
        "PIR",                    "Review",
        "Close",                  "Review",
        "Description")));
Set(varAction, Blank())
```

**How the routes work:**
- **Move** goes to the next stage on that request's route, and **Send back** to the previous one.
- **Normal:** sent back from CAB, it returns to the **TRB**. From the TRB, it returns to Requested.
- **Emergency:** sent back from CAB, it returns to **Requested**.
- **Standard:** sent back from Implementation, it returns to **Requested**. Moved from Implementation, it goes straight to **Close**.

### 9i. History shows "✔ Implementation complete"
Select `lblHistMove` (inside `galHistory`) and replace its **Text** with:
```powerfx
If(IsBlank(ThisItem.FromStage), "Created",
   ThisItem.ToStage = "Implementation complete", "✔ Implementation complete",
   ThisItem.FromStage = ThisItem.ToStage, "Comment (" & ThisItem.ToStage & ")",
   ThisItem.FromStage & " → " & ThisItem.ToStage)
```

### 9j. Emails
The **Part 7** flow already includes the new cases. When you build it after the migration, it will:
- email **TRB members** when a request reaches the TRB,
- email the **CM team** when the implementer clicks **Completed**,
- send the requester *"… needs changes before TRB review"* when the TRB uses **Needs changes**.

Add the `TRBEmails` variable (7b) with your TRB members.

### Part 9 tests

| # | Do this | Expect |
|---|---|---|
| 1 | Open the board | Seven columns, with **2. TRB** between Requested and CAB |
| 2 | Click **+ Request a New Change** and open **Change type** | Standard, Normal and Emergency only; no Informational |
| 3 | Open a **Normal** request in Requested | The tracker shows all seven steps; Move says **Move to Technical Review Board →** |
| 4 | Move it to TRB, then click **Move** again as CM | Error: *TRB decision must be Approved* |
| 5 | As a **TRB member**, tick a checklist item, type a comment, and click **Needs changes** | Back to Requested; TRB notes show *NEEDS CHANGES: …*; History shows the move |
| 6 | As CM, move it to TRB again | TRB decision is back to *Pending* |
| 7 | As a TRB member, set the decision to **Approved**, then CM clicks **Move** | Moves to **CAB** |
| 8 | As CM, **Send back** from CAB | Returns to **TRB** |
| 9 | Open an **Emergency** request in Requested | The tracker has no TRB; Move says **Move to Change Advisory Board →** |
| 10 | Open a **Standard** request in Requested | The tracker shows Requested · Implementation · Close; Move says **Move to Implementation →** |
| 11 | Move the Standard request to Implementation | **✔ Completed** appears; CAB, Authority and TRB fields aren't shown |
| 12 | Click **Completed** with no implementation notes, then add notes and click again | First: error. Then *Marked complete*; the board card shows **✔ Complete**; History shows *✔ Implementation complete* |
| 13 | As CM, click **Move** on the completed Standard request | Goes straight to **Close** |
| 14 | Open an old **Informational** request | Its tracker skips TRB and works as before |
| 15 | **Reject** a request at TRB, as a TRB member | Goes to Close; TRB notes show *REJECTED: …* |
| 16 | Move a Normal request on from Implementation | It goes to **PIR**: the board column reads **6. PIR**, the tracker says *PIR*, and the notes tab says *PIR*. Moving on needs a **PIR outcome**. |

**If something goes wrong:**
- **A stage isn't found, or Move says "Move to  →" with no name:** the `Stages` names must match the SharePoint **Stage** choices exactly, including `Technical Review Board`.
- **A Standard change shows CAB fields:** that card's **Visible** still uses an old `.Order >= …` rule. Use the pattern in 9e step 5.
- **An error on `As t` in `galNoteTabs`:** check that the `NoteTabs` field is named `StageName`, not `Stage`.
- **TRB members can't edit the TRB decision:** check their email in `TRBMembers`, in lower case, matching what `User().Email` shows.

---

## Part 10 — Tidy the action bar and the notes tabs

This part comes **after Part 9**. It adjusts controls you already built in Parts 9f and 9g, so the action-bar buttons sit side by side without covering the comment box, and the notes tab labels don't wrap.

### 10a. Action bar: smaller buttons, side by side
Every control uses **Y** = `Parent.Height - 58` and **Height** = `40`.

On the five buttons (Send back, Reject, Completed, Needs changes, Add comment), also set:
- **Size** = `11`
- **PaddingLeft** = `4`
- **PaddingRight** = `4`

That stops the text wrapping onto two lines.

| Control | X | Width | Text |
|---|---|---|---|
| `btnSendBack` | `20` | `110` | `"← Send back"` |
| `btnReject` | `136` | `110` | `"Reject"` |
| `btnCompleted` | `136` | `110` | `"✔ Completed"` *(same spot as Reject; they never show together)* |
| `btnNeedsChanges` | `252` | `120` | `"Needs changes"` |
| `btnAddComment` | `378` | `110` | `"Add comment"` |
| `txtComment` | `494` | `515` | *(no change)* |
| `btnAdvance` | `1015` | `331` | *(no change)* |

All the buttons now sit to the **left** of the comment box, so none of them can cover it, even at the TRB stage when Send back, Reject and Needs changes all show. The comment box stays directly beside **Move**.

When a button is hidden, its space is left empty. That's expected.

### 10b. Notes tabs: smaller text, no wrapping
Select **`lblTab`** (inside `galNoteTabs`) and set:

| Property | Value |
|---|---|
| Size | `8` |
| Wrap | `false` |
| PaddingLeft / PaddingRight | `0` |
| PaddingTop / PaddingBottom | `0` |
| Align | `Align.Center` |

With six tabs, each is about 71 pixels wide, so *Description* only just fits at size 8. If it's still cut off, shorten its label in **App.Formulas › `NoteTabs`**: change `Label: "Description"` to `Label: "Details"`. Only the label changes. The key stays `"Description"`, so nothing else needs editing.

### Part 10 tests

| # | Do this | Expect |
|---|---|---|
| 1 | Open a Normal request at the **TRB** stage as someone who is both CM and a TRB member | Send back, Reject, Needs changes and Add comment sit side by side, each on one line, and none covers the comment box |
| 2 | Open a request at **Implementation** | ✔ Completed shows where Reject would be; nothing overlaps |
| 3 | Look at the notes tabs on a request at **PIR** or **Close** | All tab labels (Description/Details, TRB, CAB, Authority, Implement, PIR) are on one line |

---

## Part 11 — Line up read-only drop-down values under their titles

**Why:** in read-only mode, a drop-down (or combo box) still draws its value with its own inner spacing. So on the detail screen, *2 - High*, *Approved* and similar values sit slightly out of line with their titles (*Priority*, *CAB decision*). Plain text fields don't have this problem.

**Fix:** use the same pattern as Part 8f for dates.
- When a card is **read-only**, hide its drop-down and show a plain **text label** instead, lined up exactly with the card's title.
- When the card is **editable**, the drop-down comes back.

The card still saves from the hidden drop-down, so nothing changes in SharePoint.

All changes are in `frmDetail` on the **DetailScreen**.

### 11a. Which cards
Do this for every card whose value is a drop-down or combo box:

| Card | Read-only text |
|---|---|
| Category | `ThisItem.Category.Value` |
| ChangeType | `ThisItem.ChangeType.Value` |
| Priority | `ThisItem.Priority.Value` |
| Risk | `ThisItem.Risk.Value` |
| Impact | `ThisItem.Impact.Value` |
| TRBDecision | `ThisItem.TRBDecision.Value` |
| CABDecision | `ThisItem.CABDecision.Value` |
| AuthorityDecision | `ThisItem.AuthorityDecision.Value` |
| ReviewOutcome *(PIR outcome)* | `ThisItem.ReviewOutcome.Value` |
| A6Program *(only if you gave it a drop-down on the detail screen)* | `ThisItem.A6Program` |

### 11b. For each of those cards
1. Expand the card in the Tree view. Select the drop-down or combo box inside it, which is the **visible** one: `DataCardValueN`, or your own name such as `drpRisk`. Set:
   - **Visible** = `Parent.DisplayMode = DisplayMode.Edit`
2. Select the **card**, choose **+ Insert › Text label**, and check it lands **inside the card**. Rename it after the card, for example `lblRiskView`, and set:

   | Property | Value |
   |---|---|
   | Text | the read-only text from 11a, wrapped so empty values show a dash, e.g. `Coalesce(ThisItem.Risk.Value, "—")` |
   | Visible | `Parent.DisplayMode = DisplayMode.View` |
   | X | `DataCardKeyN.X` *(the card's title label)* |
   | PaddingLeft | `DataCardKeyN.PaddingLeft` |
   | Y | the drop-down's **Y** (e.g. `DataCardValueN.Y`) |
   | Width | `Parent.Width - DataCardKeyN.X - 10` |
   | Height / Size | `FormValueHeight` / `FormLabelSize` |
   | PaddingTop / PaddingBottom | `0` |
   | VerticalAlign | `VerticalAlign.Middle` |
   | Color | `Color.Black` |

   Using the title's own **X** and **PaddingLeft** is what makes the value start at exactly the same point as the title above it.

### 11c. Same alignment for the dates and Assignee
The read-only labels you added in **Part 8e** (`lblAssigneeView`) and **Part 8f** (the one-line dates) should line up the same way. On each of those labels, set:
- **X** = `DataCardKeyN.X`
- **PaddingLeft** = `DataCardKeyN.PaddingLeft`

### Part 11 tests

| # | Do this | Expect |
|---|---|---|
| 1 | Open a request past *Requested* | Category, Change type, Priority, Risk and Impact values start exactly under their titles, like the text fields |
| 2 | Look at the decisions on a request at **CAB** or later | *Approved* / *Pending* sit directly under *CAB decision* and *Authority decision* |
| 3 | Look at the dates and Assignee | They line up under their titles too |
| 4 | Open a request in *Requested* | Priority, Risk and the rest show their drop-downs and can be changed; save and reopen to confirm they saved |
| 5 | As a CAB member, open a request at **CAB** | CAB decision shows its drop-down (editable); the other decisions show as aligned text |
