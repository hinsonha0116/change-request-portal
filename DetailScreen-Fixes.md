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

> **How to set a property:** select the control in the **Tree view**, choose the property in the dropdown at the left of the formula bar, and paste the value into the formula bar. You can also type X, Y, Width and Height into the **Properties** pane on the right.

> **Control names:** each field (card) has a label `DataCardKeyN` and a value `DataCardValueN`. The numbers differ in every app, so expand a card in the Tree view to see its real names.

**Time:** about 3½ hours in total. Do the parts in order, because the emails and filters use the columns from Part 1.

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
| Requested *(sent back)* | Requester | *CR-… was sent back to you* |
| Change Advisory Board | CAB members | *CR-… is ready for CAB review* |
| Change Authority | Change Authorities | *CR-… is awaiting Change Authority approval* |
| Implementation | Requester, CC CM team | *CR-… is approved for implementation* |
| Review | CM team | *CR-… has been implemented and is ready for review* |
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
| `Requested` | `outputs('RequesterEmails')` | | `concat(outputs('CRNumber'), ' was sent back to you: ', body('Get_item')?['Title'])` |
| `Change Advisory Board` | `variables('CABEmails')` | | `concat(outputs('CRNumber'), ' is ready for CAB review: ', body('Get_item')?['Title'])` |
| `Change Authority` | `variables('AuthorityEmails')` | | `concat(outputs('CRNumber'), ' is awaiting Change Authority approval: ', body('Get_item')?['Title'])` |
| `Implementation` | `outputs('RequesterEmails')` | `variables('CMTeamEmails')` | `concat(outputs('CRNumber'), ' is approved for implementation: ', body('Get_item')?['Title'])` |
| `Review` | `variables('CMTeamEmails')` | | `concat(outputs('CRNumber'), ' has been implemented and is ready for review: ', body('Get_item')?['Title'])` |
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
| ReviewOutcome | `"Review outcome"` |

### 8b. Let the decisions share a row
If **CABDecision** or **AuthorityDecision** sits alone on its row, its card is stretching to fill the row. Select each of those **cards** and set **WidthFit** = `false`.

Check **Assignee**, **ActualStart**, **ActualEnd** and **ReviewOutcome** the same way. Only the full-width cards should have a fixed full **Width**: ImpactDetails, Justification, AffectedSystems and Attachments.

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
| 5 | Open a request with an Assignee, at *Review* or *Close* | Shows a short name, e.g. *Hayley Hinson* |
| 6 | Look at the planned dates on a request at *CAB* or later | One line each, e.g. *22 Oct 2026  11:00* |
| 7 | Open a request in *Implementation* | Actual start and end show date pickers; set them, **Save changes**, and reopen to check they saved |
| 8 | Open a request in *Requested*, change a planned date and save | The pickers show, and the new date saves |
