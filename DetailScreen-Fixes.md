# App updates: New Request screen with a people picker

These changes build on the app from [Change-Request-PowerApp-Guide.md](Change-Request-PowerApp-Guide.md), with all earlier updates already applied.

**What changes:** new change requests are submitted **inside the app** instead of through the Microsoft Form.
- **+ Request a New Change** opens a new **NewScreen** in the app.
- **Requested By** is a **people picker**. Start typing a name and choose anyone in your organization. It defaults to you.
- Picking a person **fills in their email automatically**, and their phone number too if your directory stores one.
- **A6 Program** is a drop-down of your 16 programs.
- **Category, Change Type, Priority, Risk and Impact** are drop-downs of the SharePoint choices, and all are required.
- The **Rollback Plan PDF** and any other files are attached on the same screen.
- **Submit** saves the request straight to SharePoint with Stage = *Requested*, and writes the first History row.
- **The Power Automate flow is no longer needed** for new requests. The OneDrive, form-owner and Parse JSON steps all go away.

Requests already submitted through the form keep working as before.

> **How to set a property:** select the control in the **Tree view**, choose the property in the dropdown at the left of the formula bar, and paste the value into the formula bar. You can also type X, Y, Width and Height into the **Properties** pane on the right.

**Time:** about 60–90 minutes.

---

## 1 — Add the Office 365 Users connector

This is what lets the app search your organization's directory.

1. Click the **Data** icon (the cylinder) in the far-left bar, then **Add data**.
2. Search for **Office 365 Users**, select it, and click **Connect**.
3. It appears under **Data** as **Office365Users**.

> If **Office 365 Users** isn't in the list, your tenant may block it. Check with your Power Platform admin before going further, because the people picker depends on it.

**Check:** add a temporary **Text label** with **Text** = `Office365Users.MyProfileV2().displayName`. It should show your name. Delete the label afterwards.

---

## 2 — Create NewScreen and its banner

1. Choose **New screen › Blank** and rename it `NewScreen`.
2. With **NewScreen** selected, insert these controls:

| # | Insert | Rename to | Properties |
|---|---|---|---|
| 1 | Rectangle | `rectNewHeader` | X `0` · Y `0` · Width `Parent.Width` · Height `60` · Fill: `ColorValue("#1E3A6B")` |
| 2 | Button | `btnNewBack` | Text: `"← Board"` · OnSelect: `Navigate(BoardScreen, ScreenTransition.UnCover)` · Fill: `Color.White` · Color: `ColorValue("#1E3A6B")` · X `16` · Y `12` · Width `110` · Height `36` |
| 3 | Text label | `lblNewTitle` | Text: `"New change request"` · Color: `Color.White` · Size `18` · FontWeight: `FontWeight.Bold` · X `140` · Y `10` · Width `500` · Height `40` |
| 4 | Button | `btnNewTemplate` | Text: `"Download Rollback Plan template"` · OnSelect: `Launch(RollbackTemplateUrl, {}, LaunchTarget.New)` · Fill: `ColorValue("#1E3A6B")` · Color: `Color.White` · BorderColor: `Color.White` · X `Parent.Width - 420` · Y `12` · Width `250` · Height `36` |
| 5 | Button | `btnSubmit` | Text: `"Submit request"` · Fill: `Color.White` · Color: `ColorValue("#1E3A6B")` · FontWeight: `FontWeight.Bold` · X `Parent.Width - 160` · Y `12` · Width `140` · Height `36` · OnSelect: see section 7 |

If a button disappears behind the banner, right-click it and choose **Reorder › Bring to front**.

---

## 3 — Add the form `frmNew`

1. With **NewScreen** selected, choose **+ Insert › Edit form** and rename it `frmNew`.
2. Set these properties:

| Property | Value |
|---|---|
| DataSource | `'Change Requests'` |
| DefaultMode | `FormMode.New` |
| X / Y | `20` / `76` |
| Width / Height | `Parent.Width - 40` / `Parent.Height - 96` |
| Columns *(Properties pane)* | `2` |

