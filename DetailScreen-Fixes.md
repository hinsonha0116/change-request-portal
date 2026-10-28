# App updates: compact detail form, planned dates on New Request, and short requester names

These changes build on the app from [Change-Request-PowerApp-Guide.md](Change-Request-PowerApp-Guide.md), with all earlier updates already applied, including the New Request screen.

**What changes:**
1. **The detail form is more compact.** It's three columns instead of two, Attachments moves to the bottom and is shorter, and the text is smaller with tighter spacing, so there's less white space and less scrolling.
2. **Planned start and planned end** can be entered on the New Request screen. They're **optional**.
3. **The requester shows as just a name**, e.g. *Keegan Bowman*, instead of the full Microsoft 365 display name with rank and organisation, which was getting cut off on the board.

> **How to set a property:** select the control in the **Tree view**, choose the property in the dropdown at the left of the formula bar, and paste the value into the formula bar. You can also type X, Y, Width and Height into the **Properties** pane on the right.

> **Control names:** each field (card) has a **label** named `DataCardKey` plus a number, and a **value** control named `DataCardValue` plus a number. Date fields use `DateValueN`, `HourValueN` and `MinuteValueN` instead. The numbers are different in every app. Expand a card in the Tree view to see its real names.

**Time:** about 45 minutes.

---

## Part 1 — Compact detail form (`frmDetail`)

### 1a. Three columns
Select `frmDetail`. In the **Properties** pane, set **Columns** to `3`.

Most values are short (*Network*, *Standard*, *3 - Moderate*), so three per row fits comfortably in the form's 880-pixel width.

### 1b. Attachments: last, shorter, full width
**Why:** the Attachments box is tall, and a row is as tall as its tallest field. So the field beside it (A6 Program, in your layout) gets a large empty gap.

1. Select `frmDetail`, click **Edit fields**, and drag **Attachments** to the **bottom** of the list.
2. Expand `Attachments_DataCard…` and select the attachment control inside it (`DataCardValueN`). Set **Height** to `110`, which is enough for two or three files before it scrolls.
3. Select the **card** `Attachments_DataCard…` and set **Width** to:
   ```powerfx
   frmDetail.Width - 40
   ```
   It now spans the full width of the form at the bottom.

### 1c. Smaller text and tighter spacing
You can change many controls at once. Hold **Ctrl** and click them in the Tree view, then set the property once.

1. **Labels:** Ctrl+click every **`DataCardKey…`** inside `frmDetail` and set:

   | Property | Value |
   |---|---|
   | Size | `11` |
   | Height | `24` |

2. **Values:** Ctrl+click every **`DataCardValue…`** that's a text box or drop-down. Include your custom drop-downs (`drpRisk`, `drpA6ProgramDetail` and so on). **Skip** the attachment control and the date-picker parts. Set:

   | Property | Value |
   |---|---|
   | Size | `11` |
   | Height | `32` |

3. **Dates:** Ctrl+click the date pickers (`DateValue…`) and the hour and minute drop-downs (`HourValue…`, `MinuteValue…`) in the PlannedStart, PlannedEnd, ActualStart and ActualEnd cards. Set:

   | Property | Value |
   |---|---|
   | Size | `11` |
   | Height | `32` |

Each card works out its own height from what's inside it, so the gaps close up on their own.

> **If a card's controls overlap or leave a gap:** select the value control and set its **Y** to `DataCardKeyN.Y + DataCardKeyN.Height + 2`, using that card's own label name.

### 1d. Friendlier labels (optional)
The labels show the SharePoint column names. To change one, select its **`DataCardKey…`** and set **Text**:

| Card | Text |
|---|---|
| A6Program | `"A6 program"` |
| RequestedBy | `"Requested by"` |
| RequesterEmail | `"Requester email"` |
| ChangeType | `"Change type"` |
| PlannedStart | `"Planned start"` |
| PlannedEnd | `"Planned end"` |
| CABDecision | `"CAB decision"` |
| AuthorityDecision | `"Authority decision"` |
| ActualStart | `"Actual start"` |
| ActualEnd | `"Actual end"` |
| ReviewOutcome | `"Review outcome"` |

If the **Text** property is locked, unlock the card first: **Properties › Advanced › 🔒 Unlock to change properties**.

### 1e. Same on the New Request screen (optional)
Steps **1a**, **1c** and **1d** work the same way in `frmNew`, if you want that screen more compact too. In 1c, include `cmbRequestedBy` and `drpA6Program` with the values.

> **Blank A6 Program on older requests:** if a request shows an empty **A6 Program** on the detail screen, its saved value probably isn't one of the 16 programs. For example, it was typed before the drop-down existed. The saved value is kept when the request is saved. To fix it, correct the value in SharePoint (**Change Requests**), or pick a program from the drop-down while the request is in *Requested*.

---

## Part 2 — Planned start and end on New Request (optional fields)

### 2a. Add the fields
1. Select `frmNew` and click **Edit fields › + Add field**. Tick **PlannedStart** and **PlannedEnd**, then click **Add**.
2. Drag them to just after **Description**, before **Attachments**.
3. Unlock both cards: select each card, then **Properties › Advanced › 🔒 Unlock to change properties**.
4. Make sure **Required** is `false` on both cards. That makes them optional.

### 2b. Keep empty dates empty
Without this change, an empty date saves as midnight.

For **each** of the two cards, set the card's **Update** to this, using that card's own control names:
```powerfx
If(IsBlank(DateValueN.SelectedDate), Blank(),
   DateValueN.SelectedDate + Time(Value(HourValueN.Selected.Value), Value(MinuteValueN.Selected.Value), 0))
```

