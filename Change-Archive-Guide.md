# Change archive: a PDF record and attachments for every closed change

When a change request closes, a Power Automate flow files a permanent record of it in a SharePoint document library. The record is a PDF of everything on the request, stage by stage, with the full History at the end, plus a copy of every attachment.

```
Change Archive (document library)
└── VDI                                  ← A6 program
    └── 2026                             ← year it closed
        └── 11 - November                ← month it closed
            └── CR-2026-014 - Replace VDI gateway certificates
                ├── CR-2026-014 - Change record.pdf
                ├── Rollback Plan.pdf
                └── (every other attachment)
```

**How it works:**
- **When:** the flow runs whenever a History row moving a request to **Close** is created. That covers normal closes and rejections. Rejected changes are archived too, marked *Rejected* at the top of the PDF.
- **Filed by closed date:** the year and month folders come from the request's **ClosedDate**, in local time.
- **Folders are created automatically** the first time a program, year or month is needed.
- **The app gets a link:** the flow saves the folder's address on the request, and closed requests show an **Open archive** button on the detail screen.
- **Licences:** only standard connectors are used (SharePoint and OneDrive for Business), so no premium licence is needed.

This guide builds on the app in the [build guide](Change-Request-PowerApp-Guide.md). Step numbers like *8b* refer to that guide.

**Time:** about 2 hours.

> **Check first: OneDrive's "Convert file" action.** The PDF is made by saving the report as a web page in OneDrive and converting it with **Convert file**. That's a standard action, but it may not be available in every government cloud. Before building the whole flow, create a test flow, add **OneDrive for Business › Convert file**, and see if it's offered. If it isn't, follow **If Convert file isn't available** at the end of Step 3.

---

## Step 1 — SharePoint: the library and a link column

### 1a. Create the library
1. On the Change Management site, choose **+ New › Document library**.
2. Name it **`ChangeArchive`**, with no space, and click **Create**. This name becomes the library's web address, and a name with no space keeps the flow's paths and links simple.
3. Open **⚙ › Library settings › List name, description and navigation** and change the **Name** to **Change Archive**. Only the display name changes. The address stays `…/ChangeArchive`.

### 1b. Make it read-only for everyone except the flow
The archive is a record, so most people should only be able to read it.

1. In **Library settings**, click **Permissions for this document library**.
2. Click **Stop Inheriting Permissions** and confirm.
3. Tick the site's **Members** group, click **Edit User Permissions**, choose **Read**, and click **OK**. Leave **Owners** on Full Control and **Visitors** on Read.
4. **The flow's account must still be able to write.** If the account you'll build the flow with is only a site *member*, click **Grant Permissions**, add that account, and give it **Contribute**.

> **Optional, stop deletion:** ask your compliance admin for a **retention label** (for example *Change records, 7 years*) and apply it as the library's default label. Files then can't be deleted until the period ends.

### 1c. Add a column for the archive link
In the **Change Requests** list, add a column:

| Name | Type | Settings |
|---|---|---|
| `ArchiveLink` | Multiple lines of text | More options › *Use enhanced rich text* **off** |

It's a multiple-lines column because the address can be longer than the 255 characters a single line allows.

### 1d. A temporary folder in OneDrive
In the flow account's **OneDrive**, create a folder named **`ChangeArchiveTemp`**. The flow writes the report there for a moment while it converts it to PDF, then deletes it.

---

## Step 2 — Create the flow and gather the data

### 2a. Trigger
1. Go to **make.powerautomate.com** (or your government address). Click **+ Create › Automated cloud flow**, name it **Change Request – Archive on close**, pick **When an item is created** (SharePoint), and click **Create**.
2. Set **Site Address** to your site and **List Name** to **Change Request History**.
3. **Run only for closes.** On the trigger, open **⋯ › Settings**, under **Trigger conditions** click **+ Add**, and paste:
   ```
   @equals(triggerBody()?['ToStage'], 'Close')
   ```
   Click **Done**.

### 2b. The request and its History
Add these actions in order. **Rename each one exactly as shown** (**⋯ › Rename**), because later expressions use these names.