### 3a. Choose the fields
1. With `frmNew` selected, go to the **Properties** pane and click **Edit fields**.
2. Remove everything not in the list below (hover a field, then **⋯ › Remove**). Add any that are missing (**+ Add field**).
3. Drag the fields into this order:

> A6Program · RequestedBy · DSN · RequesterEmail · Title · Category · ChangeType · Priority · Risk · Impact · Description · **Attachments** · Stage · SubmittedBy · CABDecision · AuthorityDecision

The last four are filled in automatically and hidden in 3c.

### 3b. Unlock every card
For each card in `frmNew`:
1. Select it in the Tree view (e.g. `Category_DataCard2`).
2. Open **Properties › Advanced** and click **🔒 Unlock to change properties**.

> **Control names:** Power Apps names each card's input control `DataCardValue` plus a number (e.g. `DataCardValue27`). The number is different in every app. In this document, `DataCardValueN` means *the input control inside that card*. Expand the card in the Tree view to see its real name.

### 3c. Hide and auto-fill the four system fields
For each card below, set **Visible** to `false` and **Update** as shown:

| Card | Update |
|---|---|
| `Stage_DataCard…` | `{Value: "Requested"}` |
| `SubmittedBy_DataCard…` | `Lower(User().Email)` |
| `CABDecision_DataCard…` | `{Value: "Pending"}` |
| `AuthorityDecision_DataCard…` | `{Value: "Pending"}` |

### 3d. Make the text fields required
Set **Required** to `true` on the **A6Program**, **DSN**, **Title** and **Description** cards. A red star appears on each, and the form won't submit while any of them is empty.

### 3e. Make Description taller
Select the input control inside the **Description** card (`DataCardValueN`) and set:
- **Mode** = `TextMode.MultiLine`
- **Height** = `150`

---

## 4 — Requested By: the people picker

The **RequestedBy** column stays a plain text column. The picker sits inside the card and fills the column with the chosen person's name.

### 4a. Add the picker to the card
1. Expand **`RequestedBy_DataCard…`** in the Tree view and select its text input (`DataCardValueN`). Set its **Visible** to `false`.
2. Select the **card** itself (`RequestedBy_DataCard…`). Choose **+ Insert › Combo box**. It should appear **inside the card** in the Tree view.
3. Rename it `cmbRequestedBy` and set:

| Property | Value |
|---|---|
| Items | `Office365Users.SearchUserV2({searchTerm: Self.SearchText, top: 15, isSearchTermRequired: true}).value` |
| DefaultSelectedItems | `Office365Users.SearchUserV2({searchTerm: User().Email, top: 1}).value` |
| SelectMultiple | `false` |
| IsSearchable | `true` |
| SearchFields | `["DisplayName", "Mail"]` *(search by name or email)* |
| DisplayFields | `["DisplayName", "Mail"]` |
| X / Y | `DataCardValueN.X` / `DataCardValueN.Y` *(the hidden text input from step 1)* |
| Width | `DataCardValueN.Width` |
| Height | `40` |

4. **Optional:** `DisplayFields` usually makes each result show the name with the email underneath. If only names show, open **Fields › Edit** in the **Properties** pane. If it has a **Layout** drop-down, choose **Double**, with **Primary text** = DisplayName and **Secondary text** = Mail. Some versions don't have this option for a search-based picker. That's fine: the picker and the email auto-fill work either way.

How it works:
- **As you type,** the box searches your directory by **name or email** and shows up to 15 matches.
- **By default,** it's set to the person filling in the form, so a request for yourself needs no clicks.

### 4b. Save the chosen name
Select the **card** `RequestedBy_DataCard…` and set **Update** to:
```powerfx
cmbRequestedBy.Selected.DisplayName
```

### 4c. Auto-fill the email
Select the **card** `RequesterEmail_DataCard…` and set:

| Property | Value |
|---|---|
| Default | `cmbRequestedBy.Selected.Mail` |
| DisplayMode | `DisplayMode.View` |

