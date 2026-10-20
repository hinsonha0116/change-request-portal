<#
.SYNOPSIS
    Creates the SharePoint lists that back the Change Request Power App.

.DESCRIPTION
    Creates two lists on the target site:
      - "Change Requests"         : one item per change request (the tickets)
      - "Change Request History"  : audit trail of every stage move

    Requires PnP.PowerShell 3.x (PowerShell 7.4+) and an Entra ID app registration
    for PnP (see https://pnp.github.io/powershell/articles/registerapplication.html).

.EXAMPLE
    ./Provision-ChangeRequestLists.ps1 -SiteUrl "https://contoso.sharepoint.com/sites/ITChange" -ClientId "00000000-0000-0000-0000-000000000000"
#>
param(
    [Parameter(Mandatory)] [string] $SiteUrl,
    [Parameter(Mandatory)] [string] $ClientId
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Module -ListAvailable -Name PnP.PowerShell)) {
    Install-Module PnP.PowerShell -Scope CurrentUser -Force
}

Connect-PnPOnline -Url $SiteUrl -ClientId $ClientId -Interactive

$Stages = @(
    'Requested',
    'Change Advisory Board',
    'Change Authority',
    'Implementation',
    'Review',
    'Close'
)

function Add-ListIfMissing([string] $Title) {
    if (-not (Get-PnPList -Identity $Title -ErrorAction SilentlyContinue)) {
        New-PnPList -Title $Title -Template GenericList -OnQuickLaunch | Out-Null
        Write-Host "Created list '$Title'"
    } else {
        Write-Host "List '$Title' already exists - adding any missing columns"
    }
}

function Add-FieldIfMissing {
    param(
        [string]   $List,
        [string]   $Name,
        [string]   $Type,
        [string[]] $Choices,
        [string]   $Default,
        [switch]   $Required
    )
    if (Get-PnPField -List $List -Identity $Name -ErrorAction SilentlyContinue) {
        # Keep choice lists in sync when the script is re-run against an existing list
        if ($Choices) {
            Set-PnPField -List $List -Identity $Name -Values @{ Choices = $Choices } | Out-Null
            Write-Host "  ~ $Name choices updated"
        }
        return
    }

    $params = @{
        List             = $List
        DisplayName      = $Name
        InternalName     = $Name
        Type             = $Type
        AddToDefaultView = $true
    }
    if ($Choices)  { $params.Choices  = $Choices }
    if ($Required) { $params.Required = $true }
    Add-PnPField @params | Out-Null

    # Plain-text multi-line fields behave best in Power Apps
    if ($Type -eq 'Note') {
        Set-PnPField -List $List -Identity $Name -Values @{ RichText = $false } | Out-Null
    }
    if ($Default) {
        Set-PnPField -List $List -Identity $Name -Values @{ DefaultValue = $Default } | Out-Null
    }
    Write-Host "  + $Name ($Type)"
}

# ---------------------------------------------------------------- Change Requests
$cr = 'Change Requests'
Add-ListIfMissing $cr

# "Title" already exists on every list - it is used as the change title.
# Choice values below must match the Microsoft Form radio-button text exactly.
Add-FieldIfMissing $cr 'Stage'              Choice   -Choices $Stages -Default 'Requested' -Required
Add-FieldIfMissing $cr 'A6Program'          Text
Add-FieldIfMissing $cr 'DSN'                Text
Add-FieldIfMissing $cr 'RequestedBy'        Text
Add-FieldIfMissing $cr 'RequesterEmail'     Text
Add-FieldIfMissing $cr 'Category'           Choice   -Choices 'Hardware','Software','Network'
Add-FieldIfMissing $cr 'ChangeType'         Choice   -Choices 'Standard','Normal','Emergency','Informational'
Add-FieldIfMissing $cr 'Description'        Note
Add-FieldIfMissing $cr 'Priority'           Choice   -Choices '4 - Low','3 - Moderate','2 - High','1 - Critical'
Add-FieldIfMissing $cr 'Risk'               Choice   -Choices '3 - Moderate','2 - High','1 - Critical'
Add-FieldIfMissing $cr 'Impact'             Choice   -Choices '3 - Moderate','2 - High','1 - Critical'
Add-FieldIfMissing $cr 'FormResponseId'     Number
# Rollback plan PDF and other uploads are stored as list-item attachments (enabled by default).
Add-FieldIfMissing $cr 'PlannedStart'       DateTime
Add-FieldIfMissing $cr 'PlannedEnd'         DateTime
Add-FieldIfMissing $cr 'Assignee'           User

# Change Advisory Board stage
Add-FieldIfMissing $cr 'CABDecision'        Choice   -Choices 'Pending','Approved','Rejected' -Default 'Pending'
Add-FieldIfMissing $cr 'CABNotes'           Note

# Change Authority stage
Add-FieldIfMissing $cr 'AuthorityDecision'  Choice   -Choices 'Pending','Approved','Rejected' -Default 'Pending'
Add-FieldIfMissing $cr 'AuthorityNotes'     Note

# Implementation stage
Add-FieldIfMissing $cr 'ImplementationNotes' Note
Add-FieldIfMissing $cr 'ActualStart'        DateTime
Add-FieldIfMissing $cr 'ActualEnd'          DateTime

# Review / Close stages
Add-FieldIfMissing $cr 'ReviewOutcome'      Choice   -Choices 'Successful','Successful with issues','Failed','Rolled back','Rejected'
Add-FieldIfMissing $cr 'ReviewNotes'        Note
Add-FieldIfMissing $cr 'ClosedDate'         DateTime

# ---------------------------------------------------------------- History (audit)
$hist = 'Change Request History'
Add-ListIfMissing $hist

Add-FieldIfMissing $hist 'RequestID' Number -Required
Add-FieldIfMissing $hist 'FromStage' Text
Add-FieldIfMissing $hist 'ToStage'   Text
Add-FieldIfMissing $hist 'Comment'   Note

# Index columns the app filters on so queries stay fast as the lists grow
Set-PnPField -List $cr   -Identity 'Stage'     -Values @{ Indexed = $true } | Out-Null
Set-PnPField -List $hist -Identity 'RequestID' -Values @{ Indexed = $true } | Out-Null

# ---------------------------------------------------------------- Rollback template
# Publish the fillable PDF so the app button and the form can link to it.
$template = Join-Path $PSScriptRoot 'Rollback-Plan-Template.pdf'
if (Test-Path $template) {
    Resolve-PnPFolder -SiteRelativePath 'Shared Documents/Change Templates' | Out-Null
    $file = Add-PnPFile -Path $template -Folder 'Shared Documents/Change Templates'
    $siteRoot = $SiteUrl -replace '(https://[^/]+).*', '$1'
    Write-Host "`nRollback template uploaded: $siteRoot$($file.ServerRelativeUrl)" -ForegroundColor Cyan
    Write-Host 'Use this URL for RollbackTemplateUrl in the app and in the form question subtitle.'
}

Write-Host "`nDone. Lists are ready at $SiteUrl" -ForegroundColor Green
