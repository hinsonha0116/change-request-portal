# App updates: change-type help, "Other" A6 program, several assignees, Emergency CAB, and a log of field changes

These changes build on the app as described in the [build guide](Change-Request-PowerApp-Guide.md). Section numbers like *4.5* or *5.7* refer to that guide.

**What changes:**
1. **Change type help:** hovering over **Change type** on the New Request screen explains what Standard, Normal and Emergency mean.
2. **"Other" A6 program:** the A6 program list gets an **Other** option. Choosing it shows a box where the requester types the program name.
3. **Several assignees:** the **Assignee** field on the detail screen takes more than one person.
4. **Emergency CAB (ECAB):** Emergency changes follow their own route, **Requested → ECAB → Implementation → PIR → Close**. The ECAB replaces the CAB and Change Authority for emergencies. The CAB members record the ECAB decision.
5. **A History line for every change:** when someone saves a request and any field has changed, the History shows what changed, e.g. *Priority: 3 - Moderate → 2 - High*. This covers the CM changing the priority or change type in *Requested*.

> **How to set a property:** select the control in the **Tree view**, choose the property in the dropdown at the left of the formula bar, and paste the value into the formula bar. Unlock form cards first if needed: **Properties › Advanced › 🔒 Unlock to change properties**.

**Time:** about 3 hours. Do the parts in order: Part 5 uses the fields from Parts 3 and 4.

---

## Part 1 — Hover text that explains the change types

### 1a. The help text (App.Formulas)
Add this to the **end** of **App › Formulas**. Change the wording to match A6's change policy if it defines the types differently.
```powerfx
ChangeTypeHelp =
    "Standard: a routine, low-risk change that's pre-approved. It goes straight to Implementation." & Char(10) &
    "Normal: most changes. Reviewed by the TRB, the CAB and the Change Authority before it's made." & Char(10) &
    "Emergency: an urgent fix that can't wait for the normal schedule. Reviewed by the Emergency CAB (ECAB).";
```

### 1b. Show it on hover (NewScreen)
In `frmNew`, expand **`ChangeType_DataCard…`** and set **Tooltip** = `ChangeTypeHelp` on:
- the drop-down **`drpChangeType`**, and
- the card's title label **`DataCardKeyN`**.

Then set the title label's **Text** to `"Change type ⓘ"`. The **ⓘ** shows people there's help to hover over.

### 1c. Show the selected type's meaning under the drop-down (optional)
Tooltips need a mouse, so they don't show on touch screens. To also show a one-line explanation of the chosen type:
1. Select the **ChangeType card**, insert a **Text label** inside it, and rename it `lblChangeTypeHelp`.
2. Set:

   | Property | Value |
   |---|---|
   | Text | `Switch(drpChangeType.Selected.Value, "Standard", "Routine, pre-approved. Goes straight to Implementation.", "Normal", "Reviewed by TRB, CAB and Change Authority.", "Emergency", "Urgent. Reviewed by the Emergency CAB.", "")` |
   | X / Width | `drpChangeType.X` / `drpChangeType.Width` |
   | Y | `drpChangeType.Y + drpChangeType.Height + 2` |
   | Height / Size | `18` / `9` |
   | Color | `RGBA(0,0,0,0.6)` |
   | PaddingTop / PaddingBottom / PaddingLeft | `0` |

The card grows to fit the extra line. If the next row overlaps it, select the **card** and set **Height** = `lblChangeTypeHelp.Y + lblChangeTypeHelp.Height + 6`.

---

## Part 2 — "Other" in the A6 program list

The **A6Program** column stays **Single line of text**. When the requester picks **Other**, the program name they type is saved instead.

### 2a. Add "Other" to the list (App.Formulas)
In **App › Formulas**, add `"Other"` as the **last** entry of `A6Programs`:
```powerfx
A6Programs = ["ACBN", "Blacknet", "C2C", "Collaboration Services", "CSFC", "Exec Comm", "EVRS", "HERTR/GWRTR", "NNCS", "Secureview", "SNCS", "Unified Communications", "UPNCS", "VDI", "VOC", "X-COMM", "Other"];
```

