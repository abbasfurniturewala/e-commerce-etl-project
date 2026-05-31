param(
    [string]$WarehouseId = $env:DATABRICKS_SQL_WAREHOUSE_ID,
    [string]$Profile = "DEFAULT",
    [string]$QueryDirectory = (Join-Path $PSScriptRoot "..\sql"),
    [int]$PollIntervalSeconds = 2,
    [int]$TimeoutSeconds = 180
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($WarehouseId)) {
    throw "Set DATABRICKS_SQL_WAREHOUSE_ID or pass -WarehouseId."
}

if (-not (Get-Command databricks -ErrorAction SilentlyContinue)) {
    throw "Databricks CLI was not found. Open a fresh PowerShell window after installing it."
}

$queryPath = Resolve-Path $QueryDirectory
$queryFiles = @(Get-ChildItem -LiteralPath $queryPath -File -Filter "*.sql" | Sort-Object Name)

if ($queryFiles.Count -eq 0) {
    throw "No SQL query files were found beneath $queryPath."
}

function Invoke-DatabricksApiPost {
    param(
        [string]$Path,
        [hashtable]$Body
    )

    $requestFile = [System.IO.Path]::GetTempFileName()

    try {
        $json = $Body | ConvertTo-Json -Depth 10
        $utf8WithoutBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($requestFile, $json, $utf8WithoutBom)
        $rawResponse = (& databricks api post $Path --json "@$requestFile" --profile $Profile --output json | Out-String)

        if ($LASTEXITCODE -ne 0) {
            throw "Databricks API POST failed for $Path."
        }

        if ([string]::IsNullOrWhiteSpace($rawResponse)) {
            throw "Databricks API POST returned an empty response for $Path."
        }

        return $rawResponse | ConvertFrom-Json
    }
    finally {
        Remove-Item -LiteralPath $requestFile -Force -ErrorAction SilentlyContinue
    }
}

function Invoke-DatabricksApiGet {
    param([string]$Path)

    $rawResponse = (& databricks api get $Path --profile $Profile --output json | Out-String)

    if ($LASTEXITCODE -ne 0) {
        throw "Databricks API GET failed for $Path."
    }

    if ([string]::IsNullOrWhiteSpace($rawResponse)) {
        throw "Databricks API GET returned an empty response for $Path."
    }

    return $rawResponse | ConvertFrom-Json
}

foreach ($queryFile in $queryFiles) {
    $statement = [System.IO.File]::ReadAllText($queryFile.FullName)
    $response = Invoke-DatabricksApiPost -Path "/api/2.0/sql/statements" -Body @{
        warehouse_id = $WarehouseId
        statement = $statement
        catalog = "workspace"
        schema = "ecommerce_gold"
        wait_timeout = "10s"
        on_wait_timeout = "CONTINUE"
        format = "JSON_ARRAY"
        disposition = "INLINE"
        row_limit = 100
    }

    $timer = [System.Diagnostics.Stopwatch]::StartNew()

    while ($response.status.state -in @("PENDING", "RUNNING")) {
        if ($timer.Elapsed.TotalSeconds -ge $TimeoutSeconds) {
            throw "Timed out waiting for $($queryFile.Name)."
        }

        Start-Sleep -Seconds $PollIntervalSeconds
        $response = Invoke-DatabricksApiGet -Path "/api/2.0/sql/statements/$($response.statement_id)"
    }

    if ($response.status.state -ne "SUCCEEDED") {
        throw "$($queryFile.Name) failed: $($response.status.error.message)"
    }

    $rowCount = $response.manifest.total_row_count
    Write-Host "[PASS] $($queryFile.Name): $rowCount rows"
}
