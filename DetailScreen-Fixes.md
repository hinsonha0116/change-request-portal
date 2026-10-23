# App updates: notes tabs

These changes build on the app from [Change-Request-PowerApp-Guide.md](Change-Request-PowerApp-Guide.md), with all earlier updates already applied:
- the save-then-act buttons,
- Description and History on the right,
- Add comment,
- CM-only buttons,
- users seeing only their own requests.

**What changes:** the Description box on the right of the DetailScreen becomes a tabbed **notes** box.
- **Tabs:** across the top, **Description · CAB · Authority · Implement · Review**.
- **Tabs appear as the request reaches each stage.** A request in Change Authority shows Description, CAB and Authority.
- **Clicking a tab** shows that note in the same box. Long notes scroll.
- **Only the current stage's note is editable,** following the same rules as before:

  | Note | Editable when |
  |---|---|
  | Description | the request is in *Requested* |
  | CAB notes | the request is in the CAB stage, for CAB members |
  | Authority notes | the request is in the Change Authority stage, for Change Authorities |
  | Implementation notes | the request is in Implementation |
  | Review notes | the request is in Review |

  Every other tab is read-only. The editable tab is shown in **bold**.
- **Opening a request** shows the current stage's tab first. After a move, the box switches to the new stage's tab.
- The CAB, Authority, Implementation and Review notes **move out of the form** on the left, which leaves it shorter.

> **How to set a property:** select the control in the **Tree view**, choose the property in the dropdown at the left of the formula bar, and paste the value into the formula bar.

---

## 1 — App.Formulas: list the tabs

Select **App**, choose **Formulas**, and add this to the **end**:

```powerfx
NoteTabs = Table(
    {Key: "Description",    Label: "Description", MinStage: 1},
    {Key: "CAB",            Label: "CAB",         MinStage: 2},
    {Key: "Authority",      Label: "Authority",   MinStage: 3},
    {Key: "Implementation", Label: "Implement",   MinStage: 4},
    {Key: "Review",         Label: "Review",      MinStage: 5}
);
```

`MinStage` is the stage number at which the tab appears. "Implementation" is shortened to *Implement* so all five tabs fit in the 426-pixel width.

---

## 2 — Rename the Description boxes

In the Tree view, double-click each name and rename it:

| Old name | New name |
|---|---|
| `txtDescription` | `txtNote` |
| `lblDescription` | `lblNote` |

Power Apps updates every formula that refers to them automatically.

Then **delete `lblDescTitle`** (the "Description" heading). The tabs take its place.

---

## 3 — Hidden helper: which note is editable right now

Select **DetailScreen**, insert a **Text label**, rename it `lblEditableNote`, and set:

| Property | Value |
|---|---|
| Visible | `false` |
| Text | see below |

**Text**:
```powerfx
Switch(varCR.Stage.Value,
    "Requested",             "Description",
    "Change Advisory Board", If(IsCAB, "CAB", ""),
    "Change Authority",      If(IsAuthority, "Authority", ""),
    "Implementation",        "Implementation",
    "Review",                "Review",
    "")
```

The label shows the key of the one note the current user can edit, or nothing if they can't edit any. The other controls read it from here, so the rule is written only once.

---

## 4 — Add the tabs

### 4a. The tab gallery
Select **DetailScreen**, insert a **Blank horizontal gallery**, rename it `galNoteTabs`, and set:

| Property | Value |
|---|---|
| Items | `Filter(NoteTabs, MinStage <= LookUp(Stages, Name = varCR.Stage.Value).Order)` |
| X / Y | `920` / `146` |
| Width / Height | `426` / `30` |
| TemplateSize | `Self.Width / 5` |
| TemplatePadding | `0` |
| ShowScrollbar | `false` |
| ShowNavigation | `false` |
| OnSelect | `Set(varNoteTab, ThisItem.Key)` |

If a data-source panel pops up when you insert the gallery, close it.

