Param(
    [parameter(mandatory=$true)][String]$dumpFile
)

$scriptDir = Split-Path -Path $MyInvocation.MyCommand.Definition -Parent

$secretsDir = Resolve-Path (Join-Path -Path $scriptDir -ChildPath "..\secrets")
$userFile = Join-Path -Path $secretsDir -ChildPath "postgres_user"
$passwordFile = Join-Path -Path $secretsDir -ChildPath "postgres_password"
$dbNameFile = Join-Path -Path $secretsDir -ChildPath "postgres_db"

$dumpFileRes = Resolve-Path $dumpFile
$dumpFileLeaf = Split-Path -Path $dumpFileRes -Leaf
$serviceName = "kokkai-summary-db"

Write-Host "Starting database restore..."
Write-Host "Input file: ${dumpFileRes}"

$user = Get-Content -Path $userFile -Raw
$password = Get-Content -Path $passwordFile -Raw
$dbName = Get-Content -Path $dbNameFile -Raw

docker cp $dumpFileRes ${serviceName}:/tmp/$dumpFileLeaf
docker exec -e PGPASSWORD=$password $serviceName pg_restore -U $user -d $dbName --clean --if-exists /tmp/$dumpFileLeaf
docker exec $serviceName rm /tmp/$dumpFileLeaf

if ($LASTEXITCODE -eq 0) {
    Write-Host "Database restore completed successfully."
} else {
    Write-Host "Error: Database restore failed."
}