The email box now updates by itself whenever someone is picked, and users can't overtype it. The card's **Update** stays as it is, so it saves what's shown.

### 4d. Auto-fill the DSN (optional)
This works only if your directory stores DSN in the user's phone field. Select the **card** `DSN_DataCard…` and set **Default** to the phone field of the picked person. Start typing:
```powerfx
cmbRequestedBy.Selected.
```
Then pick the phone field from the list Power Apps suggests. It's usually `TelephoneNumber` or `BusinessPhones`. If it's `BusinessPhones`, use `First(cmbRequestedBy.Selected.BusinessPhones).Value`.

Leave the DSN card **editable**, so people can correct it. If your directory doesn't hold DSNs, skip this step: users type it in, as on the form.

---

## 5 — Category, Change Type, Priority, Risk and Impact (drop-downs)

These five fields stay as the **drop-downs** Power Apps created in each card. Their options come straight from the SharePoint choices, so they always match the list (`4 - Low`, `3 - Moderate` and so on). There's nothing to insert. You only make them required.

For each of the **Category**, **ChangeType**, **Priority**, **Risk** and **Impact** cards in `frmNew`, select the **card** and set **Required** to `true`.

A red star appears on each card, and **Submit** won't save until all five are chosen. They start empty on a new request, because these SharePoint columns have no default, so the requester has to pick each one.

> Don't hide or replace the drop-down inside these cards, and leave each card's **Update** as Power Apps created it.

---

## 5b — A6 Program drop-down

A6 Program becomes a drop-down of your programs instead of a free-text box. The SharePoint column stays **Single line of text**, so nothing else in the app, the board or SharePoint has to change.

### 5b-1. List the programs (App.Formulas)
Select **App**, choose **Formulas**, and add this to the **end**:

```powerfx
A6Programs = [
    "ACBN",
    "Blacknet",
    "C2C",
    "Collaboration Services",
    "CSFC",
    "Exec Comm",
    "EVRS",
    "HERTR/GWRTR",
    "NNCS",
    "Secureview",
    "SNCS",
    "Unified Communications",
    "UPNCS",
    "VDI",
    "VOC",
    "X-COMM"
];
```

To add, rename or remove a program later, edit this list and republish the app.

### 5b-2. Replace the text box on NewScreen
1. In `frmNew`, expand **`A6Program_DataCard…`** and select its text box (`DataCardValueN`). Set **Visible** to `false`.
2. Select the **card**, then choose **+ Insert › Drop down**. Check that it appears **inside the card** in the Tree view.
3. Rename it `drpA6Program` and set:

| Property | Value |
|---|---|
| Items | `A6Programs` |
| AllowEmptySelection | `true` |
| Default | `""` |
| X / Y | `DataCardValueN.X` / `DataCardValueN.Y` *(the hidden text box)* |
| Width / Height | `DataCardValueN.Width` / `40` |

4. Select the **card** and set **Update** to:
   ```powerfx
   drpA6Program.Selected.Value
   ```

The drop-down starts empty, so the requester has to choose. Sections 7a and 8 check it and reset it.

### 5b-3. Same drop-down on the DetailScreen (optional)
A6 Program can still be edited on the DetailScreen while a request is in *Requested*. To use the drop-down there as well:

1. In `frmDetail`, expand **`A6Program_DataCard…`**, select its text box (`DataCardValueN`), and set **Visible** to `false`.
2. Select the **card**, then choose **+ Insert › Drop down**. Rename it `drpA6ProgramDetail` and set:

| Property | Value |
|---|---|
| Items | `A6Programs` |
| AllowEmptySelection | `true` |
| Default | `ThisItem.A6Program` |
| DisplayMode | `If(varCR.Stage.Value = "Requested", DisplayMode.Edit, DisplayMode.View)` |
| X / Y | `DataCardValueN.X` / `DataCardValueN.Y` |
| Width / Height | `DataCardValueN.Width` / `40` |

3. Select the **card** and set **Update** to:
   ```powerfx
   Coalesce(drpA6ProgramDetail.Selected.Value, ThisItem.A6Program)
   ```