### 4b. What each tab looks like
Click the first item of `galNoteTabs` until the pencil ✎ shows at its top-left, then insert these into its template. They should appear **indented under `galNoteTabs`** in the Tree view.

| # | Insert | Rename to | Properties |
|---|---|---|---|
| 1 | Rectangle | `rectTab` | X `1` · Y `0` · Width `Parent.TemplateWidth - 2` · Height `30` · Fill: `If(ThisItem.Key = varNoteTab, ColorValue("#1E3A6B"), RGBA(0,0,0,0.06))` |
| 2 | Text label | `lblTab` | X `0` · Y `0` · Width `Parent.TemplateWidth` · Height `30` · Text: `ThisItem.Label` · Align: `Align.Center` · Size `10` · PaddingLeft/Right `2` · PaddingTop/Bottom `0` · FontWeight: `If(ThisItem.Key = lblEditableNote.Text, FontWeight.Bold, FontWeight.Normal)` · Color: `If(ThisItem.Key = varNoteTab, Color.White, Color.Black)` |

The selected tab is filled navy, and the tab you can edit is **bold**.

---

## 5 — Point the boxes at the selected note

The two boxes stay where they are (X `920`, Y `176`, 426 × 200), and only one is visible at a time:
- **`txtNote`** (editable) shows when you're on the tab you're allowed to edit.
- **`lblNote`** (read-only) shows for every other tab.

### 5a. `txtNote`

| Property | Value |
|---|---|
| Default | see below |
| Visible | `!IsBlank(lblEditableNote.Text) && varNoteTab = lblEditableNote.Text` |
| HintText | `"Type " & LookUp(NoteTabs, Key = varNoteTab).Label & " notes"` |

**Default**:
```powerfx
Switch(lblEditableNote.Text,
    "Description",    varCR.Description,
    "CAB",            varCR.CABNotes,
    "Authority",      varCR.AuthorityNotes,
    "Implementation", varCR.ImplementationNotes,
    "Review",         varCR.ReviewNotes)
```

**Default** follows the *editable* note, not the selected tab, on purpose. That way, anything you've typed isn't wiped when you click another tab and come back.

Leave **Mode** (`TextMode.MultiLine`), position and size as they are.

### 5b. `lblNote`

| Property | Value |
|---|---|
| Text | see below |
| Visible | `!txtNote.Visible` |

**Text**:
```powerfx
Coalesce(
    Switch(varNoteTab,
        "Description",    varCR.Description,
        "CAB",            varCR.CABNotes,
        "Authority",      varCR.AuthorityNotes,
        "Implementation", varCR.ImplementationNotes,
        "Review",         varCR.ReviewNotes),
    "No notes yet.")
```

Leave **Overflow** (`Overflow.Scroll`), the border, padding, position and size as they are.

---

## 6 — Save the notes through the form

The four notes cards come off the screen but **stay in the form**, so **Save changes** and the action buttons still write them to SharePoint.

In the Tree view, expand `frmDetail` and do this for each card below:
1. If it's locked, open **Properties › Advanced** and click **🔒 Unlock to change properties**.
2. Set **Visible** to `false`. The Description card is already hidden.
3. Set **Update** to the formula in the table.

| Card | Update |
|---|---|
| `Description_DataCard1` | `If(lblEditableNote.Text = "Description", txtNote.Text, ThisItem.Description)` |
| `CABNotes_DataCard1` | `If(lblEditableNote.Text = "CAB", txtNote.Text, ThisItem.CABNotes)` |
| `AuthorityNotes_DataCard1` | `If(lblEditableNote.Text = "Authority", txtNote.Text, ThisItem.AuthorityNotes)` |
| `ImplementationNotes_DataCard1` | `If(lblEditableNote.Text = "Implementation", txtNote.Text, ThisItem.ImplementationNotes)` |
| `ReviewNotes_DataCard1` | `If(lblEditableNote.Text = "Review", txtNote.Text, ThisItem.ReviewNotes)` |

