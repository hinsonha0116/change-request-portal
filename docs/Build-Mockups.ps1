# Regenerates the layout diagrams used in Change-Request-PowerApp-Guide.md
#   powershell -ExecutionPolicy Bypass -File .\docs\Build-Mockups.ps1
$ErrorActionPreference = 'Stop'
$out = $PSScriptRoot
$navy = '#1E3A6B'; $tag = '#C026D3'
$stageColors = '#6B7280', '#2563EB', '#7C3AED', '#D97706', '#0891B2', '#16A34A'

function Esc([string]$s) { $s.Replace('&', '&amp;').Replace('<', '&lt;').Replace('>', '&gt;') }
function Txt($x, $y, $s, $size = 13, $fill = '#111827', $weight = 'normal', $anchor = 'start') {
    "<text x='$x' y='$y' font-size='$size' fill='$fill' font-weight='$weight' text-anchor='$anchor'>$(Esc $s)</text>"
}
function Rect($x, $y, $w, $h, $fill = 'none', $stroke = 'none', $extra = '') {
    "<rect x='$x' y='$y' width='$w' height='$h' fill='$fill' stroke='$stroke' $extra/>"
}
# Magenta name tag pointing at a control
function Tag($x, $y, $s) {
    $w = 12 + 7.2 * $s.Length
    (Rect $x $y $w 20 $tag 'none' "rx='3'") + (Txt ($x + 6) ($y + 14) $s 12 '#fff' 'bold')
}
function Frame($x, $y, $w, $h) { Rect $x $y $w $h 'none' $tag "stroke-width='2' stroke-dasharray='6 4'" }
function Svg($name, $body) {
    $svg = "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1366 768' font-family='Segoe UI, Arial, sans-serif'>`n" +
           (Rect 0 0 1366 768 '#FFFFFF' '#9CA3AF') + "`n" + ($body -join "`n") + "`n</svg>`n"
    [IO.File]::WriteAllText((Join-Path $out $name), $svg, (New-Object Text.UTF8Encoding($false)))
    Write-Host "Wrote $name"
}

# ============================== BoardScreen ==============================
$b = @()
$b += Txt 20 46 'Change Request Portal' 22 '#111827' 'bold'
$b += Rect 340 15 260 40 '#fff' '#9CA3AF'
$b += Txt 352 40 'Search by title…' 14 '#9CA3AF'
$b += Rect 630 25 44 20 '#D1D5DB' 'none' "rx='10'"
$b += "<circle cx='640' cy='35' r='8' fill='#fff'/>"
$b += Txt 684 40 'All requests' 14 '#374151'
$b += "<circle cx='855' cy='35' r='10' fill='none' stroke='#374151' stroke-width='2.5' stroke-dasharray='48 15'/>"
$b += Rect 890 15 230 40 '#fff' $navy "stroke-width='1.5' rx='4'"
$b += Txt 1005 40 'Download Rollback Plan template' 13 $navy 'normal' 'middle'
$b += Rect 1130 13 216 44 $navy 'none' "rx='4'"
$b += Txt 1238 40 '+ Request a New Change' 14 '#fff' 'bold' 'middle'
$b += "<line x1='0' y1='80' x2='1366' y2='80' stroke='$tag' stroke-dasharray='4 4'/>"

