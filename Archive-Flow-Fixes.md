# Fixes for the original archive flow

The manual copy, **Change Request – Archive (run manually)**, was fixed while testing on 16 Nov 2026. The original, **Change Request – Archive on close**, needs the same changes. [Change-Archive-Guide.md](Change-Archive-Guide.md) already has all of them.

Open the original flow in **Edit** and work down it. Paste every value marked *expression* with **fx / Expression**, replacing what's there completely.

## Checklist

| # | Action | Field | Set it to |
|---|---|---|---|
| 1 | **Get history** | Filter Query | Type `RequestID eq ` (with a space at the end), then insert the expression `outputs('RequestID')`. No quotes, and nothing picked from dynamic content |
| 2 | **Get history** | Order By | Type `Created asc` as plain text. Delete any **Created** chip |
| 3 | **SafeProgram** | Inputs *(expression)* | Formula A below |
| 4 | **SafeTitle** | Inputs *(expression)* | Formula B below |
| 5 | **Assignee names** | From *(expression)* | Formula C below |
| 6 | **History rows** | From *(expression)* | `body('Get_history')?['value']` |
| 7 | **History rows** | Map *(text mode, expression)* | Formula D below |
| 8 | **Fields** | the `"A6Program"` line | Line E below |

Leave the trigger, **RequestID**, **Get item** and everything after **Fields** as they are. The **Get history** rebuild and the connection re-selection were only needed in the copy.

### A — SafeProgram
```
trim(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(if(empty(body('Get_item')?['A6Program_x002c__x0020_DSN_x002c']), 'No program', body('Get_item')?['A6Program_x002c__x0020_DSN_x002c']), decodeUriComponent('%22'), ''), '*', ''), ':', ' -'), '<', ''), '>', ''), '?', ''), '/', '-'), decodeUriComponent('%5C'), '-'), '|', '-'), '#', ''))
```

### B — SafeTitle
```
trim(take(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(coalesce(body('Get_item')?['Title'], 'Untitled'), decodeUriComponent('%22'), ''), '*', ''), ':', ' -'), '<', ''), '>', ''), '?', ''), '/', '-'), decodeUriComponent('%5C'), '-'), '|', '-'), '#', ''), '%', ''), 80))
```

### C — Assignee names › From
```
if(empty(body('Get_item')?['Assignee']), json('[]'), if(startsWith(string(body('Get_item')?['Assignee']), '['), body('Get_item')?['Assignee'], createArray(body('Get_item')?['Assignee'])))
```
**Map** stays `item()?['DisplayName']`, in text mode.

### D — History rows › Map
```
concat('<tr><td>', if(empty(item()?['Created']), '—', convertFromUtc(item()?['Created'], 'W. Europe Standard Time', 'dd MMM yyyy HH:mm')), '</td><td>', coalesce(item()?['Author']?['DisplayName'], ''), '</td><td>', if(empty(item()?['FromStage']), 'Created', if(startsWith(coalesce(item()?['Comment'], ''), '✎'), concat('Changes (', item()?['ToStage'], ')'), if(equals(item()?['FromStage'], item()?['ToStage']), concat('Comment (', item()?['ToStage'], ')'), concat(item()?['FromStage'], ' → ', item()?['ToStage'])))), '</td><td>', coalesce(item()?['Comment'], ''), '</td></tr>')
```

### E — Fields, the A6Program line
Replace only this line inside the **Fields** Compose, and keep the comma at the end:
```
  "A6Program": "@{if(empty(body('Get_item')?['A6Program_x002c__x0020_DSN_x002c']), '—', body('Get_item')?['A6Program_x002c__x0020_DSN_x002c'])}",
```

## Why each change
| # | Problem it fixes |
|---|---|
| 1–2 | Picking *RequestID* or *Created* from dynamic content inserts a value instead of the column name. **Get history** then fails, e.g. *The expression "2026-… asc" is not valid* |
| 3, 8 | The A6 program column's internal name is `A6Program_x002c__x0020_DSN_x002c`, so `['A6Program']` found nothing. Every change was filed under **No program**, and the PDF showed **—** (Troubleshooting-Notes, Issue 5) |
| 3–4 | The double quote and backslash are written with `decodeUriComponent`, so the designer can't store them wrongly |
| 5 | With one assignee, SharePoint returns a single person, and **Select** needs a list (*'from' … must be an array*). This handles one or several |
| 6–7 | With the wrong **From**, the rows have no dates (*'convertFromUtc' … type 'Null'*). The Map also shows **—** for any empty date now |

## Related, outside this flow
- **New request notifications flow, `EmailBody`:** change the A6 program row to
  `<tr><td><b>A6 program</b></td><td>@{triggerOutputs()?['body/A6Program_x002c__x0020_DSN_x002c']}</td></tr>`
- **Change Archive library:** delete the **No program** folder left by the test runs, then run the manual flow again on those closed requests.

## Test
1. **Save** the original flow.
2. Take a **TEST –** request with an assignee and an attachment all the way to **Close**.
3. Within a few minutes, check that:
   - the folder **program › year › month › CR-… - title** exists, with the PDF and the attachment,
   - the PDF shows the A6 program, the assignee, and the History with dates,
   - **📁 Open archive** shows on the request in the app.
4. Delete the test request, its History rows and its archive folder.
