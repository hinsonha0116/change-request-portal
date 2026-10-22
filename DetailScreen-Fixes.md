# App updates: role-based access

These changes build on the app from [Change-Request-PowerApp-Guide.md](Change-Request-PowerApp-Guide.md) and the DetailScreen updates you've already applied: the save-then-act buttons, the new layout, and the Add comment button.

What changes:
1. The **Move** and **Send back** buttons are shown only to members of the **Change Management (CM) team**.
2. On the board, regular users see **only their own requests**. CM, CAB and Change Authority members see all of them.

> **How to set a property:** select the control in the **Tree view**, choose the property in the dropdown at the left of the formula bar, and paste the value into the formula bar.

---

## 1 — Limit Move and Send back to the CM team

This works the same way as the existing CAB and Change Authority checks. You list the CM team once, in **App.Formulas**, then add that check to each button's **Visible** property.

### 1a. Define the CM team
Select **App** in the Tree view, choose **Formulas**, and add these lines to the **end** of the existing block:

```powerfx
// Change Management team: can move and send back requests. Use lower-case emails.
CMTeam = ["cm.lead@us.af.mil", "cm.analyst@us.af.mil"];

IsCM = Lower(User().Email) in CMTeam;
```

Replace the example addresses with your CM team's. Each address must match the email the person signs in with, exactly. If you're unsure what someone's is:
1. Add a temporary **Text label** with **Text** = `User().Email`.
2. Have them open the app and tell you what it shows.
3. Delete the label afterwards.

### 1b. Limit the buttons
Replace each button's **Visible** with:

| Button | Visible |
|---|---|
| `btnAdvance` | `varCR.Stage.Value <> "Close" && IsCM` |
| `btnSendBack` | `With({o: LookUp(Stages, Name = varCR.Stage.Value).Order}, o >= 2 && o <= 5) && IsCM` |

Anyone not on the CM team won't see these two buttons. Everything else stays the same:
- **Everyone** can still read requests, use **Add comment**, and save the fields they're allowed to edit.
- **Reject** stays limited to CAB members and Change Authorities.

> **Same pattern for other buttons:** to restrict any other button, add `&& IsCM` (or `&& IsCAB`, `&& IsAuthority`) to the end of its **Visible** formula. To grey a button out instead of hiding it, use **DisplayMode**: `If(IsCM, DisplayMode.Edit, DisplayMode.Disabled)`.

### 1c. Later: manage the team without editing the app
With the email list, you have to edit and republish the app every time the team changes. When that gets tedious, keep the team in a SharePoint list instead:

1. Create a list named **App Roles** with two columns:
   - `Email`: Single line of text. Store addresses in lower case.
   - `Role`: Choice, with the options CM, CAB and Authority.
2. Add one row per person per role.
3. In the app, add **App Roles** as a data source: **Data › Add data › SharePoint**, then pick your site.
4. In **App.Formulas**, replace the `CMTeam` and `IsCM` lines with:
   ```powerfx
   IsCM = !IsBlank(LookUp('App Roles', Email = Lower(User().Email) && Role.Value = "CM"));
   ```
   You can do the same for `IsCAB` and `IsAuthority` using `"CAB"` and `"Authority"`.

After that, changing the team is just adding or removing rows in SharePoint. Restrict who can edit the **App Roles** list to the people who should manage roles.

An **Entra security group**, checked through the Office 365 Groups connector, is another option if IT already maintains a CM group. Check that the connector is available in your government tenant first.

> **This hides buttons. It doesn't secure the data.** Anyone with Edit permission on the SharePoint site could still change a request's Stage directly in the list. To enforce the rule, lock the list down so only a Power Automate flow can change stages. See *Optional extras* in the main guide.

---

## 2 — Users see only their own requests

**Who sees what on the board:**

| User | Sees |
|---|---|
| CM team, CAB members, Change Authorities | **All** requests, with the toggle to switch to just their own |
| Everyone else | Only requests they **submitted**, or where **their email was typed in the E-mail box** |

A request counts as "theirs" if either:
- **`SubmittedBy`** matches them: the account they were signed in with when they submitted the form. Forms records this automatically, so it's always accurate.
- **`RequesterEmail`** matches them: the address typed into the form's E-mail question. This covers someone submitting on another person's behalf.

