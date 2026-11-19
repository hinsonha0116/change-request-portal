# Temporary: rebuild the Assignee card for several people

> **Delete this file once the Assignee card works.** It's a one-off fix for update Part 3 (several assignees) in [DetailScreen-Fixes.md](DetailScreen-Fixes.md).

**Why:** after **Allow multiple selections** was turned on for Assignee in SharePoint, the card's **Default** showed *"Expected record value… the rule produces table values"*. The card was built when Assignee held one person, and refreshing the data doesn't rebuild an existing card. Removing and re-adding the field builds a new card for several people.

`N` = the number Power Apps gives the new card's controls. Expand the card in the Tree view to see the real names, e.g. `DataCardKey45`, `DataCardValue45`.

## 1. Remove and re-add the field
1. Select **`frmDetail`** on DetailScreen and click **Edit fields** in the Properties pane.
2. Hover **Assignee**, click **⋯**, then **Remove**.
3. Click **+ Add field**, tick **Assignee**, and click **Add**.
4. Drag **Assignee** to just after **AuthorityDecision**, so the order runs *… CABDecision · AuthorityDecision · **Assignee** · ActualStart · ActualEnd · ReviewOutcome …*
5. Select the new card (`Assignee_DataCard…`) and click **Properties › Advanced › 🔒 Unlock to change properties**.

## 2. The card
Select the **card** and set:

| Property | Value |
|---|---|
| Visible | the formula below |
| DisplayMode | `If(varCR.Stage.Value = "Implementation", DisplayMode.Edit, DisplayMode.View)` |
| WidthFit | `false` |
| Update | `DataCardValueN.SelectedItems` *(the combo box's name)* |
| Default | leave it as `ThisItem.Assignee` |

**Visible** (shown from Implementation on, only on routes that pass through it):
```powerfx
With({s: LookUp(Stages, Name = "Implementation")},
    LookUp(Stages, Name = varCR.Stage.Value).Order >= s.Order &&
    Coalesce(varCR.ChangeType.Value, "Normal") in s.Types)
```

## 3. The title label (`DataCardKeyN`)

| Property | Value |
|---|---|
| Text | `"Assignees"` |
| Size | `FormLabelSize` |
| Height | `FormLabelHeight` |

## 4. The combo box (`DataCardValueN`)

| Property | Value |
|---|---|
| SelectMultiple | `true` |
| DefaultSelectedItems | `Parent.Default` |
| DisplayFields | `["DisplayName"]` |
| SearchFields | `["DisplayName", "Email"]` |
| Visible | `Parent.DisplayMode = DisplayMode.Edit` |
| Size | `FormLabelSize` |
| Height | `FormValueHeight` |

> If the combo box and the label overlap, set the combo box's **Y** to `DataCardKeyN.Y + DataCardKeyN.Height + 2`.

## 5. The read-only names (`lblAssigneeView`)
1. Select the **card**, choose **+ Insert › Text label**, and check that it's **indented under the card** in the Tree view.
2. Rename it `lblAssigneeView` and set:

| Property | Value |
|---|---|
| Text | the formula below |
| Visible | `Parent.DisplayMode = DisplayMode.View` |
| X | `DataCardKeyN.X` |
| PaddingLeft | `DataCardKeyN.PaddingLeft` |
| Y | `DataCardValueN.Y` *(the combo box's Y)* |
| Width | `Parent.Width - DataCardKeyN.X - 10` |
| Height | `FormValueHeight` |
| Size | `FormLabelSize` |
| PaddingTop / PaddingBottom | `0` |
| VerticalAlign | `VerticalAlign.Middle` |
| Color | `Color.Black` |

**Text** (everyone, as *First Last*, separated by commas):
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
If several names get cut off, set **Wrap** = `true` and **Height** = `FormValueHeight * 2`.

## 6. Check
1. **Save** (Ctrl+S).
2. Press **F5**, open a request at **Implementation**, pick **two** people, click **Save changes**, and reopen the request. Both names should be there.
3. Open a request at **PIR** or **Close** with assignees. The names show as plain text, lined up under the title.
4. Check that nothing else moved: **Actual start** and **Actual end** should still sit beside Assignees on the same row.

**If the Default error comes back on the new card:** save, close Power Apps Studio completely, reopen the app, refresh **Change Requests** under **Data**, then repeat step 1.

## When you're done
Tell Claude, and this file will be deleted, with update Part 3 changed to say "remove and re-add the Assignee field" so the next build doesn't hit the same error.
