# Migrating the Change Request Portal from a test site to production

*Updated 5 Nov 2026 to match the app as built.*

The app now includes:
- the in-app **New Request** screen with the people picker,
- the **Technical Review Board** and **PIR** stages, and a route for each change type,
- the **Completed** button,
- notes tabs, board filters and the compact forms,
- the **Schedule** (Forward Schedule of Change) calendar.

This guide moves the working portal from your **test** SharePoint site to the **production** (active) site:
- the two SharePoint lists,
- the Rollback Plan template,
- the Power Apps app.

The test site and test app are left untouched, so you can keep using them to try out future changes.

**What's no longer part of the migration:**
- **The Microsoft Form and its flow.** Requests are now submitted inside the app.
- **The email flows** (updates document Parts 4, 5 and 7). These get built **directly in production after go-live**, together with the App Roles list. See Step 8.

**How it works.** Power Apps can't simply "move" to another site. Instead you:
1. build the lists on the production site,
2. make a **copy** of the app,
3. point the copy at the production lists.

Each step ends with a check, so problems show up before users do.

**Time:** about 2 hours, plus testing.

> **How to set a property:** select the control in the **Tree view**, choose the property in the dropdown at the left of the formula bar, and paste the value into the formula bar.

---

## Before you start

### Decide these up front

| Decision | Recommendation |
|---|---|
| **Move the test data?** | **No.** Start production empty. Test requests and history are throwaway, and moving them changes every item ID, which breaks the History links (see the appendix if you must). |
| **Same Power Platform environment?** | Usually yes: the test and production apps both live in your normal environment, as two separate apps. If your organization uses a separate *production environment*, see Step 4, option B. |
| **Emails at go-live?** | There won't be any until Step 8 is done. Either tell the CM team to watch the board for new requests during that window, or hold the go-live announcement until the email flows work. |
| **When to switch over?** | Pick a quiet time, and tell users the new link only after Step 6 passes. |

### Write down the production values
Fill this in first. You'll need every row during the migration.

| Item | Test value (now) | Production value |
|---|---|---|
| SharePoint site URL | | |
| Rollback template link (`RollbackTemplateUrl`) | | |
| CM team emails (`CMTeam`) | | |
| TRB member emails (`TRBMembers`) | | |
| CAB member emails (`CABMembers`) | | |
| Change Authority emails (`ChangeAuthorities`) | | |
| App name | !!TEST!! Change Request Dashboard | Change Request Portal *(or your choice)* |

### Freeze changes
Don't edit the test app while you migrate. If you need a fix, make it after go-live and apply it to both copies.

---

## Step 1 — Prepare the production SharePoint site

### 1a. Check your access
You need **Owner** (Full Control) on the production site to create lists and set permissions. If you only have Edit, ask the site owner to do Step 1 or give you Owner.

### 1b. Create the two lists
Use **one** of these options. Either way, the list names must be **exactly** `Change Requests` and `Change Request History`. The app finds its lists by name.

**Option 1: copy them from the test site (recommended).** This copies every column, choice, default and view exactly as your test lists have them now, but no items.
1. On the **production** site, choose **+ New › List**.
2. Choose **From existing list**.
3. Pick the **test site**, then **Change Requests**, and click **Next**.
4. Name it `Change Requests` and click **Create**.
5. Repeat for **Change Request History**.

**Option 2: run the provisioning script.** [Provision-ChangeRequestLists.ps1](Provision-ChangeRequestLists.ps1) is up to date with every column, including the TRB, PIR, Outage and `ImplementationComplete` changes. It also uploads the Rollback Plan template:
```powershell
./Provision-ChangeRequestLists.ps1 -SiteUrl "https://<tenant>.sharepoint.com/sites/<production-site>" -ClientId "<your PnP Entra app id>"
```

### 1c. Check the columns
A wrong internal name, or a missing choice, is the most common migration problem.

**Change Requests: check these choice columns.** The text must match the app's lists exactly:

| Column | Choices |
|---|---|
| Stage | Requested · **Technical Review Board** · Change Advisory Board · Change Authority · Implementation · **PIR** · Close |
| ChangeType | Standard · Normal · Emergency *(no Informational)* |
| Category | Hardware · Software · Network |
| Priority | 4 - Low · 3 - Moderate · 2 - High · 1 - Critical |
| Risk, Impact | 3 - Moderate · 2 - High · 1 - Critical |
| TRBDecision | Pending · Approved · Needs changes · Rejected |
| CABDecision, AuthorityDecision | Pending · Approved · Rejected |
| ReviewOutcome | Successful · Successful with issues · Failed · Rolled back · Rejected |