| # | Action | Rename to | Settings |
|---|---|---|---|
| 1 | **Compose** | `RequestID` | Inputs: **RequestID** from the trigger's dynamic content |
| 2 | **Get item** (SharePoint) | `Get item` | Site Address: your site · List Name: **Change Requests** · Id: `outputs('RequestID')` *(expression)* |
| 3 | **Get items** (SharePoint) | `Get history` | Site Address: your site · List Name: **Change Request History** · **Show advanced options:** Filter Query `RequestID eq @{outputs('RequestID')}` · Order By `Created asc` · Top Count `1000` |

Every later step reads the request ID from the **RequestID** Compose, not from the trigger. That's what lets Step 6 reuse the same flow for changes that closed before the archive existed.

### 2c. Folder names
Add these **Compose** actions. Rename each, and paste each input with **fx / Expression**.

| Rename to | Inputs (expression) |
|---|---|
| `ClosedAt` | `coalesce(body('Get_item')?['ClosedDate'], utcNow())` |
| `Year` | `convertFromUtc(outputs('ClosedAt'), 'W. Europe Standard Time', 'yyyy')` |
| `MonthFolder` | `convertFromUtc(outputs('ClosedAt'), 'W. Europe Standard Time', 'MM - MMMM')` |
| `CRNumber` | `coalesce(body('Get_item')?['CRNumber'], concat('CR-', formatNumber(body('Get_item')?['ID'], '00000')))` |
| `SafeProgram` | see below |
| `SafeTitle` | see below |
| `FolderPath` | `concat('/ChangeArchive/', outputs('SafeProgram'), '/', outputs('Year'), '/', outputs('MonthFolder'), '/', outputs('CRNumber'), ' - ', outputs('SafeTitle'))` |

- **Time zone:** `W. Europe Standard Time` is Germany. Use the same time zone as your email flows. It decides which month a change that closed near midnight is filed under.
- **`MonthFolder`** gives `11 - November`, so the months sort in order.

**`SafeProgram`** and **`SafeTitle`** remove characters SharePoint doesn't allow in folder names. For example, *HERTR/GWRTR* becomes *HERTR-GWRTR*. The title is also cut to 80 characters to stay well inside SharePoint's path length limit.

> **The A6 program column's internal name is `A6Program_x002c__x0020_DSN_x002c`.** When the column was first created, its name was typed as something like *"A6Program, DSN,"*. SharePoint fixes a column's internal name when it's created, so renaming it later only changed the display name. Power Apps uses the display name, so the app is unaffected. Power Automate uses the internal name, so the expressions below use it.
>
> - **Production lists built with *From existing list*** copy this name, so the expressions work as written.
> - **Lists built with the provisioning script** name the column plain `A6Program`. Change the expressions to `['A6Program']` there.
> - **To check any list:** run the flow once, open **Get item › Show raw outputs**, and search for `Program`.

`SafeProgram`:
```
trim(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(if(empty(body('Get_item')?['A6Program_x002c__x0020_DSN_x002c']), 'No program', body('Get_item')?['A6Program_x002c__x0020_DSN_x002c']), decodeUriComponent('%22'), ''), '*', ''), ':', ' -'), '<', ''), '>', ''), '?', ''), '/', '-'), decodeUriComponent('%5C'), '-'), '|', '-'), '#', ''))
```

`SafeTitle`:
```
trim(take(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(coalesce(body('Get_item')?['Title'], 'Untitled'), decodeUriComponent('%22'), ''), '*', ''), ':', ' -'), '<', ''), '>', ''), '?', ''), '/', '-'), decodeUriComponent('%5C'), '-'), '|', '-'), '#', ''), '%', ''), 80))
```

`decodeUriComponent('%22')` is a double quote and `decodeUriComponent('%5C')` a backslash. Writing them this way avoids typing those two characters into the expression, which the designer sometimes stores differently from how they were typed.

---

## Step 3 — Build the PDF

### 3a. Assignee names and History rows
Add two **Select** actions (under *Data Operation*). For each, click the **Map** switch so it takes a single text value instead of key/value pairs.

