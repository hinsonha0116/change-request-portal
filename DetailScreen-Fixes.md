# App updates: change-type help, "Other" A6 program, several assignees, Emergency CAB, a log of field changes, and the CMDB tasker

These changes build on the app as described in the [build guide](Change-Request-PowerApp-Guide.md). Section numbers like *4.5* or *5.7* refer to that guide.

**What changes:**
1. **Change type help:** hovering over **Change type** on the New Request screen explains what Standard, Normal and Emergency mean.
2. **"Other" A6 program:** the A6 program list gets an **Other** option. Choosing it shows a box where the requester types the program name.
3. **Several assignees:** the **Assignee** field on the detail screen takes more than one person.
4. **Emergency CAB (ECAB):** Emergency changes follow their own route, **Requested → ECAB → Implementation → PIR → Close**. The ECAB replaces the CAB and Change Authority for emergencies. The CAB members record the ECAB decision.
5. **A History line for every change:** when someone saves a request and any field has changed, the History shows what changed, e.g. *Priority: 3 - Moderate → 2 - High*. This covers the CM changing the priority or change type in *Requested*.
6. **Software and hardware details, and the CMDB tasker:** software name and versions, or hardware make, model and serials, on each request; an email tasking the HW or SW managers to update the CMDB when the implementer clicks Completed; and a required *CMDB updated* check before a change can leave Implementation.

> **How to set a property:** select the control in the **Tree view**, choose the property in the dropdown at the left of the formula bar, and paste the value into the formula bar. Unlock form cards first if needed: **Properties › Advanced › 🔒 Unlock to change properties**.

**Time:** about 5½ hours. Do the parts in order: Part 5 uses the fields from Parts 3 and 4, and Part 6 adds to Part 5.

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

### 3b. Rebuild the Assignee card (detail screen)
The existing card was built for one person, and refreshing the data doesn't change that: its **Default** shows *"Expected record value… the rule produces table values"*. So the card has to be removed and added again, **after** Studio has picked up the column change.

