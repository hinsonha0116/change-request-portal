# DetailScreen fixes and the Add comment button

These are changes to the **DetailScreen** you built in Step 5 of [Change-Request-PowerApp-Guide.md](Change-Request-PowerApp-Guide.md). They fix two problems:

1. **The Send back, Move and Reject buttons stay greyed out, even after saving.** The form keeps reporting "unsaved changes" that aren't real. Fixes 1 and 2 solve this.
2. **There's no way to post a comment to the History without moving the request.** Fix 3 adds an **Add comment** button for this.

Apply them in order. They take about 15 minutes.

> **How to set a property:** select the control in the **Tree view**, choose the property in the dropdown at the left of the formula bar, and paste the value into the formula bar.

---

## Fix 1 — Keep empty date fields empty

**Why:** requests from the Microsoft Form have *PlannedStart*, *PlannedEnd*, *ActualStart* and *ActualEnd* blank. A form date card builds its value from the date picker plus the hour and minute dropdowns. When the date is empty it still produces a time (midnight), so the form thinks something changed.

**Do this for each of the four date cards** (`PlannedStart_DataCard1`, `PlannedEnd_DataCard1`, `ActualStart_DataCard1`, `ActualEnd_DataCard1`):

1. Select the card in the Tree view, under `frmDetail`.
2. If you can't edit it, open the **Properties** pane, then the **Advanced** tab, and click **🔒 Unlock to change properties**.
3. Choose the **Update** property. It looks something like:
   ```powerfx
   DateValue1.SelectedDate + Time(Value(HourValue1.Selected.Value), Value(MinuteValue1.Selected.Value), 0)
   ```
4. Wrap it so a blank date stays blank. Keep **your** control names, which may be `DateValue2`, `HourValue3` and so on:
   ```powerfx
   If(IsBlank(DateValue1.SelectedDate), Blank(),
      DateValue1.SelectedDate + Time(Value(HourValue1.Selected.Value), Value(MinuteValue1.Selected.Value), 0))
   ```

Fix 1 alone may not get rid of the phantom changes. Fix 2 removes the dependency on them entirely.

---

## Fix 2 — Buttons save first, then act

**Why:** the action buttons were disabled whenever `frmDetail.Unsaved` was true, and that flag can get stuck. With this fix:
- the buttons are **never greyed out**,
- every action button **saves the form first**, then does its action once the save succeeds,
- a CAB member can choose *Approved* and click **Move** straight away, without clicking Save first.

### 2a. Change the four buttons
For each button below:
- set **DisplayMode** to `DisplayMode.Edit`
- replace **OnSelect** with the formula shown
- leave **Visible** and **Text** as they are

| Button | OnSelect |
|---|---|
| `btnSave` | `Set(varAction, "save"); SubmitForm(frmDetail)` |
| `btnAdvance` | `Set(varAction, "advance"); SubmitForm(frmDetail)` |
| `btnSendBack` | `If(IsBlank(Trim(txtComment.Text)), Notify("Add a comment explaining why it's being sent back.", NotificationType.Warning), Set(varAction, "back"); SubmitForm(frmDetail))` |
| `btnReject` | `If(IsBlank(Trim(txtComment.Text)), Notify("Add a comment explaining the rejection.", NotificationType.Warning), Set(varAction, "reject"); SubmitForm(frmDetail))` |

### 2b. Move the action logic into the form
Select `frmDetail` and replace **OnSuccess** with this whole block. It runs after every successful save and carries out whichever button was clicked:

```powerfx
Set(varCR, Self.LastSubmit);
Switch(varAction,
    "advance",
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
                Set(varCR, Patch('Change Requests', varCR, {
                    Stage:      {Value: nxt.Name},
                    ClosedDate: If(nxt.Name = "Close", Now())
                }));
                Patch('Change Request History', Defaults('Change Request History'), {
                    Title: "CR-" & Text(varCR.ID, "00000"), RequestID: varCR.ID,
                    FromStage: cur.Name, ToStage: nxt.Name, Comment: txtComment.Text
                });
                Reset(txtComment);
                Notify("Moved to " & nxt.Name, NotificationType.Success)
            )
        )),
    "back",
        With({cur: LookUp(Stages, Name = varCR.Stage.Value)},
        With({prv: LookUp(Stages, Order = cur.Order - 1)},
            Set(varCR, Patch('Change Requests', varCR, {Stage: {Value: prv.Name}}));
            Patch('Change Request History', Defaults('Change Request History'), {
                Title: "CR-" & Text(varCR.ID, "00000"), RequestID: varCR.ID,
                FromStage: cur.Name, ToStage: prv.Name, Comment: txtComment.Text
            });
            Reset(txtComment);
            Notify("Sent back to " & prv.Name, NotificationType.Warning)
        )),
    "reject",
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
                Title: "CR-" & Text(varCR.ID, "00000"), RequestID: varCR.ID,
                FromStage: prevStage, ToStage: "Close", Comment: "REJECTED: " & txtComment.Text
            });
            Reset(txtComment);
            Notify("Change rejected and closed", NotificationType.Warning)
        ),
    Notify("Saved", NotificationType.Success)
);
Set(varAction, Blank())
```