| Rename to | From (expression) | Map (expression) |
|---|---|---|
| `Assignee names` | see below | `item()?['DisplayName']` |
| `History rows` | `body('Get_history')?['value']` | see below |

**`Assignee names` › From.** Works whether **Assignee** allows one person or several:
```
if(empty(body('Get_item')?['Assignee']), json('[]'), if(startsWith(string(body('Get_item')?['Assignee']), '['), body('Get_item')?['Assignee'], createArray(body('Get_item')?['Assignee'])))
```
With no assignee it gives an empty list; with several it uses the list as it is; with one person it wraps them in a list, because **Select** only accepts a list.

**Typed, not picked:** in **Get history**, type the column names in **Filter Query** (`RequestID eq `, then the `outputs('RequestID')` expression) and **Order By** (`Created asc`) as plain text. Picking *Created* or *RequestID* from dynamic content inserts a value instead of the column name, and the action fails.

**`History rows` › From** must be exactly `body('Get_history')?['value']`, the rows **Get history** returned. With anything else, the rows have no dates and the step fails.

**`History rows` › Map.** One table row per History entry, with the same wording as the app. An empty date shows **—** instead of stopping the flow:
```
concat('<tr><td>', if(empty(item()?['Created']), '—', convertFromUtc(item()?['Created'], 'W. Europe Standard Time', 'dd MMM yyyy HH:mm')), '</td><td>', coalesce(item()?['Author']?['DisplayName'], ''), '</td><td>', if(empty(item()?['FromStage']), 'Created', if(startsWith(coalesce(item()?['Comment'], ''), '✎'), concat('Changes (', item()?['ToStage'], ')'), if(equals(item()?['FromStage'], item()?['ToStage']), concat('Comment (', item()?['ToStage'], ')'), concat(item()?['FromStage'], ' → ', item()?['ToStage'])))), '</td><td>', coalesce(item()?['Comment'], ''), '</td></tr>')
```

### 3b. Every field, ready to print
Add a **Compose**, rename it `Fields`, and paste the block below into **Inputs** as it is (not as an expression). Each `@{…}` becomes the request's value when the flow runs, and an empty field shows as **—**.

