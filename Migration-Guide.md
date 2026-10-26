# Migrating the Change Request Portal from a test site to production

This guide moves the working portal from your **test** SharePoint site to the **production** (active) site:
- the SharePoint lists,
- the Microsoft Form,
- the Power Automate flow,
- the Power Apps app.

The test setup is left untouched, so you can keep using it to try out future changes.

**How it works.** Power Apps and Power Automate can't simply "move" to another site. Instead you:
1. build the lists on the production site,
2. make **copies** of the form, flow and app,
3. point each copy at the production site.

Each step ends with a check, so problems show up before users do.

**Time:** about 2 hours, plus testing.

> **How to set a property:** select the control in the **Tree view**, choose the property in the dropdown at the left of the formula bar, and paste the value into the formula bar.

---

## Before you start

### Decide these up front

| Decision | Recommendation |
|---|---|
| **Who owns the production form and flow?** | A **shared account** (e.g. a change-management or service account), not a person. The form owner's OneDrive stores every uploaded file, and the flow must run as that same account. If a person owns them and leaves, the portal breaks. |
| **Move the test data?** | **No.** Start production empty. Test requests and history are throwaway, and moving them changes every item ID, which breaks the History links (see the appendix if you must). |
| **Same Power Platform environment?** | Usually yes: the test and production apps both live in your normal environment, as two separate apps. If your organization uses a separate *production environment*, see Step 4, option B. |
| **When to switch over?** | Pick a quiet time, and tell users the new link only after Step 6 passes. |

### Write down the production values
Fill this in first. You'll need every row during the migration.

| Item | Test value (now) | Production value |
|---|---|---|
| SharePoint site URL | | |
| Form link (`FormUrl`) | | |
| Rollback template link (`RollbackTemplateUrl`) | | |
| Form and flow owner account | | |
| CM team emails (`CMTeam`) | | |
| CAB member emails (`CABMembers`) | | |
| Change Authority emails (`ChangeAuthorities`) | | |
| App name | Change Request Portal | Change Request Portal *(rename test to "… (TEST)")* |

### Freeze changes
Don't edit the test app, form or flow while you migrate. If you need a fix, make it after go-live and apply it to both copies.

---

## Step 1 — Prepare the production SharePoint site

### 1a. Check your access
You need **Owner** (Full Control) on the production site to create lists and set permissions. If you only have Edit, ask the site owner to do Step 1 or give you Owner.

### 1b. Create the two lists
Use **one** of these options. Either way, the list names must be **exactly** `Change Requests` and `Change Request History`. The app finds its lists by name.

**Option 1: copy them from the test site.** This is the easiest, because it copies every column, choice, default and view, but no items.
1. On the **production** site, choose **+ New › List**.
2. Choose **From existing list**.
3. Pick the **test site**, then **Change Requests**, and click **Next**.
4. Name it `Change Requests` and click **Create**.
5. Repeat for **Change Request History**.

**Option 2: run the provisioning script.** Run [Provision-ChangeRequestLists.ps1](Provision-ChangeRequestLists.ps1) with the production site URL. It also uploads the rollback template:
```powershell
./Provision-ChangeRequestLists.ps1 -SiteUrl "https://<tenant>.sharepoint.com/sites/<production-site>" -ClientId "<your PnP Entra app id>"
```

**Option 3: create them by hand.** Follow Step 1, Option B, of [Change-Request-PowerApp-Guide.md](Change-Request-PowerApp-Guide.md).

### 1c. Check the column names
A wrong internal name is the most common migration problem.
1. Open **Change Requests › ⚙ › List settings**.
2. Click **SubmittedBy**, **RequesterEmail** and **CABDecision** one at a time. The end of the browser address must read `Field=SubmittedBy`, `Field=RequesterEmail` and so on, with no `_x0020_`.
3. Check the choice values match the test list exactly, especially the plain hyphens in `2 - High`.
4. In **Change Request History**, check `RequestID`, `FromStage`, `ToStage` and `Comment` exist, and that **Title** shows as *CR Number*.

### 1d. Recreate the indexes
Copying a list doesn't always copy its indexes.
1. Open **Change Requests › ⚙ › List settings › Indexed columns**.
2. If **Stage** isn't listed, click **Create a new index**, choose **Stage**, and click **Create**.
3. Do the same in **Change Request History** with **RequestID**.

