# CMDB migration plan: Excel workbook to Dataverse

*Written 18 Nov 2026 from a review of the hardware CMDB workbook.*

The hardware CMDB lives in an Excel workbook today. Power Query merges six source folders into one asset list, and macros standardise it, add lifecycle values and build reports. This plan moves it into a Dataverse model-driven app with a scheduled Dataflow, so the CMDB updates itself and can link to change requests in the portal.

**Estimate:** about 5–7 weeks of work for one person, plus 2 weeks running Excel and Dataverse side by side.

> **Naming:** *property account* means the workbook's account column, and *Sources A–F* are the six source folders (section 4).
>
> **Handling:** the source workbook holds CUI. This plan is written to contain none of it: no asset data, counts, program names, system names or file names. Where you need those, they're in the workbook itself. Check against your marking guidance before sharing.

## Contents

1. [Before you start](#1-before-you-start)
2. [Fix or freeze the workbook](#2-fix-or-freeze-the-workbook)
3. [Data model](#3-data-model)
4. [Move the source files to SharePoint](#4-move-the-source-files-to-sharepoint)
5. [Build the Dataflow](#5-build-the-dataflow)
6. [First load](#6-first-load)
7. [Data cleanup](#7-data-cleanup)
8. [Model-driven app](#8-model-driven-app)
9. [Flows](#9-flows)
10. [Reports and dashboards](#10-reports-and-dashboards)
11. [Relationships (phase 2)](#11-relationships-phase-2)
12. [Parallel run and cutover](#12-parallel-run-and-cutover)
13. [Macro-by-macro mapping](#13-macro-by-macro-mapping)
14. [Timeline](#14-timeline)
15. [Risks](#15-risks)

---

## 1. Before you start

Don't start building until these four are settled. Each one can stop the project.

| # | Check | Who | Why |
|---|---|---|---|
| 1 | Dataverse, Dataflows and Power BI are available in your tenant's cloud (GCC High or DoD) and approved for CUI | Tenant / Power Platform admin | The data is CUI and can't go into a commercial environment. Some features arrive later in government clouds |
| 2 | Everyone who will **edit** the CMDB has a premium Power Apps licence (per user or per app) | Licensing owner | Dataverse apps are premium. Read-only users still need a licence to open the app; Power BI viewers don't |
| 3 | Two Dataverse environments exist: **CMDB Dev** and **CMDB Prod**, with Dataverse storage allocated | Power Platform admin | Build and test in Dev. Move to Prod as a managed solution |
| 4 | A named owner decides each mapping: device types, manufacturers, locations, property accounts | CM lead | Section 7 can't finish without these decisions |

Create a solution called **CMDB** in Dev and build everything below inside it, so it moves to Prod in one piece.

---

## 2. Fix or freeze the workbook

The workbook keeps running until cutover, so it needs to be trustworthy during the parallel run. The review found these bugs:

| Bug | Where | Effect today |
|---|---|---|
| **A. CI numbers are random** | `SYNC` › `DuplicateTableAndStandardize`, the `GetRandomAlphanumeric` loop | Every sync gives every asset a new `HW-XXX-?????` number. No asset in **Previous Master** kept its number, so the Decommission Log and anything else that quotes a CI number goes stale |
| **B. Registry values never applied** | Same macro. The CI number is written into `lookupKey`, which is then used to look up the Registries table (keyed by serial) | Warranty, End of Life, End of Support, Operational Status, Classification, Project, CLIN and Contract overrides never reach Asset Master. Every registry row is marked *Missing from Scan (Retired?)* |
| **C. Archive reads the wrong column** | `arciveretiredassets` › `ArchiveDecommissionedAssets` checks column 9 (Project ID) and copies column 8 into Remarks | It never archives anything. **Fixing only the column would archive every asset, because of bug B** |
| **D. Project from source name never set** | Same sync macro. It looks for a `Source` / `Source.Name` column that Asset Master doesn't have | The fallback that sets the project from the source file name never fires, so the project filter buttons show nothing |
| **E. Activity log never runs** | `Activtylog` module | `Workbook_Open` and `Workbook_BeforeSave` only fire from **ThisWorkbook**, and there's no **ActivityLog** sheet |

Do one of these:

- **Fix A and B** (recommended if the parallel run is more than a few weeks away). Use a separate variable for the CI number. Build the CI number from the serial, as **Previous Master** did (`HW-` + abbreviation + last 5 of serial), so it's the same on every run. Then fix C.
- **Freeze.** Stop running **Sync & Standardize** and **Archive**. Treat the Registries table as the master copy of the override values until the first load into Dataverse (step 6).

**About CI numbers in Dataverse.** The current numbers mean nothing, because they change on every sync. Dataverse gives every CI a new, permanent number on first load (section 3), so you don't need an old-to-new mapping. Previous Master's `HW-<type>-<last 5 of serial>` style can be kept as a separate **Legacy CI number** column if people know assets by it.

---

## 3. Data model

### 3.1 Reference tables

Create these first. Each one replaces a lookup table in the workbook.

| Table | Columns | Replaces | Seed from |
|---|---|---|---|
| **Device Type** | Name (standard type), Abbreviation (3 letters), Refresh years (whole number) | Standard types in `Typetable` + `tbl_Refresh_Rates` | `Calculations` cols F–H and `Pivot_Worker` `tbl_Refresh_Rates` |
| **Device Type Alias** | Raw value (text, alternate key), Device Type (lookup) | Raw → standard mapping in `Typetable` | `Calculations` cols E and G |
| **Manufacturer** | Name | Standard names in `manufacturetable` | `Calculations` col K (distinct) |
| **Manufacturer Alias** | Raw value (text, alternate key), Manufacturer (lookup) | `manufacturetable` | `Calculations` cols J–K |
| **Location** | Site, Building, Name = "Site, Bldg N" | Free-text Site / Building | Built during cleanup (section 7) |
| **Property Account** | Code, Description, Account owner (user) | Free-text Property Account | Distinct valid codes from Asset Master |
| **Project** | Name, Description | Free-text Project ID | The project names behind the workbook's project filter buttons, plus values in the Registries table |

Give each Device Type a real abbreviation. Some types map to `?` today, which produces CI numbers like `HW-?-7…`.

### 3.2 Configuration Item table

One row per asset. Columns are listed in the workbook's order. **Owner** says who sets the value:

- **Dataflow:** loaded from sources on every refresh. Don't edit by hand; edits are overwritten.
- **Manual:** typed by people, and never touched by the Dataflow.
- **Formula:** calculated.

| Workbook column | Dataverse column | Type | Owner | Notes |
|---|---|---|---|---|
| CI No. | **CI number** | Autonumber `HW-{SEQNUM:6}` | System | Permanent; never regenerated. Add **Legacy CI number** (text) if needed |
| — | **Name** (primary) | Text | Dataflow | Device name if there is one, otherwise the serial number |
| — | **Match key** | Text, **alternate key** | Dataflow | Serial number with spaces removed, upper case. For virtual machines (type VM or serial "virtual"), the device name. Same rule as the macro |
| Asset ID | Asset ID | Text | Dataflow | |
| Device Name | Device name | Text | Dataflow | |
| Serial Number | Serial number | Text | Dataflow | |
| Type | Device type | Lookup › Device Type | Dataflow | Through Device Type Alias |
| Manufacturer | Manufacturer | Lookup › Manufacturer | Dataflow | Through Manufacturer Alias |
| Model | Model | Text | Dataflow | |
| Part No | Part number | Text | Dataflow | |
| Site, Building | Location | Lookup › Location | Dataflow | Through the location mapping in section 7 |
| Room | Room | Text | Dataflow | |
| Rack | Rack | Text | Dataflow | |
| Position / Elevation | Rack position | Text | Manual | Empty in every row today |
| Property Account | property account | Lookup › Property Account | Dataflow | Some rows hold a location instead of an account (section 7) |
| Mfr Yr | Manufacture year | Whole number | Dataflow | |
| Date Acquired | Date acquired | Date only | Dataflow | |
| Cage | CAGE code | Text | Dataflow | |
| CLIN | CLIN | Text | Manual | |
| Contract No | Contract (source) / Contract (override) / **Contract** | Text, text, formula | Dataflow / Manual / Formula | `Coalesce(override, source)`. See 3.3 |
| Wty Exp | Warranty end (source) / (override) / **Warranty end** | Date, date, formula | Dataflow / Manual / Formula | See 3.3 |
| Wty Remaining | Warranty days left | Formula, whole number | Formula | `DateDiff(UTCToday(), 'Warranty end')`. Blank if no date |
| Asset Age | Asset age (years) | Formula, whole number | Formula | `Year(UTCToday()) - 'Manufacture year'` |
| Acq Cost | Acquisition cost | Currency | Dataflow | Blank for virtual machines (the macro writes "N/A") |
| Est Renewal Cost | Estimated renewal cost | Formula, currency | Formula | `'Acquisition cost' * 1.1` |
| Funding Code | Funding code | Text | Dataflow | |
| IP Address | IP address | Text | Dataflow | |
| MAC Address | MAC address | Text | Dataflow | |
| Last Inventory | Last inventory | Date only | Dataflow | |
| Inv Status | Inventory status | Formula, text | Formula | Green 0–335 days, amber 336–365, red otherwise or blank. Same thresholds as the macro |
| EOL / Refresh | Refresh years | Formula, whole number | Formula | From the Device Type lookup |
| — | Refresh year | Formula, whole number | Formula | `'Manufacture year' + 'Refresh years'` |
| Refresh Status | Refresh status | Formula, text | Formula | Due (age ≥ refresh years), OK, or Unknown (no year or no refresh years) |
| End of Life | End of life (source) / (override) / **End of life** | Date ×2, formula | Dataflow / Manual / Formula | See 3.3 |
| End of Support | End of support (source) / (override) / **End of support** | Date ×2, formula | Dataflow / Manual / Formula | See 3.3 |
| Operational Status | Operational status | Choice | Manual | Ordered, Received, In Build, In Stock, In Use, and the rest of the list on `Pivot_Worker` |
| Classification System | Classification system | Choice or text | Manual | |
| Project ID | Project | Lookup › Project | Manual, defaulted by Dataflow | Dataflow sets it on first load only, from the source file name (the sync macro's rule) |
| — | Directorate | Text | Manual | Only in the Registries table today |
| Last User | Last user | Text | Dataflow | Already cleaned by the query |
| — | Seen in sources | Multi-select choice | Dataflow | Sources A–F (section 4) |
| — | Last seen in sources | Date only | Dataflow | Set to today on every refresh. Drives the missing check in section 9 |
| Active Status (registry) | Record status | Choice | Flow / Manual | Active, Missing from sources, Retired |

Turn on **auditing** for this table, with every Manual column audited.

**If formula columns can't use `UTCToday()` in your environment,** keep the date columns and build the views on them instead: *Last inventory › Older than X days*, *Warranty end › Next X days* and so on. The traffic-light columns are for display; views and reports work without them.

### 3.3 Why some columns are split into source and override

In the workbook, the Registries table overrides values that also come from sources, such as warranty end, End of Life, End of Support and contract. If the Dataflow wrote straight into one column, every refresh would wipe people's corrections.

So each of these has three columns:

- **(source):** written by the Dataflow.
- **(override):** typed by people.
- **The plain column:** a formula, `Coalesce('… (override)', '… (source)')`. Forms, views and reports use only this one.

### 3.4 Decommission Log table

| Column | Type |
|---|---|
| Configuration item | Lookup › Configuration Item |
| Date of action | Date only |
| Action | Choice: Removed from sources, Disposed, Transferred, Returned to vendor |
| From / To | Text |
| Reason | Text |
| Remarks / ticket number | Text |
| Change request | Text, or a lookup once the portal is linked |

---

## 4. Move the source files to SharePoint

The queries read from a folder in one person's synced OneDrive (`Folder.Files("C:\Users\…\OneDrive - …\CMDB Sources\…")`). A Dataflow can't read a local path.

1. Confirm that the **CMDB Sources** folder sits in your team's SharePoint library. Your sync path suggests it does.
2. Keep the six source sub-folders and their names as they are. The workbook's queries reference them by name.

   In the rest of this plan, **Sources A–F** mean these six folders in the order the merge query (`Asset_Master_Table`) joins them. **Source F** is the hand-made sheets.
3. Restrict the library to the CM team. These are the raw CUI exports.
4. Write down the site URL (for example `https://<your-sharepoint-host>/sites/<site>`). The Dataflow needs it.

---

## 5. Build the Dataflow

Create it in **CMDB Dev** › **Dataflows** › **New dataflow**, named **CMDB – Source merge**.

### 5.1 Port the queries

The M code moves across almost unchanged. For each of the six source queries:

1. Paste the query from the workbook (**Data › Queries & Connections**, right-click › **Advanced editor**).
2. Replace the `Folder.Files("C:\…\<folder>")` line with:
   ```
   Source = Table.SelectRows(
       SharePoint.Files("https://<your-sharepoint-host>/sites/<site>", [ApiVersion = 15]),
       each Text.Contains([Folder Path], "/CMDB Sources/<folder>/")
   ),
   ```
3. One source query reads a single named workbook instead of a folder. Filter on `[Name] = "<that file name>"` and use `Excel.Workbook([Content], null, true)`.
4. Bring across the **Sample File / Transform File** helpers that each folder query uses, or rebuild them with **Combine files** in the Dataflow editor.

### 5.2 Fix the duplicates before the merge

The merge query (`Asset_Master_Table`) joins all six sources on Serial Number. If a source has the same serial twice, the join repeats the row. That's where the duplicate rows in Asset Master come from. Two sources repeat serials: Source D and the hand-made sheets (Source F).

In those two source queries, add these steps at the end:

1. Trim and upper-case **Serial Number**.
2. Sort by **Source.Name** descending (newest file first), or by **Last Inventory** descending for Source F.
3. **Remove duplicates** on Serial Number.

Do the same in the merge query on the distinct serial list, after trimming and upper-casing. The workbook's `Table.Distinct` treats `abc123` and `ABC123` as different.

### 5.3 Keep the priority rules

The `Master_…` custom columns in `Asset_Master_Table` decide which source wins for each field. For example, building comes from Source A, then B, then C, and so on down to F. Keep them as they are. They're the business rules.

Then add these steps:

1. **Match key:** `if [Master_Type] = "Virtual Machine" or Text.Lower([Serial Number]) = "virtual" then [Master_Device Name] else Text.Upper(Text.Remove([Serial Number], " "))`.
2. **Type and manufacturer:** merge with **Device Type Alias** and **Manufacturer Alias**, read from Dataverse with the **Dataverse** connector. The output is the alias row's ID or name, for the lookup columns.
3. **Location:** merge with the location mapping (section 7).
4. **Seen in sources:** a list of which `P1…P6` joins matched.
5. **Last seen in sources:** `DateTime.Date(DateTime.LocalNow())`.
6. **Project default:** the sync macro's rule that sets the project from the source file name. Keep `Source.Name` through the merge this time.
7. Replace the `"-"` and `"null"` placeholders with real nulls. Dataverse stores blanks properly, and `"-"` would break the date and number columns.
8. Drop the empty placeholder columns the query adds (`Wty Remaining`, `Asset Age`, `Inv Status`, `EOL / Refresh`, `Refresh Status`, `End of Life`, `End of Support`, `Operational Status`, `Classification System`, `Project ID`, `Est Renewal Cost`). Dataverse calculates or stores those itself.

### 5.4 Map to the Configuration Item table

1. **Load to existing table** › Configuration Item.
2. **Key:** Match key.
3. Map only the columns marked **Dataflow** in section 3.2. Leave every Manual and override column **unmapped**.
4. **Leave "Delete rows that no longer exist in the query output" off.** It would hard-delete assets that drop out of a source. The flow in section 9 handles missing assets instead.
5. **Refresh schedule:** daily, early morning, plus on demand after new files are dropped in.

---

## 6. First load

Run this in **Dev** first, then again in **Prod** at cutover.

1. Load the reference tables (3.1) with **Import from Excel** or a small Dataflow.
2. Run **CMDB – Source merge** once. Check that the row count equals the number of distinct serials, which is lower than Asset Master's row count because duplicates are gone.
3. **Import the overrides.** Export the Registries table (`tbl_Warranty_Registry`) to CSV. Import it into Configuration Item, keyed on **Match key** (serial number, or device name for VMs), mapping:

   | Registry column | Dataverse column |
   |---|---|
   | Warranty End Date | Warranty end (override). Skip `UNVERIFIED` and `EXPIRED`; leave those blank |
   | End of Life | End of life (override) |
   | End of Support | End of support (override) |
   | Operational Status | Operational status |
   | Classification System | Classification system |
   | Project ID | Project |
   | Directorate | Directorate |
   | CLIN | CLIN |
   | Contract No | Contract (override) |

   Rows that don't match any CI go to a reject file. Review them: they're the real "missing from scan" candidates.
4. Import `tbl_Decommission_Log` into the Decommission Log table. Rows with a placeholder serial such as `XXXXXXXXXXXX` need someone to look them up or drop them.
5. Set **Record status = Active** on every loaded CI.

---

## 7. Data cleanup

Run this alongside sections 5–6. Do it in Power Query (the Dataflow) or as mapping tables, **not** by editing the Excel sources. Fixes in the sources are lost when the next export arrives.

| # | Problem | Size | Fix | Owner |
|---|---|---|---|---|
| 1 | Duplicate serials from Sources D and F | Several hundred extra rows | Dedupe step in 5.2 | Builder |
| 2 | **Building** mixes numbers, "BLDG", base names and full addresses | Over a hundred distinct values | Build a **Location mapping** sheet: raw Site + Building → Location. Load it as a Dataflow source | CM lead |
| 3 | **Site** blank | A large share of rows | Usually follows from Building through the mapping. The rest are manual | CM lead |
| 4 | **Property account** holds a location | Several hundred rows | A fallback in the merge query's account column puts a location there. Move it to Location and leave the account blank | CM lead + property custodians |
| 5 | **Property account** blank | Several hundred rows | Data-quality view (section 8). Fix at source over time | Account owners |
| 6 | **Type = Unknown** | A few hundred rows | Add the missing raw values to Device Type Alias | CM lead |
| 7 | Types with abbreviation `?` | A few dozen CIs | Give each Device Type a real abbreviation | CM lead |
| 8 | Manufacturer variants | Dozens of standard names | Already mapped by `manufacturetable`. Add new raw values as they appear | Builder |
| 9 | Placeholders `-`, `null`, `N/A`, `UNVERIFIED` | Every column | Convert to blanks in the Dataflow (5.3 step 7) | Builder |
| 10 | Rack position, CLIN | 100% blank | Leave as Manual columns, filled as people work | — |

---

## 8. Model-driven app

Create a model-driven app called **CMDB** in the solution, or add a CMDB area to an existing app.

### 8.1 Menu

- **CMDB:** Configuration Items, Locations, Projects, Property Accounts
- **Lifecycle:** Decommission Log
- **Settings:** Device Types, Device Type Aliases, Manufacturers, Manufacturer Aliases

### 8.2 Views

These replace the filter buttons.

| View | Filter | Replaces macro |
|---|---|---|
| Active config items | Record status = Active | — |
| Project: *name* (one view per project) | Project = *name* | The nine `Show<project>` filter macros |
| Expired warranties | Warranty end › On or before today | `ShowExpiredWarranties` |
| Inventory due within 90 days | Last inventory › Older than 275 days, or blank | `ShowInventoryDue` and `ShowInventoryDue90Days` (both use the same 275-day cut-off) |
| Inventory overdue *(new)* | Last inventory › Older than 365 days, or blank | — |
| Refresh due | Refresh status = Due (the red light, value 1, in the workbook) | `ShowRefreshDue` |
| Refresh in next 180 days | Refresh year = this year (or next year from July) | `ShowRefreshUpcoming_PureVBA` |
| Missing from sources | Record status = Missing from sources | Registry *Missing from Scan* |
| Data quality: no property account | property account is blank | Health audit rule B |
| Data quality: no location | Location is blank | Health audit rule C |
| Data quality: no serial | Serial blank and type ≠ VM | Health audit rule A |

The "Refresh in next 180 days" macro treats 31 December of the refresh year as the refresh date. A view can't do that date maths, so either filter on Refresh year as shown, or add a formula column **Refresh date** = `Date('Refresh year', 12, 31)` and filter it with *Next 180 days*.

### 8.3 Forms

**Configuration Item main form:**

- **Header:** CI number, Device type, Record status, Operational status.
- **General tab:** identification (Name, Asset ID, Serial, Manufacturer, Model, Part number) and location (Location, Room, Rack, Rack position).
- **Lifecycle tab:** Manufacture year, Date acquired, Asset age, Refresh years, Refresh status, Warranty end, Warranty days left, End of life, End of support, plus the override columns in their own section labelled **Overrides**.
- **Finance tab:** property account, Acquisition cost, Estimated renewal cost, Funding code, Contract, CLIN, CAGE code.
- **Network tab:** IP, MAC, Last user.
- **Sources tab:** Seen in sources, Last seen in sources, Match key. Make these read-only.
- **Related:** Decommission Log, and later CI Relationships (section 11) and Change Affected CIs.

Make every Dataflow-owned column **read-only** on the form, so nobody edits a value the next refresh would overwrite.

### 8.4 Batch search

This replaces `BatchFilterMasterSerialNumbers` and `FilterRegistryByBatch`.

Add a **custom page** called **Batch search**: a multi-line text box where people paste serial numbers, and a gallery of matching CIs. Search with:
```
Filter('Configuration Items', 'Match key' in Split(Upper(Substitute(txtSerials.Text, " ", "")), Char(10)))
```
Then add an **Export** button that runs a flow to write the results to Excel.

Since the registry is now part of the CI record, one search covers both old buttons.

---

## 9. Flows

| Flow | Trigger | What it does | Replaces |
|---|---|---|---|
| **CMDB – Mark missing assets** | Daily, after the Dataflow refresh | Finds Active CIs whose *Last seen in sources* is more than 7 days old, sets Record status = Missing from sources, and emails the CM team a list | Sync's "Missing from Scan" reconciliation |
| **CMDB – Retire asset** | Button on the CI form (instant flow, or a command bar button) | Sets Record status = Retired and adds a Decommission Log row with today's date. Action, reason and remarks are prompted | `ArchiveDecommissionedAssets` |
| **CMDB – Monthly health audit** | Monthly | For each property account, lists CIs failing the health rules, then emails the account owner an Excel file or Power BI link | `GenerateCMDBHealthAudit` |

**Health rules,** taken from `GenerateCMDBHealthAudit`:

- A: serial missing, ignoring VMs
- B: property account missing
- C: location missing
- D: last inventory more than 30 days old

Rule D uses 30 days in the audit but 335/365 days everywhere else. Confirm which one is meant before rebuilding it.

Don't auto-retire missing assets. A file left out of one week's export would retire real equipment. People retire assets; the flow only flags them.

---

## 10. Reports and dashboards

Build these in **Power BI**, connected to the Dataverse tables, and published to the CM workspace in the same cloud. Embed them in the app.

| Report | Contents | Replaces |
|---|---|---|
| **CMDB overview** | Totals: total assets, portfolio value, expired warranties, due for refresh. Charts: assets by type, cost by type, assets per property account, operational status. Slicers: project, location | `Dashboard` and `Pivot_Worker` |
| **Executive refresh report** (paginated, one page per property account) | Header: account, asset count, total estimated renewal. Grid: the 12 fields in `ExportFilteredToExecutiveReport`, sorted by Asset ID | `ExportFilteredToExecutiveReport` |
| **Health audit** | The section 9 rules by account, with drill-through to CIs | `GenerateCMDBHealthAudit` (on-screen version) |
| **VM dependency** | Built after section 11 | `VM Dashboard` |

The Executive refresh report recalculates *EOL / Refresh* as manufacture year + refresh years. In Dataverse that's the **Refresh year** column, so the report reads it directly.

If Power BI isn't available, model-driven dashboards (charts on views) cover the overview. For the per-account report, use an Excel template from **Excel templates** on the view.

---

## 11. Relationships (phase 2)

Every virtual machine shows as *Orphaned VM* in the workbook, so there are no dependencies to migrate. Add relationships after cutover:

1. Create **Relationship Type** (Name, Reverse name) and **CI Relationship** (Parent CI, Child CI, Type) tables, as in the earlier CMDB design.
2. Seed the types: *Runs on / Hosts*, *Depends on / Used by*, *Connected to*.
3. Load *VM runs on host* pairs from the hypervisor inventory. Add it as a seventh Dataflow source if it can be exported regularly.
4. Add **Change Affected CI** to link the change request portal to CIs.
5. Rebuild the VM dependency view in Power BI.

---

## 12. Parallel run and cutover

1. **Import the solution** into **CMDB Prod** as managed. Recreate the connections and the Dataflow schedule.
2. **First load in Prod** (section 6), using a fresh export of the Registries table.
3. **Run both for two weeks.** Keep the workbook for reference only; make every manual edit in Dataverse.
4. **Reconcile weekly.** These numbers should match between Excel and Dataverse:
   - Asset count per device type. Dataverse will be lower because of the dedupe; check the difference is only duplicates.
   - Asset count per property account.
   - Total acquisition cost (**Portfolio Value** on `Pivot_Worker`).
   - Expired warranty count. Expect Dataverse to be **much higher**, because the workbook never applied the registry dates (bug B).
5. **Cut over.** Remove the macro buttons, protect every sheet, and save the workbook as `…_ARCHIVE_<date>.xlsx` without macros. Store it with the CUI marking in the restricted library.
6. Update [TODO.md](../TODO.md) and the portal guides once the Change Affected CI link is added.

---

## 13. Macro-by-macro mapping

| Module | Procedure | Lines | Becomes | Section |
|---|---|---|---|---|
| SYNC | `DuplicateTableAndStandardize` | 845 | Dataflow (merge, standardise), autonumber, formula columns, overrides | 3, 5 |
| REFRESHSOURCEDATA | `RefreshAllSourceData` | 31 | Scheduled Dataflow refresh | 5.4 |
| arciveretiredassets | `ArchiveDecommissionedAssets` | 82 | Mark-missing flow, Retire flow, Decommission Log | 9 |
| Module1 | `GenerateCMDBHealthAudit` | 380 | Data-quality views, monthly flow, Power BI | 8.2, 9, 10 |
| REFRESHREPORT | `ExportFilteredToExecutiveReport` | 391 | Power BI paginated report | 10 |
| BatchFilter | `BatchFilterMasterSerialNumbers` | 66 | Batch search page | 8.4 |
| filterregistry | `FilterRegistryByBatch` | 71 | Batch search page | 8.4 |
| Nine project modules | `Show<project>` | ~27 each | Project views | 8.2 |
| warrantydue | `ShowExpiredWarranties` | 23 | View | 8.2 |
| inventorydue | `ShowInventoryDue` | 33 | View | 8.2 |
| INVDAYSWINIETY | `ShowInventoryDue90Days` | 37 | View | 8.2 |
| Refreshdue | `ShowRefreshDue` | 24 | View | 8.2 |
| refresh180d | `ShowRefreshUpcoming_PureVBA` | 92 | View | 8.2 |
| Activtylog | `Workbook_Open`, `Workbook_BeforeSave`, `LogActivity` | 19 | Dataverse auditing | 3.2 |

The formatting code in these macros (fonts, number formats, traffic-light icons, column widths) isn't migrated. Forms, views and Power BI handle display.

---

## 14. Timeline

| Week | Work | Done when |
|---|---|---|
| 0 | Section 1 checks; fix or freeze the workbook (2) | Tenant and licences confirmed; workbook stable |
| 1 | Reference tables and Configuration Item table (3); move sources to SharePoint (4) | Tables in the Dev solution |
| 2 | Dataflow port, dedupe, mapping (5) | Dataflow loads one CI per distinct serial with no errors |
| 2–3 | First load and override import (6); cleanup mappings (7) begin | Overrides visible on CIs; reject list reviewed |
| 3–4 | App: views, forms, batch search (8); flows (9) | Every old filter button has a view; Retire and Mark missing tested |
| 4–5 | Power BI reports (10) | Overview and executive report match the workbook, apart from known fixes |
| 5–7 | Cleanup continues; Prod import and first load; parallel run (12) | Two weekly reconciliations clean |
| 7 | Cutover | Workbook archived read-only |
| Later | Relationships and the change portal link (11) | — |

---

## 15. Risks

| Risk | Effect | Mitigation |
|---|---|---|
| A feature isn't available in your government cloud (Dataflows, formula columns, paginated reports) | Redesign of that piece | Check in week 0. Fallbacks: scheduled flows instead of Dataflows, date views instead of formula columns, Excel templates instead of paginated reports |
| Licensing not approved | Project stops | Section 1, check 2 |
| A source export changes its columns | Dataflow refresh fails | Dataflow refresh failure emails to the CM team; keep column names in the source templates fixed |
| Location and property account decisions drag on | Cleanup overruns | Name owners in week 0. Go live with blanks and data-quality views rather than wait |
| People edit Dataflow-owned columns | Edits lost on next refresh | Those columns are read-only on the form; overrides have their own columns |
| A missing source file flags hundreds of assets as missing | Noise, or wrong retirements | 7-day grace period; flow only flags; retiring is manual |
