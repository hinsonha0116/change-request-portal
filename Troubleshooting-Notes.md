# Troubleshooting notes: where I left off

*Last updated 27 Oct 2026, part-way through the **New Request screen** update in [DetailScreen-Fixes.md](DetailScreen-Fixes.md).*

## Status at a glance

| Section of DetailScreen-Fixes.md | Status |
|---|---|
| 1 — Office 365 Users connector | ✅ Done |
| 2 — NewScreen and its banner | ✅ Done |
| 3 — Form `frmNew` | ✅ Done |
| 4 — Requested By people picker | ✅ Done (picker searches name **or** email) |
| 5 — Category, Change Type, Priority, Risk, Impact drop-downs | ⚠️ **In progress.** They show *Item 1, 2, 3* or nothing. See **Issue 1** |
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

**Symptom:**
- The five card drop-downs on NewScreen (Category, ChangeType, Priority, Risk, Impact) show Power Apps' sample list (*Item 1, 2, 3*) in **F5**.
- After changes, **Risk now shows nothing.**
- **A6 Program works.** It uses a list defined inside the app (`A6Programs`).

**What's been checked:**
- **Items formulas:** each drop-down's **Items** is the original `Choices([@'Change Requests'].<Column>)`, for example `Choices([@'Change Requests'].Risk)` on `DataCardValue29`. The formula looks correct, but Power Apps isn't showing the SharePoint choices.
- **Placeholder text:** "Find items" in Studio is just placeholder text and isn't the problem.

**Plan:** use **fixed lists inside the app**, the same approach that already works for A6 Program. What gets saved to SharePoint doesn't change.

### Step A — Add the lists to App.Formulas
**App › Formulas:** add this to the **end**. Make sure the line before it ends with `;`.
```powerfx
CategoryChoices   = ["Hardware", "Software", "Network"];
ChangeTypeChoices = ["Standard", "Normal", "Emergency", "Informational"];
PriorityChoices   = ["4 - Low", "3 - Moderate", "2 - High", "1 - Critical"];
LevelChoices      = ["3 - Moderate", "2 - High", "1 - Critical"];
```
The text must match the SharePoint choices **exactly**: plain hyphens, with a space on each side.

### Step B — Fix Risk first
1. Select **`DataCardValue29`** (inside `Risk_DataCard2`) and set:

   | Property | Value |
   |---|---|
   | Items | `LevelChoices` |
   | DisplayFields | `["Value"]` |
   | SearchFields | `["Value"]` |
   | DefaultSelectedItems | `Parent.Default` *(leave as is)* |

2. Select the **card** `Risk_DataCard2` and set **Update**:
   ```powerfx
   {Value: DataCardValue29.Selected.Value}
   ```
3. Press **F5**, open **Risk**. It should list `3 - Moderate`, `2 - High` and `1 - Critical`.

**If Risk is still empty:**
1. Add a temporary label on NewScreen with **Text** = `CountRows(LevelChoices)`.
   - **It shows 3:** the list is fine. Recheck **DisplayFields**: it must be exactly `["Value"]`, with straight quotes.
   - **It shows an error:** App.Formulas has a problem. Look for a missing `;` or a red underline, or open the **App checker**.
2. Delete the label afterwards.

### Step C — Repeat for the other four
Each drop-down is the `DataCardValueN` inside its card. Expand the card in the Tree view to see its name.

| Card | Drop-down **Items** | Card **Update** |
|---|---|---|
| Category | `CategoryChoices` | `{Value: <drop-down name>.Selected.Value}` |
| ChangeType | `ChangeTypeChoices` | `{Value: <drop-down name>.Selected.Value}` |
| Priority | `PriorityChoices` | `{Value: <drop-down name>.Selected.Value}` |
| Impact | `LevelChoices` | `{Value: <drop-down name>.Selected.Value}` |

Also set **DisplayFields** and **SearchFields** to `["Value"]` on each drop-down.

### Step D — Check the DetailScreen too
On the **DetailScreen**, open a request in *Requested*. If Category, ChangeType, Priority, Risk or Impact show *Item 1, 2, 3* or nothing there too, apply Steps B and C to those cards in `frmDetail`.

### Step E — Confirm it saves correctly
1. Submit a test request with all five chosen.
2. In SharePoint (**Change Requests**), check that Category, ChangeType, Priority, Risk and Impact show the right values.
3. On the board, the card should show the priority word and Risk and Impact.

**Keep in mind:** if a choice is ever added or renamed in SharePoint, update the matching list in App.Formulas too.

**After it works:** ask Claude to write the fixed-list approach into section 5 of the updates document, so the document matches the app.

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