### 1e. Upload the rollback template
If you used the script, it's already uploaded. Skip to the last step.
1. In the production site's **Documents**, create a folder **Change Templates**.
2. Upload [Rollback-Plan-Template.pdf](Rollback-Plan-Template.pdf).
3. On the file, click **⋯ › Copy link**, set it to *People in your organization*, and copy the link. Write it in the table as the production `RollbackTemplateUrl`.

### 1f. App Roles list (only if you use it)
If you moved roles into an **App Roles** list (see *Optional extras* in the main guide):
1. Copy it with **From existing list**.
2. Fill it with the **production** people.
3. Restrict who can edit it.

**Check:** both lists exist on the production site with the exact names, are empty, and the column names pass 1c.

---

## Step 2 — Production Microsoft Form

The form isn't tied to a SharePoint site. Still, make a **copy** for production, so test submissions don't create production tickets, and so production uploads go to the production owner's OneDrive.

### 2a. Copy the form
**If the production owner is the same account as test:**
1. Go to **forms.office.com**.
2. Hover the *Change Request* form and choose **⋯ › Copy** (older versions call it *Duplicate*).
3. Rename the copy to **Change Request**, and rename the old one to **Change Request (TEST)**.

**If the production owner is a different account:**
1. Open the test form and choose **⋯ › Collaborate or duplicate**.
2. Choose **Get a link to duplicate** and copy the link.
3. Sign in as the **production owner**, open that link, and click **Duplicate it**.

### 2b. Check the copy
1. Open **⋯ › Settings** and confirm:
   - **Only people in my organization** is selected. It's required for uploads and for SubmittedBy.
   - **Record name** is on.
2. Open the **Rollback Plan** question and replace the template link in its subtitle with the **production** link from 1e.
3. Check all 13 questions are present and the choice text is unchanged.

### 2c. Copy the production form link
Click **Collect responses › Copy link**. Write it in the table as the production `FormUrl`.

**Check:** open the production form link in a private browser window. It asks you to sign in, and the template link in the Rollback Plan question opens the **production** PDF.

---

## Step 3 — Production Power Automate flow

### 3a. Copy the flow
1. Sign in to Power Automate **as the production form owner**.
   - If the test flow belongs to another account, have that account share it first: open the flow, then **Share** (or **Edit › Co-owners**), and add the production owner.
2. Open the test flow **Change Request – Form to SharePoint**.
3. On its details page, click **⋯ › Save As**. Name it **Change Request – Form to SharePoint (PROD)** and save.
4. Open the new copy and click **Edit**.

### 3b. Point it at the production form
In the two Microsoft Forms steps, set **Form Id** to the **production** form:
- **When a new response is submitted:** Form Id = production *Change Request*
- **Get response details:** Form Id = the same

Changing the form can clear the dynamic content that came from it. Re-check every field in 3c.

### 3c. Point the SharePoint steps at the production site
For **each** SharePoint action, set **Site Address** to the **production** site and re-pick the list:

| Action | List |
|---|---|
| **Create CR** | Change Requests |
| **Log history** | Change Request History |
| **Add attachment** (inside both *Apply to each* loops) | Change Requests |

When you change the site or list in **Create CR** and **Log history**, the field boxes reload and may be **empty**. Re-enter them. The full mappings are in [Change-Request-Form-Setup.md](Change-Request-Form-Setup.md), Part C.

Here's a quick reminder for **Create CR**:

| Column | Value |
|---|---|
| Title, A6Program, DSN, RequestedBy, Description | the matching form answers |
| RequesterEmail | *E-mail* |
| **SubmittedBy** | *Responders' Email* |
| Category / ChangeType / Priority / Risk / Impact Value | the matching answers (**Enter custom value**) |
| Stage Value | `Requested` |
| CABDecision Value / AuthorityDecision Value | `Pending` |
| FormResponseId | *Response Id* |

The expressions that use `outputs('Create_CR')` keep working as long as you didn't rename **Create CR**.

### 3d. Check the connections
1. Open **⋯ › Edit** on each action, or look at the flow's **Connections** list.
2. Every connection (Microsoft Forms, SharePoint, **OneDrive for Business**, Outlook) must use the **production owner** account. The OneDrive connection is what reads the uploaded files, and they're in that account's OneDrive.
3. If any connection shows another account, click **⋯ › + Add new connection** and sign in as the production owner.