**Check these columns exist, with these exact internal names.** Open **⚙ › List settings**, click a column, and the end of the browser address shows `Field=…`:

> A6Program · DSN · RequestedBy · RequesterEmail · SubmittedBy · Description · ImpactDetails · Justification · Location · AffectedSystems · OutageExpected · OutageDuration · PlannedStart · PlannedEnd · Assignee · TRBRollbackReviewed · TRBTested · TRBSecurityReviewed · TRBNotes · CABNotes · AuthorityNotes · ImplementationNotes · ImplementationComplete · ActualStart · ActualEnd · ReviewNotes · ClosedDate

**Change Request History:** check that `RequestID`, `FromStage`, `ToStage` and `Comment` exist, and that **Title** shows as *CR Number*.

### 1d. Index the columns the app filters on
Copying a list doesn't always copy its indexes. In each list, go to **⚙ › List settings › Indexed columns › Create a new index**:

| List | Index these |
|---|---|
| Change Requests | **Stage** · **PlannedStart** *(used by the calendar)* |
| Change Request History | **RequestID** |

### 1e. Upload the Rollback Plan template
If you used the script, it's already uploaded. Skip to the last step.
1. In the production site's **Documents**, create a folder **Change Templates**.
2. Upload [Rollback-Plan-Template.pdf](Rollback-Plan-Template.pdf).
3. On the file, click **⋯ › Copy link**, set it to *People in your organization*, and copy the link. Write it in the table as the production `RollbackTemplateUrl`.

**Check:** both lists exist on the production site with the exact names, are empty, and pass 1c.

---

## Step 2 — *(no longer needed)* Microsoft Form

Requests are submitted inside the app now, so there's no form to copy. If your test form is still accepting responses, close it: in Forms, go to **⋯ › Settings** and turn off **Accept responses**.

## Step 3 — *(no longer needed)* form flow

The old **Change Request – Form to SharePoint** flow isn't used. Leave it **turned off**. The new email flows are built in production in Step 8.

---

## Step 4 — Production Power Apps app

### Option A: same environment (most common)

#### 4a. Make the production copy
1. Open the test app in Power Apps Studio.
2. Click the **down arrow next to the Save icon** (top right) and choose **Save as** (older versions: **File › Save as**).
3. Name it, e.g. **Change Request Portal**, and save.
4. Back on **make.powerapps.com › Apps**, make sure the original is clearly marked as test. Its name already starts with *!!TEST!!*.
5. Open the new production copy to edit it.

Check the app name at the top of Studio to make sure you're editing the **production** copy.

#### 4b. Switch the data sources to production
1. Click the **Data** icon (the cylinder) in the far-left bar.
2. Next to **Change Requests**, click **⋯ › Remove**. Do the same for **Change Request History**. Formulas show red errors for a moment. That's expected.
3. Click **Add data › SharePoint** and pick the **production** site. Type its URL if it isn't listed.
4. Tick **Change Requests** and **Change Request History**, then click **Connect**.
5. **Check Office 365 Users is still under Data.** It powers the **Requested by** people picker. If it's missing, use **Add data** to search for **Office 365 Users** and add it.

Because the lists have the same names and columns, every formula reconnects on its own and the red errors disappear.

#### 4c. Update App.Formulas
Select **App › Formulas** and change these to the **production** values from your table:

| Formula | Production value |
|---|---|
| `RollbackTemplateUrl` | the production template link (1e) |
| `CMTeam` | the production CM team, lower-case emails |
| `TRBMembers` | the production TRB members |
| `CABMembers` | the production CAB members |
| `ChangeAuthorities` | the production Change Authorities |

**Leave these as they are:** `Stages`, `NoteTabs`, the choice lists (`A6Programs`, `CategoryChoices`, `PriorityChoices`, `LevelChoices`, `TRBDecisionChoices`, `DecisionChoices`, `ReviewOutcomeChoices` and so on), the filters, and the `Form…` sizes. They already match the production lists. `FormUrl` is no longer used, so you can leave it or delete it.

#### 4d. Clean up and check
1. Delete any temporary labels you added while testing, such as `User().Email`, `frmDetail.Unsaved`, `CountRows(...)` or the CM/CAB/Auth checks.
2. Click the **App checker** (the stethoscope icon in the top toolbar). There should be **no errors**. Delegation warnings (yellow) are fine.
3. If errors remain, they almost always name a column or a stage. Compare it with Step 1c.

