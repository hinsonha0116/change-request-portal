param([Parameter(Mandatory)][string] $OutFile)
$ErrorActionPreference = 'Stop'

# ---------- object store ----------
$objs   = New-Object 'System.Collections.Generic.List[string]'
$fields = New-Object 'System.Collections.Generic.List[int]'
$pages  = New-Object 'System.Collections.Generic.List[object]'

function New-Obj([string]$body) { $objs.Add($body); return $objs.Count }
function Set-Obj([int]$n, [string]$body) { $objs[$n - 1] = $body }
function Esc([string]$s) { $s.Replace('\', '\\').Replace('(', '\(').Replace(')', '\)') }
function Stream([string]$dict, [string]$data) { "<< $dict /Length $($data.Length) >>`nstream`n$data`nendstream" }

$null = New-Obj ''   # 1 catalog
$null = New-Obj ''   # 2 pages
$null = New-Obj ''   # 3 acroform
$F1 = New-Obj '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>'
$F2 = New-Obj '<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>'
$F3 = New-Obj '<< /Type /Font /Subtype /Type1 /BaseFont /ZapfDingbats >>'
$cbOn  = New-Obj (Stream "/Type /XObject /Subtype /Form /BBox [0 0 11 11] /Resources << /Font << /ZaDb $F3 0 R >> >>" 'q 0 g BT /ZaDb 9 Tf 1.6 2 Td (4) Tj ET Q')
$cbOff = New-Obj (Stream '/Type /XObject /Subtype /Form /BBox [0 0 11 11]' '')

# ---------- drawing helpers ----------
function New-Page {
    $script:cs = New-Object System.Text.StringBuilder
    $script:annots = New-Object 'System.Collections.Generic.List[int]'
    $pages.Add(@{ Cs = $script:cs; Annots = $script:annots })
}
function Add([string]$s) { [void]$script:cs.Append($s + "`n") }

function Text {
    param($X, $Y, $Size = 9, [string]$S, [switch]$Bold, [string]$Color = '0 g')
    $f = if ($Bold) { 'F2' } else { 'F1' }
    Add "BT /$f $Size Tf $Color $X $Y Td ($(Esc $S)) Tj ET"
}
function Box {
    param($X, $Y, $W, $H, [string]$Fill)   # $Y = bottom edge
    if ($Fill) { Add "$Fill $X $Y $W $H re f" }
    Add "0.55 G 0.75 w $X $Y $W $H re S"
}
function Section {
    param($Top, [string]$Title)
    Add "0.12 0.23 0.42 rg 50 $($Top - 16) 512 16 re f"
    Text -X 56 -Y ($Top - 11.5) -Size 9.5 -Bold -S $Title -Color '1 g'
}
function Hint { param($Y, [string]$S) Text -X 50 -Y $Y -Size 7.5 -S $S -Color '0.35 g' }

function Widget {
    param([string]$Name, [string]$Tip, $X1, $Y1, $X2, $Y2, [switch]$Multi, [switch]$Sig)
    $rect = "[$X1 $Y1 $X2 $Y2]"
    $tu = Esc $Tip
    if ($Sig) {
        $d = "<< /Type /Annot /Subtype /Widget /FT /Sig /T ($Name) /TU ($tu) /Rect $rect /F 4 >>"
    } else {
        $ff = if ($Multi) { ' /Ff 4096' } else { '' }
        $d = "<< /Type /Annot /Subtype /Widget /FT /Tx /T ($Name) /TU ($tu) /Rect $rect /F 4 /DA (/Helv 9 Tf 0 g)$ff /MK << >> >>"
    }
    $n = New-Obj $d
    $script:annots.Add($n); $fields.Add($n)
}
function Field {
    param([string]$Name, [string]$Label, $X, $Top, $W, $H = 20, [switch]$Multi, [switch]$Sig)
    $boxTop = $Top
    if ($Label) { Text -X $X -Y ($Top - 7) -Size 7.5 -Bold -S $Label -Color '0.2 g'; $boxTop = $Top - 10 }
    $y = $boxTop - $H
    Box -X $X -Y $y -W $W -H $H -Fill '0.95 0.96 0.99 rg'
    Widget -Name $Name -Tip $Label -X1 ($X + 1) -Y1 ($y + 1) -X2 ($X + $W - 1) -Y2 ($boxTop - 1) -Multi:$Multi -Sig:$Sig
}
function Check {
    param([string]$Name, $X, $Y, [string]$Label)
    Box -X $X -Y $Y -W 11 -H 11 -Fill '1 g'
    Text -X ($X + 17) -Y ($Y + 2) -Size 8.5 -S $Label
    $d = "<< /Type /Annot /Subtype /Widget /FT /Btn /T ($Name) /TU ($(Esc $Label)) /Rect [$X $Y $($X + 11) $($Y + 11)] /F 4 /V /Off /AS /Off /MK << /CA (4) >> /DA (/ZaDb 0 Tf 0 g) /AP << /N << /Yes $cbOn 0 R /Off $cbOff 0 R >> >> >>"
    $n = New-Obj $d
    $script:annots.Add($n); $fields.Add($n)
}
function Footer([int]$p) {
    Add '0.7 G 0.5 w 50 40 m 562 40 l S'
    Text -X 50 -Y 28 -Size 7.5 -S 'Form CR-RB-01  |  Rollback Plan  |  Attach to Change Request' -Color '0.4 g'
    Text -X 520 -Y 28 -Size 7.5 -S "Page $p of 2" -Color '0.4 g'
}

# ================= PAGE 1 =================
New-Page
Text -X 50 -Y 752 -Size 20 -Bold -S 'ROLLBACK PLAN' -Color '0.12 0.23 0.42 rg'
Text -X 50 -Y 736 -Size 9 -S 'Required attachment for change requests submitted through the Change Request Portal' -Color '0.3 g'
Add '0.12 0.23 0.42 RG 1.5 w 50 726 m 562 726 l S'
Hint 712 'Complete every section, save the PDF, then upload it to the "Rollback Plan" question on the Change Request form.'

Section 698 '1. CHANGE INFORMATION'
Field -Name 'CRNumber'      -Label 'CR Number (if assigned)' -X 50  -Top 674 -W 150
Field -Name 'ChangeTitle'   -Label 'Change Title'            -X 210 -Top 674 -W 352
Field -Name 'A6Program'     -Label 'A6 Program'              -X 50  -Top 636 -W 200
Field -Name 'RequestedBy'   -Label 'Requested By'            -X 260 -Top 636 -W 200
Field -Name 'DSN'           -Label 'DSN'                     -X 470 -Top 636 -W 92
Field -Name 'Email'         -Label 'E-mail'                  -X 50  -Top 598 -W 250
Field -Name 'PlannedDate'   -Label 'Planned Change Date'     -X 310 -Top 598 -W 120
Field -Name 'DatePrepared'  -Label 'Date Prepared'           -X 440 -Top 598 -W 122

Section 552 '2. ROLLBACK TRIGGERS'
Hint 526 'Conditions that will cause this change to be rolled back (e.g., service outage, failed validation, error thresholds).'
Field -Name 'RollbackTriggers' -X 50 -Top 520 -W 512 -H 72 -Multi

Section 434 '3. ROLLBACK DECISION AND TIMING'
Field -Name 'DecisionAuthority'    -Label 'Rollback Decision Authority (Name / Rank / Position)' -X 50  -Top 410 -W 340
Field -Name 'DecisionAuthorityDSN' -Label 'Decision Authority DSN'                               -X 400 -Top 410 -W 162
Field -Name 'PointOfNoReturn'      -Label 'Point of No Return (date / time)'                     -X 50  -Top 372 -W 164
Field -Name 'RollbackDuration'     -Label 'Estimated Rollback Duration'                          -X 224 -Top 372 -W 164
Field -Name 'MaxOutage'            -Label 'Maximum Acceptable Outage'                            -X 398 -Top 372 -W 164

Section 326 '4. PRE-CHANGE PREPARATION'
Check -Name 'ChkConfigBackup' -X 56  -Y 290 -Label 'Configuration backup taken'
Check -Name 'ChkTested'       -X 306 -Y 290 -Label 'Rollback procedure tested (lab / test environment)'
Check -Name 'ChkSnapshot'     -X 56  -Y 272 -Label 'System snapshot / image captured'
Check -Name 'ChkMedia'        -X 306 -Y 272 -Label 'Rollback media / software available on site'
Check -Name 'ChkBaseline'     -X 56  -Y 254 -Label 'Baseline performance recorded'
Check -Name 'ChkNotified'     -X 306 -Y 254 -Label 'Stakeholders notified of rollback window'
Field -Name 'BackupDetails' -Label 'Backup / snapshot location and details' -X 50 -Top 238 -W 512 -H 70 -Multi
Field -Name 'Dependencies'  -Label 'Dependent systems / services affected by a rollback' -X 50 -Top 146 -W 512 -H 60 -Multi
Footer 1

# ================= PAGE 2 =================
New-Page
Text -X 50 -Y 752 -Size 12 -Bold -S 'ROLLBACK PLAN (continued)' -Color '0.12 0.23 0.42 rg'
Add '0.12 0.23 0.42 RG 1.5 w 50 744 m 562 744 l S'

Section 730 '5. ROLLBACK PROCEDURE'
Add '0.86 0.89 0.95 rg 50 698 512 16 re f'
Add '0.55 G 0.75 w 50 698 512 16 re S'
Text -X 54  -Y 703 -Size 8 -Bold -S 'Step'
Text -X 84  -Y 703 -Size 8 -Bold -S 'Action / Command'
Text -X 366 -Y 703 -Size 8 -Bold -S 'Responsible'
Text -X 476 -Y 703 -Size 8 -Bold -S 'Est. Time'
for ($i = 1; $i -le 10; $i++) {
    $top = 698 - ($i - 1) * 22; $bot = $top - 22
    Box -X 50  -Y $bot -W 30  -H 22
    Box -X 80  -Y $bot -W 282 -H 22 -Fill '0.95 0.96 0.99 rg'
    Box -X 362 -Y $bot -W 110 -H 22 -Fill '0.95 0.96 0.99 rg'
    Box -X 472 -Y $bot -W 90  -H 22 -Fill '0.95 0.96 0.99 rg'
    $nx = if ($i -lt 10) { 62 } else { 59 }
    Text -X $nx -Y ($bot + 7) -Size 9 -Bold -S "$i"
    Widget -Name "Step$($i)_Action"      -Tip "Step $i action"      -X1 81  -Y1 ($bot + 1) -X2 361 -Y2 ($top - 1)
    Widget -Name "Step$($i)_Responsible" -Tip "Step $i responsible" -X1 363 -Y1 ($bot + 1) -X2 471 -Y2 ($top - 1)
    Widget -Name "Step$($i)_Time"        -Tip "Step $i est. time"   -X1 473 -Y1 ($bot + 1) -X2 561 -Y2 ($top - 1)
}

Section 462 '6. POST-ROLLBACK VERIFICATION'
Hint 436 'How you will confirm the system has been restored to its pre-change state (tests, checks, monitoring).'
Field -Name 'Verification' -X 50 -Top 430 -W 512 -H 64 -Multi

Section 352 '7. COMMUNICATION PLAN'
Hint 326 'Who will be notified if a rollback occurs, and how (e-mail, phone/DSN, Teams, NOTAM / outage notice).'
Field -Name 'Communication' -X 50 -Top 320 -W 512 -H 54 -Multi

Section 252 '8. SIGNATURES'
Field -Name 'PreparedBy'     -Label 'Prepared By (Name / Rank)'          -X 50  -Top 228 -W 220 -H 24
Field -Name 'PreparedBySig'  -Label 'Signature'                           -X 280 -Top 228 -W 200 -H 24 -Sig
Field -Name 'PreparedDate'   -Label 'Date'                                -X 490 -Top 228 -W 72  -H 24
Field -Name 'ReviewedBy'     -Label 'Reviewed By - Change Manager (Name / Rank)' -X 50 -Top 182 -W 220 -H 24
Field -Name 'ReviewedBySig'  -Label 'Signature'                           -X 280 -Top 182 -W 200 -H 24 -Sig
Field -Name 'ReviewedDate'   -Label 'Date'                                -X 490 -Top 182 -W 72  -H 24
Field -Name 'ApprovedBy'     -Label 'Approved By - Change Authority (Name / Rank)' -X 50 -Top 136 -W 220 -H 24
Field -Name 'ApprovedBySig'  -Label 'Signature'                           -X 280 -Top 136 -W 200 -H 24 -Sig
Field -Name 'ApprovedDate'   -Label 'Date'                                -X 490 -Top 136 -W 72  -H 24
Footer 2

# ---------- assemble ----------
$kids = @()
foreach ($p in $pages) {
    $data = $p.Cs.ToString()
    $c = New-Obj (Stream '' $data)
    $annRefs = ($p.Annots | ForEach-Object { "$_ 0 R" }) -join ' '
    $kids += New-Obj "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 $F1 0 R /F2 $F2 0 R >> >> /Contents $c 0 R /Annots [$annRefs] >>"
}
$info = New-Obj '<< /Title (Rollback Plan - Change Request) /Subject (Form CR-RB-01) /Creator (Change Request Portal) >>'
Set-Obj 1 '<< /Type /Catalog /Pages 2 0 R /AcroForm 3 0 R /ViewerPreferences << /DisplayDocTitle true >> >>'
Set-Obj 2 "<< /Type /Pages /Kids [$(($kids | ForEach-Object { "$_ 0 R" }) -join ' ')] /Count $($kids.Count) >>"
Set-Obj 3 "<< /Fields [$(($fields | ForEach-Object { "$_ 0 R" }) -join ' ')] /NeedAppearances true /DR << /Font << /Helv $F1 0 R /ZaDb $F3 0 R >> >> /DA (/Helv 9 Tf 0 g) >>"

$sb = New-Object System.Text.StringBuilder
[void]$sb.Append("%PDF-1.7`n")
$offsets = New-Object 'System.Collections.Generic.List[int]'
for ($i = 0; $i -lt $objs.Count; $i++) {
    $offsets.Add($sb.Length)
    [void]$sb.Append("$($i + 1) 0 obj`n$($objs[$i])`nendobj`n")
}
$xref = $sb.Length
[void]$sb.Append("xref`n0 $($objs.Count + 1)`n0000000000 65535 f `n")
foreach ($o in $offsets) { [void]$sb.Append(('{0:D10} 00000 n ' -f $o) + "`n") }
[void]$sb.Append("trailer`n<< /Size $($objs.Count + 1) /Root 1 0 R /Info $info 0 R >>`nstartxref`n$xref`n%%EOF`n")

[System.IO.File]::WriteAllBytes($OutFile, [System.Text.Encoding]::ASCII.GetBytes($sb.ToString()))
Write-Host "Wrote $OutFile ($($fields.Count) fields)"