### 2b. The free-text box (NewScreen)
1. In `frmNew`, select the **A6Program card**, insert a **Text input** inside it, and rename it `txtA6Other`.
2. Set:

   | Property | Value |
   |---|---|
   | Default | `""` |
   | HintText | `"Type the program name"` |
   | Visible | `drpA6Program.Selected.Value = "Other"` |
   | Reset | `varResetNew` |
   | X / Width | `drpA6Program.X` / `drpA6Program.Width` |
   | Y | `drpA6Program.Y + drpA6Program.Height + 4` |
   | Height / Size | `FormValueHeight` / `FormLabelSize` |

3. Select the **card** and replace its **Update** with:
   ```powerfx
   If(drpA6Program.Selected.Value = "Other", Trim(txtA6Other.Text), drpA6Program.Selected.Value)
   ```
4. If the box overlaps the row below, set the **card**'s **Height** = `If(txtA6Other.Visible, txtA6Other.Y + txtA6Other.Height + 6, drpA6Program.Y + drpA6Program.Height + 6)`.

### 2c. Require the name when Other is picked
In **`btnSubmit` › OnSelect** (guide 4.8), add these two lines just **after** the *Choose an A6 Program* check:
```powerfx
    drpA6Program.Selected.Value = "Other" && IsBlank(Trim(txtA6Other.Text)),
        Notify("Type the A6 program name.", NotificationType.Error),
```

### 2d. The detail screen
On the detail screen, a request whose program isn't in the list shows **Other** with the name in the box underneath. This also covers older requests that were typed in before the drop-down existed.

1. **`drpA6ProgramDetail` › Default:**
   ```powerfx
   If(IsBlank(ThisItem.A6Program) || ThisItem.A6Program in A6Programs, ThisItem.A6Program, "Other")
   ```
2. Select the **A6Program card** in `frmDetail`, insert a **Text input** inside it, rename it `txtA6OtherDetail`, and set:

   | Property | Value |
   |---|---|
   | Default | `If(ThisItem.A6Program in A6Programs, "", ThisItem.A6Program)` |
   | HintText | `"Type the program name"` |
   | Visible | `drpA6ProgramDetail.Selected.Value = "Other" && Parent.DisplayMode = DisplayMode.Edit` |
   | DisplayMode | `Parent.DisplayMode` |
   | X / Width / Height / Size | as in 2b, using `drpA6ProgramDetail` |
   | Y | `drpA6ProgramDetail.Y + drpA6ProgramDetail.Height + 4` |

3. Select the **card** and replace its **Update** with:
   ```powerfx
   If(drpA6ProgramDetail.Selected.Value = "Other",
      Coalesce(Trim(txtA6OtherDetail.Text), ThisItem.A6Program),
      Coalesce(drpA6ProgramDetail.Selected.Value, ThisItem.A6Program))
   ```

The read-only label (`lblA6ProgramView`, `Coalesce(ThisItem.A6Program, "—")`) already shows the typed name once the request has moved on. The board cards, the calendar and the emails show the typed name too, with no change needed.

---

## Part 3 — Several assignees

### 3a. SharePoint
1. Open the **Change Requests** list, then **⚙ › List settings**, and click **Assignee**.
2. Set **Allow multiple selections** to **Yes** and click **OK**. Existing assignees are kept.
3. In Power Apps Studio, go to **Data**, click **⋯** next to **Change Requests**, then **Refresh**.

### 3b. The Assignee card (detail screen)
In `frmDetail`, expand **`Assignee_DataCard…`**.

1. Select the **combo box** (`DataCardValueN`) and set:

   | Property | Value |
   |---|---|
   | SelectMultiple | `true` |
   | DefaultSelectedItems | `Parent.Default` |
   | DisplayFields / SearchFields | `["DisplayName"]` / `["DisplayName", "Email"]` |