```json
{
  "CRNumber": "@{outputs('CRNumber')}",
  "Title": "@{body('Get_item')?['Title']}",
  "Outcome": "@{if(empty(body('Get_item')?['ReviewOutcome']?['Value']), '—', body('Get_item')?['ReviewOutcome']?['Value'])}",
  "Closed": "@{convertFromUtc(outputs('ClosedAt'), 'W. Europe Standard Time', 'dd MMM yyyy HH:mm')}",
  "Submitted": "@{convertFromUtc(body('Get_item')?['Created'], 'W. Europe Standard Time', 'dd MMM yyyy HH:mm')}",
  "SubmittedBy": "@{if(empty(body('Get_item')?['SubmittedBy']), '—', body('Get_item')?['SubmittedBy'])}",
  "A6Program": "@{if(empty(body('Get_item')?['A6Program_x002c__x0020_DSN_x002c']), '—', body('Get_item')?['A6Program_x002c__x0020_DSN_x002c'])}",
  "RequestedBy": "@{if(empty(body('Get_item')?['RequestedBy']), '—', body('Get_item')?['RequestedBy'])}",
  "RequesterEmail": "@{if(empty(body('Get_item')?['RequesterEmail']), '—', body('Get_item')?['RequesterEmail'])}",
  "DSN": "@{if(empty(body('Get_item')?['DSN']), '—', body('Get_item')?['DSN'])}",
  "Category": "@{if(empty(body('Get_item')?['Category']?['Value']), '—', body('Get_item')?['Category']?['Value'])}",
  "ChangeType": "@{if(empty(body('Get_item')?['ChangeType']?['Value']), '—', body('Get_item')?['ChangeType']?['Value'])}",
  "Priority": "@{if(empty(body('Get_item')?['Priority']?['Value']), '—', body('Get_item')?['Priority']?['Value'])}",
  "Risk": "@{if(empty(body('Get_item')?['Risk']?['Value']), '—', body('Get_item')?['Risk']?['Value'])}",
  "Impact": "@{if(empty(body('Get_item')?['Impact']?['Value']), '—', body('Get_item')?['Impact']?['Value'])}",
  "PlannedStart": "@{if(empty(body('Get_item')?['PlannedStart']), '—', convertFromUtc(body('Get_item')?['PlannedStart'], 'W. Europe Standard Time', 'dd MMM yyyy HH:mm'))}",
  "PlannedEnd": "@{if(empty(body('Get_item')?['PlannedEnd']), '—', convertFromUtc(body('Get_item')?['PlannedEnd'], 'W. Europe Standard Time', 'dd MMM yyyy HH:mm'))}",
  "OutageExpected": "@{if(equals(body('Get_item')?['OutageExpected'], true), 'Yes', 'No')}",
  "OutageDuration": "@{if(empty(body('Get_item')?['OutageDuration']), '—', body('Get_item')?['OutageDuration'])}",
  "Location": "@{if(empty(body('Get_item')?['Location']), '—', body('Get_item')?['Location'])}",
  "AffectedSystems": "@{if(empty(body('Get_item')?['AffectedSystems']), '—', body('Get_item')?['AffectedSystems'])}",
  "Description": "@{if(empty(body('Get_item')?['Description']), '—', body('Get_item')?['Description'])}",
  "ImpactDetails": "@{if(empty(body('Get_item')?['ImpactDetails']), '—', body('Get_item')?['ImpactDetails'])}",
  "Justification": "@{if(empty(body('Get_item')?['Justification']), '—', body('Get_item')?['Justification'])}",
  "TRBDecision": "@{if(empty(body('Get_item')?['TRBDecision']?['Value']), '—', body('Get_item')?['TRBDecision']?['Value'])}",
  "TRBRollbackReviewed": "@{if(equals(body('Get_item')?['TRBRollbackReviewed'], true), 'Yes', 'No')}",
  "TRBTested": "@{if(equals(body('Get_item')?['TRBTested'], true), 'Yes', 'No')}",
  "TRBSecurityReviewed": "@{if(equals(body('Get_item')?['TRBSecurityReviewed'], true), 'Yes', 'No')}",
  "TRBNotes": "@{if(empty(body('Get_item')?['TRBNotes']), '—', body('Get_item')?['TRBNotes'])}",
  "ECABDecision": "@{if(empty(body('Get_item')?['ECABDecision']?['Value']), '—', body('Get_item')?['ECABDecision']?['Value'])}",
  "ECABNotes": "@{if(empty(body('Get_item')?['ECABNotes']), '—', body('Get_item')?['ECABNotes'])}",
  "CABDecision": "@{if(empty(body('Get_item')?['CABDecision']?['Value']), '—', body('Get_item')?['CABDecision']?['Value'])}",
  "CABNotes": "@{if(empty(body('Get_item')?['CABNotes']), '—', body('Get_item')?['CABNotes'])}",
  "AuthorityDecision": "@{if(empty(body('Get_item')?['AuthorityDecision']?['Value']), '—', body('Get_item')?['AuthorityDecision']?['Value'])}",
  "AuthorityNotes": "@{if(empty(body('Get_item')?['AuthorityNotes']), '—', body('Get_item')?['AuthorityNotes'])}",
  "Assignees": "@{if(empty(body('Assignee_names')), '—', join(body('Assignee_names'), ', '))}",
  "ActualStart": "@{if(empty(body('Get_item')?['ActualStart']), '—', convertFromUtc(body('Get_item')?['ActualStart'], 'W. Europe Standard Time', 'dd MMM yyyy HH:mm'))}",
  "ActualEnd": "@{if(empty(body('Get_item')?['ActualEnd']), '—', convertFromUtc(body('Get_item')?['ActualEnd'], 'W. Europe Standard Time', 'dd MMM yyyy HH:mm'))}",
  "ImplementationComplete": "@{if(equals(body('Get_item')?['ImplementationComplete'], true), 'Yes', 'No')}",
  "ImplementationNotes": "@{if(empty(body('Get_item')?['ImplementationNotes']), '—', body('Get_item')?['ImplementationNotes'])}",
  "PIRNotes": "@{if(empty(body('Get_item')?['ReviewNotes']), '—', body('Get_item')?['ReviewNotes'])}",
  "Generated": "@{convertFromUtc(utcNow(), 'W. Europe Standard Time', 'dd MMM yyyy HH:mm')}"
}
```