### 3e. Save and turn on
1. Click **Save**.
2. Make sure the flow is **On**.
3. Leave the **test** flow on as well. It now only listens to the test form, so the two can't clash.

**Check:**
1. Submit **one** response through the **production** form, uploading the rollback PDF.
2. In the PROD flow's **Run history**, the run should be green on every step.
3. On the production site, **Change Requests** should have a new item with:
   - Stage = Requested
   - SubmittedBy filled in
   - the attachment `RollbackPlan_CR-00001.pdf`
4. **Change Request History** should have its *Created* row.

Keep this item for the app test in Step 6.

---

## Step 4 — Production Power Apps app

### Option A: same environment (most common)

#### 4a. Make the production copy
1. Open the test app in Power Apps Studio.
2. Click the **down arrow next to the Save icon** (top right) and choose **Save as** (older versions: **File › Save as**).
3. Name it **Change Request Portal** and save.
4. Go back to **make.powerapps.com › Apps** and rename the *original* to **Change Request Portal (TEST)**: click **⋯ › Settings** and change the **Name**.
5. Open the new **Change Request Portal** to edit it.

Check the app name at the top of Studio to make sure you're editing the **production** copy, not the test one.

#### 4b. Switch the data sources to production
1. Click the **Data** icon (the cylinder) in the far-left bar.
2. Next to **Change Requests**, click **⋯ › Remove**. Do the same for **Change Request History**, and for **App Roles** if you use it. Formulas show red errors for a moment. That's expected.
3. Click **Add data › SharePoint** and pick the **production** site. Type its URL if it isn't listed.
4. Tick **Change Requests** and **Change Request History** (and **App Roles**), then click **Connect**.

Because the lists have the same names and columns, every formula reconnects on its own, and the red errors disappear.

#### 4c. Update App.Formulas
Select **App › Formulas** and change these to the **production** values from your table:
- `FormUrl`: the production form link (2c)
- `RollbackTemplateUrl`: the production template link (1e)
- `CMTeam`, `CABMembers`, `ChangeAuthorities`: the production people. Skip this if you use **App Roles**.

#### 4d. Clean up and check
1. Delete any temporary labels you added while testing, such as `User().Email`, `frmDetail.Unsaved` or the CM/CAB/Auth checks.
2. Click the **App checker** (the stethoscope icon in the top toolbar). There should be **no errors**. Delegation warnings (yellow) are fine.
3. If errors remain, they almost always name a column. Compare that column in the production list with the test list (Step 1c).

#### 4e. Publish
Press **Ctrl+S**, then click **Publish › Publish this version**.

### Option B: separate production environment
Use this only if your organization has a separate Power Platform environment for production. The environment picker at the top right of Power Apps shows more than one.

1. Do Steps 1 to 3 first. The flow can be rebuilt in the production environment with **Save As**, or exported along with the app.
2. In the **test** environment, go to **Apps**, select the app, then **⋯ › Export package**:
   - set **Import setup** to *Create as new*,
   - include the flow if you want it,
   - then export the `.zip`.
3. Switch to the **production** environment, go to **Apps › Import canvas app**, and upload the `.zip`.
4. When asked, choose or create the SharePoint (and flow) connections **as the production owner**.
5. Open the imported app and follow **4b to 4e** above to switch the lists, App.Formulas and so on.

> If your organization manages apps with **Solutions** and environment variables, ask your Power Platform admin. That's a cleaner long-term setup, but it needs admin involvement.

---

## Step 5 — Share and set permissions

### 5a. SharePoint permissions on the production site
1. On the production site, go to **⚙ › Site permissions** (or **Share site**).
2. Add everyone who'll use the portal with **Edit**.
   - A security group is easiest. Your IT team may already have one for the unit.
3. Give the **production form and flow owner** account at least **Edit**, because the flow writes the items.
4. If you use **App Roles**, restrict who can edit that list to the role managers.

### 5b. Share the app
1. Go to **make.powerapps.com › Apps**.
2. Click **⋯** next to **Change Request Portal** (the production one), then **Share**.
3. Add the same users or group, and click **Share**.
4. Optionally add a co-owner, for example a second admin, so the app isn't tied to one person.