2. Select the **card** and set **Update** = `DataCardValueN.SelectedItems` (the combo box's own name).
3. **If the card shows errors after the change** (it was built for a single person): remove **Assignee** in **Edit fields** and add it again, then put it back after **AuthorityDecision** and redo its settings from guide 5.3 and 5.4.

### 3c. The read-only names
Select **`lblAssigneeView`** and replace its **Text** with this, which lists everyone in the short *First Last* style:
```powerfx
Coalesce(
    Concat(ThisItem.Assignee As a,
        With({n: a.DisplayName},
            If(Find(",", n) > 0,
                Proper(First(Split(Trim(Mid(n, Find(",", n) + 1)), " ")).Value & " " & Trim(Left(n, Find(",", n) - 1))),
                n)),
        ", "),
    "—")
```
With several names, the line can run long. If it's cut off, set the label's **Wrap** = `true` and **Height** = `FormValueHeight * 2`.

### 3d. Other files
The provisioning script now creates **Assignee** as a person column that allows multiple selections. The build guide gets the change when this update is folded in.

---

## Part 4 — Emergency CAB (ECAB) route for Emergency changes

**New routes:**

| Change type | Route |
|---|---|
| **Normal** | Requested → TRB → CAB → Change Authority → Implementation → PIR → Close *(no change)* |
| **Emergency** | Requested → **Emergency CAB** → Implementation → PIR → Close |
| **Standard** | Requested → Implementation → Close *(no change)* |
| *Informational (older requests)* | Requested → CAB → Change Authority → Implementation → PIR → Close *(no change)* |

- **Who decides:** the **CAB members** (`CABMembers`) record the ECAB decision and can **Reject** at the ECAB stage.
- **The rule:** the **ECAB decision** must be *Approved* before the CM team can move the request to Implementation.
- **The board** gets an eighth column, **ECAB**, between TRB and CAB.

> **Before you switch:** finish any **Emergency** request that's currently at **CAB** or **Change Authority**, or move it back to *Requested*. After this change, Emergency requests don't pass through those stages, so one sitting there would be stuck.

### 4a. SharePoint (Change Requests list)
1. **Stage column:** add the choice `Emergency CAB`, directly after `Technical Review Board`. Keep the spelling and capitals exactly as shown.
2. **Add these columns:**

   | Name | Type | Settings |
   |---|---|---|
   | `ECABDecision` | Choice | `Pending`, `Approved`, `Rejected` · default **Pending** |
   | `ECABNotes` | Multiple lines of text | More options › *Use enhanced rich text* **off** |

3. In Power Apps Studio, go to **Data › ⋯ › Refresh** next to **Change Requests**.

### 4b. App.Formulas
1. **Replace the `Stages` table** with this one. ECAB is added as stage 3, and Emergency is taken off CAB and Change Authority:
   ```powerfx
   Stages = Table(
       {Order: 1, Name: "Requested",              Short: "Requested",      Color: ColorValue("#6B7280"), Types: "Standard,Normal,Emergency,Informational"},
       {Order: 2, Name: "Technical Review Board", Short: "TRB",            Color: ColorValue("#0D9488"), Types: "Normal"},
       {Order: 3, Name: "Emergency CAB",          Short: "ECAB",           Color: ColorValue("#DC2626"), Types: "Emergency"},
       {Order: 4, Name: "Change Advisory Board",  Short: "CAB",            Color: ColorValue("#2563EB"), Types: "Normal,Informational"},
       {Order: 5, Name: "Change Authority",       Short: "Authority",      Color: ColorValue("#7C3AED"), Types: "Normal,Informational"},
       {Order: 6, Name: "Implementation",         Short: "Implementation", Color: ColorValue("#D97706"), Types: "Standard,Normal,Emergency,Informational"},
       {Order: 7, Name: "PIR",                    Short: "PIR",            Color: ColorValue("#0891B2"), Types: "Normal,Emergency,Informational"},
       {Order: 8, Name: "Close",                  Short: "Close",          Color: ColorValue("#16A34A"), Types: "Standard,Normal,Emergency,Informational"}
   );
   ```
2. **Add the ECAB tab** to `NoteTabs`, after the TRB line:
   ```powerfx
       {Key: "ECAB",           Label: "ECAB",        StageName: "Emergency CAB"},
   ```

A request only ever shows the tabs on its own route (at most six), so `galNoteTabs` › **TemplateSize** stays `Self.Width / 6`.

### 4c. The board: eight columns
**`galStages` › TemplateSize:** `Self.Width / 8 - 9`.

Columns are now about 160 pixels wide, so titles wrap sooner. The column headers already use the short names (*3. ECAB*).

### 4d. ECAB fields on the detail form
1. Select `frmDetail`, click **Edit fields › + Add field**, tick **ECABDecision** and **ECABNotes**, and click **Add**.
2. **Placement:** drag **ECABDecision** to just **before** CABDecision, and **ECABNotes** to the **bottom**, with the other hidden cards.
3. **ECABNotes card:** **Visible** = `false` and **Update** = `If(lblEditableNote.Text = "ECAB", txtNote.Text, ThisItem.ECABNotes)`.
4. **ECABDecision card:**
   - **Visible:**
     ```powerfx
     With({s: LookUp(Stages, Name = "Emergency CAB")},
         LookUp(Stages, Name = varCR.Stage.Value).Order >= s.Order &&
         Coalesce(varCR.ChangeType.Value, "Normal") in s.Types)
     ```
   - **DisplayMode:** `If(varCR.Stage.Value = "Emergency CAB" && IsCAB, DisplayMode.Edit, DisplayMode.View)`
   - **Label Text:** `"ECAB decision"`, with the sizes from guide 4.3.
   - **Drop-down and read-only label:** as in guide 5.4. The drop-down is `drpECABDecision` with **Items** `DecisionChoices`, **Default** `Coalesce(ThisItem.ECABDecision.Value, "Pending")`, and card **Update** `{Value: drpECABDecision.Selected.Value}`. The read-only label is `lblECABDecisionView` with `Coalesce(ThisItem.ECABDecision.Value, "—")`.

### 4e. Notes tabs
**`lblEditableNote` › Text:** add the ECAB line after the TRB line:
```powerfx
    "Emergency CAB",          If(IsCAB, "ECAB", ""),
```

**Add `"ECAB", varCR.ECABNotes,`** to the `Switch` in both of these, right after the `"TRB"` line:
- `txtNote` › **Default**
- `lblNote` › **Text**

**Open on the ECAB tab.** In both places that set `varNoteTab` (**DetailScreen › OnVisible**, and the end of **`frmDetail` › OnSuccess**), add this line after the `"Technical Review Board"` line:
```powerfx
    "Emergency CAB",          "ECAB",
```

### 4f. Action bar and OnSuccess
**`btnReject` › Visible:** add the ECAB line:
```powerfx
(varCR.Stage.Value = "Technical Review Board" && IsTRB) ||
(varCR.Stage.Value = "Emergency CAB" && IsCAB) ||
(varCR.Stage.Value = "Change Advisory Board" && IsCAB) ||
(varCR.Stage.Value = "Change Authority" && IsAuthority)
```

**`frmDetail` › OnSuccess** (guide 5.7), two additions:
1. In the `"advance"` section, add this rule just **before** the `cur.Name = "Change Advisory Board"` line:
   ```powerfx
                cur.Name = "Emergency CAB" && varCR.ECABDecision.Value <> "Approved",
                    Notify("The ECAB decision must be Approved before this change can move on.", NotificationType.Error),
   ```
2. In the `"reject"` section, add this case to the `Switch(cur.Name, …)`, just **before** `"Change Advisory Board",`:
   ```powerfx
            "Emergency CAB",
                Set(varCR, Patch('Change Requests', varCR, {
                    Stage: {Value: "Close"}, ReviewOutcome: {Value: "Rejected"}, ClosedDate: Now(),
                    ECABDecision: {Value: "Rejected"},
                    ECABNotes: Trim(varCR.ECABNotes & Char(10) & "REJECTED: " & txtComment.Text)})),
   ```

**Move** and **Send back** already follow the routes from the `Stages` table, so nothing else changes: an Emergency request in *Requested* shows **Move to Emergency CAB →**, and one sent back from Implementation returns to the ECAB.

### 4g. Stage-change email
In the **Change Request – Stage notifications** flow (guide 8b), add a case to the **Switch**:

| Case equals | To | Subject (expression) |
|---|---|---|
| `Emergency CAB` | `variables('CABEmails')` | `concat(outputs('CRNumber'), ' needs EMERGENCY CAB review: ', body('Get_item')?['Title'])` |

Set its **Importance** to **High** (**Show advanced options**).

### 4h. Other files
- **The provisioning script** adds the `Emergency CAB` stage and the two ECAB columns.
- **[SharePoint-Intro.md](SharePoint-Intro.md)** now shows the Emergency route through the ECAB. Update the text on the SharePoint page once this is live.

---

## Part 5 — A History line for every change

When a request is saved and any field has changed, `frmDetail` › OnSuccess writes one History line listing what changed, e.g.:

> ✎ Priority: 3 - Moderate → 2 - High; Change type: Normal → Standard

- **When:** every save through the form, including **Save changes**, **Move**, **Send back**, **Reject**, **Needs changes** and **Completed**. The change line comes just before the move's own line.
- **Who:** the History already shows who made the change and when.
- **Notes:** changes to the Description or a stage's notes show as *Description updated*, without repeating the text.
- **Not logged:** attachments added or removed, and the fields the buttons set themselves (Stage, the TRB reset, *Completed*), because those already have their own History lines.
- **No emails:** the line is a comment (same stage in *From* and *To*), so the stage-email flow skips it.

### 5a. `frmDetail` › OnSuccess: compare old and new
`varCR` still holds the request as it was **before** the save until the first line of OnSuccess replaces it. So the comparison has to come first.

Add this to the **very start** of **`frmDetail` › OnSuccess**, before `Set(varCR, Self.LastSubmit);`:
```powerfx
With({o: varCR, n: Self.LastSubmit, fmt: "dd mmm yyyy hh:mm"},
    Set(varChanges,
        Concat(
            Filter(
                Table(
                    {f: "Title",                  a: o.Title,                              b: n.Title,                              big: false},
                    {f: "A6 program",             a: o.A6Program,                          b: n.A6Program,                          big: false},
                    {f: "Requested by",           a: o.RequestedBy,                        b: n.RequestedBy,                        big: false},
                    {f: "Requester email",        a: o.RequesterEmail,                     b: n.RequesterEmail,                     big: false},
                    {f: "DSN",                    a: o.DSN,                                b: n.DSN,                                big: false},
                    {f: "Category",               a: o.Category.Value,                     b: n.Category.Value,                     big: false},
                    {f: "Change type",            a: o.ChangeType.Value,                   b: n.ChangeType.Value,                   big: false},
                    {f: "Priority",               a: o.Priority.Value,                     b: n.Priority.Value,                     big: false},
                    {f: "Risk",                   a: o.Risk.Value,                         b: n.Risk.Value,                         big: false},
                    {f: "Impact",                 a: o.Impact.Value,                       b: n.Impact.Value,                       big: false},
                    {f: "Planned start",          a: Text(o.PlannedStart, fmt),            b: Text(n.PlannedStart, fmt),            big: false},
                    {f: "Planned end",            a: Text(o.PlannedEnd, fmt),              b: Text(n.PlannedEnd, fmt),              big: false},
                    {f: "Outage expected",        a: If(o.OutageExpected, "Yes", "No"),    b: If(n.OutageExpected, "Yes", "No"),    big: false},
                    {f: "Outage duration",        a: o.OutageDuration,                     b: n.OutageDuration,                     big: false},
                    {f: "Location",               a: o.Location,                           b: n.Location,                           big: false},
                    {f: "Affected systems",       a: o.AffectedSystems,                    b: n.AffectedSystems,                    big: false},
                    {f: "TRB decision",           a: o.TRBDecision.Value,                  b: n.TRBDecision.Value,                  big: false},
                    {f: "Rollback plan reviewed", a: If(o.TRBRollbackReviewed, "Yes", "No"), b: If(n.TRBRollbackReviewed, "Yes", "No"), big: false},
                    {f: "Tested",                 a: If(o.TRBTested, "Yes", "No"),         b: If(n.TRBTested, "Yes", "No"),         big: false},
                    {f: "Security reviewed",      a: If(o.TRBSecurityReviewed, "Yes", "No"), b: If(n.TRBSecurityReviewed, "Yes", "No"), big: false},
                    {f: "ECAB decision",          a: o.ECABDecision.Value,                 b: n.ECABDecision.Value,                 big: false},
                    {f: "CAB decision",           a: o.CABDecision.Value,                  b: n.CABDecision.Value,                  big: false},
                    {f: "Authority decision",     a: o.AuthorityDecision.Value,            b: n.AuthorityDecision.Value,            big: false},
                    {f: "Assignees",              a: Concat(o.Assignee, DisplayName, ", "), b: Concat(n.Assignee, DisplayName, ", "), big: false},
                    {f: "Actual start",           a: Text(o.ActualStart, fmt),             b: Text(n.ActualStart, fmt),             big: false},
                    {f: "Actual end",             a: Text(o.ActualEnd, fmt),               b: Text(n.ActualEnd, fmt),               big: false},
                    {f: "PIR outcome",            a: o.ReviewOutcome.Value,                b: n.ReviewOutcome.Value,                big: false},
                    {f: "Description",            a: o.Description,                        b: n.Description,                        big: true},
                    {f: "Impact details",         a: o.ImpactDetails,                      b: n.ImpactDetails,                      big: true},
                    {f: "Justification",          a: o.Justification,                      b: n.Justification,                      big: true},
                    {f: "TRB notes",              a: o.TRBNotes,                           b: n.TRBNotes,                           big: true},
                    {f: "ECAB notes",             a: o.ECABNotes,                          b: n.ECABNotes,                          big: true},
                    {f: "CAB notes",              a: o.CABNotes,                           b: n.CABNotes,                           big: true},
                    {f: "Authority notes",        a: o.AuthorityNotes,                     b: n.AuthorityNotes,                     big: true},
                    {f: "Implementation notes",   a: o.ImplementationNotes,                b: n.ImplementationNotes,                big: true},
                    {f: "PIR notes",              a: o.ReviewNotes,                        b: n.ReviewNotes,                        big: true}
                ),
                Coalesce(a, "") <> Coalesce(b, "")
            ),
            If(big, f & " updated", f & ": " & Coalesce(a, "(blank)") & " → " & Coalesce(b, "(blank)")),
            "; "
        )
    );
    If(!IsBlank(varChanges),
        Patch('Change Request History', Defaults('Change Request History'), {
            Title:     Coalesce(o.CRNumber, "CR-" & Text(o.ID, "00000")),
            RequestID: o.ID,
            FromStage: o.Stage.Value,
            ToStage:   o.Stage.Value,
            Comment:   "✎ " & varChanges
        })
    )
);
```
Leave the rest of OnSuccess as it is, starting with `Set(varCR, Self.LastSubmit);`.

**Notes:**
- **Do Parts 3 and 4 first.** The formula uses the multiple **Assignee** column and the **ECAB** columns. If you skip Part 4, delete the two ECAB lines.
- **Adding a field later:** add a line to the table with the field's label, its old (`o.`) and new (`n.`) value as text, and `big: false`.
- **Assignees** show the full directory names here, to keep the formula short.

### 5b. History shows it as a change
1. **`lblHistMove` › Text:** add the change line, just after the `"Implementation complete"` line:
   ```powerfx
   If(IsBlank(ThisItem.FromStage), "Created",
      ThisItem.ToStage = "Implementation complete", "✔ Implementation complete",
      StartsWith(ThisItem.Comment, "✎ "), "✎ Changes (" & ThisItem.ToStage & ")",
      ThisItem.FromStage = ThisItem.ToStage, "Comment (" & ThisItem.ToStage & ")",
      ThisItem.FromStage & " → " & ThisItem.ToStage)
   ```
2. **`lblHistComment`:** a long list of changes can run past two lines. Set **Tooltip** = `ThisItem.Comment` so hovering shows the whole line. To show more of it, raise `galHistory` › **TemplateSize** to `96` and `lblHistComment` › **Height** to `44`.

---

## Test

| # | Do this | Expect |
|---|---|---|
| 1 | On NewScreen, hover over **Change type ⓘ** and over the drop-down | The explanation of Standard, Normal and Emergency appears |
| 2 | Pick each change type *(if you did 1c)* | The one-line meaning under the drop-down changes with it |
| 3 | Pick **Other** as the A6 program | A *Type the program name* box appears under it |
| 4 | Submit with Other picked and the box empty | Error: *Type the A6 program name* |
| 5 | Type a name and submit | The card, the detail screen and SharePoint show the typed name |
| 6 | Open that request in *Requested* | The drop-down shows **Other**, with the name in the box; change the name, save, and it's kept |
| 7 | Open a request at **Implementation** and pick **two** assignees, then **Save changes** | Both saved; read-only, they show as *First Last, First Last* |
| 8 | Open the board | There are eight columns, with **3. ECAB** |
| 9 | Submit an **Emergency** request and open it | The tracker shows Requested · Emergency CAB · Implementation · Post Implementation Review · Close; Move says **Move to Emergency CAB →** |
| 10 | As CM, move it to the ECAB, then click **Move** again | Error: *ECAB decision must be Approved* |
| 11 | As a **CAB member**, set the ECAB decision to **Approved**; CM clicks **Move** | Moves to **Implementation**; the CAB members got *"… needs EMERGENCY CAB review"* when it reached the ECAB |
| 12 | **Reject** another Emergency request at the ECAB, as a CAB member | Closes as *Rejected*; the ECAB tab shows *REJECTED: …* |
| 13 | Open a **Normal** request | No ECAB on its tracker, and no ECAB decision field |
| 14 | As CM, open a request in *Requested*, change **Priority** and **Change type**, and click **Save changes** | History shows **✎ Changes (Requested)** with *Priority: … → …; Change type: … → …* |
| 15 | Change the Description only and save | History shows *✎ … Description updated* |
| 16 | Save without changing anything | No new History line |
| 17 | As a CAB member, set **Approved** and click **Move** in one step | History shows *✎ … CAB decision: Pending → Approved*, then the move |
| 18 | Check your inbox after test 14 | No stage email was sent for the change line |

**If something goes wrong:**
- **`txtA6Other` or `lblChangeTypeHelp` isn't recognized:** it was inserted on the screen, not inside the card. Cut it (**Ctrl+X**), select the card, and paste (**Ctrl+V**).
- **The Assignee card shows an error about a table or record:** remove the field in **Edit fields** and add it again (3b step 3).
- **An Emergency request says "Move to  →" with no name, or skips the ECAB:** the stage name must be `Emergency CAB` in both SharePoint and the `Stages` table.
- **An Emergency request is stuck at CAB or Change Authority:** it was there before the switch. Send it back to *Requested* (as CM), then move it on.
- **The change line never appears:** the formula in 5a must be **before** `Set(varCR, Self.LastSubmit);`, otherwise it compares the new values with themselves.
- **A field name in 5a is red:** that column doesn't exist under that name. Check its internal name in **List settings**, or delete that line.
- **Anything else:** open the **App checker** (the stethoscope icon) and send me the exact text of any red error banner.