> **Older requests:** requests submitted before this change keep whatever was typed. If an old value isn't one of the 16 programs, the DetailScreen drop-down shows blank. The `Coalesce` in the Update formula then keeps the old value when the request is saved, so nothing is lost unless someone picks a program.

---

## 6 — Attachments

The **Attachments** card is already in the form. Use it for the **Rollback Plan PDF** and any other files.

1. Select the **Attachments** card and set **DisplayName** to `"Rollback Plan (required) and other attachments"`. If DisplayName is locked, set the card label's **Text** instead.
2. Select the attachment control inside the card (`DataCardValueN`) and check **MaxAttachments**. Set it to `10` to match the old form.

Files are uploaded when **Submit** is clicked. **Download Rollback Plan template** in the banner opens the blank PDF.

> The app keeps each file's own name. Attachments added here won't be renamed `RollbackPlan_CR-…` the way the flow did. Ask requesters to keep "Rollback" in the PDF's file name.

---

## 7 — Submit

### 7a. `btnSubmit` › OnSelect
This checks everything, then saves. Replace `DataCardValueN` with the name of the **attachment control** in the Attachments card.

```powerfx
If(
    IsBlank(drpA6Program.Selected.Value),
        Notify("Choose an A6 Program.", NotificationType.Error),
    IsBlank(cmbRequestedBy.Selected),
        Notify("Choose who is requesting this change.", NotificationType.Error),
    IsEmpty(DataCardValueN.Attachments),
        Notify("Attach the completed Rollback Plan PDF.", NotificationType.Error),
    !frmNew.Valid,
        Notify("Fill in every field marked with a red star.", NotificationType.Error),
    SubmitForm(frmNew)
)
```

The last check (`frmNew.Valid`) covers every card set to **Required**: A6 Program, DSN, Title and Description (3d), plus the five choice drop-downs (section 5).

### 7b. `frmNew` › OnSuccess
This writes the first History row, the same way the flow did, then returns to the board:
```powerfx
Patch('Change Request History', Defaults('Change Request History'), {
    Title:     "CR-" & Text(Self.LastSubmit.ID, "00000"),
    RequestID: Self.LastSubmit.ID,
    FromStage: "",
    ToStage:   "Requested",
    Comment:   "Submitted in the app by " & User().FullName &
               If(Lower(cmbRequestedBy.Selected.Mail) <> Lower(User().Email),
                  " on behalf of " & cmbRequestedBy.Selected.DisplayName, "")
});
Notify("Change request CR-" & Text(Self.LastSubmit.ID, "00000") & " submitted", NotificationType.Success);
Navigate(BoardScreen, ScreenTransition.UnCover)
```

### 7c. `frmNew` › OnFailure
```powerfx
Notify("Couldn't submit: " & Self.Error, NotificationType.Error)
```

---

## 8 — Point the board button at the new screen

### 8a. `btnNew` › OnSelect (BoardScreen)
Replace **OnSelect** with:
```powerfx
NewForm(frmNew);
Set(varResetNew, true);
Set(varResetNew, false);
Navigate(NewScreen, ScreenTransition.Cover)
```

### 8b. Let the button reset the picker and A6 Program
`Reset(...)` can't be used here: controls inside a form can only be reset from within that form. Instead, each control has its own **Reset** property, which the button triggers through `varResetNew`.

On **NewScreen**, select each control, find **Reset** (type "reset" in the property dropdown), and set it:

| Control | Reset |
|---|---|
| `cmbRequestedBy` | `varResetNew` |
| `drpA6Program` | `varResetNew` |

The form is cleared every time:
- the picker goes back to you,
- A6 Program is empty,
- the five choice drop-downs are empty, because `NewForm` clears everything else in the form by itself.

---

## 9 — Who can see the new request

Nothing to change. The app writes **SubmittedBy** (the person who clicked Submit) and **RequesterEmail** (the person picked in Requested By). The board's "see only your own requests" filter matches either one, so:
- **the submitter** sees the request,
- **the person it was submitted for** sees it too,
- **CM, CAB and Authority** see everything, as before.