Don't send the link yet.

---

## Step 6 — Test in production

Use the request from Step 3 and work through this list **as yourself (CM)**, then as **one regular user**:

| # | Do this | Expect |
|---|---|---|
| 1 | Open the **production** app link | The board loads, and the request from Step 3 is in **1. Requested** |
| 2 | Click **+ Request a New Change** | The **production** form opens, not the test one |
| 3 | Click **Download Rollback Plan template** | The **production** PDF opens |
| 4 | Open the request | The detail screen loads; notes tabs, History and the attachment work |
| 5 | Type a comment and click **Add comment** | It appears in History |
| 6 | **Move** it to CAB | It moves; a History row is added |
| 7 | As a CAB member, approve and **Move** | It moves to Change Authority |
| 8 | As a regular user, open the app | They see only their own requests, with no toggle, and no Move or Send back |
| 9 | Check the **test** app and site | They're unchanged; a test-form submission still lands on the **test** site only |

### 6a. Clean up the test tickets
1. Delete the test item or items from **Change Requests** and their rows from **Change Request History** on the **production** site.
2. Empty the site **Recycle bin** if you want them gone completely.

**About CR numbers:** SharePoint never reuses item IDs, so after deleting test items the first real request won't be `CR-00001`. If you want real numbering to start at 1, you have two choices:
- do the Step 3 and Step 6 tests on the production lists, then delete **both lists** and recreate them (Step 1b, *From existing list*), then repeat 4b to reconnect;
- or simply accept the gap.

---

## Step 7 — Go live

1. **Announce it.** Send users the **production app link**: **Apps › ⋯ › Details › Web link**. Tell them to fully close any old copy of the app they have open, because the player caches versions.
2. **Pin it.** If you use Teams, add the production app as a tab, or pin it in **Apps** for the team.
3. **Label the test copies.** Make sure the test app, form and flow have **(TEST)** in their names so no one uses them by mistake.
4. **Watch the first day.** Check the PROD flow's **Run history** after the first few real submissions.

### Making changes after go-live
- **Try changes in the TEST app first,** against the test site.
- **Then make the same change in the PRODUCTION app,** and publish it. Don't **Save as** from test again: that creates a new production app with a new link, and you'd have to repeat Steps 4 and 5.
- **Keep the guides up to date** with each change, so both copies stay alike.

---

## If something goes wrong (rollback)

The test setup is untouched, so you can fall back at any time:
1. Tell users to keep using the **test** app link, and give them the test form link if needed.
2. Turn **off** the PROD flow so the production form stops creating items.
3. Fix the problem, then re-run the Step 6 tests.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Red errors after re-adding the data sources | A list name or column internal name differs from test | Check the list names exactly, and the column `Field=` names (1c). Recreate any wrong column without spaces, then **Refresh** the data source |
| *SubmittedBy isn't recognized* (or any column) | Data source cached before the column existed | **Data › ⋯ › Refresh** next to the list, or remove and re-add it |
| The production form creates items on the **test** site | The PROD flow's SharePoint steps still point at the test site | Repeat 3c for **every** SharePoint action, including Add attachment inside both loops |
| Test-form submissions appear on production | The PROD flow's trigger still uses the test form | Repeat 3b |
| Flow fails at **Get file content** | The OneDrive connection isn't the production form owner | Repeat 3d. The connection must be the account that owns the production form |
| Flow fails at **Create CR**: *column not found* | Field mappings were cleared when the list changed | Re-enter the mappings (3c) |
| SubmittedBy is empty | The production form isn't set to *Only people in my organization* | Fix the setting (2b) and re-map SubmittedBy to **Responders' Email** |
| The template link opens the test PDF | Old link in the form subtitle or in `RollbackTemplateUrl` | Update both (2b, 4c) |
| Users don't see the latest changes | The app player caches the old version | Have them fully close and reopen the app, sometimes twice, and restart Teams if they use it there |
| Users get access errors | They have the app but not the production site | Give them **Edit** on the production site (5a) |
| CM, CAB or Authority buttons are missing for the right people | Production emails not in App.Formulas (or App Roles) | Update the role lists (4c or 1f). Check with a temporary label showing `User().Email` |

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