This section uses `IsCM` from section 1, so do section 1 first.

### 2a. Add a SubmittedBy column in SharePoint
1. Open the **Change Requests** list and click **+ Add column › Single line of text**.
2. Name it `SubmittedBy` exactly, with no space, and click **Save**.

### 2b. Fill SubmittedBy from the flow
1. Open the **Change Request – Form to SharePoint** flow in Power Automate and click **Edit**.
2. Open the **Create CR** step. If `SubmittedBy` doesn't appear yet, refresh the browser page so the flow picks up the new column.
3. Click in **SubmittedBy**, then in the dynamic content list, under *Get response details*, choose **Responders' Email**.
4. **Save** the flow.

Requests already in the list have SubmittedBy blank. Their submitters can still see them through the E-mail box match. To be safe, you can type the submitter's address into SubmittedBy for those items in SharePoint, or delete old test requests.

> **If Responders' Email is empty in the flow run:** the form must be set to **Only people in my organization** (Forms › ⋯ › Settings). That's what makes Forms record who submitted it.

### 2c. Define who can see everything
Select **App**, choose **Formulas**, and add this line to the **end**, after the `IsCM` line from section 1:

```powerfx
CanSeeAll = IsCM || IsCAB || IsAuthority;
```

### 2d. Change the board filter
Select **`galCards`** (inside `galStages` on BoardScreen) and replace its **Items** with:

```powerfx
Sort(
    Filter(
        'Change Requests',
        Stage.Value = ThisItem.Name,
        (CanSeeAll && !tglMine.Value) || SubmittedBy = User().Email || RequesterEmail = User().Email,
        IsBlank(txtSearch.Text) || StartsWith(Title, txtSearch.Text)
    ),
    Modified,
    SortOrder.Descending
)
```

How the middle line works:
- **CM, CAB or Authority with the toggle off:** every request shows.
- **Everyone else, or anyone with the toggle on:** only requests where SubmittedBy *or* RequesterEmail is their own address.

SharePoint ignores upper and lower case when comparing the emails.

The column counts in the headers (`lblHeader`) follow automatically, because they count what `galCards` shows.

### 2e. Show the toggle only to people who need it
Regular users only ever see their own requests, so the **My requests / All requests** toggle does nothing for them. Select **`tglMine`** and set **Visible** to:
```powerfx
CanSeeAll
```

> **This hides requests in the app. It doesn't secure them.** Anyone with permission on the SharePoint site can still open the **Change Requests** list directly and see every request. If requesters mustn't be able to see each other's changes even outside the app, you also need SharePoint item-level permissions:
> - give regular users no direct access to the list,
> - have the flow grant each submitter access to their own item (SharePoint's *Grant access to an item or a folder* action),
> - give CM, CAB and Authority members access to the whole list.

> **Other files to update later:** the provisioning script and the main guide's column table don't include `SubmittedBy` yet. Add it there if you rebuild the lists from scratch.

---

## Test

Press **F5** on **BoardScreen** and check each row:

| # | Do this | Expect |
|---|---|---|
| 1 | Open a request as a **CM team** member | **Move** and **Send back** are visible (Send back from the CAB stage onward) |
| 2 | Have someone **not** on the CM team open the same request | **Move** and **Send back** are hidden; they can still use **Add comment** and **Save changes** |
| 3 | Submit a new request through the form, then open the flow's latest run | **Create CR** shows SubmittedBy filled with your sign-in email |
| 4 | Open the board as a **regular user** who has submitted one request | Only that request shows; column counts match; the toggle is hidden |
| 5 | Submit a request with a colleague's address in the **E-mail** box, then have them open the board | The colleague sees it (they're named in RequesterEmail) |
| 6 | Open the board as a **CM, CAB or Authority** member | All requests show; the toggle is visible, and switching it on shows only your own |

**If something goes wrong:**
- **A red error banner** appears: send the exact text.
- **A control shows a red error:** check that its formula has no red underlines, and open the **App checker** (the stethoscope icon in the top toolbar) to see every error in the app.
- **A regular user sees no requests at all:** check that SubmittedBy is being filled (row 3), and that their sign-in email matches. A temporary label with **Text** = `User().Email` shows what the app sees.