The ECAB lines show **—** until the ECAB columns exist (Part 4 of the current updates), so you can build this now.

### 3c. The report page
Add a **Compose**, rename it `Report HTML`, and paste this into **Inputs** as plain text. Every value is read from the `Fields` Compose.

```html
<html><head><meta charset="utf-8"><style>
body{font-family:Segoe UI,Arial,sans-serif;font-size:10pt;color:#111;margin:24px}
h1{font-size:16pt;margin:0 0 4px}
h2{font-size:12pt;color:#1E3A6B;border-bottom:2px solid #1E3A6B;margin:18px 0 6px;padding-bottom:2px}
.meta{color:#555;margin-bottom:8px}
.rejected{color:#B91C1C;font-weight:bold}
table{border-collapse:collapse;width:100%}
td,th{border:1px solid #ccc;padding:4px 6px;vertical-align:top;text-align:left}
th{background:#EEF2F7}
td.l{width:24%;background:#F7F7F7;font-weight:bold}
td.v{white-space:pre-wrap}
</style></head><body>
<h1>@{outputs('Fields')?['CRNumber']} — @{outputs('Fields')?['Title']}</h1>
<div class="meta">Closed @{outputs('Fields')?['Closed']} · Outcome: <span class="@{if(equals(outputs('Fields')?['Outcome'], 'Rejected'), 'rejected', '')}">@{outputs('Fields')?['Outcome']}</span> · Record generated @{outputs('Fields')?['Generated']}</div>

<h2>Request</h2>
<table>
<tr><td class="l">A6 program</td><td class="v">@{outputs('Fields')?['A6Program']}</td><td class="l">Change type</td><td class="v">@{outputs('Fields')?['ChangeType']}</td></tr>
<tr><td class="l">Requested by</td><td class="v">@{outputs('Fields')?['RequestedBy']} (@{outputs('Fields')?['RequesterEmail']})</td><td class="l">DSN</td><td class="v">@{outputs('Fields')?['DSN']}</td></tr>
<tr><td class="l">Submitted</td><td class="v">@{outputs('Fields')?['Submitted']} by @{outputs('Fields')?['SubmittedBy']}</td><td class="l">Category</td><td class="v">@{outputs('Fields')?['Category']}</td></tr>
<tr><td class="l">Priority</td><td class="v">@{outputs('Fields')?['Priority']}</td><td class="l">Risk / Impact</td><td class="v">@{outputs('Fields')?['Risk']} / @{outputs('Fields')?['Impact']}</td></tr>
<tr><td class="l">Planned start</td><td class="v">@{outputs('Fields')?['PlannedStart']}</td><td class="l">Planned end</td><td class="v">@{outputs('Fields')?['PlannedEnd']}</td></tr>
<tr><td class="l">Outage expected</td><td class="v">@{outputs('Fields')?['OutageExpected']}</td><td class="l">Outage duration</td><td class="v">@{outputs('Fields')?['OutageDuration']}</td></tr>
<tr><td class="l">Location</td><td class="v">@{outputs('Fields')?['Location']}</td><td class="l">Affected systems</td><td class="v">@{outputs('Fields')?['AffectedSystems']}</td></tr>
</table>
<table>
<tr><td class="l">Description</td><td class="v">@{outputs('Fields')?['Description']}</td></tr>
<tr><td class="l">Impact details</td><td class="v">@{outputs('Fields')?['ImpactDetails']}</td></tr>
<tr><td class="l">Justification</td><td class="v">@{outputs('Fields')?['Justification']}</td></tr>
</table>

<h2>Technical Review Board</h2>
<table>
<tr><td class="l">TRB decision</td><td class="v">@{outputs('Fields')?['TRBDecision']}</td><td class="l">Rollback plan reviewed</td><td class="v">@{outputs('Fields')?['TRBRollbackReviewed']}</td></tr>
<tr><td class="l">Tested in lab / test</td><td class="v">@{outputs('Fields')?['TRBTested']}</td><td class="l">Security / STIG reviewed</td><td class="v">@{outputs('Fields')?['TRBSecurityReviewed']}</td></tr>
</table>
<table><tr><td class="l">TRB notes</td><td class="v">@{outputs('Fields')?['TRBNotes']}</td></tr></table>

<h2>Emergency CAB</h2>
<table>
<tr><td class="l">ECAB decision</td><td class="v">@{outputs('Fields')?['ECABDecision']}</td></tr>
<tr><td class="l">ECAB notes</td><td class="v">@{outputs('Fields')?['ECABNotes']}</td></tr>
</table>

<h2>Change Advisory Board and Change Authority</h2>
<table>
<tr><td class="l">CAB decision</td><td class="v">@{outputs('Fields')?['CABDecision']}</td></tr>
<tr><td class="l">CAB notes</td><td class="v">@{outputs('Fields')?['CABNotes']}</td></tr>
<tr><td class="l">Authority decision</td><td class="v">@{outputs('Fields')?['AuthorityDecision']}</td></tr>
<tr><td class="l">Authority notes</td><td class="v">@{outputs('Fields')?['AuthorityNotes']}</td></tr>
</table>

<h2>Implementation</h2>
<table>
<tr><td class="l">Assignees</td><td class="v">@{outputs('Fields')?['Assignees']}</td><td class="l">Marked complete</td><td class="v">@{outputs('Fields')?['ImplementationComplete']}</td></tr>
<tr><td class="l">Actual start</td><td class="v">@{outputs('Fields')?['ActualStart']}</td><td class="l">Actual end</td><td class="v">@{outputs('Fields')?['ActualEnd']}</td></tr>
</table>
<table><tr><td class="l">Implementation notes</td><td class="v">@{outputs('Fields')?['ImplementationNotes']}</td></tr></table>

<h2>Post Implementation Review</h2>
<table>
<tr><td class="l">PIR outcome</td><td class="v">@{outputs('Fields')?['Outcome']}</td></tr>
<tr><td class="l">PIR notes</td><td class="v">@{outputs('Fields')?['PIRNotes']}</td></tr>
</table>

<h2>History</h2>
<table>
<tr><th style="width:16%">When</th><th style="width:20%">Who</th><th style="width:22%">What</th><th>Comment</th></tr>
@{join(body('History_rows'), '')}
</table>
</body></html>
```