$cards = @(
    @(@('CR-00014', 'Replace core router PSU', 'P2 · Hardware · Normal', 'Risk 2 · Impact 3', 'SSgt Lee · 3 CS'),
      @('CR-00013', 'Patch VPN concentrator', 'P1 · Network · Emergency', 'Risk 1 · Impact 2', 'TSgt Diaz · 3 CS')),
    @(, @('CR-00011', 'Upgrade switch firmware', 'P3 · Network · Normal', 'Risk 3 · Impact 3', 'A1C Park · 5 CS')),
    @(, @('CR-00009', 'New SharePoint site', 'P4 · Software · Standard', 'Risk 3 · Impact 3', 'Mr. Cole · A6X')),
    @(, @('CR-00007', 'Firewall rule update', 'P2 · Network · Normal', 'Risk 2 · Impact 2', 'SrA Kim · 3 CS')),
    @(),
    @(, @('CR-00003', 'Printer driver rollout', 'P4 · Software · Standard', 'Risk 3 · Impact 3', 'Ms. Ford · A6O'))
)
$names = 'Requested', 'Change Advisory Board', 'Change Authority', 'Implementation', 'Review', 'Close'
$pcol = @{ '1' = '#DC2626'; '2' = '#EA580C'; '3' = '#CA8A04'; '4' = '#6B7280' }
$colW = 1366 / 6
for ($i = 0; $i -lt 6; $i++) {
    $x = [math]::Round(4 + $i * $colW); $w = [math]::Round($colW - 9)
    $b += Rect $x 84 $w 680 '#F3F4F6'
    $b += Rect $x 84 $w 44 $stageColors[$i]
    $label = "$($i + 1). $($names[$i])  ($($cards[$i].Count))"
    $b += Txt ($x + 8) 111 $label 13 '#fff' 'bold'
    $j = 0
    foreach ($c in $cards[$i]) {
        $y = 136 + $j * 124; $cx = $x + 4; $cw = $w - 8
        $b += Rect $cx $y $cw 116 '#fff' '#D1D5DB'
        $b += Rect $cx $y 5 116 $pcol[$c[2].Substring(1, 1)]
        $b += Txt ($cx + 12) ($y + 18) $c[0] 11 '#6B7280' 'bold'
        $b += Txt ($cx + 12) ($y + 40) $c[1] 13 '#111827' 'bold'
        $b += Txt ($cx + 12) ($y + 72) $c[2] 11 '#374151'
        $b += Txt ($cx + 12) ($y + 90) $c[3] 11 '#374151'
        $b += Txt ($cx + 12) ($y + 108) $c[4] 11 '#6B7280'
        $j++
    }
}
# name tags
$b += Tag 20 60 'lblAppTitle'
$b += Tag 340 58 'txtSearch'
$b += Tag 620 58 'tglMine'
$b += Tag 818 58 'icoRefresh'
$b += Tag 960 58 'btnTemplate'
$b += Tag 1240 58 'btnNew'
$b += Frame 2 82 1362 684
$b += Tag 1180 740 'galStages (whole area)'
$b += Frame ([math]::Round(4 + 4 * $colW)) 84 ([math]::Round($colW - 9)) 44
$b += Tag ([math]::Round(8 + 4 * $colW)) 136 'rectHeader + lblHeader'
$b += Frame 8 134 ([math]::Round($colW - 17)) 626
$b += Tag 20 500 'galCards'
$b += Frame ([math]::Round(8 + $colW)) 136 ([math]::Round($colW - 17)) 116
$b += Tag ([math]::Round(8 + $colW)) 258 'galCards template = 1 card'
$b += Tag 1080 640 'tmrRefresh: invisible, place anywhere'
Svg 'board-layout.svg' $b