This is the same fix already on the detail screen's date cards.

### 2c. Stop an end date before the start date (optional)
Select `btnSubmit` and open **OnSelect**. Add these lines just **before** the line `!frmNew.Valid,`:
```powerfx
!IsBlank(DateValueS.SelectedDate) && !IsBlank(DateValueE.SelectedDate) &&
DateValueE.SelectedDate < DateValueS.SelectedDate,
    Notify("Planned end can't be before planned start.", NotificationType.Error),
```
Replace the placeholder names:
- **`DateValueS`:** the date picker in the **PlannedStart** card.
- **`DateValueE`:** the date picker in the **PlannedEnd** card.

### 2d. Smaller text (optional)
To match the rest of the compact form, set **Size** `11` and **Height** `32` on the two date pickers and their hour and minute drop-downs.

---

## Part 3 — Show just the requester's name

**Why:** Microsoft 365 display names here look like **`BOWMAN, KEEGAN L CTR USAF USAFE A6/A654`**. Since Requested By became a people picker, that whole string is saved, and it gets cut off on the board cards.

There are two parts to the fix:
- **3a** shows a short name for requests already saved.
- **3b** saves only the name on new requests.

### 3a. Short name on the board cards
On **BoardScreen**, select **`lblOwner`** (inside `galCards`) and replace its **Text** with:
```powerfx
With({n: ThisItem.RequestedBy},
    If(Find(",", n) > 0,
        Proper(
            First(Split(Trim(Mid(n, Find(",", n) + 1)), " ")).Value & " " &
            Trim(Left(n, Find(",", n) - 1))
        ),
        n
    )
) & " · " & ThisItem.A6Program & " · " & Text(ThisItem.Created, "dd mmm yyyy")
```

How it works:
- **`BOWMAN, KEEGAN L CTR …`** becomes **`Keegan Bowman`**. The first word after the comma is the first name, the part before the comma is the last name, and `Proper` gives them normal capitalisation.
- **A name with no comma** (e.g. *Keegan Bowman*, from requests submitted through the old form) is shown as it is.

### 3b. Save only the name on new requests
On **NewScreen**, select the **card** `RequestedBy_DataCard…` and replace its **Update** with:
```powerfx
Coalesce(
    Trim(cmbRequestedBy.Selected.GivenName & " " & cmbRequestedBy.Selected.Surname),
    cmbRequestedBy.Selected.DisplayName
)
```

This saves the person's first and last name from the directory, for example *Keegan Bowman*. If someone has no first or last name in the directory, it falls back to the full display name.

Requests submitted before this change keep the long name in SharePoint. 3a only changes how they're shown.

### 3c. Short names in History (optional)
On the **DetailScreen**, select **`lblHistWho`** (inside `galHistory`) and replace its **Text** with:
```powerfx
With({n: ThisItem.Author.DisplayName},
    If(Find(",", n) > 0,
        Proper(
            First(Split(Trim(Mid(n, Find(",", n) + 1)), " ")).Value & " " &
            Trim(Left(n, Find(",", n) - 1))
        ),
        n
    )
) & " · " & Text(ThisItem.Created, "dd mmm yyyy hh:mm")
```

> **Capitalisation:** `Proper` makes the first letter of each name upper case and the rest lower case, so *McDONALD* shows as *Mcdonald* and *O'NEIL* as *O'neil*. To keep the directory's capitals instead (*KEEGAN BOWMAN*), remove `Proper(` and its matching `)` in 3a and 3c.

---

## Test

Press **F5** on **BoardScreen** and check each row:

| # | Do this | Expect |
|---|---|---|
| 1 | Open any request | The form shows **three** fields per row with smaller text and less white space; **Attachments** is at the bottom, full width and short |
| 2 | Scroll the form on a request in *Requested* | Every field is still readable, and no labels or values overlap |
| 3 | Open a request with two or more attachments | The attachment box scrolls; clicking a file opens it |
| 4 | Click **+ Request a New Change** | **Planned start** and **Planned end** appear after Description, without red stars |
| 5 | Submit a request with **no** planned dates | It saves; in SharePoint, PlannedStart and PlannedEnd are **blank** (not midnight) |
| 6 | Submit a request **with** both dates and times | It saves; the detail screen shows the same dates and times |
| 7 | Set Planned end **before** Planned start and click Submit *(if you did 2c)* | Error: *Planned end can't be before planned start*; nothing is saved |
| 8 | On a request in *Requested*, change a planned date and click **Save changes** | Saved; reopen it and the new date is there |
| 9 | Look at the board cards | Each shows *First Last · A6 program · date*, with no rank or organisation |
| 10 | Submit a request for a colleague | The new card, the detail screen's **Requested by**, and the item in SharePoint all show just *First Last* |
| 11 | Open a request's History *(if you did 3c)* | Entries show short names, e.g. *Keegan Bowman · 23 Oct 2026 14:04* |

**If something goes wrong:**
- **A field's text is cut off:** increase that control's **Height** a little (e.g. `36`), or check that its **Y** follows the label (see 1c).
- **The Attachments card is still narrow:** check its **Width** is `frmDetail.Width - 40`, and that **Attachments** is last in **Edit fields**.
- **An empty planned date saves as midnight:** the card's **Update** doesn't have the `If(IsBlank(...), Blank(), ...)` wrapper from 2b.
- **The board still shows the long name:** check that `lblOwner` **Text** starts with `With({n: ThisItem.RequestedBy}`. A name with no comma is shown unchanged on purpose.
- **Anything else:** open the **App checker** (the stethoscope icon in the top toolbar) to see every formula error, and send me the exact text of any red error banner.