Sections that don't apply to a change's route (for example the TRB on a Standard change) simply show **—**.

> If the `@{...}` parts come out as plain text in the PDF, the designer stored them as literal text. Rebuild each one: delete it, then insert it from **Expression** (for example `outputs('Fields')?['Title']`).

### 3d. Convert to PDF
Add these actions in order:

| # | Action | Rename to | Settings |
|---|---|---|---|
| 1 | **Create file** (OneDrive for Business) | `Save temp HTML` | Folder Path: `/ChangeArchiveTemp` · File Name: `concat(outputs('CRNumber'), '.html')` *(expression)* · File Content: the **Outputs** of `Report HTML` |
| 2 | **Convert file** (OneDrive for Business) | `Convert to PDF` | File: `body('Save_temp_HTML')?['Id']` *(expression)* · Target type: **PDF** |
| 3 | **Create file** (SharePoint) | `Save PDF` | Site Address: your site · Folder Path: `outputs('FolderPath')` *(expression)* · File Name: `concat(outputs('CRNumber'), ' - Change record.pdf')` *(expression)* · File Content: **File content** from `Convert to PDF` |
| 4 | **Delete file** (OneDrive for Business) | `Delete temp HTML` | File: `body('Save_temp_HTML')?['Id']` *(expression)* |

**Save PDF** creates the program, year, month and change folders if they don't exist yet.