# ============================== DetailScreen ==============================
$d = @()
$d += Rect 0 0 1366 60 $navy
$d += Rect 16 12 110 36 '#fff' 'none' "rx='4'"
$d += Txt 71 36 '← Board' 14 $navy 'bold' 'middle'
$d += Txt 140 38 'CR-00011 — Upgrade switch firmware' 20 '#fff' 'bold'
# progress
$pw = 1326 / 6
for ($i = 0; $i -lt 6; $i++) {
    $cx = [math]::Round(20 + $pw * $i + $pw / 2)
    $fill = if ($i -lt 2) { '#16A34A' } elseif ($i -eq 2) { $stageColors[2] } else { '#E5E7EB' }
    $num = if ($i -lt 2) { '#fff' } elseif ($i -eq 2) { '#fff' } else { '#6B7280' }
    $d += "<circle cx='$cx' cy='88' r='14' fill='$fill'/>"
    $d += Txt $cx 93 "$($i + 1)" 12 $num 'bold' 'middle'
    $wt = if ($i -eq 2) { 'bold' } else { 'normal' }
    $d += Txt $cx 128 $names[$i] 12 '#111827' $wt 'middle'
}
# form
$rows = @(
    @('A6 Program', 'A6X Cyber', 'DSN', '312-555-0142'),
    @('Requested By', 'A1C Jordan Park', 'Requester Email', 'jordan.park@us.af.mil'),
    @('Title', 'Upgrade switch firmware', 'Category', 'Network'),
    @('Change Type', 'Normal', 'Priority', '3 - Moderate'),
    @('Risk', '3 - Moderate', 'Impact', '3 - Moderate'),
    @('Attachments', 'RollbackPlan_CR-00011.pdf', 'Planned Start', '24 Oct 2026 18:00'),
    @('CAB Decision', 'Approved', 'Authority Decision', 'Pending ▾')
)
$y = 162
foreach ($r in $rows) {
    foreach ($k in 0, 1) {
        $fx = 32 + $k * 440
        $d += Txt $fx $y $r[$k * 2] 11 '#374151' 'bold'
        $editable = $r[$k * 2] -eq 'Authority Decision'
        $bg = if ($editable) { '#fff' } else { '#F9FAFB' }
        $st = if ($editable) { $navy } else { '#E5E7EB' }
        $d += Rect $fx ($y + 6) 420 32 $bg $st
        $d += Txt ($fx + 8) ($y + 27) $r[$k * 2 + 1] 13 '#111827'
    }
    $y += 64
}
$d += Frame 20 146 880 532
$d += Tag 700 146 'frmDetail (2 columns, scrolls)'
# history
$d += Txt 920 172 'History' 16 '#111827' 'bold'
$hist = @(
    @('Change Advisory Board → Change Authority', 'Maj. Reyes · 21 Oct 2026 09:12', 'Approved at CAB'),
    @('Requested → Change Advisory Board', 'Mr. Cole · 20 Oct 2026 15:40', 'Ready for CAB review'),
    @('Created', 'Flow · 20 Oct 2026 14:05', 'Submitted via Microsoft Forms by A1C Park')
)
$hy = 188
foreach ($h in $hist) {
    $d += Txt 928 ($hy + 18) $h[0] 12 '#111827' 'bold'
    $d += Txt 928 ($hy + 38) $h[1] 11 '#6B7280'
    $d += Txt 928 ($hy + 58) $h[2] 12 '#374151'
    $d += "<line x1='920' y1='$($hy + 78)' x2='1346' y2='$($hy + 78)' stroke='#E5E7EB'/>"
    $hy += 80
}
$d += Frame 916 182 434 496
$d += Tag 1200 652 'galHistory'
$d += Tag 1010 156 'lblHistoryTitle'
# action bar
$d += Rect 0 688 1366 80 '#F3F4F6'
$d += Rect 20 706 520 44 '#fff' '#9CA3AF'
$d += Txt 32 733 'Comment for the history log' 14 '#9CA3AF'
$d += Rect 560 706 130 44 '#E5E7EB' 'none' "rx='4'"
$d += Txt 625 733 'Save changes' 13 '#9CA3AF' 'bold' 'middle'
$d += Rect 705 706 150 44 '#fff' $navy "rx='4'"
$d += Txt 780 733 '← Send back' 13 $navy 'bold' 'middle'
$d += Rect 870 706 130 44 '#B22222' 'none' "rx='4'"
$d += Txt 935 733 'Reject' 13 '#fff' 'bold' 'middle'
$d += Rect 1015 706 331 44 $navy 'none' "rx='4'"
$d += Txt 1180 733 'Move to Implementation →' 14 '#fff' 'bold' 'middle'
# tags
$d += Tag 1240 4 'rectDetailHeader'
$d += Tag 16 50 'btnHome'
$d += Tag 560 40 'lblCRTitle'
$d += Frame 18 66 1330 70
$d += Tag 1200 112 'galProgress'
$d += Tag 210 686 'rectActionBar'
$d += Tag 380 686 'txtComment'
$d += Tag 572 686 'btnSave'
$d += Tag 718 686 'btnSendBack'
$d += Tag 880 686 'btnReject'
$d += Tag 1130 686 'btnAdvance'
Svg 'detail-layout.svg' $d