#### 4e. Publish
Press **Ctrl+S**, then click **Publish › Publish this version**.

### Option B: separate production environment
Use this only if your organization has a separate Power Platform environment for production. The environment picker at the top right of Power Apps shows more than one.

1. Do Step 1 first.
2. In the **test** environment, go to **Apps**, select the app, then **⋯ › Export package**. Set **Import setup** to *Create as new*, and export the `.zip`.
3. Switch to the **production** environment, go to **Apps › Import canvas app**, and upload the `.zip`.
4. When asked, choose or create the **SharePoint** and **Office 365 Users** connections.
5. Open the imported app and follow **4b to 4e** above.

> If your organization manages apps with **Solutions** and environment variables, ask your Power Platform admin. That's a cleaner long-term setup, but it needs admin involvement.

---

## Step 5 — Share and set permissions

### 5a. SharePoint permissions on the production site
1. On the production site, go to **⚙ › Site permissions** (or **Share site**).
2. Add everyone who'll use the portal with **Edit**. That includes requesters, the CM team, TRB, CAB and Change Authorities, and implementers. A security group is easiest.
3. The app reads and writes both lists using each user's own permissions. Without Edit, they'll see errors when submitting or moving requests.

### 5b. Share the app
1. Go to **make.powerapps.com › Apps**.
2. Click **⋯** next to the **production** app, then **Share**.
3. Add the same users or group and click **Share**.
4. Add a **co-owner**, for example a second admin, so the app isn't tied to one person.
5. Users are asked to **Allow** the SharePoint and Office 365 Users connections the first time they open it. That's expected.

Don't send the link yet.

---

## Step 6 — Test in production

Work through this list in the **published** production app. Use your own account (CM), a **TRB member**, a **CAB member**, and one **regular user**. Prefix test titles with **TEST –** so they're easy to delete.

| # | Do this | Expect |
|---|---|---|
| 1 | Open the production app link | The board loads with seven empty columns (*Requested · TRB · CAB · Authority · Implementation · PIR · Close*) |
| 2 | Click **+ Request a New Change** | NewScreen opens; **Requested by** shows you; Change type lists only Standard, Normal and Emergency |
| 3 | Pick a colleague in **Requested by**, by name or email | Their email fills in |
| 4 | Click **Download Rollback Plan template** | The **production** PDF opens |
| 5 | Submit a **Normal** request with planned dates, an outage and the Rollback PDF | "CR-000NN submitted"; the card appears in **1. Requested** |
| 6 | Open it | The tracker shows all seven steps; Description, History and the attachment work |
| 7 | As CM, **Move** it to TRB | It moves; History records the move |
| 8 | As a TRB member, click **Needs changes** with a comment | It returns to Requested; TRB notes show *NEEDS CHANGES* |
| 9 | Move it to TRB again; the TRB member sets **Approved**; CM moves it on | Moves to **CAB** |
| 10 | CAB, then Authority, approve; CM moves it to **Implementation** | Moves each time |
| 11 | Click **✔ Completed** with implementation notes | The card shows **✔ Complete**; History shows *✔ Implementation complete* |
| 12 | CM moves it to **PIR**, picks a PIR outcome, then moves to **Close** | It closes; PIR outcome shows as read-only text |
| 13 | Submit a **Standard** request and follow it | Requested → Implementation → Close; no TRB, CAB or PIR fields |
| 14 | Submit an **Emergency** request | Requested → CAB (skips TRB) |
| 15 | On the board, try the **Category** and **Change type** filters | Only matching cards show, and the counts update |
| 16 | Click **Schedule** | The calendar shows the test requests on their planned dates; the day panel and links back work |
| 17 | Open the app as a **regular user** | They see only their own requests, with no toggle, Move or Send back |
| 18 | Check the **test** app | Unchanged, and still pointing at the test site |

### 6a. Clean up the test tickets
1. Delete the **TEST –** items from **Change Requests**, and their rows from **Change Request History**, on the **production** site.
2. Empty the site **Recycle bin** if you want them gone completely.

**About CR numbers:** SharePoint never reuses item IDs, so after deleting test items the first real request won't be `CR-00001`. If you want real numbering to start at 1, you have two choices:
- do the tests above, then delete **both lists** and recreate them (Step 1b, *From existing list*), then repeat 4b to reconnect;
- or simply accept the gap.

---

## Step 7 — Go live