---

## 10 — Retire the form and flow

When the tests below pass and the app is published:

1. **Turn off the flow.** In Power Automate, open **Change Request – Form to SharePoint**, click **Turn off**, and leave it there in case you need it again.
2. **Close the form.** In Microsoft Forms, open the *Change Request* form, go to **⋯ › Settings**, and turn off **Accept responses**. Add a message such as *"Submit change requests in the Change Request Portal app."*
3. **Leave `FormUrl` in App.Formulas.** Nothing uses it any more, and it does no harm.

Requests that were submitted through the form stay on the board and work exactly as before.

> **Migration guide:** if you migrate to production after this change, skip Steps 2 and 3 (form and flow) of [Migration-Guide.md](Migration-Guide.md). Also add **Office 365 Users** back as a data source in Step 4b if it's missing.

---

## Test

Press **F5** on **BoardScreen** and check each row:

| # | Do this | Expect |
|---|---|---|
| 1 | Click **+ Request a New Change** | NewScreen opens; **Requested By** shows **you**; your email is filled in and greyed out; A6 Program and the five choice drop-downs are empty |
| 2 | Click in **Requested By** and type part of a colleague's name or email | Matching people appear, with names and emails |
| 3 | Pick the colleague | Their email replaces yours; DSN fills in too, if you did 4d |
| 4 | Open the **A6 Program** drop-down | All 16 programs are listed, ACBN to X-COMM |
| 5 | Open the **Priority** drop-down | The four SharePoint choices are listed, `4 - Low` to `1 - Critical` |
| 6 | Click **Submit request** with nothing else filled | Error: *Choose an A6 Program* |
| 7 | Choose an A6 Program and click Submit with no attachment | Error: *Attach the completed Rollback Plan PDF* |
| 8 | Attach a PDF, leave **Priority** (or Title) empty, and click Submit | Error: *Fill in every field marked with a red star*; the empty field shows its star |
| 9 | Fill everything and click **Submit request** | "CR-000NN submitted"; back on the board, the new card is in **1. Requested** |
| 10 | Open the new request | All fields match what you entered, including the five choices; the PDF opens from Attachments; History shows **Created** with *"Submitted in the app by … on behalf of …"* |
| 11 | Check the item in SharePoint | Stage = Requested, CAB and Authority = Pending, SubmittedBy = your email, RequesterEmail = the colleague's |
| 12 | Have the colleague (a regular user) open the board | They see the request submitted for them |
| 13 | Pick a colleague and an A6 Program, click **← Board**, then **+ Request a New Change** again | The form is empty, Requested By is back to you, and A6 Program is empty; no error appears |
| 14 | Click **Download Rollback Plan template** | The blank PDF opens |
| 15 | Open a request in *Requested* on the DetailScreen *(if you did 5b-3)* | The drop-down shows its saved program and can be changed; at later stages it's read-only |

**If something goes wrong:**
- ***Office365Users isn't recognized*:** the connector wasn't added (section 1), or your tenant blocks it.
- **The people picker shows nothing as you type:** check that **IsSearchable** is `true` and that **Items** uses `Self.SearchText`.
- **The email doesn't fill in:** check the RequesterEmail card's **Default** is `cmbRequestedBy.Selected.Mail`, and that you set it on the **card**, not the text box inside it.
- **The picker or A6 Program drop-down appears in the wrong place or outside its card:** in the Tree view it must be indented under its card. Cut it (**Ctrl+X**), select the card, and paste (**Ctrl+V**).
- **A choice saves blank or shows an error:** make sure the drop-down inside that card is the one Power Apps created, and that the card's **Update** hasn't been changed. If in doubt, remove the field (**Edit fields › ⋯ › Remove**), add it again, and set **Required** to `true`.
- **Anything else:** open the **App checker** (the stethoscope icon in the top toolbar) to see every formula error, and send me the exact text of any red error banner.
