# Change Request form: Microsoft Forms + Power Automate setup

This document sets up the intake for new change requests:

1. A user clicks **+ Request a New Change** in the app, which opens a Microsoft Form.
2. They fill in the form and upload their completed Rollback Plan PDF.
3. A Power Automate flow creates the ticket in the *Change Requests* list with Stage = **Requested** and attaches the uploaded files to it.

Before you start, create the SharePoint lists (see Step 1 of [Change-Request-PowerApp-Guide.md](Change-Request-PowerApp-Guide.md)).

---

## Part A — Publish the Rollback Plan template

[Rollback-Plan-Template.pdf](Rollback-Plan-Template.pdf) is a fillable 2-page form (63 fields). It covers:
- change information
- rollback triggers
- decision authority and timing
- a pre-change checklist
- a 10-step rollback procedure table
- verification
- a communication plan
- signatures

The three signature boxes are real PDF signature fields, so a CAC/PIV digital signature works in Adobe Acrobat or Reader.

If you put the PDF in the same folder as the provisioning script, the script uploads it for you to **Documents › Change Templates** and prints its URL. To upload it by hand instead:
1. In the SharePoint site, go to **Documents**, create a folder named **Change Templates**, and upload the PDF.
2. Open the file's **⋯** menu, choose **Copy link**, and set the link to *People in your organization*.
3. Keep this link handy. You'll paste it into the form (Part B) and into `RollbackTemplateUrl` in the app.

> Tell users to fill the PDF in **Adobe Acrobat or Reader** and to *save* it rather than print it to PDF. Browser PDF viewers can usually fill the fields, but they can't apply CAC signatures.

---

## Part B — Build the Microsoft Form

1. Go to **forms.office.com** and sign in with your work account. Choose **New Form** and name it **Change Request**.
   - Who should own it: the account that owns the form must also own the flow in Part C. A shared change-management account is best, so the process doesn't break if one person leaves.
2. Open **⋯ › Settings** and set:
   - **Who can fill out this form:** *Only people in my organization*. This is required, because Forms only allows file uploads on organization-only forms.
   - **Record name:** On. This records each responder's sign-in e-mail. The flow stores it in SubmittedBy, and the app uses that to show people their own requests.
   - **Accept responses:** On.
3. Add the questions below. This is the suggested order, but you can rearrange them: the flow finds each answer by its question name, not its position.

| # | Question | Type | Required | Options / settings |
|---|---|---|---|---|
| 1 | A6 Program | Text | ✔ | |
| 2 | Requested By | Text | ✔ | Subtitle: *Rank and full name* |
| 3 | DSN | Text | ✔ | Subtitle: *e.g., 312-555-1234* |
| 4 | E-mail | Text | ✔ | |
| 5 | Category | Choice | ✔ | Hardware · Software · Network |
| 6 | Change Type | Choice | ✔ | Standard · Normal · Emergency · Informational |
| 7 | Title | Text | ✔ | |
| 8 | Description | Text, **Long answer** on | ✔ | |
| 9 | Priority | Choice | ✔ | 4 - Low · 3 - Moderate · 2 - High · 1 - Critical |
| 10 | Risk | Choice | ✔ | 3 - Moderate · 2 - High · 1 - Critical |
| 11 | Impact | Choice | ✔ | 3 - Moderate · 2 - High · 1 - Critical |
| 12 | Rollback Plan | **Upload file** | ✔ | File number limit **1** · size limit **10 MB** · file type **PDF** only. Subtitle: *Download the template here: &lt;template link from Part A&gt;. Complete it, save it, and upload it here.* |
| 13 | Additional attachments | **Upload file** | — | File number limit **10** · size limit **100 MB** · all file types |

Notes on these questions:
- **Choice questions** are radio buttons by default, so leave *Multiple answers* off. Also leave *Shuffle options* off.
- **Choice text must match exactly**, character for character: a plain hyphen with a space on each side, as in `2 - High`. The flow copies these values straight into SharePoint choice columns. If the text is different, the item will contain a value the app doesn't recognise.

4. Choose **Collect responses**, then **Copy link** (it looks like `https://forms.office.com/r/AbC123xyz`). Paste it into `FormUrl` in the app's **App.Formulas**.

> **Government tenants:** if your tenant is GCC High or DoD, Forms is at a different address (`forms.office365.us` or similar), and you should confirm the *Upload file* question type is available in your environment.

---

## Part C — Build the Power Automate flow

Sign in to **make.powerautomate.com** with the **same account that owns the form**. Choose **Create**, then **Automated cloud flow**, name it **Change Request – Form to SharePoint**, and pick the trigger **When a new response is submitted** (Microsoft Forms).

