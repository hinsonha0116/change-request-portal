# Troubleshooting notes: where I left off

*Last updated 28 Oct 2026, part-way through the **New Request screen** update in [DetailScreen-Fixes.md](DetailScreen-Fixes.md).*

## Status at a glance

| Section of DetailScreen-Fixes.md | Status |
|---|---|
| 1 — Office 365 Users connector | ✅ Done |
| 2 — NewScreen and its banner | ✅ Done |
| 3 — Form `frmNew` | ✅ Done |
| 4 — Requested By people picker | ✅ Done (picker searches name **or** email) |
| 5 — Category, Change Type, Priority, Risk, Impact drop-downs | ⚠️ **In progress.** Risk fixed with a classic Drop down; the other four next. See **Issue 1** |
| 5b — A6 Program drop-down | ✅ Working |
| 6 — Attachments | ⬜ Check |
| 7 — Submit | ⬜ Check |
| 8 — Board button (`btnNew`) | ⚠️ **Fix needed.** A Reset error shows when the app opens. See **Issue 2** |
| 9 — Who can see the new request | Nothing to do |
| 10 — Retire the form and flow | ⬜ After testing |
| Test checklist (15 rows) | ⬜ After everything above |

**Start tomorrow with Issue 2.** It's quick and removes the error. **Then Issue 1.**

> **How to set a property:** select the control in the **Tree view**, choose the property in the dropdown at the left of the formula bar, and paste the value into the formula bar.

---

## Issue 2 — "The Reset function can only be used with a resettable control…" (do this first)

**Where it comes from:** `btnNew` on **BoardScreen**. Its OnSelect calls `Reset(cmbRequestedBy)` and `Reset(drpA6Program)`. Those controls are inside `frmNew`, and Power Apps only lets you reset controls in a form from *inside that form*. Section 8 of the updates document originally said to do this. It has since been corrected.

**Fix:**

1. **BoardScreen › `btnNew` › OnSelect.** Replace it with:
   ```powerfx
   NewForm(frmNew);
   Set(varResetNew, true);
   Set(varResetNew, false);
   Navigate(NewScreen, ScreenTransition.Cover)
   ```
2. **NewScreen:** set the **Reset** property (type "reset" in the property dropdown) on both controls:

   | Control | Reset |
   |---|---|
   | `cmbRequestedBy` | `varResetNew` |
   | `drpA6Program` | `varResetNew` |

3. **Check:**
   - The error no longer appears when the app opens. If it does, open the **App checker** (the stethoscope icon) and look for any other `Reset(...)` that names a control inside `frmNew`.
   - Press **F5** and click **+ Request a New Change**. Pick a colleague and a program, then click **← Board**, then **+ Request a New Change** again. Requested By should be back to **you**, and A6 Program should be empty.

---

## Issue 1 — Choice drop-downs show *Item 1, Item 2, Item 3*, or nothing

**Symptom:** the five card drop-downs on NewScreen (Category, ChangeType, Priority, Risk, Impact) showed Power Apps' sample list (*Item 1, 2, 3*) in **F5**, and later nothing at all.

**What we found:**
- **The lists are fine.** A test label with `CountRows(LevelChoices)` showed **3**, and DisplayFields was correct.
- **The control is the problem.** The **combo box** Power Apps puts in these cards won't display the options in this environment.
- **The fix:** a classic **Drop down**, the same control A6 Program uses (which works), is shown in each card instead.

**Status:** ✅ **Risk fixed** using the steps below. ⬜ **Category, ChangeType, Priority and Impact** still to do, the same way.

### Step A — Lists in App.Formulas (✅ done)
**App › Formulas**, at the end:
```powerfx
CategoryChoices   = ["Hardware", "Software", "Network"];
ChangeTypeChoices = ["Standard", "Normal", "Emergency", "Informational"];
PriorityChoices   = ["4 - Low", "3 - Moderate", "2 - High", "1 - Critical"];
LevelChoices      = ["3 - Moderate", "2 - High", "1 - Critical"];
```

### Step B — For each card, swap the combo box for a Drop down
Do these steps for each card. Risk is already done, and the full values are in the table in Step C.