1. **Announce it.** Send users the **production app link**: **Apps › ⋯ › Details › Web link**. Tell them to fully close any old copy of the app they have open, because the player caches versions, sometimes twice over.
2. **Pin it.** If you use Teams, add the production app as a tab, or pin it in **Apps** for the team.
3. **Label the test copy.** It already starts with *!!TEST!!*, so no one should use it by mistake.
4. **Remind the CM team** that **no emails are sent yet**, until Step 8. They should check the board for new requests.

### Making changes after go-live
- **Try changes in the TEST app first,** against the test site.
- **Then make the same change in the production app,** and publish it. Don't **Save as** from test again: that creates a new production app with a new link, and you'd have to repeat Steps 4 and 5.
- **Keep the updates document and [TODO.md](TODO.md) up to date** with each change.

---

## Step 8 — After go-live: roles and email notifications (in production)

Build these directly in production, in this order.

1. **App Roles list.** One SharePoint list holding the CM, TRB, CAB, Authority and SW/HW manager emails, so people are managed in one place. Then:
   - switch `IsCM`, `IsTRB`, `IsCAB` and `IsAuthority` in App.Formulas to read from the list.

   *Claude will write the App Roles guide when you're ready.*
2. **New-request emails:** updates document **Part 4**. CM on every request; SW or HW managers by category.
3. **Stage emails:** updates document **Part 7**. TRB, CAB and Authority at their stages, the requester when a request is sent back, needs changes or is closed, CM on *Completed* and PIR. Point both flows at the **production** site and lists.
4. **Email link:** updates document **Part 5**. Use the **production** app's web link.
5. **Test the emails** with a couple of **TEST –** requests, then delete them and their History rows.

Until App Roles exists, the flows can use the typed email variables shown in Parts 4 and 7. Switch them to App Roles afterwards.

---

## If something goes wrong (rollback)

The test setup is untouched, so you can fall back at any time:
1. Tell users to keep using the **test** app link.
2. Fix the problem in the production app or lists.
3. Re-run the Step 6 tests before announcing again.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Red errors after re-adding the data sources | A list name or column internal name differs from test | Check the list names exactly and the column `Field=` names (1c). Recreate any wrong column without spaces, then **Refresh** the data source |
| *"…isn't recognized"* for a new column (e.g. `TRBNotes`, `ImplementationComplete`) | The column is missing, or the data source was connected before it existed | Add the column (1c), then **Data › ⋯ › Refresh** |
| A request doesn't appear in any board column | Its **Stage** text doesn't match the `Stages` table | The production Stage choices must be exactly as in 1c, including `Technical Review Board` and `PIR` |
| **Move** says "Move to  →" with no stage name | Stage or ChangeType choice text doesn't match the app | Check the choices in 1c; the `Stages` **Types** use *Standard, Normal, Emergency* |
| **Requested by** picker shows nothing | Office 365 Users isn't connected in the production app | **Data › Add data › Office 365 Users** (4b step 5) |
| A drop-down shows *Item 1, 2, 3* | A card's combo box isn't reading the choices | Refresh the data source. See [Troubleshooting-Notes.md](Troubleshooting-Notes.md), Issues 1 and 4 |
| Calendar is empty | No requests have **PlannedStart**, or the calendar hasn't reloaded | Add planned dates to a test request; reopen the Schedule screen |
| The template button opens the test PDF | `RollbackTemplateUrl` not updated | Update it in App.Formulas (4c) and republish |
| Users don't see the latest version | The app player caches the old version | Have them fully close and reopen the app, sometimes twice, and restart Teams if they use it there |
| Users get access errors | They have the app but not the production site | Give them **Edit** on the production site (5a) |
| TRB, CAB, Authority or CM buttons are missing for the right people | Production emails aren't in App.Formulas, or don't match `User().Email` | Update the role lists (4c). Check with a temporary label showing `User().Email` |

---

## Appendix — If you must move test data

Moving existing requests is possible but fiddly, and usually not worth it:
- **IDs change.** Items get new IDs on the production list, so every `CR-000NN` number changes. **Change Request History** rows link to requests by `RequestID`, so they would point at the wrong requests unless you remap each one.
- **Attachments** don't come across with a simple copy. They must be re-attached per item.
- **Created By, Created, Modified** become the person and time of the copy, not the original.

If you still need it, the cleanest way is a one-off Power Automate flow:
1. For each test request, create the production item and capture its **new ID**.
2. Copy its attachments.
3. Create its History rows with `RequestID` set to the **new ID** and `Title` set to the new CR number.

Ask before attempting it, and test it on a copy first.