1. In `frmDetail`, click **Edit fields**, hover **Assignee**, and click **⋯ › Remove**. Use **Remove** in Edit fields, not **Delete** in the Tree view, which leaves the field behind. If an `Assignee_DataCard…` is still in the Tree view afterwards, delete that too.
2. **Save** (Ctrl+S), refresh **Change Requests** under **Data**, then **close Studio completely** (the browser tab) and reopen the app from **Apps › ⋯ › Edit**. Without the close and reopen, Studio keeps its old copy of the column, and the new card is built for one person again.
3. **Check:** a temporary label with **Text** `CountRows(varCR.Assignee)` should show a number, not an error. Remove the label afterwards.
4. **+ Add field › Assignee**, drag it to just after **AuthorityDecision**, and **Unlock** the new card.
5. Set the **card**: **Visible** = the stage pattern with `"Implementation"` (guide 5.3), **DisplayMode** = `If(varCR.Stage.Value = "Implementation", DisplayMode.Edit, DisplayMode.View)`, **WidthFit** = `false`, **Update** = `DataCardValueN.SelectedItems` (the combo box's name). Leave **Default** as `ThisItem.Assignee`.
6. Set the **title label** (`DataCardKeyN`): **Text** `"Assignees"`, **Size** `FormLabelSize`, **Height** `FormLabelHeight`.
7. Set the **combo box** (`DataCardValueN`):

   | Property | Value |
   |---|---|
   | SelectMultiple | `true` |
   | DefaultSelectedItems | `Parent.Default` |
   | DisplayFields / SearchFields | `["DisplayName"]` / `["DisplayName", "Email"]` |
   | Visible | `Parent.DisplayMode = DisplayMode.Edit` |
   | Size / Height | `FormLabelSize` / `FormValueHeight` |

8. Add the read-only label in 3c.

### 3c. The read-only names
The old `lblAssigneeView` went with the old card. Select the new **card**, insert a **Text label** inside it, rename it `lblAssigneeView`, and give it the read-only label settings from guide 5.4: **Visible** `Parent.DisplayMode = DisplayMode.View`, **X** / **PaddingLeft** from `DataCardKeyN`, **Y** = the combo box's Y, **Height** `FormValueHeight`, **Size** `FormLabelSize`. Set its **Text** to this, which lists everyone in the short *First Last* style:
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

### 4c. The board: an ECAB column only while it's in use
The ECAB column shows only while an emergency the user can see is at the ECAB. The rest of the time, the board keeps its seven columns.

1. **App.Formulas:** add to the end:
   ```powerfx
   // Board columns: the ECAB column shows only while a request this user can see is in it.
   ECABActive  = !IsEmpty(Filter('Change Requests', Stage.Value = "Emergency CAB",
                     CanSeeAll || SubmittedBy = User().Email || RequesterEmail = User().Email));
   BoardStages = Filter(Stages, Name <> "Emergency CAB" || ECABActive);
   ```
2. **BoardScreen › `galStages`:**

   | Property | Value |
   |---|---|
   | Items | `BoardStages` |
   | TemplateSize | `Self.Width / CountRows(BoardStages) - 9` |

3. **`lblHeader` › Text:** number the columns by position, so they don't skip a number while ECAB is hidden:
   ```powerfx
   CountRows(Filter(BoardStages, Order <= ThisItem.Order)) & ". " & ThisItem.Short & "  (" & CountRows(galCards.AllItems) & ")"
   ```

**How it behaves:**
- **No emergency at the ECAB:** seven columns, as before.
- **An emergency reaches the ECAB:** the column appears at the board's next refresh: automatically every minute, with ⟳, or on returning to the board. It disappears again once the request moves on.
- **Visibility:** the check uses the board's own visibility rule, so regular users don't see an empty ECAB column for someone else's emergency. CM, TRB, CAB and Authority members see it whenever any emergency is at the ECAB.
- **Filters:** the Category and Type filters don't hide it. Like any column, it shows **(0)** while the filters hide its cards, so the board doesn't jump around as people filter.
- **Unchanged:** the detail screen's progress tracker and the Schedule still use the full `Stages` list.

With eight columns, each is about 160 pixels wide, so titles wrap sooner.

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
| 8 | Open the board with no emergency at the ECAB, then move an Emergency request to the ECAB and refresh | First seven columns numbered 1–7; then **3. ECAB** appears and the columns renumber 1–8. Once it moves on, ECAB disappears again |
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

---

## Part 6 — Software and hardware details, and the CMDB tasker

**What changes:**
- **Category-specific fields** on every request, shown only for their category:

  | Category | Fields |
  |---|---|
  | **Software** | Software name · Current version · New version *(if applicable)* |
  | **Hardware** | Make · Model · Serial number(s) · New serial number(s) *(if replaced)* |
  | **Network** | *(none: Affected systems describes it)* |

  **Affected systems** stays on every request. It's required for Network changes and optional for Software and Hardware.
- **A CMDB tasker email** goes to the **HW or SW managers**, the same people who already get the new-request emails, when a change has been implemented:

  | Category | To | CC |
  |---|---|---|
  | Hardware | HW managers | CM team |
  | Software | SW managers | CM team |
  | Network | HW **and** SW managers | CM team |

  - **When:** for every change type, as soon as the implementer clicks **✔ Completed** in Implementation.
  - **Rejected changes** never get one.
- **A required "CMDB updated" check:** a Yes/No field that the CM team or an HW or SW manager ticks once the CMDB is updated.
  - It shows from **Implementation** onward, and can only be changed **during Implementation**.
  - **No change can leave Implementation** until it's ticked.

**Time:** about 2½ hours. Do Parts 1–5 first: 6f adds lines to the Part 5 formula.

> **Requests already in Implementation** when you turn this on need **CMDB updated** ticked before they can move on. If the implementer had already clicked Completed, no tasker was sent, so contact the HW or SW managers directly. Requests already past Implementation aren't affected.

### 6a. SharePoint (Change Requests list)
Add these columns. Type each name exactly as shown, with no spaces.

| Name | Type | Settings |
|---|---|---|
| `SoftwareName` | Single line of text | |
| `CurrentVersion` | Single line of text | |
| `NewVersion` | Single line of text | |
| `HardwareMake` | Single line of text | |
| `HardwareModel` | Single line of text | |
| `SerialNumbers` | Multiple lines of text | More options › *Use enhanced rich text* **off** |
| `NewSerialNumbers` | Multiple lines of text | More options › *Use enhanced rich text* **off** |
| `CMDBUpdated` | Yes/No | Default **No** |

Then, in Power Apps Studio, go to **Data**, click **⋯** next to **Change Requests**, then **Refresh**.

> **Check the internal names.** Type each name in one go, exactly as above. If a name is mistyped and then renamed, the flows have to use the original internal name, as happened with A6 program (Troubleshooting-Notes, Issue 5).

### 6b. App.Formulas
Add to the **end**:
```powerfx
// HW and SW managers (the same people who get the new-request emails): they receive the CMDB tasker and can tick "CMDB updated". Use lower-case emails.
HWManagers = ["hw.manager1@us.af.mil", "hw.manager2@us.af.mil"];
SWManagers = ["sw.manager1@us.af.mil", "sw.manager2@us.af.mil"];
IsHWSWManager  = Lower(User().Email) in HWManagers || Lower(User().Email) in SWManagers;
```

Then change `CanSeeAll`, so the HW and SW managers can find any request on the board:
```powerfx
CanSeeAll = IsCM || IsTRB || IsCAB || IsAuthority || IsHWSWManager;
```

### 6c. New Request screen (`frmNew`)
1. Click **Edit fields › + Add field**, tick the seven new detail fields (not CMDBUpdated), and click **Add**.
2. **Placement:** drag them to just after **Location**, in this order:

   > … Location · **SoftwareName · CurrentVersion · NewVersion · HardwareMake · HardwareModel · SerialNumbers · NewSerialNumbers** · AffectedSystems · Description …

   The Software fields make one row of three, and Hardware makes one row of three plus New serial number(s) on its own row. Because each category fills whole rows, hiding the other category's fields shouldn't upset the 3-column layout. Check it in test 2.
3. **Unlock** each new card and apply the sizes from guide 4.3.
4. Set on each **card**:

   | Card | Label Text | Visible | Required |
   |---|---|---|---|
   | SoftwareName | `"Software name"` | `drpCategory.Selected.Value = "Software"` | same as Visible |
   | CurrentVersion | `"Current version"` | `drpCategory.Selected.Value = "Software"` | same as Visible |
   | NewVersion | `"New version (if applicable)"` | `drpCategory.Selected.Value = "Software"` | `false` |
   | HardwareMake | `"Make"` | `drpCategory.Selected.Value = "Hardware"` | same as Visible |
   | HardwareModel | `"Model"` | `drpCategory.Selected.Value = "Hardware"` | same as Visible |
   | SerialNumbers | `"Serial number(s)"` | `drpCategory.Selected.Value = "Hardware"` | same as Visible |
   | NewSerialNumbers | `"New serial number(s) (if replaced)"` | `drpCategory.Selected.Value = "Hardware"` | `false` |

5. **Update on each card:** save the value only for the chosen category, so switching category after typing doesn't leave stray values. Use the card's own text box name, and `"Hardware"` on the four hardware cards:
   ```powerfx
   If(drpCategory.Selected.Value = "Software", DataCardValueN.Text, Blank())
   ```
6. **Serial number boxes** (SerialNumbers and NewSerialNumbers): set the text box's **Mode** = `TextMode.MultiLine`, **Height** = `60` and **HintText** = `"One per line"`.
7. **Hints** on the other boxes: Software name `"e.g. Adobe Acrobat Pro"`, Current version `"e.g. 23.1"`, New version `"e.g. 24.2"`, Make `"e.g. Dell"`, Model `"e.g. OptiPlex 7090"`.
8. **AffectedSystems card › Required:** `drpCategory.Selected.Value = "Network"`.

### 6d. Detail screen (`frmDetail`)
1. **Edit fields › + Add field**: tick the seven detail fields and **CMDBUpdated**, then click **Add**.
2. **Placement:** the seven detail fields go just after **Location**, in the same order as 6c. **CMDBUpdated** goes just after **ReviewOutcome**.
3. **Unlock** each card, apply the sizes from guide 4.3, and use the same labels as 6c. CMDBUpdated's label is `"CMDB updated"`.
4. **The seven detail cards:**
   - **Visible**, with that card's category (`"Software"` or `"Hardware"`):
     ```powerfx
     Coalesce(drpCategoryDetail.Selected.Value, ThisItem.Category.Value) = "Software"
     ```
     For **NewVersion** and **NewSerialNumbers**, also hide them once read-only and empty (use that card's own column):
     ```powerfx
     Coalesce(drpCategoryDetail.Selected.Value, ThisItem.Category.Value) = "Software" &&
     (!IsBlank(ThisItem.NewVersion) || Parent.DisplayMode = DisplayMode.Edit)
     ```
   - **DisplayMode:** editable while the request is in *Requested*, and again in *Implementation*, so the implementer can correct versions or serials to what was actually installed:
     ```powerfx
     If(varCR.Stage.Value in ["Requested", "Implementation"], DisplayMode.Edit, DisplayMode.View)
     ```
   - **Update:**
     ```powerfx
     If(Coalesce(drpCategoryDetail.Selected.Value, ThisItem.Category.Value) = "Software", DataCardValueN.Text, Blank())
     ```
   - **Serial number boxes:** **Mode** `TextMode.MultiLine`, **Height** `60`.
5. **AffectedSystems:** keep the guide's Visible rule. It already shows the field while in *Requested* and hides it later when empty.
6. **CMDBUpdated card:**
   - **Visible:** from Implementation onward, for every change type:
     ```powerfx
     LookUp(Stages, Name = varCR.Stage.Value).Order >= LookUp(Stages, Name = "Implementation").Order
     ```
   - **DisplayMode:** editable only during Implementation, for the CM team and the HW and SW managers:
     ```powerfx
     If(varCR.Stage.Value = "Implementation" && (IsCM || IsHWSWManager), DisplayMode.Edit, DisplayMode.View)
     ```
   - Inside it, set the toggle's **TrueText** = `"Yes"` and **FalseText** = `"No"`.

### 6e. The closing rule (`frmDetail` › OnSuccess)
In the `"advance"` section, add this rule just **after** the `cur.Name = "Implementation" && IsBlank(varCR.ImplementationNotes)` rule:
```powerfx
                cur.Name = "Implementation" && !varCR.CMDBUpdated,
                    Notify("Confirm the CMDB has been updated (set CMDB updated to Yes) before moving on.", NotificationType.Error),
```

It applies to every change type, whether the next stage is PIR (Normal, Emergency) or Close (Standard). **Completed** isn't blocked: the implementer clicks it, which sends the tasker, and the request then waits in Implementation until the CMDB is updated.

Because Move saves first, a CM can set **CMDB updated** to Yes and click **Move** in one step. An HW or SW manager who isn't on the CM team ticks it and clicks **Save changes**, and CM moves the request on afterwards.

### 6f. Change log (Part 5)
In the Part 5 formula at the start of **`frmDetail` › OnSuccess**, add these lines to the `Table(…)`, just after the **Affected systems** line. Serial numbers are listed on one line, separated by commas.
```powerfx
                    {f: "Software name",          a: o.SoftwareName,                       b: n.SoftwareName,                       big: false},
                    {f: "Current version",        a: o.CurrentVersion,                     b: n.CurrentVersion,                     big: false},
                    {f: "New version",            a: o.NewVersion,                         b: n.NewVersion,                         big: false},
                    {f: "Make",                   a: o.HardwareMake,                       b: n.HardwareMake,                       big: false},
                    {f: "Model",                  a: o.HardwareModel,                      b: n.HardwareModel,                      big: false},
                    {f: "Serial numbers",         a: Substitute(o.SerialNumbers, Char(10), ", "),    b: Substitute(n.SerialNumbers, Char(10), ", "),    big: false},
                    {f: "New serial numbers",     a: Substitute(o.NewSerialNumbers, Char(10), ", "), b: Substitute(n.NewSerialNumbers, Char(10), ", "), big: false},
                    {f: "CMDB updated",           a: If(o.CMDBUpdated, "Yes", "No"),       b: If(n.CMDBUpdated, "Yes", "No"),       big: false},
```
The History then shows who ticked **CMDB updated** and when, e.g. *✎ CMDB updated: No → Yes*.

### 6g. The CMDB tasker email (stage-change flow)
Open **Change Request – Stage notifications** (guide 8b) in **Edit**.

1. **Recipients.** Next to the other **Initialize variable** actions, add two (String) holding the **same addresses** as the new-request flow (guide 8a). A flow can only read its own variables, so the addresses are copied here:

   | Name | Value |
   |---|---|
   | `HWManagerEmails` | `hw.manager1@us.af.mil;hw.manager2@us.af.mil` (same as the new-request flow) |
   | `SWManagerEmails` | `sw.manager1@us.af.mil;sw.manager2@us.af.mil` (same as the new-request flow) |

2. **After the Switch** (not inside it), add a **Condition** and rename it `Needs CMDB tasker`. In its first row, put this on the left as an **expression**, choose **is equal to**, and type `true` on the right:
   ```
   equals(triggerOutputs()?['body/ToStage'], 'Implementation complete')
   ```
   It's true when the implementer clicks **Completed**, for every change type.

3. **In the "True" branch**, add these actions. Rename each as shown.

   | # | Action | Rename to | Settings |
   |---|---|---|---|
   | 1 | **Compose** | `TaskerEmails` | expression below |
   | 2 | **Select** *(Map in text mode)* | `Tasker assignees` | **From:** expression below · **Map:** `item()?['DisplayName']` |
   | 3 | **Compose** | `CIDetails` | expression below |
   | 4 | **Compose** | `TaskerBody` | the HTML below |
   | 5 | **Send an email (V2)** *(or from a shared mailbox, guide 8d)* | `Send CMDB tasker` | To: `outputs('TaskerEmails')` · CC: `variables('CMTeamEmails')` · Subject: `concat('CMDB update required: ', outputs('CRNumber'), ' – ', body('Get_item')?['Title'])` · Body: **Code view**, then the **Outputs** of `TaskerBody` · Importance: `if(equals(body('Get_item')?['ChangeType']?['Value'], 'Emergency'), 'High', 'Normal')` |

   **`TaskerEmails`:**
   ```
   if(equals(body('Get_item')?['Category']?['Value'], 'Hardware'), variables('HWManagerEmails'), if(equals(body('Get_item')?['Category']?['Value'], 'Software'), variables('SWManagerEmails'), concat(variables('HWManagerEmails'), ';', variables('SWManagerEmails'))))
   ```

   **`Tasker assignees` › From** (works with one assignee or several):
   ```
   if(empty(body('Get_item')?['Assignee']), json('[]'), if(startsWith(string(body('Get_item')?['Assignee']), '['), body('Get_item')?['Assignee'], createArray(body('Get_item')?['Assignee'])))
   ```

   **`CIDetails`.** Builds the Software or Hardware rows, with serial numbers one per line:
   ```
   if(equals(body('Get_item')?['Category']?['Value'], 'Software'), concat('<tr><td><b>Software</b></td><td>', coalesce(body('Get_item')?['SoftwareName'], '—'), '</td></tr><tr><td><b>Current version</b></td><td>', coalesce(body('Get_item')?['CurrentVersion'], '—'), '</td></tr><tr><td><b>New version</b></td><td>', coalesce(body('Get_item')?['NewVersion'], '—'), '</td></tr>'), if(equals(body('Get_item')?['Category']?['Value'], 'Hardware'), concat('<tr><td><b>Make / model</b></td><td>', coalesce(body('Get_item')?['HardwareMake'], '—'), ' ', coalesce(body('Get_item')?['HardwareModel'], ''), '</td></tr><tr><td valign="top"><b>Serial number(s)</b></td><td>', replace(coalesce(body('Get_item')?['SerialNumbers'], '—'), decodeUriComponent('%0A'), '<br>'), '</td></tr><tr><td valign="top"><b>New serial number(s)</b></td><td>', replace(coalesce(body('Get_item')?['NewSerialNumbers'], '—'), decodeUriComponent('%0A'), '<br>'), '</td></tr>'), ''))
   ```

   **`TaskerBody`.** Paste as plain text, and replace `YOUR-WEB-LINK` as in guide 8c. The A6 program uses the column's internal name (Troubleshooting-Notes, Issue 5).
   ```html
   <p><b>CMDB update required</b></p>
   <p>Change <b>@{outputs('CRNumber')} – @{body('Get_item')?['Title']}</b> has been implemented. Please update the CMDB to reflect it <b>within 5 working days</b>.</p>
   <table cellpadding="6" style="border-collapse:collapse;font-family:Segoe UI,Arial,sans-serif;font-size:14px">
   <tr><td><b>CR number</b></td><td>@{outputs('CRNumber')}</td></tr>
   <tr><td><b>A6 program</b></td><td>@{body('Get_item')?['A6Program_x002c__x0020_DSN_x002c']}</td></tr>
   <tr><td><b>Category / type</b></td><td>@{body('Get_item')?['Category']?['Value']} / @{body('Get_item')?['ChangeType']?['Value']}</td></tr>
   @{outputs('CIDetails')}
   <tr><td><b>Affected systems</b></td><td>@{body('Get_item')?['AffectedSystems']}</td></tr>
   <tr><td><b>Location</b></td><td>@{body('Get_item')?['Location']}</td></tr>
   <tr><td><b>Implemented by</b></td><td>@{join(body('Tasker_assignees'), ', ')}</td></tr>
   <tr><td><b>Implemented</b></td><td>@{if(empty(body('Get_item')?['ActualStart']), '—', convertFromUtc(body('Get_item')?['ActualStart'], 'W. Europe Standard Time', 'dd MMM yyyy HH:mm'))} → @{if(empty(body('Get_item')?['ActualEnd']), '—', convertFromUtc(body('Get_item')?['ActualEnd'], 'W. Europe Standard Time', 'dd MMM yyyy HH:mm'))}</td></tr>
   <tr><td valign="top"><b>What was done</b></td><td style="white-space:pre-wrap">@{body('Get_item')?['ImplementationNotes']}</td></tr>
   </table>
   <p><b>Please:</b></p>
   <ol>
   <li>Update the configuration items above in the CMDB: add, change or retire records, versions, serial numbers or locations as applicable.</li>
   <li>Open the request and set <b>CMDB updated</b> to <b>Yes</b>, then click <b>Save changes</b>. Add a comment with the CI IDs you changed. The change can't be closed until this is done.</li>
   </ol>
   <p>If the change was rolled back, or doesn't match what's in the CMDB, contact the CM team before updating.</p>
   <p><a href="YOUR-WEB-LINK&crid=@{triggerOutputs()?['body/RequestID']}">Open @{outputs('CRNumber')} in the Change Request Portal</a></p>
   ```
   Change **5 working days** to the deadline your organization sets.

4. **Save** the flow.

> **Sent again after a send-back:** Send back clears *Completed*, so if a request is sent back to Implementation and the implementer clicks Completed again, the managers get a second tasker. That's useful when what was implemented changed. If it's not wanted, use `and(equals(triggerOutputs()?['body/ToStage'], 'Implementation complete'), equals(body('Get_item')?['CMDBUpdated'], false))` as the condition instead.

### 6h. Archive PDF (recommended)
In the **Change Request – Archive on close** flow and the manual copy, add the new fields so the record keeps them:

1. **`Fields`:** add these lines before the `"Generated"` line:
   ```json
     "SoftwareName": "@{if(empty(body('Get_item')?['SoftwareName']), '—', body('Get_item')?['SoftwareName'])}",
     "CurrentVersion": "@{if(empty(body('Get_item')?['CurrentVersion']), '—', body('Get_item')?['CurrentVersion'])}",
     "NewVersion": "@{if(empty(body('Get_item')?['NewVersion']), '—', body('Get_item')?['NewVersion'])}",
     "HardwareMake": "@{if(empty(body('Get_item')?['HardwareMake']), '—', body('Get_item')?['HardwareMake'])}",
     "HardwareModel": "@{if(empty(body('Get_item')?['HardwareModel']), '—', body('Get_item')?['HardwareModel'])}",
     "SerialNumbers": "@{if(empty(body('Get_item')?['SerialNumbers']), '—', body('Get_item')?['SerialNumbers'])}",
     "NewSerialNumbers": "@{if(empty(body('Get_item')?['NewSerialNumbers']), '—', body('Get_item')?['NewSerialNumbers'])}",
     "CMDBUpdated": "@{if(equals(body('Get_item')?['CMDBUpdated'], true), 'Yes', 'No')}",
   ```
2. **`Report HTML`:** add this section just **before** `<h2>Technical Review Board</h2>`:
   ```html
   <h2>Configuration items</h2>
   <table>
   <tr><td class="l">Software</td><td class="v">@{outputs('Fields')?['SoftwareName']}</td><td class="l">Version</td><td class="v">@{outputs('Fields')?['CurrentVersion']} → @{outputs('Fields')?['NewVersion']}</td></tr>
   <tr><td class="l">Make / model</td><td class="v">@{outputs('Fields')?['HardwareMake']} @{outputs('Fields')?['HardwareModel']}</td><td class="l">CMDB updated</td><td class="v">@{outputs('Fields')?['CMDBUpdated']}</td></tr>
   <tr><td class="l">Serial number(s)</td><td class="v">@{outputs('Fields')?['SerialNumbers']}</td><td class="l">New serial number(s)</td><td class="v">@{outputs('Fields')?['NewSerialNumbers']}</td></tr>
   </table>
   ```

### Part 6 tests

| # | Do this | Expect |
|---|---|---|
| 1 | On New Request, choose **Software** | Software name, Current version and New version appear as one row; the hardware fields are hidden |
| 2 | Switch to **Hardware** | Make, Model, Serial number(s) and New serial number(s) appear; the software fields are hidden; no gaps in the layout |
| 3 | Choose **Network** | No category fields; Affected systems shows a red star |
| 4 | Submit a Hardware request without a serial number | Error: *Fill in every field marked with a red star* |
| 5 | Type software details, switch to Hardware, fill that in and submit | Only the hardware values are saved in SharePoint |
| 6 | Take a **Normal Hardware** request to Implementation | **CMDB updated** shows (No); CM and the HW and SW managers can change it, others see it read-only |
| 7 | The implementer adds notes and clicks **✔ Completed** | The HW managers get *"CMDB update required: CR-…"*, CC the CM team, with make, model and serials one per line |
| 8 | CM clicks **Move to PIR** without CMDB updated ticked | Error: *Confirm the CMDB has been updated* |
| 9 | As an HW manager, open the request from the email link, set **CMDB updated** to Yes and **Save changes** | Saved; History shows *✎ CMDB updated: No → Yes* with their name |
| 10 | CM clicks **Move** | Moves to PIR; CMDB updated shows *Yes*, read-only |
| 11 | Take a **Standard Software** request to Implementation, click **✔ Completed**, then **Move** | The SW managers get the tasker; Move to Close is blocked until CMDB updated is Yes |
| 12 | Take a **Network** request to Implementation and click **✔ Completed** | Both the HW and SW managers get the tasker |
| 13 | Reject a request at CAB | No tasker is sent |
| 14 | Close a request and open its archive PDF *(if you did 6h)* | The *Configuration items* section shows the details and *CMDB updated: Yes* |

**If something goes wrong:**
- **Both categories' fields show, or neither:** check each card's **Visible** uses `drpCategory` (New Request) or `drpCategoryDetail` (detail screen), and the exact text `"Software"` or `"Hardware"`.
- **Fields leave gaps when hidden:** check the order in **Edit fields** matches 6c, so each category fills whole rows, and that the hidden system cards are still at the bottom.
- **No tasker email:** check the **Condition** is after the Switch, not inside a case, and that its right-hand side is `true`. The tasker comes from **Completed**, not from Move.
- **The tasker's details are blank:** check the new columns' internal names in **Get item › Show raw outputs** (see the note in 6a).
- **CMDB updated can't be ticked:** the person isn't in `CMTeam`, `HWManagers` or `SWManagers`, or the request isn't in Implementation.