### 2c. Clear the pending action if a save fails
Replace `frmDetail` **OnFailure** with:
```powerfx
Set(varAction, Blank());
Notify("Couldn't save: " & Self.Error, NotificationType.Error)
```

If you added a temporary label showing `frmDetail.Unsaved` while troubleshooting, delete it.

---

## Fix 3 — Add comment button

**Why:** the comment box was only logged when a request moved. This button posts the comment to the History straight away and leaves the stage as it is.

### 3a. Make room for the button
Select `txtComment` and change **Width** to `400`.

### 3b. Add the button
Select **DetailScreen**, insert a **Button**, rename it `btnAddComment`, and set:

| Property | Value |
|---|---|
| Text | `"Add comment"` |
| X / Y | `430` / `Parent.Height - 62` |
| Width / Height | `120` / `44` |
| Fill | `Color.White` |
| Color | `ColorValue("#1E3A6B")` |
| BorderColor | `ColorValue("#1E3A6B")` |

**OnSelect**:
```powerfx
If(IsBlank(Trim(txtComment.Text)),
    Notify("Type a comment first.", NotificationType.Warning),
    Patch('Change Request History', Defaults('Change Request History'), {
        Title:     "CR-" & Text(varCR.ID, "00000"),
        RequestID: varCR.ID,
        FromStage: varCR.Stage.Value,
        ToStage:   varCR.Stage.Value,
        Comment:   txtComment.Text
    });
    Reset(txtComment);
    Notify("Comment added", NotificationType.Success)
)
```

The button doesn't touch the form, so it works at any stage, even with unsaved edits.

### 3c. Label comments in the History panel
A comment is saved with the *same* stage in FromStage and ToStage. Update the History label so these rows read **Comment (stage)** instead of showing an arrow.

Select `lblHistMove` (inside `galHistory`) and replace its **Text** with:
```powerfx
If(IsBlank(ThisItem.FromStage), "Created",
   ThisItem.FromStage = ThisItem.ToStage, "Comment (" & ThisItem.ToStage & ")",
   ThisItem.FromStage & " → " & ThisItem.ToStage)
```

**Layout of the action bar after this fix:**

| Control | X | Width |
|---|---|---|
| `txtComment` | 20 | 400 |
| `btnAddComment` | 430 | 120 |
| `btnSave` | 560 | 130 |
| `btnSendBack` | 705 | 150 |
| `btnReject` | 870 | 130 |
| `btnAdvance` | 1015 | 331 |

---

## Test

Press **F5** on **BoardScreen**, open a request, and check each row:

| # | Do this | Expect |
|---|---|---|
| 1 | Open any request | Save, Move and Send back are **not** greyed out |
| 2 | Type a comment and click **Add comment** | History shows **Comment (current stage)**; the stage doesn't change |
| 3 | Edit a field and click **Save changes** | "Saved" message; the edit is kept; no History row is added |
| 4 | On a request in CAB or later, type a comment and click **Send back** | Moves back one stage; a History row shows your comment |
| 5 | Click **Send back** with an empty comment box | Warning asks for a comment; nothing moves |
| 6 | On a CAB-stage request with CAB Decision *Pending*, click **Move** | Error: *CAB decision must be Approved*; it stays in CAB |
| 7 | As a CAB member, set CAB Decision to **Approved** and click **Move** *without saving first* | Saves and moves to Change Authority in one click |
| 8 | On a CAB-stage request, type a comment and click **Reject** | Goes to Close; History shows **REJECTED:** and your comment |

**If something goes wrong:**
- **A red error banner** appears: send the exact text.
- **A button does nothing:** check that its formula has no red underlines. Then open the **App checker** (the stethoscope icon in the top toolbar), which lists every formula error in the app.