> **If Convert file isn't available** in your cloud, skip actions 1, 2 and 4. In action 3, use File Name `concat(outputs('CRNumber'), ' - Change record.html')` and File Content = the **Outputs** of `Report HTML`. The record is then a web page that opens in any browser, and anyone who needs a PDF can print it to PDF from there.

---

## Step 4 — Copy the attachments and save the link

### 4a. Attachments
| # | Action | Rename to | Settings |
|---|---|---|---|
| 1 | **Get attachments** (SharePoint) | `Get attachments` | Site Address: your site · List Name: **Change Requests** · Id: `outputs('RequestID')` |
| 2 | **Apply to each** (Control) | `Each attachment` | Select an output: `body('Get_attachments')` |
| 3 | inside it: **Get attachment content** (SharePoint) | `Get attachment content` | Site Address: your site · List Name: **Change Requests** · Id: `outputs('RequestID')` · File Identifier: `items('Each_attachment')?['Id']` |
| 4 | inside it: **Create file** (SharePoint) | `Save attachment` | Site Address: your site · Folder Path: `outputs('FolderPath')` · File Name: `items('Each_attachment')?['DisplayName']` · File Content: **Attachment Content** from `Get attachment content` |

The attachments keep their own file names, next to the PDF.

### 4b. Save the folder link on the request
Add **Update item** (SharePoint), rename it `Save archive link`, and set:

| Field | Value |
|---|---|
| Site Address / List Name | your site / **Change Requests** |
| Id | `outputs('RequestID')` |
| Title | `body('Get_item')?['Title']` *(required by the action, so pass the same title back)* |
| Stage Value | `Close` |
| ArchiveLink | `concat('https://YOUR-TENANT.sharepoint.us/sites/YOUR-SITE', replace(outputs('FolderPath'), ' ', '%20'))` |

Replace `https://YOUR-TENANT.sharepoint.us/sites/YOUR-SITE` with your site's address, as it shows in the browser, with no `/` at the end.

Only **Title**, **Stage** and **ArchiveLink** are sent. The action leaves every other field as it is.

### 4c. Save and turn on
Click **Save**, and make sure the flow is **On**.

The finished flow, top to bottom:
> Trigger (History, *To stage = Close*) → RequestID → Get item → Get history → ClosedAt → Year → MonthFolder → CRNumber → SafeProgram → SafeTitle → FolderPath → Assignee names → History rows → Fields → Report HTML → Save temp HTML → Convert to PDF → Save PDF → Delete temp HTML → Get attachments → Each attachment (Get attachment content → Save attachment) → Save archive link

---

## Step 5 — "Open archive" in the app

1. In Power Apps Studio, go to **Data**, click **⋯** next to **Change Requests**, then **Refresh**, so the app sees **ArchiveLink**. Don't add it to any form.
2. On **DetailScreen**, insert a **Button** in the header, rename it `btnArchive`, and set:

   | Property | Value |
   |---|---|
   | Text | `"📁 Open archive"` |
   | OnSelect | `Launch(varCR.ArchiveLink, {}, LaunchTarget.New)` |
   | Visible | `varCR.Stage.Value = "Close" && !IsBlank(varCR.ArchiveLink)` |
   | Fill / Color / BorderColor | `Color.White` / `ColorValue("#1E3A6B")` / `ColorValue("#1E3A6B")` |
   | X / Y / Width / Height | `Parent.Width - 320` / `12` / `150` / `36` |

   If it disappears behind the banner, right-click it and choose **Reorder › Bring to front**.
3. **Save** and **Publish**.

The flow takes a minute or two after a change closes, so the button appears once the request is opened again after that.

---

## Step 6 — Archive changes that closed before this existed (optional)

Changes closed before the flow was turned on aren't archived automatically. A copy of the flow that you run from the list archives them one at a time.