Each card takes the text from `txtNote` only when that note is the editable one. Otherwise it keeps what's already saved.

The rule that blocks moving to Review until Implementation notes are filled in keeps working, because it checks the saved value.

---

## 7 — Open on the right tab

### 7a. When the screen opens
Select **DetailScreen** and replace **OnVisible** with:
```powerfx
Set(varCR, LookUp('Change Requests', ID = varCR.ID));
Set(varNoteTab, Switch(varCR.Stage.Value,
    "Change Advisory Board", "CAB",
    "Change Authority",      "Authority",
    "Implementation",        "Implementation",
    "Review",                "Review",
    "Close",                 "Review",
    "Description"))
```

### 7b. After a move
Select `frmDetail`, open **OnSuccess**, and add this just **before** the last line, `Set(varAction, Blank())`:
```powerfx
If(varAction <> "save",
    Set(varNoteTab, Switch(varCR.Stage.Value,
        "Change Advisory Board", "CAB",
        "Change Authority",      "Authority",
        "Implementation",        "Implementation",
        "Review",                "Review",
        "Close",                 "Review",
        "Description")));
```

After a **Move**, **Send back** or **Reject**, the box switches to the new stage's tab. A plain **Save changes** leaves you on the tab you were on.

---

## 8 — Stop Reject from overwriting notes (recommended)

**Reject** currently *replaces* CAB Notes or Authority Notes with the rejection comment. Now that the notes are visible in tabs, it's better to **add** the comment underneath what's already there.

In `frmDetail` › **OnSuccess**, find the `"reject"` section and make two changes:

| Find | Replace with |
|---|---|
| `CABNotes: txtComment.Text` | `CABNotes: Trim(varCR.CABNotes & Char(10) & "REJECTED: " & txtComment.Text)` |
| `AuthorityNotes: txtComment.Text` | `AuthorityNotes: Trim(varCR.AuthorityNotes & Char(10) & "REJECTED: " & txtComment.Text)` |

---

## Test

Press **F5** on **BoardScreen** and check each row:

| # | Do this | Expect |
|---|---|---|
| 1 | Open a request in **Requested** | Only the **Description** tab shows; it's bold, selected, and editable |
| 2 | Edit the description and click **Save changes** | "Saved"; reopen the request and the new text is there |
| 3 | As CM, **Move** it to CAB | The **CAB** tab appears and opens automatically |
| 4 | As a **CAB member**, type CAB notes and click **Save changes** | Saved; reopen and the CAB tab shows your notes |
| 5 | Click the **Description** tab | Description shows read-only and scrolls if it's long |
| 6 | Open the same CAB-stage request as someone **not** on the CAB | The CAB tab is read-only; no tab is bold |
| 7 | Type in the CAB tab, click Description, then click CAB again | Your unsaved text is still there |
| 8 | Move a request to **Implementation** and click **Move** with no Implementation notes | Error: *Add implementation notes before moving to Review* |
| 9 | Type notes on the **Implement** tab, then click **Move** | Saves and moves to Review; the box switches to the **Review** tab |
| 10 | **Reject** a CAB-stage request that already has CAB notes | The CAB tab shows the original notes, then a **REJECTED:** line with your comment |
| 11 | Open a **closed** request | All five tabs show, every tab is read-only, and the box opens on **Review** |

**If something goes wrong:**
- **A tab shows *ThisItem isn't recognized*:** the control is on the screen instead of inside `galNoteTabs`. Cut it (**Ctrl+X**), click the first tab until the pencil ✎ shows, and paste (**Ctrl+V**).
- **Notes don't save:** check the card's **Update** formula in section 6, and that the card is still in `frmDetail`. It should be hidden, not removed.
- **The editable box shows the wrong note:** check that `txtNote` **Default** uses `lblEditableNote.Text`, not `varNoteTab`.
- **Anything else:** open the **App checker** (the stethoscope icon in the top toolbar) to see every formula error, and send me the exact text of any red error banner.