1. Expand the card in the Tree view. Select its **combo box** (`DataCardValueN`) and set **Visible** to `false`. Don't delete it.
2. Select the **card**, then choose **+ Insert › Drop down**. Check that it lands **inside the card**.
3. Rename the drop-down. Set its **Items** and **Default** from the table, plus these on every one:

   | Property | Value |
   |---|---|
   | AllowEmptySelection | `true` |
   | Reset | `varResetNew` |
   | X / Y | `DataCardValueN.X` / `DataCardValueN.Y` *(that card's hidden combo box)* |
   | Width / Height | `DataCardValueN.Width` / `40` |

4. Select the **card** and set **Update** from the table.

### Step C — Values to copy

| Card | Drop-down name | Items | Default |
|---|---|---|---|
| Risk ✅ | `drpRisk` | `LevelChoices` | `ThisItem.Risk.Value` |
| Category | `drpCategory` | `CategoryChoices` | `ThisItem.Category.Value` |
| ChangeType | `drpChangeType` | `ChangeTypeChoices` | `ThisItem.ChangeType.Value` |
| Priority | `drpPriority` | `PriorityChoices` | `ThisItem.Priority.Value` |
| Impact | `drpImpact` | `LevelChoices` | `ThisItem.Impact.Value` |

**Card Update** formulas:

Risk ✅
```powerfx
If(IsBlank(drpRisk.Selected.Value), Blank(), {Value: drpRisk.Selected.Value})
```
Category
```powerfx
If(IsBlank(drpCategory.Selected.Value), Blank(), {Value: drpCategory.Selected.Value})
```
ChangeType
```powerfx
If(IsBlank(drpChangeType.Selected.Value), Blank(), {Value: drpChangeType.Selected.Value})
```
Priority
```powerfx
If(IsBlank(drpPriority.Selected.Value), Blank(), {Value: drpPriority.Selected.Value})
```
Impact
```powerfx
If(IsBlank(drpImpact.Selected.Value), Blank(), {Value: drpImpact.Selected.Value})
```

What each part does:
- **`If(IsBlank(...), Blank(), ...)`:** keeps the red-star required check working. An empty choice saves as blank, so Submit catches it.
- **`ThisItem.<Column>.Value`:** shows the request's saved choice. Use this, not `Parent.Default.Value`, which gave a *"Value isn't recognized"* error.
- **`Reset = varResetNew`:** clears the drop-down each time **+ Request a New Change** is clicked (see Issue 2).

### Step D — Check the DetailScreen too
On the **DetailScreen**, open a request in *Requested*. If any of these five show *Item 1, 2, 3* or nothing in `frmDetail`, apply the same swap there.
- Use names like `drpRiskDetail`.
- Use the same Items, Default and Update formulas.
- Leave out **Reset** on the DetailScreen versions.
- Set each drop-down's **DisplayMode** to `If(varCR.Stage.Value = "Requested", DisplayMode.Edit, DisplayMode.View)`.

### Step E — Test
1. Press **F5** and click **+ Request a New Change**. All five drop-downs list their choices and start empty.
2. Leave **Priority** empty and click **Submit**. You should get *"Fill in every field marked with a red star"*.
3. Fill everything in and submit. In SharePoint (**Change Requests**), check that Category, ChangeType, Priority, Risk and Impact all saved correctly.
4. Click **+ Request a New Change** again. All five are empty again.

**Keep in mind:** if a choice is ever added or renamed in SharePoint, update the matching list in App.Formulas too.

---

## Then carry on

1. **Section 6, Attachments:** set the card label and **MaxAttachments** = `10`.
2. **Section 7, Submit:** `btnSubmit` OnSelect, plus `frmNew` OnSuccess and OnFailure. Replace `DataCardValueN` in the attachment check with the Attachments card's control name (it was `DataCardValue32` in the screenshot).
3. **Run the 15-row test checklist** at the end of the updates document.
4. **Section 10:** once everything passes, turn off the flow and close the Microsoft Form.
5. **Publish**, and have users fully close and reopen the app, sometimes twice.

## Handy checks
- **App checker** (the stethoscope icon in the top toolbar): lists every formula error and where it is.
- **Temporary label with `User().Email`:** shows which email the app sees for the signed-in user.
- **Data › ⋯ › Refresh** next to a list: picks up new or changed SharePoint columns.
- **A control that should be inside a card or gallery** must be indented under it in the Tree view. To move one there: **Ctrl+X**, select the card or gallery, then **Ctrl+V**.
