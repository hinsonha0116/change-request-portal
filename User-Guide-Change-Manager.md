# Change Request Portal: Change Manager's guide

This guide is for the **Change Management (CM) team**. It walks through every part of the Change Request Portal, then follows a change from the moment it's submitted to the moment it's closed and archived.

> **This guide describes the app as built from the [build guide](Change-Request-PowerApp-Guide.md).** The pending updates in [DetailScreen-Fixes.md](DetailScreen-Fixes.md) change a few things. They're listed in the last section, **Coming with the next update**.

## Contents
1. [The portal at a glance](#1-the-portal-at-a-glance)
2. [Opening the portal](#2-opening-the-portal)
3. [The board](#3-the-board)
4. [Submitting a change request](#4-submitting-a-change-request)
5. [The request screen](#5-the-request-screen)
6. [A change from start to finish](#6-a-change-from-start-to-finish)
7. [Sending back, rejecting and commenting](#7-sending-back-rejecting-and-commenting)
8. [Emails](#8-emails)
9. [The Schedule](#9-the-schedule)
10. [The change archive](#10-the-change-archive)
11. [Looking after the portal](#11-looking-after-the-portal)
12. [Quick reference](#12-quick-reference)
13. [Coming with the next update](#13-coming-with-the-next-update)

---

## 1. The portal at a glance

Every change to A6 systems is raised as a **change request** and moves through review stages until it's closed. The portal keeps the request, every decision, the notes from each stage, the attachments and a full history in one place.

### The stages

| # | Stage | What happens | Must be true before it moves on |
|---|---|---|---|
| 1 | **Requested** | The requester submits; CM checks it's complete | — |
| 2 | **Technical Review Board (TRB)** | The TRB checks the technical plan, testing and rollback plan | TRB decision = **Approved** |
| 3 | **Change Advisory Board (CAB)** | The CAB reviews risk, impact and timing | CAB decision = **Approved** |
| 4 | **Change Authority** | The Change Authority gives final approval | Authority decision = **Approved** |
| 5 | **Implementation** | The assignee makes the change and clicks **✔ Completed** | Implementation notes filled in |
| 6 | **PIR** (Post Implementation Review) | CM confirms the change worked | PIR outcome chosen |
| 7 | **Close** | Done, or rejected | — |

### The route depends on the change type

| Change type | Route |
|---|---|
| **Normal** | Requested → TRB → CAB → Change Authority → Implementation → PIR → Close |
| **Emergency** | Requested → CAB → Change Authority → Implementation → PIR → Close |
| **Standard** | Requested → Implementation → Close |
| *Informational (older requests only)* | Requested → CAB → Change Authority → Implementation → PIR → Close |

The portal knows each route. **Move** always goes to the next stage on that request's route, and the progress tracker only shows the stages it will pass through.

### Who does what

| Role | Can |
|---|---|
| **CM team (you)** | See every request · **Move** requests forward · **Send back** · edit the request while in *Requested* · record the PIR outcome |
| **TRB members** | See every request · record the TRB decision and checklist · **Needs changes** · **Reject** at the TRB |
| **CAB members** | See every request · record the CAB decision · **Reject** at the CAB |
| **Change Authority** | See every request · record the Authority decision · **Reject** at the Authority stage |
| **Implementer / assignee** | Fill in implementation details · **✔ Completed** |
| **Requesters** (everyone else) | Submit requests · see only their own, or ones submitted for them · edit them while in *Requested* · **Add comment** |

**Only the CM team moves requests between stages.** The boards record their decisions, and CM moves the request on once the decision is in. Someone can hold more than one role: a CM team member who is also on the CAB can approve and move in one step.

---

## 2. Opening the portal

- **From the Change Management SharePoint page:** the portal is embedded on the page.
- **From the app link** or the team's **Teams tab**, if one has been added.
- **From an email:** every notification email has a link that opens that request directly.

**The first time** you open it, you're asked to **Allow** the SharePoint and Office 365 Users connections. That's normal, and it only happens once.

If the app ever looks out of date after an update, close it completely and open it again (sometimes twice).

---

## 3. The board

The board is the home screen. It has one column per stage, and each change request is a card in its stage's column.

### The header

| Control | What it does |
|---|---|
| **Search** | Finds requests whose **title** or **CR number** starts with what you type. Typing `CR-2026-01` finds CR-2026-010 to 019 |
| **Category filter** | All categories · Hardware · Software · Network |
| **Type filter** | All types · Standard · Normal · Emergency |
| **All requests / My requests** | You see everyone's requests. Switch to *My requests* to see only the ones you submitted or that were submitted for you |
| **⟳ Refresh** | Reloads the board now. It also refreshes itself every minute |
| **Schedule** | Opens the calendar of planned changes (section 9) |
| **+ Request a New Change** | Opens the New Request screen (section 4) |

The number in each column header, e.g. **3. CAB (4)**, is how many cards are in that column with the current search and filters.

### The cards

```
┃ CR-2026-014   ✔ Complete              ← CR number; ✔ Complete once the implementer has finished
┃ Replace VDI gateway certificates      ← title
┃ High · Hardware · Normal              ← priority · category · change type
┃ Risk Moderate · Impact High
┃ Keegan Bowman · VDI · 12 Nov 2026     ← requester · A6 program · submitted
```

- **The coloured stripe** on the left is the priority: red = Critical, orange = High, gold = Moderate, grey = Low.
- **✔ Complete** (green) appears in the Implementation column once the implementer has clicked Completed. It means the request is waiting for **you** to move it on.
- **Each column is sorted** by last changed, newest at the top.
- **Click a card** to open the request.

> **Tip:** the board only hides other people's requests inside the app. Anyone with access to the SharePoint site could still open the list directly.

---

## 4. Submitting a change request

Anyone can submit a request, including the CM team on someone else's behalf.

1. Click **+ Request a New Change**.
2. **Requested by** starts as you. To submit for someone else, start typing their name or email and pick them. Their email fills in automatically.
3. Fill in the form:

   | Field | Notes |
   |---|---|
   | **A6 program** | Pick from the list |
   | **DSN** | Required |
   | **Title** | A short description of the change |
   | **Category · Change type · Priority · Risk · Impact** | All required |
   | **Planned start / end** | Optional, but needed for the change to appear on the Schedule. End can't be before start |
   | **Outage expected?** | If **Yes**, **Outage duration** becomes required |
   | **Location** | Base and building |
   | **Affected systems** | What the change touches |
   | **Description · Impact details · Justification** | What, who's affected, and why |
   | **Attachments** | The **completed Rollback Plan** is required. Add any other files too |

4. **Download Rollback Plan template** at the top gives the blank PDF to fill in.
5. Click **Submit request**. The portal checks every required field and that a file is attached. You'll see *Change request CR-2026-0NN submitted*, and the card appears in **1. Requested**.

**What happens next:**
- The History starts with *Created: Submitted in the app by … (on behalf of …)*.
- The **CM team** gets a *New change request* email. **SW** or **HW managers** get one too for Software or Hardware changes.
- Both the submitter and the person it was submitted for can see it on their board.

**CR numbers** look like **CR-2026-001**. The middle part is the year, and the count restarts at 001 every 1 January. Requests from before this numbering keep their old number, e.g. CR-00012.

---

## 5. The request screen

Click any card to open its request.

### The banner
- **← Board** (or **← Schedule**, if you came from the calendar) goes back.
- The **CR number and title**.
- **Save changes** saves your edits without moving the request.

### The progress tracker
A row of numbered circles for the stages on this request's route. **Green** = done, **coloured** = where it is now, **grey** = still to come.

### The form (left)
Fields appear as the request reaches their stage, and are only editable at their own stage, by the right people:

| Fields | Editable when | By |
|---|---|---|
| The request details (program, title, category, type, priority, risk, impact, dates, outage, location, affected systems, impact details, justification) | in *Requested* | anyone who can open it, including CM |
| TRB decision and checklist (rollback plan reviewed, tested, security / STIG reviewed) | at the TRB | TRB members |
| CAB decision | at the CAB | CAB members |
| Authority decision | at the Change Authority | Change Authorities |
| Assignee · Actual start / end | in Implementation | anyone |
| PIR outcome | at PIR | anyone (CM records it) |
| Attachments | at every stage except Close | anyone |

Read-only fields show as plain text. Empty optional fields are hidden once the request has left *Requested*.

### Notes (top right)
Tabs: **Description · TRB · CAB · Authority · Implement · PIR**. A tab appears once the request reaches that stage.
- **Only one note is editable at a time:** the current stage's note, for the people who work on that stage. That tab is shown in **bold**.
- Every other tab is read-only and scrolls if it's long.
- When you open a request, or after a move, the box jumps to the current stage's tab.

| Note | Editable when | By |
|---|---|---|
| Description | in *Requested* | anyone |
| TRB notes | at the TRB | TRB members |
| CAB notes | at the CAB | CAB members |
| Authority notes | at the Change Authority | Change Authorities |
| Implementation notes | in Implementation | anyone |
| PIR notes | at PIR | anyone |

### History (bottom right)
Every event, newest first, with who and when:
- **Created** — the submission
- **Requested → Technical Review Board** — a move, with the comment typed at the time
- **Comment (CAB)** — a comment added without moving
- **✔ Implementation complete** — the implementer clicked Completed
- **REJECTED: …** / **NEEDS CHANGES: …** — in the comment of those moves

### The action bar (bottom)

| Button | Who sees it | What it does |
|---|---|---|
| **← Send back** | CM, at any stage except Requested and Close | Returns the request to the previous stage on its route. **A comment is required** |
| **Reject** | TRB / CAB / Authority members at their own stage | Closes the request as *Rejected*. **A comment is required** |
| **✔ Completed** | Anyone, in Implementation (until clicked) | Marks the work done and emails the CM team. Needs implementation notes |
| **Needs changes** | TRB members at the TRB | Sends the request back to the requester. **A comment is required** |
| **Add comment** | Everyone | Adds the comment to the History without moving the request |
| *comment box* | Everyone | The comment that goes with the next action |
| **Move to … →** | CM, at any stage except Close | Saves, checks the stage's rule, and moves to the next stage on the route |

**Every button saves first.** You never lose an edit by clicking Move, and a board member who is also on the CM team can set *Approved* and click **Move** in one step.

A comment you type but don't post is cleared when you leave the screen.

---

## 6. A change from start to finish

This follows a **Normal** change. The differences for Emergency and Standard changes come after.

### Stage 1 — Requested: check it's complete
You'll get the *New change request* email, or you'll see the card in **1. Requested**.

1. Open the request and check:
   - the details are complete and make sense,
   - the **change type** is right (it decides the route),
   - the **Rollback Plan** is attached and filled in,
   - the **planned dates** are set, and the **Schedule** shows no clash (section 9).
2. **Fix small things yourself.** While the request is in *Requested*, you can edit any request field and the Description, then click **Save changes**.
3. **For anything bigger, ask the requester.** Type a question and click **Add comment**, or contact them directly. Requesters can edit their own request while it's in *Requested*.
4. When it's ready, type a short comment if you like and click **Move to Technical Review Board →**.

> The TRB decision is reset to *Pending* every time a request moves into the TRB.

### Stage 2 — TRB
The TRB members get an email (*… is ready for TRB review*).

The TRB member:
- ticks the **checklist** items that apply (none are required),
- writes **TRB notes**,
- sets the **TRB decision**:

| TRB decision | What happens next |
|---|---|
| **Approved** | They click **Save changes**. You then click **Move to Change Advisory Board →** |
| **Needs changes** | They type what needs to change and click **Needs changes**. The request goes straight back to **Requested**, the TRB notes get a *NEEDS CHANGES: …* line, and the requester gets an email. Once it's fixed, you move it to the TRB again |
| **Rejected** | They type the reason and click **Reject**. The request closes as *Rejected* (section 7) |

If you click **Move** before the decision is *Approved*, you'll see *The TRB decision must be Approved before this change can move on*.

### Stage 3 — CAB
The CAB members get an email (*… is ready for CAB review*). A CAB member sets the **CAB decision**, writes **CAB notes**, and saves, or rejects. Once it's *Approved*, you click **Move to Change Authority →**.

### Stage 4 — Change Authority
The Change Authority gets an email (*… is awaiting Change Authority approval*). They set the **Authority decision** and notes, or reject. Once it's *Approved*, you click **Move to Implementation →**. The requester (CC CM) gets *… is approved for implementation*.

### Stage 5 — Implementation
The implementer:
1. sets the **Assignee** and the **Actual start / end** as the work happens,
2. writes **Implementation notes**: what was done and any issues,
3. clicks **✔ Completed**.

Completed needs implementation notes. It adds *✔ Implementation complete* to the History, shows **✔ Complete** on the board card, and emails the **CM team** (*… has been completed by the implementer*).

You then check the notes and dates, and click **Move to PIR →**. The CM team gets *… has been implemented and is ready for PIR*.

> You can move a request on without the implementer clicking Completed, as long as there are implementation notes. Completed is the implementer's signal to you.

### Stage 6 — PIR
1. Confirm with the implementer and requester that the change worked.
2. Set the **PIR outcome**: *Successful*, *Successful with issues*, *Failed* or *Rolled back*.
3. Write **PIR notes**: lessons learned, follow-up actions.
4. Click **Move to Close →**.

You'll see *Choose a PIR outcome before closing* if the outcome is empty.

### Stage 7 — Close
- The request is now read-only, and **Closed date** is set.
- The requester (CC CM) gets *… is closed*.
- Within a few minutes, the **archive flow** files a PDF record and the attachments in the Change Archive library (section 10).

### Emergency changes
Same as Normal, but **without the TRB**: Requested → CAB → Change Authority → Implementation → PIR → Close. Expect to move them quickly. If the new-request flow was set up to flag emergencies, their email arrives marked **High importance**.

### Standard changes
Routine, pre-approved changes: **Requested → Implementation → Close**.
- There's no TRB, CAB, Authority or PIR, and those fields and tabs don't appear.
- From Requested, **Move** goes straight to Implementation.
- Once the implementer has clicked Completed, **Move** goes straight to **Close**.
- Check the change type is really *Standard* while it's in Requested. If it isn't, correct it before you move it.

---

## 7. Sending back, rejecting and commenting

### Send back (CM)
Returns a request to the **previous stage on its route**, for example from CAB back to the TRB, or from Implementation back to the Change Authority.
- **A comment is required.** It goes into the History and the email.
- If the request goes back to **Requested**, the requester gets *… was sent back to you*.
- Sending back from Implementation also clears **✔ Complete**, so the implementer can mark it complete again.

| Sent back from | Goes to (Normal) | Goes to (Emergency) | Goes to (Standard) |
|---|---|---|---|
| TRB | Requested | — | — |
| CAB | TRB | Requested | — |
| Change Authority | CAB | CAB | — |
| Implementation | Change Authority | Change Authority | Requested |
| PIR | Implementation | Implementation | — |

### Reject (TRB, CAB or Authority)
- Only the board whose stage it is can reject, with a **required comment**.
- The request goes straight to **Close**, with PIR outcome *Rejected*.
- The comment is added under that board's notes as *REJECTED: …*, without replacing what was there.
- The requester (CC CM) gets *… was rejected*.
- Rejected changes are archived like any other closed change.

### Needs changes (TRB)
- Sends a request at the TRB back to **Requested**, with a **required comment**.
- Sets the TRB decision to *Needs changes* and adds *NEEDS CHANGES: …* to the TRB notes.
- The requester gets *… needs changes before TRB review*.

### Add comment (everyone)
Adds a note to the History without changing anything else. It doesn't send an email, so contact people directly if they need to act on it.

---

## 8. Emails

All emails come from the flows, about 1–5 minutes after the action. Each one has a link that opens the request.

| When | Who gets it | Subject starts with |
|---|---|---|
| A request is submitted | CM team; SW managers (Software) or HW managers (Hardware) | *New change request CR-…* |
| Moved to TRB | TRB members | *CR-… is ready for TRB review* |
| Moved to CAB | CAB members | *CR-… is ready for CAB review* |
| Moved to Change Authority | Change Authorities | *CR-… is awaiting Change Authority approval* |
| Moved to Implementation | Requester, CC CM | *CR-… is approved for implementation* |
| Implementer clicks Completed | CM team | *CR-… has been completed by the implementer* |
| Moved to PIR | CM team | *CR-… has been implemented and is ready for PIR* |
| Sent back to Requested | Requester | *CR-… was sent back to you* |
| TRB clicks Needs changes | Requester | *CR-… needs changes before TRB review* |
| Closed | Requester, CC CM | *CR-… is closed* |
| Rejected | Requester, CC CM | *CR-… was rejected* |

Comments and saves don't send emails.

**"Requester"** means both the person in *Requested by* and the person who submitted it.

---

## 9. The Schedule

Click **Schedule** on the board to open a month calendar of planned changes (the Forward Schedule of Change).

- **‹ ›** move between months, and **Today** jumps back to now.
- Each change shows as a **chip** on every day it runs, with its **CR number and A6 program**. Hover over a chip to see its title.
- **The chip's colour is the request's stage**, the same colours as the board.
- **A red outline** marks a possible clash: another change at the **same location** or for the **same A6 program**, at overlapping times.
- **Click a day** to list its changes on the right, with times, title, program, location, stage, and outage and clash warnings.
- **Click a change** (a chip or a row in the day list) to open it. **← Schedule** brings you back.

Rejected changes aren't shown. Only requests with a **planned start** appear, so planned dates matter.

**Use it in Requested** to check a new request's dates before you move it on, and **before CAB** to spot clashes the board should discuss.

---

## 10. The change archive

When a request closes (including rejections), a flow files a permanent record in the **Change Archive** library on the SharePoint site:

```
Change Archive › A6 program › year › month › CR-2026-014 - Title
                                              ├── CR-2026-014 - Change record.pdf
                                              └── every attachment
```

- **The PDF** has every field, grouped by stage, every stage's notes, and the full History at the end. Rejected changes say **Rejected** at the top.
- **Year and month** are the month the change **closed**.
- **Open archive:** a closed request shows **📁 Open archive** on its request screen, which opens the folder. It appears a minute or two after closing, the next time the request is opened.
- **The library is read-only** for most people, so the records can't be changed or deleted by accident.

Changes closed before the archive existed can be archived one at a time: in the **Change Requests** list, select the closed request, then **Automate › Change Request – Archive (run manually)**.

---

## 11. Looking after the portal

### Daily
- **Requested column:** check and move new requests on.
- **✔ Complete cards** in Implementation: review and move to PIR (or to Close, for Standard).
- **PIR column:** record outcomes and close.
- **Stuck requests:** a request waiting a long time at a board stage may need a nudge. Use **Add comment** for the record, and contact the board directly.

### People and roles
Who's on the CM team, TRB, CAB and Change Authority is set in the app (**App › Formulas**: `CMTeam`, `TRBMembers`, `CABMembers`, `ChangeAuthorities`), and the email recipients are set in the flows. When someone joins or leaves:
1. Update the list in App.Formulas, using their sign-in email in **lower case**, then **Save** and **Publish** the app.
2. Update the matching email variable in the flows.
3. Make sure they have access to the SharePoint site.

### Programs and choices
The A6 program list and the choice lists also live in **App › Formulas**. Changing a choice also means changing the same choice in the SharePoint column.

### Common questions

| Question | Answer |
|---|---|
| A board member can't change their decision | Their email in App.Formulas must exactly match the account they sign in with (e.g. `@us.af.mil` vs `@af.mil`), in lower case |
| A requester can't see their request | It's matched on the submitter's and the requester's email. Check *Requested by* on the request |
| **Move** says the decision must be Approved | The board member hasn't saved *Approved* yet. Ask them to save it, or check the decision field |
| **Move** isn't there | You're not in `CMTeam`, or the request is closed |
| Someone didn't get an email | Check junk mail, then the flow's **Run history** in Power Automate. Emails can take up to 5 minutes |
| A request is at the wrong stage | Use **Send back** (or Move) with a comment explaining why. Don't change the stage directly in SharePoint, because that skips the History and the emails |
| A request was submitted with the wrong change type | Correct it while it's in *Requested*, then save. Its route changes to match |
| Open archive doesn't show | Wait a few minutes after closing, then reopen the request. If it still doesn't show, check the archive flow's Run history |

For anything else, see the troubleshooting table in the [build guide](Change-Request-PowerApp-Guide.md) (Step 10) and [Troubleshooting-Notes.md](Troubleshooting-Notes.md).

---

## 12. Quick reference

### Your checklist, stage by stage (Normal)

| Stage | You do | Then click |
|---|---|---|
| Requested | Check completeness, change type, rollback plan, dates and Schedule. Fix or ask | **Move to Technical Review Board →** |
| TRB | Wait for *Approved* (or Needs changes / Rejected) | **Move to Change Advisory Board →** |
| CAB | Wait for *Approved* | **Move to Change Authority →** |
| Change Authority | Wait for *Approved* | **Move to Implementation →** |
| Implementation | Wait for **✔ Complete**; check notes and dates | **Move to PIR →** |
| PIR | Confirm the result; set the PIR outcome and notes | **Move to Close →** |
| Close | Check the archive was filed | — |

### Messages you might see

| Message | Meaning |
|---|---|
| *The TRB / CAB / Change Authority decision must be Approved before this change can move on* | The board hasn't approved yet |
| *Add implementation notes before moving on* | Implementation notes are empty |
| *Choose a PIR outcome before closing* | The PIR outcome is empty |
| *Add a comment explaining why it's being sent back* | Send back needs a comment |
| *Add a comment explaining the rejection* | Reject needs a comment |
| *Couldn't save: …* | Something in the form stopped the save. Read the rest of the message, or check for a red-starred field |

---

## 13. Coming with the next update

These changes are in [DetailScreen-Fixes.md](DetailScreen-Fixes.md) and will be folded into this guide once they're built:

| Update | What changes for you |
|---|---|
| **Change type help** | Hovering over *Change type ⓘ* on New Request explains Standard, Normal and Emergency |
| **"Other" A6 program** | Requesters can pick **Other** and type a program name. It shows as *Other* plus the name on the request |
| **Several assignees** | Implementation can have more than one assignee |
| **Emergency CAB (ECAB)** | Emergency changes go **Requested → Emergency CAB → Implementation → PIR → Close**. The CAB members record the **ECAB decision**, and the board gets an **ECAB** column |
| **History of every change** | When anyone saves a change to a field (e.g. you correct the priority in Requested), the History shows *✎ Changes: Priority: 3 - Moderate → 2 - High* |
| **Software and hardware details** | Software requests record the software name and versions; hardware requests record make, model and serial numbers |
| **CMDB tasker** | When the implementer clicks **Completed**, the HW or SW asset manager is emailed to update the CMDB. **CMDB updated** must then be ticked (by CM or an asset manager) during Implementation before any change can move on |