| # | Action | Settings |
|---|---|---|
| 1 | **When a new response is submitted** *(Forms)* | Form Id = *Change Request* |
| 2 | **Get response details** *(Forms)* | Form Id = *Change Request* · Response Id = `Response Id` from step 1 |
| 3 | **Create item** *(SharePoint)*, rename to **Create CR** | Site = your site · List = **Change Requests**, then map the fields as shown below |
| 4 | **Create item** *(SharePoint)*, rename to **Log history** | List = **Change Request History** · see below |
| 5 | **Get file content** + **Add attachment** in a loop for the **Rollback Plan** | see below |
| 6 | The same loop again for **Additional attachments** | see below |
| 7 | *(optional)* **Send an email (V2)** *(Outlook)* | confirmation to the requester |

### Step 3 — map the fields in "Create CR"
| SharePoint column | Value (dynamic content from *Get response details*) |
|---|---|
| Title | *Title* |
| A6Program | *A6 Program* |
| DSN | *DSN* |
| RequestedBy | *Requested By* |
| RequesterEmail | *E-mail* |
| SubmittedBy | *Responders' Email*. The submitter's sign-in account, which the app uses to show people their own requests |
| Category Value | *Category* |
| ChangeType Value | *Change Type* |
| Description | *Description* |
| Priority Value | *Priority* |
| Risk Value | *Risk* |
| Impact Value | *Impact* |
| Stage Value | type `Requested` |
| CABDecision Value / AuthorityDecision Value | type `Pending` |
| FormResponseId | *Response Id* (from step 1) |

To put a form answer into a choice column: open the column's dropdown, choose **Enter custom value**, and then insert the dynamic content.

### Step 4 — map the fields in "Log history"
| Column | Value |
|---|---|
| Title | Expression: `concat('CR-', formatNumber(outputs('Create_CR')?['body/ID'], '00000'))` |
| RequestID | *ID* (from *Create CR*) |
| FromStage | *(leave blank)* |
| ToStage | `Requested` |
| Comment | `Submitted via Microsoft Forms by ` + *Requested By* |

### Step 5 — attach the Rollback Plan PDF
The file questions in Forms return a JSON text listing the uploaded files. The files themselves are saved in the form owner's OneDrive, under *Apps › Microsoft Forms › Change Request*.

1. **Parse JSON** *(Data Operation)*. Rename it to **Parse Rollback**.
   - Content = *Rollback Plan* (dynamic content)
   - Schema:
     ```json
     {
       "type": "array",
       "items": {
         "type": "object",
         "properties": {
           "name": { "type": "string" },
           "link": { "type": "string" },
           "id":   { "type": "string" },
           "size": { "type": "integer" }
         },
         "required": ["name", "id"]
       }
     }
     ```
2. **Apply to each** over `body('Parse_Rollback')`. Inside the loop:
   - **Get file content** *(OneDrive for Business)*, renamed to **Get Rollback File**: set File = expression `items('Apply_to_each')?['id']`
   - **Add attachment** *(SharePoint)* with these settings:
     - Site / List = **Change Requests**
     - Id = *ID* from *Create CR*
     - File Name = expression `concat('RollbackPlan_CR-', formatNumber(outputs('Create_CR')?['body/ID'], '00000'), '.pdf')`
     - File Content = *File Content* from *Get Rollback File*

### Step 6 — attach the additional files
Additional attachments is optional, so its answer can be blank, and **Parse JSON** fails on blank text. Guard against that:

1. **Compose**, renamed to **AttachmentsRaw**: Inputs = *Additional attachments* (dynamic content).
2. **Parse JSON**, renamed to **Parse Attachments**:
   - Content = expression `if(empty(outputs('AttachmentsRaw')), '[]', outputs('AttachmentsRaw'))`
   - Schema = the same as in step 5.
3. **Apply to each** over `body('Parse_Attachments')`. Inside the loop:
   - **Get file content** *(OneDrive for Business)*: File = `items('Apply_to_each_2')?['id']`
   - **Add attachment**: Id = *ID* from *Create CR* · File Name = `items('Apply_to_each_2')?['name']` · File Content = the content from the previous action

> The names `Apply_to_each` and `Apply_to_each_2` assume you kept the default loop names. If you renamed the loops, use the names you gave them.

### Step 7 (optional) — confirmation e-mail
Use **Send an email (V2)** with these settings:
- **To** = *E-mail*
- **Subject** = `concat('Change request CR-', formatNumber(outputs('Create_CR')?['body/ID'], '00000'), ' received')`
- **Body**: tell the requester their change is now in the **Requested** stage and will be reviewed by the Change Advisory Board.

### Test it
1. Save the flow, then submit a test response through the form, uploading the template as the rollback plan.
2. Open the flow's **Run history**. Every step should be green.
3. In **Change Requests**, check that the new item has Stage = Requested and the attachment `RollbackPlan_CR-000NN.pdf`.
4. Refresh the app board. The new card should appear in **1. Requested**.
