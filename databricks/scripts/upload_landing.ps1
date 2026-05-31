param(
    [Parameter(Mandatory = $true)]
    [string]$Catalog,

    [string]$BronzeSchema = "ecommerce_bronze",
    [string]$VolumeName = "landing",
    [string]$Profile = "DEFAULT"
)

$projectRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$landingDir = Join-Path $projectRoot "data\landing"
$target = "dbfs:/Volumes/$Catalog/$BronzeSchema/$VolumeName"

Get-ChildItem -LiteralPath $landingDir -Directory | ForEach-Object {
    $batchDir = $_
    $batchTarget = "$target/$($batchDir.Name)"

    databricks fs mkdir $batchTarget --profile $Profile
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }

    Get-ChildItem -LiteralPath $batchDir.FullName -File | ForEach-Object {
        $destination = "$batchTarget/$($_.Name)"
        databricks fs cp $_.FullName $destination --overwrite --profile $Profile
        if ($LASTEXITCODE -ne 0) {
            exit $LASTEXITCODE
        }
    }
}

databricks fs ls $target --profile $Profile