1. On the flow's page, click **Save As** and name the copy **Change Request – Archive (run manually)**. Open the copy.
2. **Swap the trigger.** Click the trigger, **⋯ › Delete**, then add the trigger **For a selected item** (SharePoint) with your site and **List Name** = **Change Requests**.
3. Change the **RequestID** Compose's **Inputs** to the **ID** of the selected item, from the new trigger's dynamic content.
4. **Save** and turn the copy **On**.
5. In the **Change Requests** list, select a **closed** request, then **Automate › Change Request – Archive (run manually)** (or **⋯ › Automate**), and click **Run flow**.

Use it only on closed requests. A request with no ClosedDate would be filed under today's month.

---

## Test

Do these with **TEST –** requests, and delete them and their archive folders afterwards.

| # | Do this | Expect |
|---|---|---|
| 1 | Take a Normal request with two attachments all the way to **Close** | Within a few minutes, **Change Archive › program › year › month › CR-… - title** exists, with the PDF and both attachments |
| 2 | Open the PDF | Every section is filled in; empty fields show **—**; long notes wrap; the History is at the end, oldest first |
| 3 | **Reject** a request at CAB | It's archived too; the PDF's outcome reads **Rejected** in red |
| 4 | Close a request for a program with a `/` in its name (e.g. *HERTR/GWRTR*) | Its folder is named *HERTR-GWRTR* |
| 5 | Close a request whose title has `:` or `?` in it | The folder name has those characters removed or replaced; the PDF shows the title as typed |
| 6 | Open the closed request in the app | **📁 Open archive** shows and opens the folder |
| 7 | As a regular site member, try to delete a file in **Change Archive** | Not allowed: they can only read |
| 8 | Move a request to any stage other than Close | The archive flow doesn't run (it shows as skipped, or not at all, in its run history) |
| 9 | Run the manual copy on an older closed request *(Step 6)* | It's filed under the month it closed |

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| The flow never runs | The trigger condition isn't saved, or the trigger watches the wrong list | Check the trigger is on **Change Request History**, and the condition from 2a is under **⋯ › Settings** |
| **Get item** fails with *Item not found* | The RequestID Compose is empty | Check its Inputs is **RequestID** from the trigger (or **ID** in the manual copy) |
| An expression says an action *doesn't exist* | An action wasn't renamed exactly | Rename it as in the tables. Spaces in a name become `_` in expressions, e.g. `Get history` → `body('Get_history')` |
| **Convert to PDF** fails or isn't offered | Convert file isn't available, or the file isn't in OneDrive | Use the HTML fallback at the end of 3d |
| **Save PDF** fails: *file already exists* | The flow ran twice for the same change | Delete the change's folder in the archive and resubmit the run |
| A folder name is wrong or the save fails with *invalid characters* | A character the sanitizing doesn't cover | Add another `replace(…, 'x', '')` around the value in `SafeProgram` or `SafeTitle` |
| **Save attachment** fails with *Forbidden* | The flow's account can't write to the library | Give it **Contribute** on the library (1b step 4) |
| **Save archive link** fails | A required field wasn't passed, or the column name differs | Pass **Title** and **Stage**; check the column's internal name is `ArchiveLink` |
| **Open archive** doesn't show | The flow hadn't finished when the request was opened, or the app didn't refresh the data source | Reopen the request a few minutes later; refresh **Change Requests** in **Data** and republish |
| The PDF shows `@{...}` text | The expression was stored as plain text | Rebuild those parts with **Expression** (note under 3c) |
| **Assignee names** fails: *'from' … is of type 'Object'. The value must be an array* | An older **From** formula, and Assignee allows only one person | Use the **From** in 3a, which handles one or several |
| **Get history** fails: *The expression "2026-… asc" is not valid* | **Order By** holds the dynamic *Created* date instead of the text | Clear it and type `Created asc` |
| Every change is filed under **No program**, and the PDF's A6 program shows **—** | The flow reads `A6Program`, but the column's internal name differs | Use the internal name from **Get item › Show raw outputs** (here `A6Program_x002c__x0020_DSN_x002c`), as in Step 2c |
| **History rows** fails: *'convertFromUtc' expects … a string … The provided value is of type 'Null'* | **History rows › From** isn't the History rows | Set **From** to `body('Get_history')?['value']` |
| Dates are an hour or a day off | Time zone | Use the same time zone name in every expression |
